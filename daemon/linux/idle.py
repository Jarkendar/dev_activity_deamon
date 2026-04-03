"""Module for detecting user idle time using XScreenSaver."""
import ctypes
import ctypes.util
from typing import Optional


class XScreenSaverInfo(ctypes.Structure):
    """XScreenSaverInfo structure from XScreenSaver library."""
    _fields_ = [
        ('window', ctypes.c_ulong),
        ('state', ctypes.c_int),
        ('kind', ctypes.c_int),
        ('til_or_since', ctypes.c_ulong),
        ('idle', ctypes.c_ulong),
        ('eventMask', ctypes.c_ulong)
    ]


class IdleDetector:
    """User idle time detector."""
    
    def __init__(self):
        """Initialize the idle detector."""
        self.xlib = None
        self.xss = None
        self.display = None
        self._initialize()
    
    def _initialize(self):
        """Initialize X11 and XScreenSaver libraries."""
        try:
            # Load libraries
            xlib_path = ctypes.util.find_library('X11')
            xss_path = ctypes.util.find_library('Xss')
            
            if not xlib_path or not xss_path:
                raise RuntimeError("Cannot find X11 or Xss libraries")
            
            self.xlib = ctypes.cdll.LoadLibrary(xlib_path)
            self.xss = ctypes.cdll.LoadLibrary(xss_path)
            
            # Open connection to X display
            self.xlib.XOpenDisplay.restype = ctypes.c_void_p
            self.display = self.xlib.XOpenDisplay(None)
            
            if not self.display:
                raise RuntimeError("Cannot open X display")
            
            # Configure XScreenSaver functions
            self.xss.XScreenSaverAllocInfo.restype = ctypes.POINTER(XScreenSaverInfo)
            self.xss.XScreenSaverQueryInfo.argtypes = [
                ctypes.c_void_p,
                ctypes.c_ulong,
                ctypes.POINTER(XScreenSaverInfo)
            ]
            
        except Exception as e:
            print(f"IdleDetector initialization error: {e}")
            self.xlib = None
            self.xss = None
            self.display = None
    
    def get_idle_time(self) -> Optional[int]:
        """
        Get idle time in milliseconds.
        
        Returns:
            int: Idle time in ms or None on error
        """
        if not self.display or not self.xss:
            return None
        
        try:
            info = self.xss.XScreenSaverAllocInfo()
            root = self.xlib.XDefaultRootWindow(self.display)
            self.xss.XScreenSaverQueryInfo(self.display, root, info)
            idle_time = info.contents.idle
            return idle_time
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
    
    def __del__(self):
        """Close X display connection."""
        if self.display and self.xlib:
            try:
                self.xlib.XCloseDisplay(self.display)
            except Exception:
                pass
