from .base_analyzer import BaseAnalyzer
import re

class JavaAnalyzer(BaseAnalyzer):
    def analyze(self, source_code):
        """
        Analyze Java source code for feature flag dependencies, e.g. FeatureFlag.isEnabled("FLAG") or isFeatureEnabled("FLAG").
        Extracts the enclosing method as context if possible.
        Matches all forms: optional class/object prefixes, static imports, extra args, and variable usage.
        """
        dependencies = []
        # Regex for (optional prefix) isEnabled("flag") or isFeatureEnabled(flag_var)
        pattern = re.compile(r"(?:[\w_]+\.)?(isEnabled|isFeatureEnabled)\s*\(([^)]*)\)")
        method_pattern = re.compile(r'^\s*(public|private|protected)?\s*(static)?\s*[\w\<\>\[\]]+\s+([\w_]+)\s*\(')
        lines = source_code.split('\n')
        current_method = None
        for idx, line in enumerate(lines, 1):
            method_match = method_pattern.match(line)
            if method_match:
                current_method = method_match.group(3)
            for match in pattern.finditer(line):
                arg = match.group(2).split(',')[0].strip()
                str_match = re.match(r'"([\w\-]+)"', arg)
                if str_match:
                    flag_name = str_match.group(1)
                else:
                    flag_name = arg  # variable or expression
                dependencies.append({
                    'type': match.group(1),
                    'dependency': flag_name,
                    'lineno': idx,
                    'context': current_method,
                    'code': line.strip()
                })
        return dependencies
