"""
Sample Emoji Analyzer Plugin
Analyzes emoji usage patterns in chat conversations
"""

from src.utils.plugin_system import AnalyzerPlugin
from typing import Dict, List
from collections import Counter
import re


class EmojiAnalyzer(AnalyzerPlugin):
    """Analyzes emoji usage in conversations"""
    
    def get_name(self) -> str:
        return "emoji_analyzer"
    
    def get_description(self) -> str:
        return "Analyzes emoji usage patterns and trends"
    
    def get_version(self) -> str:
        return "1.0.0"
    
    def analyze(self, messages: List[Dict]) -> Dict:
        """Analyze emoji usage in messages"""
        
        # Emoji regex pattern
        emoji_pattern = re.compile(
            "["
            "\U0001F600-\U0001F64F"  # emoticons
            "\U0001F300-\U0001F5FF"  # symbols & pictographs
            "\U0001F680-\U0001F6FF"  # transport & map symbols
            "\U0001F1E0-\U0001F1FF"  # flags
            "\U00002702-\U000027B0"
            "\U000024C2-\U0001F251"
            "]+", 
            flags=re.UNICODE
        )
        
        all_emojis = []
        sender_emojis = {}
        emoji_by_sentiment = {'positive': [], 'negative': [], 'neutral': []}
        
        # Common emoji sentiment mapping
        positive_emojis = {'😀', '😁', '😂', '🤣', '😃', '😄', '😅', '😆', '😉', '😊', 
                          '🥰', '😍', '😘', '😗', '😙', '😚', '🙂', '🤗', '🤩', '🥳',
                          '👍', '👌', '💪', '🙌', '👏', '❤️', '💕', '💖', '💗', '💓'}
        
        negative_emojis = {'😞', '😔', '😟', '😕', '🙁', '😣', '😖', '😫', '😩', '🥺',
                          '😢', '😭', '😤', '😠', '😡', '🤬', '😱', '😨', '😰', '😥',
                          '👎', '💔', '😷', '🤒', '🤕', '🤢', '🤮'}
        
        for msg in messages:
            message_text = msg.get('message', '')
            sender = msg.get('sender', 'Unknown')
            
            # Find all emojis
            emojis = emoji_pattern.findall(message_text)
            
            if emojis:
                all_emojis.extend(emojis)
                
                # Track by sender
                if sender not in sender_emojis:
                    sender_emojis[sender] = []
                sender_emojis[sender].extend(emojis)
                
                # Categorize by sentiment
                for emoji in emojis:
                    if emoji in positive_emojis:
                        emoji_by_sentiment['positive'].append(emoji)
                    elif emoji in negative_emojis:
                        emoji_by_sentiment['negative'].append(emoji)
                    else:
                        emoji_by_sentiment['neutral'].append(emoji)
        
        # Count occurrences
        emoji_counts = Counter(all_emojis)
        
        # Calculate per-sender stats
        sender_stats = {}
        for sender, emojis in sender_emojis.items():
            sender_stats[sender] = {
                'total_emojis': len(emojis),
                'unique_emojis': len(set(emojis)),
                'most_used': Counter(emojis).most_common(5)
            }
        
        # Calculate sentiment distribution
        sentiment_distribution = {
            'positive': len(emoji_by_sentiment['positive']),
            'negative': len(emoji_by_sentiment['negative']),
            'neutral': len(emoji_by_sentiment['neutral'])
        }
        
        return {
            'total_emojis': len(all_emojis),
            'unique_emojis': len(set(all_emojis)),
            'most_common': emoji_counts.most_common(20),
            'sender_stats': sender_stats,
            'sentiment_distribution': sentiment_distribution,
            'emoji_diversity': len(set(all_emojis)) / len(all_emojis) if all_emojis else 0,
            'messages_with_emojis': sum(1 for msg in messages if emoji_pattern.search(msg.get('message', ''))),
            'emoji_percentage': (sum(1 for msg in messages if emoji_pattern.search(msg.get('message', ''))) / len(messages) * 100) if messages else 0
        }
