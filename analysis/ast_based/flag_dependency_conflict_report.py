"""
Enhanced summary report: show feature flag dependencies and detect conflicts (flags used in multiple contexts or with overlapping logic).
"""
import json
from collections import defaultdict

with open('merged_flag_dependencies.json') as f:
    merged = json.load(f)

graph = defaultdict(set)
flag_to_contexts = defaultdict(set)
context_to_flags = defaultdict(set)

for entry in merged:
    dep = entry.get('dependency')
    context = entry.get('context')
    if dep and context:
        graph[dep].add(context)
        flag_to_contexts[dep].add(context)
        context_to_flags[context].add(dep)

print("Feature Flag Dependency Graph (flag -> function context):\n")
for flag, contexts in graph.items():
    print(f"  {flag} -> {', '.join(contexts)}")

print("\nSummary Report:")
print(f"  Total unique flags: {len(flag_to_contexts)}")
print(f"  Total unique contexts: {len(context_to_flags)}")
print(f"  Total flag->context edges: {sum(len(c) for c in graph.values())}")

# Detect conflicts: flags used in multiple contexts
print("\nPotential Conflicts (flags used in multiple contexts):")
conflict_found = False
for flag, contexts in flag_to_contexts.items():
    if len(contexts) > 1:
        print(f"  [CONFLICT] Flag '{flag}' is used in multiple contexts: {', '.join(contexts)}")
        conflict_found = True
if not conflict_found:
    print("  No conflicts detected.")

# Detect contexts with multiple flags (possible complex logic)
print("\nContexts with multiple flags (possible complex/compound logic):")
complex_found = False
for ctx, flags in context_to_flags.items():
    if len(flags) > 1:
        print(f"  [COMPLEX] Context '{ctx}' checks multiple flags: {', '.join(flags)}")
        complex_found = True
if not complex_found:
    print("  No complex/compound flag logic detected.")
