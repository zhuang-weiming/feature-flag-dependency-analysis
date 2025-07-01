"""
AST-based feature flag dependency analysis runner.
Scans Python source files and outputs feature flag dependencies as JSON.
"""
import sys
import json
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../src')))
from cli.end_to_end_demo import collect_files, EXTENSIONS
from feature_flag.reasoning import AnalyzerFactory

def run_ast_analysis(target_dir, lang, output_path):
    analyzer = AnalyzerFactory.get_analyzer(lang)
    files = collect_files(target_dir, EXTENSIONS[lang])
    dependencies = []
    for file_path in files:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            code = f.read()
        deps = analyzer.analyze(code)
        for dep in deps:
            dep['file'] = file_path
            dependencies.append(dep)
    with open(output_path, 'w') as f:
        json.dump(dependencies, f, indent=2)
    print(f"AST-based dependencies saved to {output_path}")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Run AST-based feature flag analysis.")
    parser.add_argument("target_dir", help="Directory to scan")
    parser.add_argument("lang", help="Language (python, java, etc.)")
    parser.add_argument("output_path", help="Output JSON file")
    args = parser.parse_args()
    run_ast_analysis(args.target_dir, args.lang, args.output_path)
