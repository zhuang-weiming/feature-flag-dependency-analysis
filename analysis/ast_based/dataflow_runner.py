"""
Data Flow Analysis runner for feature flag dependencies.
Scans Python source files and outputs feature flag dependencies as JSON, with source marked as 'dataflow_analysis'.
"""
import sys
import json
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../src')))
from cli.end_to_end_demo import collect_files, EXTENSIONS
from ast_analysis.dataflow_analysis import FeatureFlagDataFlowAnalyzer

def run_dataflow_analysis(target_dir, lang, output_path):
    if lang != 'python':
        raise NotImplementedError('Only Python is supported for dataflow analysis prototype.')
    files = collect_files(target_dir, EXTENSIONS[lang])
    findings = []
    for file_path in files:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            code = f.read()
        analyzer = FeatureFlagDataFlowAnalyzer()
        analyzer.visit(__import__('ast').parse(code))
        # Collect all taint flows to sensitive operations
        for sink_func, tainted_var, node in analyzer.taint_to_sensitive:
            findings.append({
                'file': file_path,
                'line': getattr(node, 'lineno', None),
                'code': getattr(node, 'source', code.splitlines()[node.lineno-1] if hasattr(node, 'lineno') else ''),
                'context': None,
                'dependency': tainted_var,
                'source': 'dataflow_analysis',
                'detail': f"Taint flows to sensitive op '{sink_func}'"
            })
    with open(output_path, 'w') as f:
        json.dump(findings, f, indent=2)
    print(f"Dataflow analysis results saved to {output_path}")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Run Data Flow Analysis for feature flag dependencies.")
    parser.add_argument("target_dir", help="Directory to scan")
    parser.add_argument("lang", help="Language (python only)")
    parser.add_argument("output_path", help="Output JSON file")
    args = parser.parse_args()
    run_dataflow_analysis(args.target_dir, args.lang, args.output_path)
