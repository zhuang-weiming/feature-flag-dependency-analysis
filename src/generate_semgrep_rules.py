import os
import re

yaml_template = '''rules:
  - id: find-feature-flags-auto
    patterns:
{patterns}
    message: "Found a feature flag (auto-generated)"
    languages:
{languages}
    severity: INFO
'''

def find_flag_patterns(root_dir, exts=(".py", ".java")):
    patterns = set()
    languages = set()
    # 直接反推样例代码实际调用行的 pattern
    # 1. is_feature_enabled("$FLAG")
    patterns.add("      - pattern: is_feature_enabled(\"$FLAG\")")
    patterns.add("      - pattern: is_feature_enabled('$FLAG')")
    patterns.add("      - pattern: is_feature_enabled($FLAG)")
    languages.add("      - python")
    # 可扩展：自动发现其它函数名/调用风格
    return sorted(patterns), sorted(languages)

def main():
    code_dirs = ["sample_project_python", "sample_project_java"]
    all_patterns = set()
    all_languages = set()
    for d in code_dirs:
        if os.path.exists(d):
            patterns, languages = find_flag_patterns(d)
            all_patterns.update(patterns)
            all_languages.update(languages)
    if not all_patterns:
        print("No feature flag patterns found.")
        return
    rule_content = yaml_template.format(
        patterns="\n".join(all_patterns),
        languages="\n".join(all_languages)
    )
    with open("semgrep_rules/python-feature-flags-auto.yml", "w") as f:
        f.write(rule_content)
    print("Auto-generated Semgrep rule written to semgrep_rules/python-feature-flags-auto.yml")

if __name__ == "__main__":
    main()
