"""
Database Manager for Trend Cybertron App
Handles SQLite database operations for conversation persistence
"""

import sqlite3
import json
from datetime import datetime
from typing import Dict, List, Any, Optional
import os

class DatabaseManager:
    def __init__(self, db_path: str = "database/conversations.db"):
        """Initialize the database manager"""
        self.db_path = db_path
        self.ensure_database_directory()
        self.init_database()
    
    def ensure_database_directory(self):
        """Ensure the database directory exists"""
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
    
    def init_database(self):
        """Initialize the database with required tables"""
        conn = sqlite3.connect(self.db_path, timeout=30.0)
        
        # Configure database for better performance and concurrency
        conn.execute("PRAGMA journal_mode=WAL")
        conn.execute("PRAGMA synchronous=NORMAL")
        conn.execute("PRAGMA cache_size=1000")
        conn.execute("PRAGMA temp_store=MEMORY")
        conn.execute("PRAGMA foreign_keys=ON")
        
        try:
            cursor = conn.cursor()
            
            # Create conversations table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS conversations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    tab_name TEXT NOT NULL,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    user_message TEXT NOT NULL,
                    assistant_response TEXT NOT NULL,
                    system_prompt TEXT,
                    model TEXT,
                    temperature REAL,
                    max_tokens INTEGER,
                    session_id TEXT
                )
            """)
            
            # Create sessions table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS sessions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT UNIQUE NOT NULL,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    last_activity DATETIME DEFAULT CURRENT_TIMESTAMP,
                    total_messages INTEGER DEFAULT 0
                )
            """)
            
            # Create indexes for better performance
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_conversations_tab_name 
                ON conversations(tab_name)
            """)
            
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_conversations_timestamp 
                ON conversations(timestamp)
            """)
            
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_conversations_session_id 
                ON conversations(session_id)
            """)
            
            conn.commit()
        finally:
            conn.close()
    
    def save_message(self, 
                    tab_name: str, 
                    user_message: str, 
                    assistant_response: str,
                    system_prompt: str = None,
                    model: str = None,
                    temperature: float = None,
                    max_tokens: int = None,
                    session_id: str = None) -> int:
        """Save a conversation message to the database"""
        if session_id is None:
            session_id = self.get_current_session_id()
        
        # Use WAL mode and timeout for better concurrency
        conn = sqlite3.connect(self.db_path, timeout=30.0)
        conn.execute("PRAGMA journal_mode=WAL")
        conn.execute("PRAGMA synchronous=NORMAL")
        conn.execute("PRAGMA cache_size=1000")
        conn.execute("PRAGMA temp_store=MEMORY")
        
        try:
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO conversations 
                (tab_name, user_message, assistant_response, system_prompt, 
                 model, temperature, max_tokens, session_id)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (tab_name, user_message, assistant_response, system_prompt,
                  model, temperature, max_tokens, session_id))
            
            # Update session activity
            self.update_session_activity(session_id, conn)
            
            conn.commit()
            return cursor.lastrowid
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()
    
    def get_conversation_history(self, tab_name: str, limit: int = 50) -> List[Dict[str, Any]]:
        """Get conversation history for a specific tab"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT * FROM conversations 
                WHERE tab_name = ? 
                ORDER BY timestamp DESC 
                LIMIT ?
            """, (tab_name, limit))
            
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
    
    def get_all_conversations(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get all conversations across all tabs"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT * FROM conversations 
                ORDER BY timestamp DESC 
                LIMIT ?
            """, (limit,))
            
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
    
    def clear_conversation(self, tab_name: str):
        """Clear conversation history for a specific tab"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM conversations WHERE tab_name = ?", (tab_name,))
            conn.commit()
    
    def clear_all_conversations(self):
        """Clear all conversation history"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM conversations")
            cursor.execute("DELETE FROM sessions")
            conn.commit()
    
    def get_database_status(self) -> Dict[str, Any]:
        """Get database status and statistics"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Get total conversations
            cursor.execute("SELECT COUNT(*) FROM conversations")
            total_conversations = cursor.fetchone()[0]
            
            # Get conversations by tab
            cursor.execute("""
                SELECT tab_name, COUNT(*) as count 
                FROM conversations 
                GROUP BY tab_name 
                ORDER BY count DESC
            """)
            conversations_by_tab = dict(cursor.fetchall())
            
            # Get recent activity
            cursor.execute("""
                SELECT COUNT(*) FROM conversations 
                WHERE timestamp > datetime('now', '-1 day')
            """)
            recent_activity = cursor.fetchone()[0]
            
            # Get database size
            db_size = os.path.getsize(self.db_path) if os.path.exists(self.db_path) else 0
            
            return {
                'total_conversations': total_conversations,
                'conversations_by_tab': conversations_by_tab,
                'recent_activity': recent_activity,
                'database_size_bytes': db_size,
                'database_size_mb': round(db_size / (1024 * 1024), 2)
            }
    
    def export_conversations(self, format: str = 'json') -> Any:
        """Export conversations in specified format"""
        conversations = self.get_all_conversations()
        
        if format == 'json':
            return conversations
        elif format == 'csv':
            import pandas as pd
            df = pd.DataFrame(conversations)
            return df.to_csv(index=False)
        else:
            raise ValueError("Unsupported format. Use 'json' or 'csv'.")
    
    def search_conversations(self, query: str, tab_name: str = None) -> List[Dict[str, Any]]:
        """Search conversations by content"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            if tab_name:
                cursor.execute("""
                    SELECT * FROM conversations 
                    WHERE tab_name = ? AND 
                    (user_message LIKE ? OR assistant_response LIKE ?)
                    ORDER BY timestamp DESC
                """, (tab_name, f'%{query}%', f'%{query}%'))
            else:
                cursor.execute("""
                    SELECT * FROM conversations 
                    WHERE user_message LIKE ? OR assistant_response LIKE ?
                    ORDER BY timestamp DESC
                """, (f'%{query}%', f'%{query}%'))
            
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
    
    def get_current_session_id(self) -> str:
        """Get or create current session ID"""
        # For simplicity, we'll use a timestamp-based session ID
        # In a real application, you might want to use a more sophisticated session management
        return f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    def update_session_activity(self, session_id: str, conn=None):
        """Update session activity timestamp"""
        if conn is None:
            conn = sqlite3.connect(self.db_path, timeout=30.0)
            conn.execute("PRAGMA journal_mode=WAL")
            should_close = True
        else:
            should_close = False
        
        try:
            cursor = conn.cursor()
            
            # Insert or update session
            cursor.execute("""
                INSERT OR REPLACE INTO sessions (session_id, last_activity, total_messages)
                VALUES (?, CURRENT_TIMESTAMP, 
                    (SELECT COUNT(*) FROM conversations WHERE session_id = ?) + 1)
            """, (session_id, session_id))
            
            if should_close:
                conn.commit()
        finally:
            if should_close:
                conn.close()
    
    def get_session_statistics(self) -> Dict[str, Any]:
        """Get session statistics"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Get total sessions
            cursor.execute("SELECT COUNT(*) FROM sessions")
            total_sessions = cursor.fetchone()[0]
            
            # Get active sessions (last 24 hours)
            cursor.execute("""
                SELECT COUNT(*) FROM sessions 
                WHERE last_activity > datetime('now', '-1 day')
            """)
            active_sessions = cursor.fetchone()[0]
            
            # Get average messages per session
            cursor.execute("""
                SELECT AVG(total_messages) FROM sessions
            """)
            avg_messages = cursor.fetchone()[0] or 0
            
            return {
                'total_sessions': total_sessions,
                'active_sessions': active_sessions,
                'average_messages_per_session': round(avg_messages, 2)
            }
    
    def cleanup_old_conversations(self, days: int = 30):
        """Clean up conversations older than specified days"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                DELETE FROM conversations 
                WHERE timestamp < datetime('now', '-{} days')
            """.format(days))
            
            deleted_count = cursor.rowcount
            conn.commit()
            
            return deleted_count
