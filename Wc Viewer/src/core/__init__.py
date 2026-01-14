"""
WhatsApp Chat Viewer - Core Package
Contains the main analysis and parsing functionality
"""

from .chat_analyzer import ChatAIAnalyzer
from .chat_parser import ChatParser

__version__ = "2.0.0"
__author__ = "AI Assistant"

__all__ = [
    "ChatAIAnalyzer",
    "ChatParser"
]
