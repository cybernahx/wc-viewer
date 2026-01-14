"""
WhatsApp Chat Database Handler
SQLite-based storage for efficient querying and performance with large datasets
"""

import sqlite3
import os
import json
from datetime import datetime
from typing import List, Dict, Any, Optional, Tuple
import hashlib


class ChatDatabase:
    """SQLite database handler for chat storage and querying"""
    
    def __init__(self, db_path: str = None):
        """Initialize database connection"""
        if db_path is None:
            # Use default path in user's app data
            app_data = os.path.join(os.path.expanduser("~"), ".whatsapp_viewer")
            os.makedirs(app_data, exist_ok=True)
            db_path = os.path.join(app_data, "chats.db")
        
        self.db_path = db_path
        self.conn = None
        self.cursor = None
        self.current_chat_id = None
        self._initialize_database()
    
    def _initialize_database(self):
        """Create database schema if not exists"""
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row  # Access columns by name
        self.cursor = self.conn.cursor()
        
        # Create tables
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS chats (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                file_path TEXT UNIQUE,
                file_hash TEXT UNIQUE,
                total_messages INTEGER,
                total_senders INTEGER,
                date_range_start TEXT,
                date_range_end TEXT,
                created_at TEXT,
                last_accessed TEXT,
                metadata TEXT
            )
        ''')
        
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                chat_id INTEGER,
                timestamp TEXT,
                sender TEXT,
                message TEXT,
                sentiment REAL,
                sentiment_category TEXT,
                message_length INTEGER,
                word_count INTEGER,
                emoji_count INTEGER,
                has_media BOOLEAN,
                has_url BOOLEAN,
                FOREIGN KEY (chat_id) REFERENCES chats(id) ON DELETE CASCADE
            )
        ''')
        
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS senders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                chat_id INTEGER,
                sender_name TEXT,
                message_count INTEGER,
                avg_message_length REAL,
                total_words INTEGER,
                emoji_count INTEGER,
                first_message_date TEXT,
                last_message_date TEXT,
                FOREIGN KEY (chat_id) REFERENCES chats(id) ON DELETE CASCADE,
                UNIQUE(chat_id, sender_name)
            )
        ''')
        
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS analysis_cache (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                chat_id INTEGER,
                analysis_type TEXT,
                results TEXT,
                created_at TEXT,
                FOREIGN KEY (chat_id) REFERENCES chats(id) ON DELETE CASCADE,
                UNIQUE(chat_id, analysis_type)
            )
        ''')
        
        # Create indexes for fast querying
        self.cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_messages_chat_id 
            ON messages(chat_id)
        ''')
        
        self.cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_messages_timestamp 
            ON messages(timestamp)
        ''')
        
        self.cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_messages_sender 
            ON messages(sender)
        ''')
        
        self.cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_messages_sentiment 
            ON messages(sentiment_category)
        ''')
        
        self.cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_messages_search 
            ON messages(message)
        ''')
        
        self.conn.commit()
    
    def _calculate_file_hash(self, file_path: str) -> str:
        """Calculate MD5 hash of file for tracking"""
        hash_md5 = hashlib.md5()
        try:
            with open(file_path, "rb") as f:
                # Read in chunks for large files
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_md5.update(chunk)
            return hash_md5.hexdigest()
        except Exception as e:
            return f"error_{datetime.now().timestamp()}"
    
    def load_chat(self, file_path: str, chat_data: List[Dict], force_reload: bool = False) -> int:
        """
        Load chat data into database
        Returns chat_id for further operations
        """
        file_hash = self._calculate_file_hash(file_path)
        
        # Check if chat already exists
        if not force_reload:
            self.cursor.execute(
                "SELECT id FROM chats WHERE file_hash = ?", 
                (file_hash,)
            )
            existing = self.cursor.fetchone()
            if existing:
                self.current_chat_id = existing['id']
                # Update last accessed
                self.cursor.execute(
                    "UPDATE chats SET last_accessed = ? WHERE id = ?",
                    (datetime.now().isoformat(), self.current_chat_id)
                )
                self.conn.commit()
                return self.current_chat_id
        
        # Extract metadata
        senders = set()
        dates = []
        for msg in chat_data:
            senders.add(msg['sender'])
            dates.append(msg['timestamp'])
        
        date_range_start = min(dates) if dates else None
        date_range_end = max(dates) if dates else None
        
        metadata = {
            'file_size': os.path.getsize(file_path) if os.path.exists(file_path) else 0,
            'senders': list(senders)
        }
        
        # Insert or replace chat record
        self.cursor.execute('''
            INSERT OR REPLACE INTO chats 
            (file_path, file_hash, total_messages, total_senders, 
             date_range_start, date_range_end, created_at, last_accessed, metadata)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            file_path,
            file_hash,
            len(chat_data),
            len(senders),
            date_range_start,
            date_range_end,
            datetime.now().isoformat(),
            datetime.now().isoformat(),
            json.dumps(metadata)
        ))
        
        self.current_chat_id = self.cursor.lastrowid
        
        # Delete old messages if reloading
        if force_reload:
            self.cursor.execute("DELETE FROM messages WHERE chat_id = ?", (self.current_chat_id,))
            self.cursor.execute("DELETE FROM senders WHERE chat_id = ?", (self.current_chat_id,))
        
        # Batch insert messages for performance
        message_records = []
        for msg in chat_data:
            # Calculate message metrics
            message_text = msg.get('message', '')
            word_count = len(message_text.split())
            emoji_count = sum(1 for char in message_text if char in '😀😁😂🤣😃😄😅😆😉😊😋😎😍😘🥰')
            has_url = 'http' in message_text.lower() or 'www.' in message_text.lower()
            has_media = '<Media omitted>' in message_text or '<attached:' in message_text.lower()
            
            message_records.append((
                self.current_chat_id,
                msg.get('timestamp', ''),
                msg.get('sender', 'Unknown'),
                message_text,
                None,  # sentiment - calculated later
                None,  # sentiment_category
                len(message_text),
                word_count,
                emoji_count,
                has_media,
                has_url
            ))
        
        # Batch insert (1000 at a time for optimal performance)
        batch_size = 1000
        for i in range(0, len(message_records), batch_size):
            batch = message_records[i:i + batch_size]
            self.cursor.executemany('''
                INSERT INTO messages 
                (chat_id, timestamp, sender, message, sentiment, sentiment_category,
                 message_length, word_count, emoji_count, has_media, has_url)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', batch)
        
        # Calculate sender statistics
        self._calculate_sender_stats()
        
        self.conn.commit()
        return self.current_chat_id
    
    def _calculate_sender_stats(self):
        """Calculate and store sender statistics"""
        if not self.current_chat_id:
            return
        
        # Delete existing sender stats
        self.cursor.execute("DELETE FROM senders WHERE chat_id = ?", (self.current_chat_id,))
        
        # Calculate stats
        self.cursor.execute('''
            INSERT INTO senders 
            (chat_id, sender_name, message_count, avg_message_length, 
             total_words, emoji_count, first_message_date, last_message_date)
            SELECT 
                chat_id,
                sender,
                COUNT(*) as message_count,
                AVG(message_length) as avg_message_length,
                SUM(word_count) as total_words,
                SUM(emoji_count) as emoji_count,
                MIN(timestamp) as first_message_date,
                MAX(timestamp) as last_message_date
            FROM messages
            WHERE chat_id = ?
            GROUP BY sender
        ''', (self.current_chat_id,))
        
        self.conn.commit()
    
    def query_messages(self, 
                      start_date: str = None,
                      end_date: str = None,
                      sender: str = None,
                      search_term: str = None,
                      sentiment: str = None,
                      limit: int = None,
                      offset: int = 0) -> List[Dict]:
        """
        Query messages with filters
        Returns list of message dictionaries
        """
        if not self.current_chat_id:
            return []
        
        query = "SELECT * FROM messages WHERE chat_id = ?"
        params = [self.current_chat_id]
        
        if start_date:
            query += " AND timestamp >= ?"
            params.append(start_date)
        
        if end_date:
            query += " AND timestamp <= ?"
            params.append(end_date)
        
        if sender:
            query += " AND sender = ?"
            params.append(sender)
        
        if search_term:
            query += " AND message LIKE ?"
            params.append(f"%{search_term}%")
        
        if sentiment:
            query += " AND sentiment_category = ?"
            params.append(sentiment)
        
        query += " ORDER BY timestamp ASC"
        
        if limit:
            query += f" LIMIT {limit} OFFSET {offset}"
        
        self.cursor.execute(query, params)
        rows = self.cursor.fetchall()
        
        return [dict(row) for row in rows]
    
    def get_sender_stats(self) -> List[Dict]:
        """Get statistics for all senders"""
        if not self.current_chat_id:
            return []
        
        self.cursor.execute(
            "SELECT * FROM senders WHERE chat_id = ? ORDER BY message_count DESC",
            (self.current_chat_id,)
        )
        
        return [dict(row) for row in self.cursor.fetchall()]
    
    def get_chat_overview(self) -> Dict:
        """Get overview statistics for current chat"""
        if not self.current_chat_id:
            return {}
        
        self.cursor.execute("SELECT * FROM chats WHERE id = ?", (self.current_chat_id,))
        chat_row = self.cursor.fetchone()
        
        if not chat_row:
            return {}
        
        return dict(chat_row)
    
    def update_sentiment(self, message_id: int, sentiment: float, category: str):
        """Update sentiment for a specific message"""
        self.cursor.execute('''
            UPDATE messages 
            SET sentiment = ?, sentiment_category = ?
            WHERE id = ?
        ''', (sentiment, category, message_id))
        self.conn.commit()
    
    def batch_update_sentiment(self, updates: List[Tuple[int, float, str]]):
        """Batch update sentiments for performance"""
        self.cursor.executemany('''
            UPDATE messages 
            SET sentiment = ?, sentiment_category = ?
            WHERE id = ?
        ''', [(sent, cat, mid) for mid, sent, cat in updates])
        self.conn.commit()
    
    def cache_analysis(self, analysis_type: str, results: Dict):
        """Cache analysis results"""
        if not self.current_chat_id:
            return
        
        self.cursor.execute('''
            INSERT OR REPLACE INTO analysis_cache
            (chat_id, analysis_type, results, created_at)
            VALUES (?, ?, ?, ?)
        ''', (
            self.current_chat_id,
            analysis_type,
            json.dumps(results),
            datetime.now().isoformat()
        ))
        self.conn.commit()
    
    def get_cached_analysis(self, analysis_type: str) -> Optional[Dict]:
        """Retrieve cached analysis results"""
        if not self.current_chat_id:
            return None
        
        self.cursor.execute('''
            SELECT results FROM analysis_cache
            WHERE chat_id = ? AND analysis_type = ?
        ''', (self.current_chat_id, analysis_type))
        
        row = self.cursor.fetchone()
        if row:
            return json.loads(row['results'])
        return None
    
    def get_message_count(self, filters: Dict = None) -> int:
        """Get total message count with optional filters"""
        if not self.current_chat_id:
            return 0
        
        query = "SELECT COUNT(*) as count FROM messages WHERE chat_id = ?"
        params = [self.current_chat_id]
        
        if filters:
            if 'start_date' in filters:
                query += " AND timestamp >= ?"
                params.append(filters['start_date'])
            if 'end_date' in filters:
                query += " AND timestamp <= ?"
                params.append(filters['end_date'])
            if 'sender' in filters:
                query += " AND sender = ?"
                params.append(filters['sender'])
            if 'search_term' in filters:
                query += " AND message LIKE ?"
                params.append(f"%{filters['search_term']}%")
        
        self.cursor.execute(query, params)
        return self.cursor.fetchone()['count']
    
    def get_activity_timeline(self, granularity: str = 'day') -> List[Dict]:
        """
        Get message activity timeline
        granularity: 'hour', 'day', 'week', 'month'
        """
        if not self.current_chat_id:
            return []
        
        date_format_map = {
            'hour': '%Y-%m-%d %H:00',
            'day': '%Y-%m-%d',
            'week': '%Y-W%W',
            'month': '%Y-%m'
        }
        
        date_format = date_format_map.get(granularity, '%Y-%m-%d')
        
        self.cursor.execute(f'''
            SELECT 
                strftime('{date_format}', timestamp) as period,
                COUNT(*) as message_count,
                COUNT(DISTINCT sender) as active_senders
            FROM messages
            WHERE chat_id = ?
            GROUP BY period
            ORDER BY period ASC
        ''', (self.current_chat_id,))
        
        return [dict(row) for row in self.cursor.fetchall()]
    
    def get_sentiment_distribution(self) -> Dict:
        """Get distribution of sentiments"""
        if not self.current_chat_id:
            return {}
        
        self.cursor.execute('''
            SELECT 
                sentiment_category,
                COUNT(*) as count,
                AVG(sentiment) as avg_sentiment
            FROM messages
            WHERE chat_id = ? AND sentiment_category IS NOT NULL
            GROUP BY sentiment_category
        ''', (self.current_chat_id,))
        
        results = {}
        for row in self.cursor.fetchall():
            results[row['sentiment_category']] = {
                'count': row['count'],
                'avg_sentiment': row['avg_sentiment']
            }
        
        return results
    
    def close(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()
    
    def __del__(self):
        """Cleanup on deletion"""
        self.close()
