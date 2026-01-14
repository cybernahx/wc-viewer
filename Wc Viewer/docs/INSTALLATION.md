# Installation Guide

## Prerequisites

- Python 3.8 or higher
- pip package manager
- Git (optional, for development)

## Quick Installation

### Method 1: Using pip (Recommended)
```bash
pip install whatsapp-chat-viewer
```

### Method 2: From Source
```bash
# Clone the repository
git clone https://github.com/user/whatsapp-chat-viewer.git
cd whatsapp-chat-viewer

# Create virtual environment
python -m venv .venv

# Activate virtual environment
# Windows:
.venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

## Development Installation

For developers who want to contribute:

```bash
# Install development dependencies
pip install -r requirements-dev.txt

# Install in development mode
pip install -e .
```

## Verification

Test your installation:
```bash
# Using the launcher
python launcher.py

# Or using the entry point (if installed via pip)
whatsapp-chat-viewer
```

## Troubleshooting

### Common Issues

1. **Import Error**: Make sure all dependencies are installed
2. **Permission Error**: Run with administrator privileges on Windows
3. **Virtual Environment**: Ensure you're using the correct Python environment

### Getting Help

If you encounter issues:
1. Check the [FAQ](FAQ.md)
2. Look at [Common Issues](../README.md#troubleshooting)
3. Create an issue on GitHub
