from .base_analyzer import BaseAnalyzer
import re

class PythonAnalyzer(BaseAnalyzer):
    def analyze(self, source_code):
        """
        Analyze Python source code for feature flag dependencies, e.g. is_feature_enabled("flag").
        Extracts the enclosing function as context if possible.
        Matches all forms: module/object prefixes, extra args, and variable usage.
        """
        dependencies = []
        # Regex for (optional prefix) is_feature_enabled('flag') or is_feature_enabled(flag_var)
        pattern = re.compile(r"(?:[\w_]+\.)*is_feature_enabled\s*\(([^)]*)\)")
        # Regex for function definitions
        func_pattern = re.compile(r'^\s*def\s+([\w_]+)\s*\(')
        lines = source_code.split('\n')
        current_func = None
        for idx, line in enumerate(lines, 1):
            # Check if the line defines a new function
            func_match = func_pattern.match(line)
            if func_match:
                current_func = func_match.group(1)
            # Find all feature flag usages in the line
            for match in pattern.finditer(line):
                arg = match.group(1).split(',')[0].strip()
                # Try to extract string literal, else record as variable
                str_match = re.match(r"['\"]([\w\-]+)['\"]", arg)
                if str_match:
                    flag_name = str_match.group(1)
                else:
                    flag_name = arg  # variable or expression
                dependencies.append({
                    'type': 'is_feature_enabled',
                    'dependency': flag_name,
                    'lineno': idx,
                    'context': current_func,
                    'code': line.strip()
                })
        return dependencies
