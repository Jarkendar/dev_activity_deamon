"""Module for getting active window information using pywin32."""
from typing import Optional, Tuple

try:
    import win32gui
    import win32process
    import psutil
except ImportError:
    win32gui = None
    win32process = None
    psutil = None


def get_active_window() -> Optional[Tuple[str, str]]:
    """
    Get the title and process name of the active window.
    
    Returns:
        Tuple[str, str]: (window_title, process_name) or None on error
    """
    if not win32gui or not win32process or not psutil:
        return None
    
    try:
        # Get foreground window handle
        hwnd = win32gui.GetForegroundWindow()
        
        # Get window title
        window_title = win32gui.GetWindowText(hwnd)
        
        # Get process ID
        _, pid = win32process.GetWindowThreadProcessId(hwnd)
        
        # Get process name
        process = psutil.Process(pid)
        process_name = process.name()
        
        return (window_title, process_name)
    
    except Exception:
        return None
