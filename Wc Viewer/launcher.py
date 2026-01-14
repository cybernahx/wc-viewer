"""
WhatsApp Chat Viewer - Launcher
Simple launcher script for the optimized chat viewer
"""

import sys
import os

try:
    # Import the main application from new structure
    from src.ui.main_window import WhatsAppChatViewer
    
    def main():
        """Main launcher function"""
        print("🚀 Starting WhatsApp Chat Viewer...")
        print("📱 AI-Enhanced Chat Analysis Tool")
        print("=" * 50)
        
        try:
            # Create and run the application
            app = WhatsAppChatViewer()
            app.run()
            
        except Exception as e:
            print(f"❌ Error starting application: {e}")
            input("Press Enter to exit...")
            return 1
        
        return 0

    if __name__ == "__main__":
        sys.exit(main())

except ImportError as e:
    print("❌ Import Error: Missing dependencies")
    print(f"Error: {e}")
    print("\n📋 Required packages:")
    print("- customtkinter")
    print("- tkcalendar") 
    print("- pandas")
    print("- numpy")
    print("- scikit-learn")
    print("- nltk")
    print("- textblob")
    print("- sentence-transformers")
    print("- emoji")
    
    print("\n💡 Install with: pip install -r requirements.txt")
    input("Press Enter to exit...")
    sys.exit(1)

except Exception as e:
    print(f"❌ Unexpected error: {e}")
    input("Press Enter to exit...")
    sys.exit(1)
