"""
Merge and deduplicate Semgrep and AST-based feature flag dependency results for unified reporting.
Filters out function definitions from AST results for parity with Semgrep.
"""
import json
import re

# Load Semgrep results
with open('semgrep_auto_scan_result.json') as f:
    semgrep_data = json.load(f)

semgrep_flags = set()
semgrep_entries = []
for finding in semgrep_data.get('results', []):
    file = finding.get('path')
    line = finding.get('start', {}).get('line')
    code = finding.get('extra', {}).get('lines')
    # Use a tuple for deduplication
    key = (file, line, code)
    semgrep_flags.add(key)
    semgrep_entries.append({'file': file, 'line': line, 'code': code, 'source': 'semgrep'})

# Load AST results
with open('ast_auto_scan_result.json') as f:
    ast_data = json.load(f)

ast_flags = set()
ast_entries = []
for dep in ast_data:
    file = dep.get('file')
    line = dep.get('lineno')
    code = dep.get('code')
    context = dep.get('context')
    dependency = dep.get('dependency')
    # Filter out function definitions (e.g., code starts with 'def is_feature_enabled')
    if re.match(r'^def is_feature_enabled', code):
        continue
    key = (file, line, code)
    ast_flags.add(key)
    ast_entries.append({'file': file, 'line': line, 'code': code, 'context': context, 'dependency': dependency, 'source': 'ast'})

# Merge and deduplicate
merged = {}
for entry in semgrep_entries + ast_entries:
    key = (entry['file'], entry['line'], entry['code'])
    if key not in merged:
        merged[key] = entry
    else:
        # Merge sources
        merged[key]['source'] = (
            merged[key]['source'] + '+' + entry['source']
            if entry['source'] not in merged[key]['source'] else merged[key]['source']
        )

# Output merged results
merged_list = list(merged.values())
print(f"Total unique feature flag dependencies: {len(merged_list)}\n")
for entry in merged_list:
    print(entry)

# Optionally, save to file
with open('merged_flag_dependencies.json', 'w') as f:
    json.dump(merged_list, f, indent=2)
print("\nMerged results saved to merged_flag_dependencies.json")
