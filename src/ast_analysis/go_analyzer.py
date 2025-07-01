from .base_analyzer import BaseAnalyzer
import re

class GoAnalyzer(BaseAnalyzer):
    def analyze(self, source_code):
        """
        Analyze Go source code to extract feature flag dependencies.
        Attempts to extract the enclosing function as context.
        """
        dependencies = []
        func_pattern = re.compile(r'^func\s+([\w_]+)\s*\(')
        lines = source_code.split('\n')
        current_func = None
        for idx, line in enumerate(lines, 1):
            func_match = func_pattern.match(line)
            if func_match:
                current_func = func_match.group(1)
            if 'if' in line and ('feature' in line or 'flag' in line):
                dependencies.append({
                    'type': 'if_condition',
                    'dependency': None,  # Could be improved with better parsing
                    'lineno': idx,
                    'context': current_func,
                    'code': line.strip()
                })
        return dependencies
