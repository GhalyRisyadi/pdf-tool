"""Application errors that can be rendered consistently by CLI frontends."""


class DependencyError(RuntimeError):
    """A required package, executable, or model is unavailable."""


class ConversionError(RuntimeError):
    """An input, output, or conversion operation is invalid."""
