"""Main activity tracker module."""
import time
from typing import Optional
from daemon.window import get_active_window
from daemon.idle import IdleDetector
from daemon.db import Database
from daemon.categorizer import Categorizer


class ActivityTracker:
    """User activity tracker."""
    
    def __init__(self, poll_interval: int = 5, idle_threshold: int = 120):
        """
        Initialize activity tracker.
        
        Args:
            poll_interval: Polling interval in seconds (default 5s)
            idle_threshold: Idle threshold in seconds (default 120s = 2 minutes)
        """
        self.poll_interval = poll_interval
        self.idle_threshold = idle_threshold
        
        self.db = Database()
        self.idle_detector = IdleDetector()
        self.categorizer = Categorizer()
        
        self.current_session_id: Optional[int] = None
        self.last_window_title: Optional[str] = None
        self.last_process_name: Optional[str] = None
        self.running = False
    
    def start(self):
        """Start the tracker."""
        self.running = True
        print("Dev-tracker started. Press Ctrl+C to stop.")
        
        try:
            while self.running:
                self._poll()
                time.sleep(self.poll_interval)
        except KeyboardInterrupt:
            print("\nStopping tracker...")
            self.stop()
    
    def _poll(self):
        """Perform a single activity check."""
        # Check for idle
        is_idle = self.idle_detector.is_idle(self.idle_threshold)
        
        if is_idle:
            # If user is idle, end active session
            if self.current_session_id is not None:
                self.db.end_session(self.current_session_id, is_idle=True)
                print(f"Session ended (idle): {self.last_window_title}")
                self.current_session_id = None
                self.last_window_title = None
                self.last_process_name = None
            return
        
        # Get active window information
        window_info = get_active_window()
        
        if window_info is None:
            return
        
        window_title, process_name = window_info
        
        # Check if window changed
        if (window_title != self.last_window_title or 
            process_name != self.last_process_name):
            
            # End previous session
            if self.current_session_id is not None:
                self.db.end_session(self.current_session_id, is_idle=False)
                print(f"Session ended: {self.last_window_title}")
            
            # Categorize new activity
            category = self.categorizer.categorize(window_title, process_name)
            
            # Start new session
            self.current_session_id = self.db.start_session(
                window_title, process_name, category
            )
            
            self.last_window_title = window_title
            self.last_process_name = process_name
            
            print(f"New session: {window_title} [{process_name}] - Category: {category or 'None'}")
    
    def stop(self):
        """Stop the tracker."""
        self.running = False
        
        # End active session
        if self.current_session_id is not None:
            self.db.end_session(self.current_session_id, is_idle=False)
        
        # Close connections
        self.db.close()
        
        print("Tracker stopped.")
