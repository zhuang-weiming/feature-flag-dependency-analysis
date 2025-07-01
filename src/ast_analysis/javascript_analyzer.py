from .base_analyzer import BaseAnalyzer
import re

class JavaScriptAnalyzer(BaseAnalyzer):
    def analyze(self, source_code):
        """
        Analyze JavaScript source code for Unleash feature flag dependencies, e.g. unleash.isEnabled('FLAG_NAME').
        Extracts the enclosing function as context if possible.
        """
        dependencies = []
        # Regex for unleash.isEnabled('flag') or isEnabled('flag')
        pattern = re.compile(r"(?:unleash\s*\.)?isEnabled\(['\"]([\w\-\.]+)['\"]")
        # Regex for function declarations to extract context
        func_pattern = re.compile(r'^\s*function\s+([\w_]+)\s*\(')
        lines = source_code.split('\n')
        current_func = None
        for idx, line in enumerate(lines, 1):
            # Check if the line defines a function and update current_func
            func_match = func_pattern.match(line)
            if func_match:
                current_func = func_match.group(1)
            # Find all matches for the unleash.isEnabled pattern in the line
            for match in pattern.finditer(line):
                flag_name = match.group(1)
                dependencies.append({
                    'type': 'unleash_isEnabled',
                    'dependency': flag_name,
                    'lineno': idx,
                    'context': current_func,
                    'code': line.strip()
                })
        return dependencies
