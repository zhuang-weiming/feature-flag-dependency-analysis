import subprocess
import json
from collections import defaultdict, deque
import re
import os
import networkx as nx
from pyvis.network import Network

def run_semgrep(rule_path, target_dir):
    """运行 Semgrep 并返回 JSON 结果"""
    result = subprocess.run([
        'semgrep',
        '--config', rule_path,
        '--json',
        target_dir
    ], capture_output=True, text=True)
    if result.returncode > 1:
        print(f"Error running Semgrep: {result.stderr}")
        return None
    try:
        return json.loads(result.stdout)
    except json.JSONDecodeError:
        print("Error parsing Semgrep JSON output:")
        print(result.stdout)
        return None

def find_function_for_line(file_path, line_number):
    with open(file_path, 'r') as f:
        lines = f.readlines()
    
    function_name = None
    for i in range(line_number - 1, -1, -1):
        match = re.match(r"^def\s+([a-zA-Z0-9_]+)", lines[i].strip())
        if match:
            function_name = match.group(1)
            break
    return function_name

def extract_flag_usages(flag_json):
    """提取特性开关使用点"""
    usages = []
    flag_regex = re.compile(r'is_feature_enabled\((?:"|\')?([a-zA-Z0-9_\-]+)(?:"|\')?\)')
    for r in flag_json.get("results", []):
        file_path = r["path"]
        line_number = r["start"]["line"]
        with open(file_path, 'r') as f:
            lines = f.readlines()
            code_line = lines[line_number - 1]
        match = flag_regex.search(code_line)
        if not match:
            continue
        flag_name = match.group(1)
        function_name = find_function_for_line(file_path, line_number)
        usages.append({
            'flag': flag_name,
            'file': file_path,
            'line': line_number,
            'function': function_name
        })
    return usages

def extract_call_graph(call_json):
    """构建函数调用图（函数名->被调用函数名集合）"""
    call_graph = defaultdict(set)
    for r in call_json.get("results", []):
        if r['check_id'] == 'python-function-call':
            # 这里简单用正则提取调用者函数名
            file_path = r["path"]
            line_number = r["start"]["line"]
            called_func = r['extra']['metavars'].get('$FUNC')
            caller_func = find_function_for_line(file_path, line_number)
            if caller_func and called_func:
                call_graph[(caller_func, file_path)].add((called_func, file_path))
    return call_graph

def aggregate_flags_by_function(flag_usages):
    """统计每个函数直接使用的flag集合"""
    function_flags = defaultdict(set)
    for usage in flag_usages:
        if usage['function']:
            function_flags[(usage['function'], usage['file'])].add(usage['flag'])
    return function_flags

def propagate_flags(call_graph, function_flags):
    """沿调用图向上传播flag依赖"""
    all_flags = {f: set(flags) for f, flags in function_flags.items()}
    changed = True
    while changed:
        changed = False
        for caller, callees in call_graph.items():
            for callee in callees:
                before = len(all_flags.get(caller, set()))
                all_flags.setdefault(caller, set()).update(all_flags.get(callee, set()))
                if len(all_flags[caller]) > before:
                    changed = True
    return all_flags

def detect_cycles(call_graph):
    """检测循环依赖"""
    G = nx.DiGraph()
    for caller, callees in call_graph.items():
        for callee in callees:
            G.add_edge(caller, callee)
    cycles = list(nx.simple_cycles(G))
    return cycles

def visualize_dependency_graph(all_flags, call_graph, cycles, output_html='dependency_graph.html'):
    """可视化依赖图谱"""
    net = Network(height='800px', width='100%', notebook=False, directed=True)
    # 节点：函数@文件，标签包含flag
    for func, flags in all_flags.items():
        label = f"{func[0]}\n{os.path.basename(func[1])}\nFlags: {', '.join(flags)}"
        color = 'red' if len(flags) > 1 else 'lightblue'
        net.add_node(str(func), label=label, color=color)
    # 边：调用关系
    for caller, callees in call_graph.items():
        for callee in callees:
            net.add_edge(str(caller), str(callee))
    # 高亮循环依赖
    for cycle in cycles:
        for i in range(len(cycle)):
            net.add_edge(str(cycle[i]), str(cycle[(i+1)%len(cycle)]), color='orange', width=3)
    net.show(output_html)
    print(f"Interactive dependency graph saved to {output_html}")

def analyze_dependencies():
    # 配置路径
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    flag_rule = os.path.join(base_dir, 'semgrep_rules', 'python-feature-flags.yml')
    callgraph_rule = os.path.join(base_dir, 'semgrep_rules', 'python-call-graph.yml')
    sample_dir = os.path.join(base_dir, 'sample_project_python')

    # 1. 提取特性开关使用点
    flag_json = run_semgrep(flag_rule, sample_dir)
    if not flag_json:
        return
    flag_usages = extract_flag_usages(flag_json)
    print('Feature flag usages:', flag_usages)

    # 2. 提取函数调用关系
    call_json = run_semgrep(callgraph_rule, sample_dir)
    if not call_json:
        return
    call_graph = extract_call_graph(call_json)
    print('Call graph:', dict(call_graph))

    # 3. 统计每个函数的flag集合
    function_flags = aggregate_flags_by_function(flag_usages)
    # 4. 沿调用图传播flag依赖
    all_flags = propagate_flags(call_graph, function_flags)

    # 检测循环依赖
    cycles = detect_cycles(call_graph)
    if cycles:
        print("Cyclic dependencies detected:")
        for cycle in cycles:
            print(" -> ".join([f"{c[0]}@{os.path.basename(c[1])}" for c in cycle]))
    else:
        print("No cyclic dependencies detected.")

    # 交互式依赖图谱
    visualize_dependency_graph(all_flags, call_graph, cycles)

    # 控制台输出共现依赖
    print("\nFeature Flag Dependencies (including call graph propagation):")
    for function, flags in all_flags.items():
        if len(flags) > 1:
            print(f"  - In function '{function[0]}' ({os.path.basename(function[1])}), the following flags are used together:")
            for flag in sorted(list(flags)):
                print(f"    - {flag}")

if __name__ == "__main__":
    analyze_dependencies()
