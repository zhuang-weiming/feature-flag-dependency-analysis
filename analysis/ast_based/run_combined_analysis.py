"""
Combined static analysis runner: runs Semgrep and AST-based analyzers for feature flag dependencies in Python projects.
"""
import os
import subprocess
import json
from src.feature_flag.reasoning import AnalyzerFactory, Reasoner

PYTHON_PROJECT = "sample_project_python"
SEMGREP_RULE = "semgrep_rules/python-feature-flags.yml"
SEMGREP_OUTPUT = "semgrep_auto_scan_result.json"

# 1. Run Semgrep
print("Running Semgrep static analysis...")
semgrep_cmd = [
    "semgrep",
    "--config", SEMGREP_RULE,
    "--json", "-o", SEMGREP_OUTPUT,
    PYTHON_PROJECT
]
result = subprocess.run(semgrep_cmd, capture_output=True, text=True)
print(result.stdout)
print(result.stderr)

# 2. Run AST-based analyzer
print("\nRunning AST-based analyzer...")
from src.cli.end_to_end_demo import collect_files, EXTENSIONS
analyzer = AnalyzerFactory.get_analyzer("python")
files = collect_files(PYTHON_PROJECT, EXTENSIONS["python"])
print(f"  Found {len(files)} source files.")
dependencies = []
for file_path in files:
    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
        code = f.read()
    deps = analyzer.analyze(code)
    for dep in deps:
        dep['file'] = file_path
        dependencies.append(dep)
print(f"  Found {len(dependencies)} feature flag dependencies.")

# 3. Print summary and compare
print("\nSummary:")
print(f"Semgrep results saved to: {SEMGREP_OUTPUT}")
print(f"AST-based dependencies found: {len(dependencies)}")

# Optionally, print details
print("\nAST-based dependencies:")
for dep in dependencies:
    print(dep)

# Optionally, compare with Semgrep output
try:
    with open(SEMGREP_OUTPUT) as f:
        semgrep_data = json.load(f)
    print("\nSemgrep findings:")
    for finding in semgrep_data.get('results', []):
        print({
            'file': finding.get('path'),
            'start': finding.get('start', {}).get('line'),
            'match': finding.get('extra', {}).get('lines')
        })
except Exception as e:
    print(f"Could not read Semgrep output: {e}")
