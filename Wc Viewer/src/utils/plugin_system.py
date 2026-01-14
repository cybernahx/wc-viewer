"""
Plugin System - Extensible architecture for custom analyzers and features
"""

import importlib
import inspect
import os
import sys
from typing import Dict, List, Any, Callable
from abc import ABC, abstractmethod
import json


class AnalyzerPlugin(ABC):
    """Base class for analyzer plugins"""
    
    @abstractmethod
    def get_name(self) -> str:
        """Return plugin name"""
        pass
    
    @abstractmethod
    def get_description(self) -> str:
        """Return plugin description"""
        pass
    
    @abstractmethod
    def get_version(self) -> str:
        """Return plugin version"""
        pass
    
    @abstractmethod
    def analyze(self, messages: List[Dict]) -> Dict:
        """
        Analyze messages and return results
        
        Args:
            messages: List of message dictionaries
            
        Returns:
            Dictionary with analysis results
        """
        pass
    
    def get_config_schema(self) -> Dict:
        """Return configuration schema (optional)"""
        return {}
    
    def configure(self, config: Dict):
        """Configure plugin with settings (optional)"""
        pass


class ExportPlugin(ABC):
    """Base class for export plugins"""
    
    @abstractmethod
    def get_name(self) -> str:
        """Return plugin name"""
        pass
    
    @abstractmethod
    def get_file_extension(self) -> str:
        """Return file extension (e.g., 'json', 'csv')"""
        pass
    
    @abstractmethod
    def export(self, messages: List[Dict], output_path: str) -> bool:
        """
        Export messages to file
        
        Args:
            messages: List of message dictionaries
            output_path: Path for output file
            
        Returns:
            True if successful, False otherwise
        """
        pass


class VisualizationPlugin(ABC):
    """Base class for visualization plugins"""
    
    @abstractmethod
    def get_name(self) -> str:
        """Return plugin name"""
        pass
    
    @abstractmethod
    def create_visualization(self, parent_widget, messages: List[Dict], analysis_results: Dict = None):
        """
        Create visualization widget
        
        Args:
            parent_widget: Parent tkinter widget
            messages: List of message dictionaries
            analysis_results: Optional analysis results
        """
        pass


