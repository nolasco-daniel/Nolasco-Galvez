from .tracker import ProgressTracker, TypingTestResult, save_typing_result, get_typing_progress
from .dashboard import ProgressDashboard, show_quick_progress

__version__ = "1.0.0"
__all__ = [
    "ProgressTracker",
    "TypingTestResult", 
    "save_typing_result",
    "get_typing_progress",
    "ProgressDashboard",
    "show_quick_progress"
]
