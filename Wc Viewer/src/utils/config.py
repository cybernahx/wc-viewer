"""
WhatsApp Chat Viewer - Utilities Package
Shared utility functions and helpers
"""

import os
import json
from typing import Dict, Any


def load_config(config_path: str = None) -> Dict[str, Any]:
    """Load configuration from JSON file"""
    if config_path is None:
        # Default config path relative to project root
        project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        config_path = os.path.join(project_root, "config", "settings.json")
    
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"Warning: Could not load config from {config_path}: {e}")
        return get_default_config()


def get_default_config() -> Dict[str, Any]:
    """Get default configuration if config file is not available"""
    return {
        "app_name": "WhatsApp Chat Viewer",
        "version": "2.0.0",
        "ui_settings": {
            "default_theme": "dark",
            "window_size": "1600x1000",
            "min_size": "1400x800",
            "display_limit": 1000
        },
        "ai_settings": {
            "model_name": "all-MiniLM-L6-v2",
            "similarity_threshold": 0.3
        }
    }


def get_project_root() -> str:
    """Get the project root directory"""
    return os.path.dirname(os.path.dirname(os.path.dirname(__file__)))


def ensure_directory(path: str) -> bool:
    """Ensure directory exists, create if not"""
    try:
        os.makedirs(path, exist_ok=True)
        return True
    except Exception as e:
        print(f"Error creating directory {path}: {e}")
        return False
