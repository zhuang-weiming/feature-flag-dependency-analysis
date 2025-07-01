"""
Data Flow Analysis for Feature Flag Variables (Prototype)
- Tracks definitions and uses of feature flag variables in Python code using AST.
- Step 1: Identify feature flag variable definitions and uses.
"""
import ast
from collections import defaultdict

class FeatureFlagDataFlowAnalyzer(ast.NodeVisitor):
    def __init__(self, flag_names=None, sensitive_ops=None):
        # Optionally provide a set of known feature flag variable names
        self.flag_names = set(flag_names) if flag_names else set()
        self.definitions = defaultdict(list)  # {flag_name: [definition_node]}
        self.uses = defaultdict(list)         # {flag_name: [use_node]}
        self.tainted_vars = set(self.flag_names)  # variables tainted by feature flags
        self.assignments = []  # (target, value, node)
        # Allow user to customize sensitive operations
        if sensitive_ops:
            self.sensitive_ops = set(sensitive_ops)
        else:
            self.sensitive_ops = {'print', 'log', 'send', 'write', 'save', 'record', 'execute', 'commit'}
        self.taint_to_sensitive = []  # (sink_func, tainted_var, node)
        self.function_params = {}  # {func_name: [param_names]}
        self.tainted_params = defaultdict(set)  # {func_name: set(param_names)}
        self.tainted_returns = set()  # functions whose return value is tainted

    def visit_FunctionDef(self, node):
        param_names = [arg.arg for arg in node.args.args]
        self.function_params[node.name] = param_names
        # If any parameter is tainted at call site, mark as tainted in function
        for param in param_names:
            if param in self.tainted_vars:
                self.tainted_params[node.name].add(param)
        # Analyze function body for tainted return
        self.current_function = node.name
        self.return_tainted = False
        self.generic_visit(node)
        if self.return_tainted:
            self.tainted_returns.add(node.name)
        self.current_function = None

    def visit_Return(self, node):
        # If returning a tainted variable, mark function as tainted-return
        if isinstance(node.value, ast.Name):
            if node.value.id in self.tainted_vars or (
                self.current_function and node.value.id in self.tainted_params[self.current_function]
            ):
                self.return_tainted = True
        self.generic_visit(node)

    def visit_Assign(self, node):
        # Track assignments to feature flag variables and taint propagation
        for target in node.targets:
            if isinstance(target, ast.Name):
                var_name = target.id
                # Check if assigning from a function call with tainted return
                if isinstance(node.value, ast.Call):
                    func_name = self._get_func_name(node.value.func)
                    if func_name in self.tainted_returns:
                        self.tainted_vars.add(var_name)
                        self.assignments.append((var_name, f"{func_name}()", node))
                # Check if assigning from a feature flag or tainted variable
                if isinstance(node.value, ast.Name):
                    src_var = node.value.id
                    if src_var in self.tainted_vars:
                        self.tainted_vars.add(var_name)
                        self.assignments.append((var_name, src_var, node))
                # If this is a feature flag definition
                if self.is_feature_flag(var_name, node):
                    self.flag_names.add(var_name)
                    self.tainted_vars.add(var_name)
                    self.definitions[var_name].append(node)
        self.generic_visit(node)

    def visit_Name(self, node):
        # Track uses of feature flag variables
        if node.id in self.flag_names and not isinstance(node.ctx, ast.Store):
            self.uses[node.id].append(node)
        self.generic_visit(node)

    def visit_Call(self, node):
        func_name = self._get_func_name(node.func)
        # Sensitive operation taint check
        if func_name and func_name in self.sensitive_ops:
            for arg in node.args:
                if isinstance(arg, ast.Name) and arg.id in self.tainted_vars:
                    self.taint_to_sensitive.append((func_name, arg.id, node))
        # Cross-function taint propagation: if tainted var is passed as arg, mark param as tainted
        if func_name in self.function_params:
            for idx, arg in enumerate(node.args):
                if isinstance(arg, ast.Name) and arg.id in self.tainted_vars:
                    params = self.function_params[func_name]
                    if idx < len(params):
                        self.tainted_params[func_name].add(params[idx])
        self.generic_visit(node)

    def _get_func_name(self, func):
        # Helper to extract function name from ast node
        if isinstance(func, ast.Name):
            return func.id
        elif isinstance(func, ast.Attribute):
            return func.attr
        return None

    def is_feature_flag(self, var_name, node):
        # Heuristic: variable name contains 'flag' or is in known set
        return 'flag' in var_name.lower() or var_name in self.flag_names

    def report(self):
        print("Feature Flag Definitions:")
        for flag, defs in self.definitions.items():
            for d in defs:
                print(f"  {flag} defined at line {d.lineno}")
        print("\nFeature Flag Uses:")
        for flag, uses in self.uses.items():
            for u in uses:
                print(f"  {flag} used at line {u.lineno}")
        print("\nTainted Variable Propagation:")
        for tgt, src, node in self.assignments:
            print(f"  {tgt} tainted by {src} at line {node.lineno}")
        print("\nTainted Function Parameters:")
        for func, params in self.tainted_params.items():
            for param in params:
                print(f"  Parameter '{param}' in function '{func}' is tainted by feature flag")
        print("\nTaint Reaching Sensitive Operations:")
        for sink_func, tainted_var, node in self.taint_to_sensitive:
            print(f"  {tainted_var} flows to sensitive op '{sink_func}' at line {node.lineno}")

# Example usage
if __name__ == "__main__":
    code = '''
flag_a = True
if flag_a:
    print("Feature enabled")
flag_b = False
x = flag_b
if x:
    print("Another feature")
def func_with_flag_param(flag_param):
    if flag_param:
        print("Flagged function executed")
func_with_flag_param(flag_a)
'''
    tree = ast.parse(code)
    analyzer = FeatureFlagDataFlowAnalyzer()
    analyzer.visit(tree)
    analyzer.report()
