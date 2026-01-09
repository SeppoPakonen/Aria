class AriaError(Exception):
    """Base class for all Aria-related errors."""
    pass

class BrowserError(AriaError):
    """Raised when there is an error interacting with the browser."""
    pass

class SessionError(BrowserError):
    """Raised when there is an issue with the browser session (e.g., disconnected)."""
    pass

class NavigationError(BrowserError):
    """Raised when navigation fails."""
    pass

class ScriptError(AriaError):
    """Raised when there is an error in script management or execution."""
    pass

class AIServiceError(AriaError):
    """Raised when the AI service (Gemini) returns an error or is unavailable."""
    pass

class ReportError(AriaError):
    """Raised when report generation fails."""
    pass
