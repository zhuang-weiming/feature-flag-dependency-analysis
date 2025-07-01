"""
End-to-end demo: Analyze feature flag dependencies in real sample projects (Python, Java, Go, JavaScript).
"""
import os
from feature_flag.reasoning import AnalyzerFactory, Reasoner

# Use absolute paths for all projects
PROJECTS = [
    ("/Users/weimingzhuang/Documents/source_code/feature-flag-dependency-analysis/sample_project_python", "python"),
    ("/Users/weimingzhuang/Documents/source_code/feature-flag-dependency-analysis/sample_project_java", "java"),
    ("/Users/weimingzhuang/Documents/source_code/unleash-managed-projects-sample", "javascript"),
    ("/Users/weimingzhuang/Documents/source_code/unleash-managed-projects-sample", "java"),
    ("/Users/weimingzhuang/Documents/source_code/CloudBees-sample-Go-app", "go"),
]

# Helper: collect all source files for a language
EXTENSIONS = {
    'python': ['.py'],
    'java': ['.java'],
    'go': ['.go'],
    'javascript': ['.js', '.jsx'],
}

def collect_files(root, exts):
    files = []
    for dirpath, _, filenames in os.walk(root):
        for f in filenames:
            if any(f.endswith(ext) for ext in exts):
                files.append(os.path.join(dirpath, f))
    return files

def main():
    dependency_graph = {}
    total_dependencies = 0
    for project_path, lang in PROJECTS:
        print(f"\nAnalyzing project: {project_path} (language: {lang})")
        analyzer = AnalyzerFactory.get_analyzer(lang)
        files = collect_files(project_path, EXTENSIONS[lang])
        print(f"  Found {len(files)} source files.")
        project_dependencies = 0
        for file_path in files:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                code = f.read()
            deps = analyzer.analyze(code)
            for dep in deps:
                flag = dep.get('flag') or dep.get('dependency')
                context = dep.get('context')
                if flag:
                    key = (flag, context) if context else flag
                    dependency_graph.setdefault(key, set())
                    dependency_graph[key].add(flag)  # For demo: self-loop
                    project_dependencies += 1
        print(f"  Found {project_dependencies} feature flag dependencies.")
        total_dependencies += project_dependencies
    if not dependency_graph:
        print("\nNo feature flag dependencies found in any project.")
        return
    # Convert sets to lists
    for k in dependency_graph:
        dependency_graph[k] = list(dependency_graph[k])
    reasoner = Reasoner(dependency_graph)
    print(f"\nTotal unique feature flag dependencies: {len(dependency_graph)}")
    print("Cycles:", reasoner.detect_cycles())
    print("Dead flags:", reasoner.find_dead_flags())
    if dependency_graph:
        print("Impact of first flag:", reasoner.flag_impact(next(iter(dependency_graph))))

if __name__ == "__main__":
    main()
