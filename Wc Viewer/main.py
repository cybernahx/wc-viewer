"""
WhatsApp Chat Viewer - Main Application Entry Point
Enhanced with Message Bubbles, Charts, PDF Export, and Plugin System
"""

import sys
import os

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def check_dependencies():
    """Check if all required dependencies are installed"""
    missing = []
    
    required_packages = {
        'customtkinter': 'customtkinter',
        'tkcalendar': 'tkcalendar',
        'dateutil': 'python-dateutil',
        'PIL': 'Pillow',
        'emoji': 'emoji',
        'sklearn': 'scikit-learn',
        'pandas': 'pandas',
        'numpy': 'numpy',
        'nltk': 'nltk',
        'textblob': 'textblob',
        'sentence_transformers': 'sentence-transformers',
        'matplotlib': 'matplotlib',
        'reportlab': 'reportlab'
    }
    
    for package, pip_name in required_packages.items():
        try:
            __import__(package)
        except ImportError:
            missing.append(pip_name)
    
    return missing

def install_dependencies(packages):
    """Install missing dependencies"""
    import subprocess
    
    print(f"\n📦 Installing {len(packages)} missing packages...")
    for package in packages:
        print(f"   Installing {package}...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", package, "--quiet"])
            print(f"   ✅ {package} installed")
        except subprocess.CalledProcessError:
            print(f"   ❌ Failed to install {package}")
            return False
    
    print("\n✅ All dependencies installed!\n")
    return True

def main():
    """Main application entry point"""
    print("=" * 60)
    print("🚀 WhatsApp Chat Viewer v4.0 - Enhanced Edition")
    print("=" * 60)
    print()
    
    # Check dependencies
    print("📋 Checking dependencies...")
    missing = check_dependencies()
    
    if missing:
        print(f"\n⚠️  Missing {len(missing)} required packages:")
        for pkg in missing:
            print(f"   - {pkg}")
        
        print("\n❓ Would you like to install them now? (y/n): ", end="")
        response = input().strip().lower()
        
        if response == 'y' or response == 'yes':
            if not install_dependencies(missing):
                print("\n❌ Failed to install some dependencies.")
                print("   Please run: pip install -r requirements.txt")
                sys.exit(1)
            
            print("🔄 Restarting application...\n")
            # Restart with dependencies installed
            os.execv(sys.executable, [sys.executable] + sys.argv)
        else:
            print("\n❌ Cannot start without required dependencies.")
            print("   Please run: pip install -r requirements.txt")
            sys.exit(1)
    
    print("✅ All dependencies available!\n")
    
    # Import and run the application
    try:
        print("🎨 Loading UI components...")
        from src.ui.main_window import WhatsAppChatViewer
        
        print("✅ UI loaded successfully!")
        print("\n" + "=" * 60)
        print("💡 KEYBOARD SHORTCUTS:")
        print("   Ctrl+O - Open chat file")
        print("   Ctrl+F - Search messages")
        print("   Ctrl+P - Export to PDF")
        print("   Ctrl+E - Export data")
        print("   Ctrl+T - Toggle theme")
        print("   F5     - Refresh view")
        print("   Esc    - Clear filters")
        print("=" * 60)
        print("\n🚀 Starting application...\n")
        
        # Create and run app
        app = WhatsAppChatViewer()
        app.run()
        
    except ImportError as e:
        print(f"\n❌ Import Error: {e}")
        print("\n💡 Try running: pip install -r requirements.txt")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error starting application: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
