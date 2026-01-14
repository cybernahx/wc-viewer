"""
Test suite for WhatsApp Chat Viewer
"""

import unittest
import sys
import os

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))


class TestChatParser(unittest.TestCase):
    """Test cases for ChatParser"""
    
    def setUp(self):
        from core.chat_parser import ChatParser
        self.parser = ChatParser()
    
    def test_parser_initialization(self):
        """Test parser initializes correctly"""
        self.assertIsNotNone(self.parser)
        self.assertEqual(len(self.parser.chat_data), 0)
    
    def test_supported_formats(self):
        """Test supported formats method"""
        formats = self.parser.get_supported_formats()
        self.assertIsInstance(formats, list)
        self.assertGreater(len(formats), 0)


class TestChatAnalyzer(unittest.TestCase):
    """Test cases for ChatAnalyzer"""
    
    def setUp(self):
        from core.chat_analyzer import ChatAIAnalyzer
        self.analyzer = ChatAIAnalyzer()
    
    def test_analyzer_initialization(self):
        """Test analyzer initializes correctly"""
        self.assertIsNotNone(self.analyzer)
        self.assertFalse(self.analyzer.is_trained)
    
    def test_clean_message(self):
        """Test message cleaning functionality"""
        test_message = "Hello World! 😊 http://example.com"
        cleaned = self.analyzer.clean_message(test_message)
        self.assertIsInstance(cleaned, str)
        self.assertNotIn("http://", cleaned)


if __name__ == '__main__':
    unittest.main()