class PluginManager:
    """Manages plugins for the chat viewer"""
    
    def __init__(self, plugin_dir: str = None):
        """
        Initialize plugin manager
        
        Args:
            plugin_dir: Directory containing plugins (default: ./plugins)
        """
        if plugin_dir is None:
            plugin_dir = os.path.join(os.path.dirname(__file__), '..', '..', 'plugins')
        
        self.plugin_dir = plugin_dir
        self.analyzer_plugins: Dict[str, AnalyzerPlugin] = {}
        self.export_plugins: Dict[str, ExportPlugin] = {}
        self.visualization_plugins: Dict[str, VisualizationPlugin] = {}
        
        # Create plugin directory if it doesn't exist
        os.makedirs(plugin_dir, exist_ok=True)
        
        # Load plugins
        self.discover_plugins()
    
    def discover_plugins(self):
        """Discover and load all plugins from plugin directory"""
        if not os.path.exists(self.plugin_dir):
            return
        
        # Add plugin directory to path
        import sys
        if self.plugin_dir not in sys.path:
            sys.path.insert(0, self.plugin_dir)
        
        # Scan for Python files
        for filename in os.listdir(self.plugin_dir):
            if filename.endswith('.py') and not filename.startswith('_'):
                module_name = filename[:-3]
                try:
                    self._load_plugin_module(module_name)
                except Exception as e:
                    print(f"Error loading plugin {module_name}: {e}")
    
    def _load_plugin_module(self, module_name: str):
        """Load a plugin module and register its plugins"""
        try:
            module = importlib.import_module(module_name)
            
            # Find all classes that inherit from plugin base classes
            for name, obj in inspect.getmembers(module, inspect.isclass):
                if issubclass(obj, AnalyzerPlugin) and obj != AnalyzerPlugin:
                    plugin = obj()
                    self.register_analyzer(plugin)
                elif issubclass(obj, ExportPlugin) and obj != ExportPlugin:
                    plugin = obj()
                    self.register_export_plugin(plugin)
                elif issubclass(obj, VisualizationPlugin) and obj != VisualizationPlugin:
                    plugin = obj()
                    self.register_visualization_plugin(plugin)
        except Exception as e:
            raise Exception(f"Failed to load plugin module {module_name}: {e}")
    
    def register_analyzer(self, plugin: AnalyzerPlugin):
        """Register an analyzer plugin"""
        plugin_name = plugin.get_name()
        self.analyzer_plugins[plugin_name] = plugin
        print(f"✅ Registered analyzer plugin: {plugin_name}")
    
    def register_export_plugin(self, plugin: ExportPlugin):
        """Register an export plugin"""
        plugin_name = plugin.get_name()
        self.export_plugins[plugin_name] = plugin
        print(f"✅ Registered export plugin: {plugin_name}")
    
    def register_visualization_plugin(self, plugin: VisualizationPlugin):
        """Register a visualization plugin"""
        plugin_name = plugin.get_name()
        self.visualization_plugins[plugin_name] = plugin
        print(f"✅ Registered visualization plugin: {plugin_name}")
    
    def get_analyzer_plugins(self) -> Dict[str, AnalyzerPlugin]:
        """Get all registered analyzer plugins"""
        return self.analyzer_plugins
    
    def get_export_plugins(self) -> Dict[str, ExportPlugin]:
        """Get all registered export plugins"""
        return self.export_plugins
    
    def get_visualization_plugins(self) -> Dict[str, VisualizationPlugin]:
        """Get all registered visualization plugins"""
        return self.visualization_plugins
    
    def run_analyzer(self, plugin_name: str, messages: List[Dict]) -> Dict:
        """
        Run a specific analyzer plugin
        
        Args:
            plugin_name: Name of the plugin
            messages: Messages to analyze
            
        Returns:
            Analysis results
        """
        if plugin_name not in self.analyzer_plugins:
            raise ValueError(f"Analyzer plugin '{plugin_name}' not found")
        
        plugin = self.analyzer_plugins[plugin_name]
        return plugin.analyze(messages)
    
    def run_all_analyzers(self, messages: List[Dict]) -> Dict[str, Dict]:
        """
        Run all registered analyzer plugins
        
        Args:
            messages: Messages to analyze
            
        Returns:
            Dictionary mapping plugin names to their results
        """
        results = {}
        for name, plugin in self.analyzer_plugins.items():
            try:
                results[name] = plugin.analyze(messages)
            except Exception as e:
                results[name] = {'error': str(e)}
        
        return results
    
    def export_with_plugin(self, plugin_name: str, messages: List[Dict], output_path: str) -> bool:
        """
        Export messages using a specific plugin
        
        Args:
            plugin_name: Name of the export plugin
            messages: Messages to export
            output_path: Output file path
            
        Returns:
            True if successful
        """
        if plugin_name not in self.export_plugins:
            raise ValueError(f"Export plugin '{plugin_name}' not found")
        
        plugin = self.export_plugins[plugin_name]
        return plugin.export(messages, output_path)
    
    def create_visualization(self, plugin_name: str, parent_widget, messages: List[Dict], 
                           analysis_results: Dict = None):
        """
        Create visualization using a specific plugin
        
        Args:
            plugin_name: Name of the visualization plugin
            parent_widget: Parent tkinter widget
            messages: Messages to visualize
            analysis_results: Optional analysis results
        """
        if plugin_name not in self.visualization_plugins:
            raise ValueError(f"Visualization plugin '{plugin_name}' not found")
        
        plugin = self.visualization_plugins[plugin_name]
        plugin.create_visualization(parent_widget, messages, analysis_results)
    
    def get_plugin_info(self) -> Dict:
        """Get information about all loaded plugins"""
        info = {
            'analyzers': [],
            'exporters': [],
            'visualizations': []
        }
        
        for name, plugin in self.analyzer_plugins.items():
            info['analyzers'].append({
                'name': name,
                'description': plugin.get_description(),
                'version': plugin.get_version()
            })
        
        for name, plugin in self.export_plugins.items():
            info['exporters'].append({
                'name': name,
                'extension': plugin.get_file_extension()
            })
        
        for name, plugin in self.visualization_plugins.items():
            info['visualizations'].append({
                'name': name
            })
        
        return info
    
    def save_plugin_config(self, config_path: str):
        """Save plugin configurations"""
        config = {
            'plugin_dir': self.plugin_dir,
            'loaded_plugins': list(self.analyzer_plugins.keys())
        }
        
        with open(config_path, 'w') as f:
            json.dump(config, f, indent=2)
    
    def create_plugin_template(self, plugin_type: str, plugin_name: str) -> str:
        """
        Create a template plugin file
        
        Args:
            plugin_type: 'analyzer', 'export', or 'visualization'
            plugin_name: Name for the plugin
            
        Returns:
            Path to created template file
        """
        templates = {
            'analyzer': '''"""
Custom Analyzer Plugin
"""

from src.utils.plugin_system import AnalyzerPlugin
from typing import Dict, List


class {class_name}(AnalyzerPlugin):
    """Custom analyzer plugin"""
    
    def get_name(self) -> str:
        return "{plugin_name}"
    
    def get_description(self) -> str:
        return "Custom analysis functionality"
    
    def get_version(self) -> str:
        return "1.0.0"
    
    def analyze(self, messages: List[Dict]) -> Dict:
        """Analyze messages"""
        # Your analysis code here
        results = {{
            'message_count': len(messages),
            'custom_metric': 0
        }}
        
        return results
''',
            'export': '''"""
Custom Export Plugin
"""

from src.utils.plugin_system import ExportPlugin
from typing import Dict, List
import json


class {class_name}(ExportPlugin):
    """Custom export plugin"""
    
    def get_name(self) -> str:
        return "{plugin_name}"
    
    def get_file_extension(self) -> str:
        return "txt"
    
    def export(self, messages: List[Dict], output_path: str) -> bool:
        """Export messages"""
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                for msg in messages:
                    f.write(f"{{msg['sender']}}: {{msg['message']}}\\n")
            return True
        except Exception as e:
            print(f"Export error: {{e}}")
            return False
'''
        }
        
        if plugin_type not in templates:
            raise ValueError(f"Unknown plugin type: {plugin_type}")
        
        class_name = ''.join(word.capitalize() for word in plugin_name.split('_'))
        template_code = templates[plugin_type].format(
            class_name=class_name,
            plugin_name=plugin_name
        )
        
        # Save template
        filename = os.path.join(self.plugin_dir, f"{plugin_name}.py")
        with open(filename, 'w') as f:
            f.write(template_code)
        
        return filename


# Example built-in plugins

class WordCountAnalyzer(AnalyzerPlugin):
    """Built-in word count analyzer"""
    
    def get_name(self) -> str:
        return "word_counter"
    
    def get_description(self) -> str:
        return "Counts words and analyzes vocabulary"
    
    def get_version(self) -> str:
        return "1.0.0"
    
    def analyze(self, messages: List[Dict]) -> Dict:
        """Analyze word usage"""
        from collections import Counter
        
        all_words = []
        for msg in messages:
            words = msg.get('message', '').lower().split()
            all_words.extend(words)
        
        word_counts = Counter(all_words)
        
        return {
            'total_words': len(all_words),
            'unique_words': len(word_counts),
            'most_common': word_counts.most_common(20),
            'vocabulary_richness': len(word_counts) / len(all_words) if all_words else 0
        }


class JSONExporter(ExportPlugin):
    """Built-in JSON exporter"""
    
    def get_name(self) -> str:
        return "json_exporter"
    
    def get_file_extension(self) -> str:
        return "json"
    
    def export(self, messages: List[Dict], output_path: str) -> bool:
        """Export to JSON"""
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(messages, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"JSON export error: {e}")
            return False
