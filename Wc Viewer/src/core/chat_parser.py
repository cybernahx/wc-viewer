"""
WhatsApp Chat Parser
Handles parsing and processing of WhatsApp chat export files
"""

import re
from datetime import datetime
import os


class ChatParser:
    """Parse WhatsApp chat export files into structured data"""
    
    def __init__(self):
        self.chat_data = []
        self.parsing_stats = {}
    
    def parse_chat_file(self, file_path):
        """Parse WhatsApp chat export file with optimized performance"""
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Chat file not found: {file_path}")
        
        self.chat_data = []
        self.parsing_stats = {
            'total_lines': 0,
            'parsed_messages': 0,
            'failed_lines': 0,
            'date_range': None,
            'unique_senders': set(),
            'file_size': 0
        }
        
        try:
            # Get file size for progress tracking
            file_size = os.path.getsize(file_path)
            self.parsing_stats['file_size'] = file_size
            
            # Use buffered reading for large files
            buffer_size = 8192 if file_size < 10*1024*1024 else 65536  # 8KB for small, 64KB for large files
            
            with open(file_path, 'r', encoding='utf-8', buffering=buffer_size) as file:
                # Read in chunks for memory efficiency
                if file_size > 50 * 1024 * 1024:  # Files larger than 50MB
                    return self._parse_large_file(file)
                else:
                    lines = file.readlines()
                    self.parsing_stats['total_lines'] = len(lines)
                    
                    current_message = None
                    processed_lines = 0
                    
                    for line_num, line in enumerate(lines, 1):
                        line = line.strip()
                        if not line:
                            continue
                        
                        # Try to parse as new message
                        parsed_message = self._parse_message_line(line)
                        
                        if parsed_message:
                            # Save previous message if exists
                            if current_message:
                                self._add_message(current_message)
                            current_message = parsed_message
                        else:
                            # Continuation of previous message
                            if current_message:
                                # Limit message length to prevent memory issues
                                if len(current_message['message']) < 10000:  # 10KB per message limit
                                    current_message['message'] += ' ' + line
                            else:
                                self.parsing_stats['failed_lines'] += 1
                        
                        processed_lines += 1
                        
                        # Progress callback for large files
                        if processed_lines % 1000 == 0 and file_size > 10*1024*1024:
                            progress = (processed_lines / len(lines)) * 100
                            print(f"Parsing progress: {progress:.1f}%", end='\r')
                    
                    # Add the last message
                    if current_message:
                        self._add_message(current_message)
        
        except Exception as e:
            raise Exception(f"Error parsing chat file: {str(e)}")
        
        self._finalize_parsing_stats()
        return self.chat_data
    
    def _parse_large_file(self, file):
        """Parse large files using streaming approach"""
        current_message = None
        line_num = 0
        chunk_size = 1000  # Process in chunks of 1000 lines
        
        print("Processing large file... Please wait.")
        
        while True:
            lines = []
            for _ in range(chunk_size):
                line = file.readline()
                if not line:
                    break
                lines.append(line.strip())
            
            if not lines:
                break
            
            self.parsing_stats['total_lines'] += len(lines)
            
            for line in lines:
                if not line:
                    continue
                
                line_num += 1
                
                # Try to parse as new message
                parsed_message = self._parse_message_line(line)
                
                if parsed_message:
                    # Save previous message if exists
                    if current_message:
                        self._add_message(current_message)
                    current_message = parsed_message
                else:
                    # Continuation of previous message
                    if current_message:
                        # Limit message length to prevent memory issues
                        if len(current_message['message']) < 10000:
                            current_message['message'] += ' ' + line
                    else:
                        self.parsing_stats['failed_lines'] += 1
            
            # Progress feedback
            if line_num % 10000 == 0:
                print(f"Processed {line_num:,} lines, found {len(self.chat_data):,} messages", end='\r')
        
        # Add the last message
        if current_message:
            self._add_message(current_message)
        
        return self.chat_data
    
    def _parse_message_line(self, line):
        """Parse a single message line"""
        # WhatsApp patterns for different date formats
        patterns = [
            # Pattern 1: DD/MM/YY, HH:MM - Sender: Message
            r'^(\d{1,2}/\d{1,2}/\d{2,4}),?\s*(\d{1,2}:\d{2}(?::\d{2})?)\s*[-–]\s*([^:]+?):\s*(.*)$',
            # Pattern 2: [DD/MM/YY, HH:MM:SS] Sender: Message
            r'^\[(\d{1,2}/\d{1,2}/\d{2,4}),?\s*(\d{1,2}:\d{2}:\d{2})\]\s*([^:]+?):\s*(.*)$',
            # Pattern 3: DD.MM.YY, HH:MM - Sender: Message
            r'^(\d{1,2}\.\d{1,2}\.\d{2,4}),?\s*(\d{1,2}:\d{2}(?::\d{2})?)\s*[-–]\s*([^:]+?):\s*(.*)$',
            # Pattern 4: MM/DD/YY, HH:MM AM/PM - Sender: Message
            r'^(\d{1,2}/\d{1,2}/\d{2,4}),?\s*(\d{1,2}:\d{2}(?::\d{2})?\s*(?:AM|PM))\s*[-–]\s*([^:]+?):\s*(.*)$'
        ]
        
        for pattern in patterns:
            match = re.match(pattern, line, re.IGNORECASE)
            if match:
                date_str, time_str, sender, message = match.groups()
                
                try:
                    timestamp = self._parse_datetime(date_str, time_str)
                    return {
                        'timestamp': timestamp,
                        'sender': sender.strip(),
                        'message': message.strip()
                    }
                except ValueError:
                    continue
        
        return None
    
    def _parse_datetime(self, date_str, time_str):
        """Parse date and time strings into datetime object"""
        # Clean up time string
        time_str = time_str.strip()
        
        # Handle AM/PM format
        if 'AM' in time_str.upper() or 'PM' in time_str.upper():
            datetime_str = f"{date_str} {time_str}"
            formats = [
                "%m/%d/%y %I:%M %p",
                "%d/%m/%y %I:%M %p",
                "%m/%d/%Y %I:%M %p",
                "%d/%m/%Y %I:%M %p",
                "%m/%d/%y %I:%M:%S %p",
                "%d/%m/%y %I:%M:%S %p"
            ]
        else:
            datetime_str = f"{date_str} {time_str}"
            formats = [
                "%d/%m/%y %H:%M",
                "%m/%d/%y %H:%M",
                "%d/%m/%Y %H:%M",
                "%m/%d/%Y %H:%M",
                "%d.%m.%y %H:%M",
                "%d.%m.%Y %H:%M",
                "%d/%m/%y %H:%M:%S",
                "%m/%d/%y %H:%M:%S",
                "%d/%m/%Y %H:%M:%S",
                "%m/%d/%Y %H:%M:%S"
            ]
        
        # Try each format
        for fmt in formats:
            try:
                return datetime.strptime(datetime_str, fmt)
            except ValueError:
                continue
        
        raise ValueError(f"Unable to parse datetime: {datetime_str}")
    
    def _add_message(self, message):
        """Add a parsed message to the dataset"""
        # Clean and validate message
        if not message['message'].strip():
            return
        
        # Skip system messages
        if self._is_system_message(message['message']):
            return
        
        # Add to dataset
        self.chat_data.append(message)
        self.parsing_stats['parsed_messages'] += 1
        self.parsing_stats['unique_senders'].add(message['sender'])
    
    def _is_system_message(self, message):
        """Check if message is a system message"""
        system_patterns = [
            r'.*added.*',
            r'.*left.*',
            r'.*joined.*',
            r'.*removed.*',
            r'.*changed.*group.*',
            r'.*security code changed.*',
            r'.*end-to-end encrypted.*',
            r'.*created group.*',
            r'Messages and calls are end-to-end encrypted.*',
            r'.*missed voice call.*',
            r'.*missed video call.*'
        ]
        
        message_lower = message.lower()
        return any(re.search(pattern, message_lower, re.IGNORECASE) for pattern in system_patterns)
    
    def _finalize_parsing_stats(self):
        """Finalize parsing statistics"""
        if self.chat_data:
            timestamps = [msg['timestamp'] for msg in self.chat_data]
            self.parsing_stats['date_range'] = {
                'start': min(timestamps),
                'end': max(timestamps)
            }
        
        self.parsing_stats['unique_senders'] = len(self.parsing_stats['unique_senders'])
    
    def get_parsing_stats(self):
        """Get parsing statistics"""
        return self.parsing_stats.copy()
    
    def validate_chat_data(self):
        """Validate parsed chat data"""
        if not self.chat_data:
            return {'valid': False, 'error': 'No data parsed'}
        
        # Check for required fields
        required_fields = ['timestamp', 'sender', 'message']
        for i, message in enumerate(self.chat_data[:10]):  # Check first 10 messages
            for field in required_fields:
                if field not in message:
                    return {'valid': False, 'error': f'Missing field {field} in message {i}'}
        
        # Check for reasonable data
        if len(self.chat_data) < 10:
            return {'valid': False, 'error': 'Too few messages parsed (less than 10)'}
        
        if self.parsing_stats['unique_senders'] < 2:
            return {'valid': False, 'error': 'Only one sender found - check if this is a group chat'}
        
        return {'valid': True, 'message': f"Successfully parsed {len(self.chat_data)} messages"}
    
    def get_chat_data(self):
        """Get parsed chat data"""
        return self.chat_data.copy()
    
    def export_to_json(self, output_path):
        """Export parsed data to JSON file"""
        import json
        
        try:
            # Convert datetime objects to strings for JSON serialization
            export_data = []
            for msg in self.chat_data:
                export_msg = msg.copy()
                export_msg['timestamp'] = msg['timestamp'].isoformat()
                export_data.append(export_msg)
            
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump({
                    'chat_data': export_data,
                    'parsing_stats': {
                        'total_lines': self.parsing_stats['total_lines'],
                        'parsed_messages': self.parsing_stats['parsed_messages'],
                        'failed_lines': self.parsing_stats['failed_lines'],
                        'unique_senders': self.parsing_stats['unique_senders'],
                        'date_range': {
                            'start': self.parsing_stats['date_range']['start'].isoformat() if self.parsing_stats['date_range'] else None,
                            'end': self.parsing_stats['date_range']['end'].isoformat() if self.parsing_stats['date_range'] else None
                        } if self.parsing_stats['date_range'] else None
                    }
                }, f, indent=2, ensure_ascii=False)
            
            return True
        except Exception as e:
            print(f"Error exporting to JSON: {e}")
            return False
    
    @staticmethod
    def get_supported_formats():
        """Get list of supported chat file formats"""
        return [
            "WhatsApp Chat Export (.txt)",
            "Date formats: DD/MM/YY, MM/DD/YY, DD.MM.YY",
            "Time formats: 24-hour (HH:MM) and 12-hour (HH:MM AM/PM)",
            "Encoding: UTF-8"
        ]
