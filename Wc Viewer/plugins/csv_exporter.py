"""
Sample CSV Exporter Plugin
Exports chat messages to CSV format with metadata
"""

from src.utils.plugin_system import ExportPlugin
from typing import Dict, List
import csv


class CSVExporter(ExportPlugin):
    """Export chat messages to CSV format"""
    
    def get_name(self) -> str:
        return "csv_exporter"
    
    def get_file_extension(self) -> str:
        return "csv"
    
    def export(self, messages: List[Dict], output_path: str) -> bool:
        """Export messages to CSV file"""
        try:
            with open(output_path, 'w', newline='', encoding='utf-8-sig') as csvfile:
                # Define CSV columns
                fieldnames = ['timestamp', 'sender', 'message', 'message_length', 'word_count']
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                
                # Write header
                writer.writeheader()
                
                # Write messages
                for msg in messages:
                    message_text = msg.get('message', '')
                    writer.writerow({
                        'timestamp': msg.get('timestamp', ''),
                        'sender': msg.get('sender', 'Unknown'),
                        'message': message_text,
                        'message_length': len(message_text),
                        'word_count': len(message_text.split())
                    })
            
            return True
            
        except Exception as e:
            print(f"CSV export error: {e}")
            return False
