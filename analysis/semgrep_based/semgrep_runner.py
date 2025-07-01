"""
Semgrep-based feature flag dependency analysis runner.
Runs Semgrep with the provided rules and outputs results as JSON.
"""
import subprocess
import sys
import json

def run_semgrep(target_dir, rule_path, output_path):
    cmd = [
        "semgrep",
        "--config", rule_path,
        "--json", "-o", output_path,
        target_dir
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    print(result.stdout)
    print(result.stderr)
    if result.returncode != 0:
        print(f"Semgrep failed with exit code {result.returncode}")
        sys.exit(result.returncode)
    print(f"Semgrep results saved to {output_path}")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Run Semgrep for feature flag analysis.")
    parser.add_argument("target_dir", help="Directory to scan")
    parser.add_argument("rule_path", help="Semgrep rule YAML file")
    parser.add_argument("output_path", help="Output JSON file")
    args = parser.parse_args()
    run_semgrep(args.target_dir, args.rule_path, args.output_path)
