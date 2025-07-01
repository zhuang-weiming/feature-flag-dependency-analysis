"""
Visualize the merged feature flag dependency graph and print a summary report.
- Shows a simple text-based graph (flag -> function context)
- Prints counts and unique flags/contexts
- Optionally, outputs a Graphviz DOT file for visualization
"""
import json
from collections import defaultdict

with open('merged_flag_dependencies.json') as f:
    merged = json.load(f)

graph = defaultdict(set)
flag_counts = defaultdict(int)
context_counts = defaultdict(int)
unique_flags = set()
unique_contexts = set()

for entry in merged:
    dep = entry.get('dependency')
    context = entry.get('context')
    if dep and context:
        graph[dep].add(context)
        flag_counts[dep] += 1
        context_counts[context] += 1
        unique_flags.add(dep)
        unique_contexts.add(context)

print("Feature Flag Dependency Graph (flag -> function context):\n")
for flag, contexts in graph.items():
    print(f"  {flag} -> {', '.join(contexts)}")

print("\nSummary Report:")
print(f"  Total unique flags: {len(unique_flags)}")
print(f"  Total unique contexts: {len(unique_contexts)}")
print(f"  Total flag->context edges: {sum(len(c) for c in graph.values())}")

print("\nTop flags by usage:")
for flag, count in sorted(flag_counts.items(), key=lambda x: -x[1]):
    print(f"  {flag}: {count}")

print("\nTop contexts by flag checks:")
for ctx, count in sorted(context_counts.items(), key=lambda x: -x[1]):
    print(f"  {ctx}: {count}")

# Optionally, output Graphviz DOT file
with open('flag_dependency_graph.dot', 'w') as f:
    f.write('digraph FeatureFlagDeps {\n')
    for flag, contexts in graph.items():
        for ctx in contexts:
            f.write(f'  "{flag}" -> "{ctx}";\n')
    f.write('}\n')
print("\nGraphviz DOT file saved as flag_dependency_graph.dot (for visualization)")
