"""Module for detecting user idle time using Windows API."""
import ctypes
from ctypes import Structure, windll, c_uint, sizeof, byref
from typing import Optional


class LASTINPUTINFO(Structure):
    """LASTINPUTINFO structure from Windows API."""
    _fields_ = [
        ('cbSize', c_uint),
        ('dwTime', c_uint),
    ]


class IdleDetector:
    """User idle time detector."""
    
    def __init__(self):
        """Initialize the idle detector."""
        pass
    
    def get_idle_time(self) -> Optional[int]:
        """
        Get idle time in milliseconds.
        
        Returns:
            int: Idle time in ms or None on error
        """
        try:
            lastInputInfo = LASTINPUTINFO()
            lastInputInfo.cbSize = sizeof(lastInputInfo)
            
            if windll.user32.GetLastInputInfo(byref(lastInputInfo)):
                millis = windll.kernel32.GetTickCount()
                idle_time = millis - lastInputInfo.dwTime
                return idle_time
            else:
                return None
        except Exception:
            return None
    
    def is_idle(self, threshold_seconds: int = 120) -> bool:
        """
        Check if user is idle.
        
        Args:
            threshold_seconds: Idle threshold in seconds (default 120s = 2 minutes)
        
        Returns:
            bool: True if user is idle
        """
        idle_time = self.get_idle_time()
        if idle_time is None:
            return False
        
        return idle_time >= (threshold_seconds * 1000)
