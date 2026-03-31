"""Module for managing SQLite database."""
import sqlite3
from datetime import datetime
from typing import Optional
from pathlib import Path


class Database:
    """Class for managing session database."""
    
    def __init__(self, db_path: str = "dev_tracker.db"):
        """
        Initialize database connection.
        
        Args:
            db_path: Path to database file
        """
        self.db_path = db_path
        self.conn: Optional[sqlite3.Connection] = None
        self._initialize_db()
    
    def _initialize_db(self):
        """Create database tables if they don't exist."""
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row
        
        cursor = self.conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                window_title TEXT NOT NULL,
                process_name TEXT NOT NULL,
                category TEXT,
                start_time TIMESTAMP NOT NULL,
                end_time TIMESTAMP,
                duration_seconds INTEGER,
                is_idle BOOLEAN DEFAULT 0
            )
        ''')
        
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_start_time 
            ON sessions(start_time)
        ''')
        
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_category 
            ON sessions(category)
        ''')
        
        self.conn.commit()
    
    def start_session(self, window_title: str, process_name: str, 
                     category: Optional[str] = None) -> int:
        """
        Start a new session.
        
        Args:
            window_title: Window title
            process_name: Process name
            category: Activity category
        
        Returns:
            int: New session ID
        """
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT INTO sessions (window_title, process_name, category, start_time)
            VALUES (?, ?, ?, ?)
        ''', (window_title, process_name, category, datetime.now()))
        
        self.conn.commit()
        return cursor.lastrowid
    
    def end_session(self, session_id: int, is_idle: bool = False):
        """
        End a session.
        
        Args:
            session_id: Session ID to end
            is_idle: Whether session ended due to idle
        """
        cursor = self.conn.cursor()
        cursor.execute('''
            UPDATE sessions 
            SET end_time = ?,
                duration_seconds = CAST((julianday(?) - julianday(start_time)) * 86400 AS INTEGER),
                is_idle = ?
            WHERE id = ?
        ''', (datetime.now(), datetime.now(), is_idle, session_id))
        
        self.conn.commit()
    
    def get_active_session(self) -> Optional[sqlite3.Row]:
        """
        Get active session (without end_time).
        
        Returns:
            sqlite3.Row: Row with active session or None
        """
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT * FROM sessions 
            WHERE end_time IS NULL 
            ORDER BY start_time DESC 
            LIMIT 1
        ''')
        
        return cursor.fetchone()
    
    def close(self):
        """Close database connection."""
        if self.conn:
            self.conn.close()
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()
