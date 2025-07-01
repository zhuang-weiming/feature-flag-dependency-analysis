"""
Full demo: Run Semgrep-based and AST-based feature flag analysis, merge, report, and visualize in one script.
"""
import subprocess
import sys
import os

# Paths
PYTHON_PROJECT = "sample_project_python"
SEMGREP_RULE = "semgrep_rules/python-feature-flags.yml"
SEMGREP_OUTPUT = "semgrep_auto_scan_result.json"
AST_OUTPUT = "ast_auto_scan_result.json"
MERGED_OUTPUT = "merged_flag_dependencies.json"

# 1. Run Semgrep-based analysis
print("[1/5] Running Semgrep-based analysis...")
subprocess.run([
    sys.executable, "analysis/semgrep_based/semgrep_runner.py",
    PYTHON_PROJECT, SEMGREP_RULE, SEMGREP_OUTPUT
], check=True)

# 2. Run AST-based analysis
print("[2/5] Running AST-based analysis...")
subprocess.run([
    sys.executable, "analysis/ast_based/ast_runner.py",
    PYTHON_PROJECT, "python", AST_OUTPUT
], check=True, env={**os.environ, "PYTHONPATH": "src"})

# 3. Merge and deduplicate results
print("[3/5] Merging and deduplicating results...")
subprocess.run([
    sys.executable, "analysis/ast_based/merge_flag_results.py"
], check=True)

# 4. Generate conflict/complexity report
print("[4/5] Generating conflict/complexity report...")
subprocess.run([
    sys.executable, "analysis/ast_based/flag_dependency_conflict_report.py"
], check=True)

# 5. Visualize the dependency graph
print("[5/5] Visualizing the dependency graph...")
subprocess.run([
    sys.executable, "analysis/ast_based/visualize_flag_graph.py"
], check=True)

print("\nDemo complete! See outputs in:")
print(f"- {SEMGREP_OUTPUT}\n- {AST_OUTPUT}\n- {MERGED_OUTPUT}\n- flag_dependency_graph.dot\n")
