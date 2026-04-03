"""Module for getting active window information using xdotool."""
import subprocess
from typing import Optional, Tuple


def get_active_window() -> Optional[Tuple[str, str]]:
    """
    Get the title and process name of the active window.
    
    Returns:
        Tuple[str, str]: (window_title, process_name) or None on error
    """
    try:
        # Get active window ID
        window_id = subprocess.check_output(
            ['xdotool', 'getactivewindow'],
            stderr=subprocess.DEVNULL
        ).decode('utf-8').strip()
        
        # Get window title
        window_title = subprocess.check_output(
            ['xdotool', 'getwindowname', window_id],
            stderr=subprocess.DEVNULL
        ).decode('utf-8').strip()
        
        # Get process PID
        pid = subprocess.check_output(
            ['xdotool', 'getwindowpid', window_id],
            stderr=subprocess.DEVNULL
        ).decode('utf-8').strip()
        
        # Get process name from /proc
        with open(f'/proc/{pid}/comm', 'r') as f:
            process_name = f.read().strip()
        
        return (window_title, process_name)
    
    except (subprocess.CalledProcessError, FileNotFoundError, IOError):
        return None
