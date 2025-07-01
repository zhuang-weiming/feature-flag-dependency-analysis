from abc import ABC, abstractmethod

# Abstract base class for AST analyzers
class BaseAnalyzer(ABC):
    @abstractmethod
    def analyze(self, source_code):
        """
        Analyze the given source code and return feature flag dependencies.
        Should be implemented by language-specific analyzers.
        """
        pass
