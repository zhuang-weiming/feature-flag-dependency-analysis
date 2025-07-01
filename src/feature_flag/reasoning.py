# Static reasoning algorithms (placeholder)

class Reasoner:
    """
    Provides static reasoning algorithms for feature flag dependency analysis.
    """
    def __init__(self, dependency_graph):
        self.graph = dependency_graph

    def detect_cycles(self):
        """Detect cycles in the feature flag dependency graph."""
        visited = set()
        stack = set()
        cycles = []

        def visit(node, path):
            if node in stack:
                cycles.append(path + [node])
                return
            if node in visited:
                return
            visited.add(node)
            stack.add(node)
            for neighbor in self.graph.get(node, []):
                visit(neighbor, path + [node])
            stack.remove(node)

        for node in self.graph:
            visit(node, [])
        return cycles

    def find_dead_flags(self):
        """Find feature flags that are never used as dependencies."""
        all_flags = set(self.graph.keys())
        used_flags = set()
        for deps in self.graph.values():
            used_flags.update(deps)
        return list(all_flags - used_flags)

    def flag_impact(self, flag):
        """Return all flags transitively impacted by the given flag."""
        impacted = set()
        def dfs(node):
            for neighbor in self.graph.get(node, []):
                if neighbor not in impacted:
                    impacted.add(neighbor)
                    dfs(neighbor)
        dfs(flag)
        return list(impacted)

# --- Language-agnostic analyzer interface ---

class AnalyzerFactory:
    """
    Factory to select the correct analyzer based on language.
    Extend this to support more languages (Python, Java, Go, JavaScript, etc).
    """
    @staticmethod
    def get_analyzer(language):
        """
        Returns the appropriate analyzer instance for the given language.
        Supported: python, java, go, javascript.
        """
        if language == 'python':
            from ast_analysis.python_analyzer import PythonAnalyzer
            return PythonAnalyzer()
        elif language == 'java':
            from ast_analysis.java_analyzer import JavaAnalyzer
            return JavaAnalyzer()
        elif language == 'go':
            from ast_analysis.go_analyzer import GoAnalyzer
            return GoAnalyzer()
        elif language == 'javascript':
            from ast_analysis.javascript_analyzer import JavaScriptAnalyzer
            return JavaScriptAnalyzer()
        else:
            raise ValueError(f"Unsupported language: {language}")

# --- Example usage ---
if __name__ == "__main__":
    # Example: Run reasoning on a sample dependency graph
    sample_graph = {
        'flag_a': ['flag_b', 'flag_c'],
        'flag_b': ['flag_c'],
        'flag_c': [],
    }
    reasoner = Reasoner(sample_graph)
    print("Sample dependency graph:", sample_graph)
    print("Cycles:", reasoner.detect_cycles())
    print("Dead flags:", reasoner.find_dead_flags())
    print("Impact of 'flag_a':", reasoner.flag_impact('flag_a'))
