# Plugins Directory

This directory contains plugins that extend the functionality of WhatsApp Chat Viewer.

## 📦 **Available Plugins**

### 1. **Emoji Analyzer** (`emoji_analyzer.py`)
Analyzes emoji usage patterns in conversations.

**Features:**
- Total and unique emoji counts
- Most commonly used emojis (top 20)
- Per-sender emoji statistics
- Emoji sentiment distribution (positive/negative/neutral)
- Emoji diversity score
- Percentage of messages containing emojis

**Usage:**
```python
# Plugin auto-loads on app start
# Access via Plugin Manager (🔌 button)
# Results appear in AI analysis tabs
```

### 2. **CSV Exporter** (`csv_exporter.py`)
Exports chat messages to CSV format with metadata.

**Features:**
- Timestamp, sender, message columns
- Message length and word count
- UTF-8 encoding with BOM for Excel
- Compatible with Excel, Google Sheets, pandas

**Usage:**
```python
# Use via Export menu
# Select "CSV Export" option
# Opens in Excel/spreadsheet software
```

## 🛠️ **Creating Your Own Plugin**

### Analyzer Plugin Example
```python
from src.utils.plugin_system import AnalyzerPlugin
from typing import Dict, List

class MyAnalyzer(AnalyzerPlugin):
    def get_name(self) -> str:
        return "my_custom_analyzer"
    
    def get_description(self) -> str:
        return "Description of what it does"
    
    def get_version(self) -> str:
        return "1.0.0"
    
    def analyze(self, messages: List[Dict]) -> Dict:
        # Your analysis logic here
        results = {
            'metric1': 0,
            'metric2': []
        }
        return results
```

### Export Plugin Example
```python
from src.utils.plugin_system import ExportPlugin
from typing import Dict, List

class MyExporter(ExportPlugin):
    def get_name(self) -> str:
        return "my_exporter"
    
    def get_file_extension(self) -> str:
        return "txt"  # or json, xml, etc.
    
    def export(self, messages: List[Dict], output_path: str) -> bool:
        try:
            # Your export logic here
            with open(output_path, 'w') as f:
                f.write("Data")
            return True
        except:
            return False
```

## 📋 **Plugin Guidelines**

### Requirements
1. Must inherit from base plugin class
2. Must implement all required methods
3. Should handle errors gracefully
4. Should be well-documented

### Best Practices
- Use type hints for parameters
- Return meaningful error messages
- Test with large datasets (100K+ messages)
- Optimize for performance
- Add progress callbacks for long operations

### File Structure
```
plugins/
├── __init__.py              # Leave empty or add imports
├── my_plugin.py             # Your plugin file
├── README.md                # This file
└── tests/                   # Optional test files
    └── test_my_plugin.py
```

## 🔧 **Plugin API Reference**

### AnalyzerPlugin Methods
- `get_name()` → str: Unique plugin identifier
- `get_description()` → str: Human-readable description
- `get_version()` → str: Semantic version (e.g., "1.0.0")
- `analyze(messages)` → Dict: Main analysis function
- `get_config_schema()` → Dict: Optional configuration schema
- `configure(config)` → None: Optional configuration handler

### ExportPlugin Methods
- `get_name()` → str: Unique plugin identifier
- `get_file_extension()` → str: File extension without dot
- `export(messages, output_path)` → bool: Export function

### Message Dictionary Format
```python
{
    'timestamp': '2023-01-15 14:30:00',
    'sender': 'John Doe',
    'message': 'Hello world!'
}
```

## 🚀 **Loading Plugins**

### Automatic Loading
Plugins are automatically discovered and loaded when the app starts.

### Manual Loading
```python
from src.utils.plugin_system import PluginManager

pm = PluginManager()
pm.discover_plugins()  # Scans plugins/ directory
```

### Verification
Check Plugin Manager (🔌 button) to see loaded plugins.

## 🎯 **Plugin Ideas**

Here are some plugin ideas you can implement:

### Analysis Plugins
- **Language Detector**: Detect and analyze multiple languages
- **Link Analyzer**: Analyze shared URLs and domains
- **Time Pattern Analyzer**: Analyze response times and patterns
- **Conversation Flow**: Analyze conversation turn-taking
- **Word Cloud Generator**: Generate word clouds from messages
- **Spam Detector**: Detect spam or promotional messages

### Export Plugins
- **HTML Exporter**: Export as styled HTML page
- **Markdown Exporter**: Export as Markdown document
- **XML Exporter**: Export as XML for data exchange
- **Database Exporter**: Export to SQL database
- **Excel Exporter**: Export with formatting and charts

### Visualization Plugins
- **Network Graph**: Show conversation network
- **Timeline Viewer**: Interactive timeline of messages
- **Heatmap Generator**: Activity heatmaps by day/hour
- **Word Cloud Viewer**: Visual word frequency
- **Emoji Cloud**: Visual emoji frequency

## 📚 **Examples in the Wild**

Check out community plugins at:
- GitHub: [coming soon]
- Plugin Registry: [coming soon]

## 🐛 **Debugging Plugins**

### Common Issues

**Plugin not loading:**
```python
# Check: File is in plugins/ directory
# Check: Class inherits from correct base
# Check: All required methods implemented
# Check: No syntax errors (run python -m py_compile plugin.py)
```

**Plugin crashes:**
```python
# Add try-catch blocks
# Log errors to console
# Test with small dataset first
# Check for None values in messages
```

### Testing Your Plugin
```python
# Create test file: tests/test_my_plugin.py
import unittest
from plugins.my_plugin import MyPlugin

class TestMyPlugin(unittest.TestCase):
    def test_analysis(self):
        plugin = MyPlugin()
        messages = [{'sender': 'Test', 'message': 'Hello'}]
        result = plugin.analyze(messages)
        self.assertIsNotNone(result)
```

## 📝 **Contributing**

Want to share your plugin?

1. Test thoroughly with various datasets
2. Document functionality and API
3. Add example usage
4. Submit pull request
5. Join plugin registry (coming soon)

## 🎓 **Advanced Topics**

### Async Plugins
For long-running operations:
```python
import threading

def analyze(self, messages):
    def worker():
        # Long operation
        pass
    
    thread = threading.Thread(target=worker)
    thread.start()
    return {'status': 'processing'}
```

### Configuration
Allow users to configure your plugin:
```python
def get_config_schema(self):
    return {
        'max_results': {'type': 'int', 'default': 10},
        'include_images': {'type': 'bool', 'default': True}
    }

def configure(self, config):
    self.max_results = config.get('max_results', 10)
```

## 🔒 **Security**

- Don't access files outside plugin directory
- Validate all user inputs
- Don't execute arbitrary code
- Don't make network requests without permission
- Respect user privacy

## 📞 **Support**

Need help creating a plugin?
- Check documentation: `docs/API.md`
- Ask in GitHub Issues
- Join discussions
- Read source code of example plugins

---

**Happy Plugin Development!** 🎉
