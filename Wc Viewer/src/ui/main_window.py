"""
WhatsApp Chat Viewer - Main Application
Optimized and streamlined UI with AI capabilities
Enhanced with message bubbles, visualization, PDF export, and plugin system
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import customtkinter as ctk
from datetime import datetime, timedelta
import re
from tkcalendar import DateEntry, Calendar
import json
import os
import threading
from collections import Counter
import emoji
import time

# Import our custom modules
try:
    from ..core.chat_analyzer import ChatAIAnalyzer
    from ..core.chat_parser import ChatParser
    from ..core.chat_database import ChatDatabase
    from ..ui.message_bubble import ChatBubbleView
    from ..ui.visualization_dashboard import VisualizationDashboard
    from ..utils.pdf_exporter import PDFExporter
    from ..utils.plugin_system import PluginManager
except ImportError:
    # Fallback for direct execution
    import sys
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
    from src.core.chat_analyzer import ChatAIAnalyzer
    from src.core.chat_parser import ChatParser
    from src.core.chat_database import ChatDatabase
    from src.ui.message_bubble import ChatBubbleView
    from src.ui.visualization_dashboard import VisualizationDashboard
    from src.utils.pdf_exporter import PDFExporter
    from src.utils.plugin_system import PluginManager


class WhatsAppChatViewer:
    """Main WhatsApp Chat Viewer Application"""
    
    def __init__(self):
        # Set appearance mode and theme
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        
        self.root = ctk.CTk()
        self.root.title("WhatsApp Chat Viewer - AI Enhanced Analysis Tool v3.0")
        self.root.geometry("1600x1000")
        self.root.minsize(1400, 800)
        
        # Bind window resize event for responsive layout
        self.root.bind("<Configure>", self.on_window_resize)
        
        # NEW: Bind keyboard shortcuts
        self.root.bind("<Control-f>", lambda e: self.focus_search())
        self.root.bind("<Control-F>", lambda e: self.focus_search())
        self.root.bind("<Control-e>", lambda e: self.export_data())
        self.root.bind("<Control-E>", lambda e: self.export_data())
        self.root.bind("<Control-o>", lambda e: self.import_chat_file())
        self.root.bind("<Control-O>", lambda e: self.import_chat_file())
        self.root.bind("<Control-t>", lambda e: self.toggle_theme())
        self.root.bind("<Control-T>", lambda e: self.toggle_theme())
        self.root.bind("<Control-p>", lambda e: self.export_to_pdf())
        self.root.bind("<Control-P>", lambda e: self.export_to_pdf())
        self.root.bind("<F5>", lambda e: self.refresh_view())
        self.root.bind("<Escape>", lambda e: self.clear_filters())
        
        # Data storage
        self.chat_data = []
        self.filtered_data = []
        self.current_file = None
        
        # Components
        self.ai_analyzer = ChatAIAnalyzer()
        self.chat_parser = ChatParser()
        self.chat_db = ChatDatabase()  # NEW: Database backend
        self.plugin_manager = PluginManager()  # NEW: Plugin system
        self.analysis_results = {}
        
        # NEW: UI Components
        self.bubble_view = None
        self.viz_dashboard = None
        
        # UI optimization variables
        self.display_limit = 1000
        self.current_theme = "dark"
        self.user_stats_cache = {}
        self.stats_cache_valid = False
        
        # Performance tracking
        self._stats_cache = {}
        self.display_limit_var = None  # Will be set in UI creation
        self.font_size_var = None      # Will be set in UI creation
        
        self.setup_ui()
        
        # Show keyboard shortcuts hint
        self.update_status("💡 Tip: Press Ctrl+F to search, Ctrl+E to export, Ctrl+P for PDF")
    
    def on_window_resize(self, event):
        """Handle window resize events for responsive layout adjustments"""
        # Only handle resize events for the root window
        if event.widget != self.root:
            return
        
        # Get current window width
        window_width = self.root.winfo_width()
        
        # Adjust main column weights based on window width
        try:
            # Get the main content frame for the chat analysis tab
            if hasattr(self, 'tab_view'):
                chat_tab = self.tab_view.tab("💬 Chat Analysis")
                if chat_tab and chat_tab.winfo_children():
                    content_frame = chat_tab.winfo_children()[0]  # Main content frame
                    
                    if window_width < 1200:
                        # Small screen: hide stats panel, expand chat
                        content_frame.grid_columnconfigure(0, weight=0, minsize=280)  # Filter panel smaller
                        content_frame.grid_columnconfigure(1, weight=1)  # Chat panel expand more
                        content_frame.grid_columnconfigure(2, weight=0, minsize=0)   # Hide stats panel
                    elif window_width < 1500:
                        # Medium screen: smaller panels
                        content_frame.grid_columnconfigure(0, weight=0, minsize=300)
                        content_frame.grid_columnconfigure(1, weight=1)
                        content_frame.grid_columnconfigure(2, weight=0, minsize=250)
                    else:
                        # Large screen: full layout
                        content_frame.grid_columnconfigure(0, weight=0, minsize=350)
                        content_frame.grid_columnconfigure(1, weight=1)
                        content_frame.grid_columnconfigure(2, weight=0, minsize=300)
        except Exception as e:
            # Ignore resize errors during initialization
            pass
        
        # Adjust date filter layout based on filter panel width
        try:
            if hasattr(self, 'date_container'):
                filter_width = window_width * 0.25  # Approximate filter panel width
                
                if filter_width < 320:
                    # Very small: stack date sections vertically
                    from_section = self.date_container.winfo_children()[0]
                    to_section = self.date_container.winfo_children()[1]
                    
                    from_section.grid_configure(row=0, column=0, columnspan=2, sticky="ew")
                    to_section.grid_configure(row=1, column=0, columnspan=2, sticky="ew")
                else:
                    # Normal: side by side
                    from_section = self.date_container.winfo_children()[0]
                    to_section = self.date_container.winfo_children()[1]
                    
                    from_section.grid_configure(row=0, column=0, columnspan=1, sticky="ew")
                    to_section.grid_configure(row=0, column=1, columnspan=1, sticky="ew")
        except Exception as e:
            # Ignore layout errors
            pass
    
    def setup_ui(self):
        """Setup the main user interface"""
        # Main container
        main_container = ctk.CTkFrame(self.root)
        main_container.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Top toolbar
        self.create_toolbar(main_container)
        
        # Content area with tabbed interface
        self.create_tabbed_interface(main_container)
    
    def create_toolbar(self, parent):
        """Create top toolbar with main actions"""
        toolbar = ctk.CTkFrame(parent, height=60)
        toolbar.pack(fill="x", padx=5, pady=(5, 10))
        
        # Left side buttons
        # Import button
        import_btn = ctk.CTkButton(
            toolbar, 
            text="📁 Import (Ctrl+O)",
            command=self.import_chat_file,
            width=150,
            height=35
        )
        import_btn.pack(side="left", padx=10, pady=12)
        
        # Theme toggle button
        self.theme_btn = ctk.CTkButton(
            toolbar,
            text="🌙 Dark (Ctrl+T)",
            command=self.toggle_theme,
            width=130,
            height=35
        )
        self.theme_btn.pack(side="left", padx=5, pady=12)
        
        # NEW: Visualization button
        viz_btn = ctk.CTkButton(
            toolbar,
            text="📊 Charts",
            command=self.show_visualization_dashboard,
            width=100,
            height=35,
            fg_color="#8B5CF6"
        )
        viz_btn.pack(side="left", padx=5, pady=12)
        
        # NEW: Plugin manager button
        plugin_btn = ctk.CTkButton(
            toolbar,
            text="🔌 Plugins",
            command=self.show_plugin_manager,
            width=100,
            height=35,
            fg_color="#EC4899"
        )
        plugin_btn.pack(side="left", padx=5, pady=12)
        
        # File info label (center)
        self.file_info_label = ctk.CTkLabel(
            toolbar, 
            text="No file loaded | Use Ctrl+O to import",
            font=ctk.CTkFont(size=12)
        )
        self.file_info_label.pack(side="left", padx=20, pady=12)
        
        # Right side buttons
        # AI Analysis button
        ai_btn = ctk.CTkButton(
            toolbar,
            text="🤖 AI Analysis",
            command=self.run_ai_analysis,
            width=130,
            height=35,
            fg_color="green"
        )
        ai_btn.pack(side="right", padx=5, pady=12)
        
        # NEW: PDF Export button
        pdf_btn = ctk.CTkButton(
            toolbar,
            text="📄 PDF (Ctrl+P)",
            command=self.export_to_pdf,
            width=130,
            height=35,
            fg_color="#EF4444"
        )
        pdf_btn.pack(side="right", padx=5, pady=12)
        
        # Export button
        export_btn = ctk.CTkButton(
            toolbar,
            text="💾 Export (Ctrl+E)",
            command=self.export_data,
            width=140,
            height=35
        )
        export_btn.pack(side="right", padx=5, pady=12)
        
        # Clear filters button
        clear_btn = ctk.CTkButton(
            toolbar,
            text="🔄 Clear (Esc)",
            command=self.clear_filters,
            width=120,
            height=35
        )
        clear_btn.pack(side="right", padx=5, pady=12)
    
    def create_tabbed_interface(self, parent):
        """Create tabbed interface for different views"""
        # Create tab view
        self.tab_view = ctk.CTkTabview(parent)
        self.tab_view.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Chat Analysis Tab
        chat_tab = self.tab_view.add("📱 Chat Analysis")
        self.create_chat_analysis_tab(chat_tab)
        
        # AI Insights Tab
        ai_tab = self.tab_view.add("🤖 AI Insights")
        self.create_ai_tab(ai_tab)
        
        # Statistics Tab
        stats_tab = self.tab_view.add("📊 Statistics")
        self.create_statistics_tab(stats_tab)
    
    def create_chat_analysis_tab(self, parent):
        """Create the main chat analysis tab with responsive layout"""
        content_frame = ctk.CTkFrame(parent)
        content_frame.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Configure grid weights for responsive design
        content_frame.grid_rowconfigure(0, weight=1)
        content_frame.grid_columnconfigure(0, weight=0, minsize=320)  # Filter panel
        content_frame.grid_columnconfigure(1, weight=1, minsize=400)  # Chat panel
        content_frame.grid_columnconfigure(2, weight=0, minsize=280)  # Stats panel
        
        # Left panel - Filters (responsive width)
        self.create_filter_panel(content_frame)
        
        # Middle panel - Chat viewer (expandable)
        self.create_chat_panel(content_frame)
        
        # Right panel - Quick stats (responsive width)
        self.create_quick_stats_panel(content_frame)
    
    def create_filter_panel(self, parent):
        """Create responsive left filter panel"""
        filter_frame = ctk.CTkFrame(parent)
        filter_frame.grid(row=0, column=0, sticky="nsew", padx=(5, 2), pady=5)
        
        # Configure internal grid
        filter_frame.grid_rowconfigure(1, weight=1)
        filter_frame.grid_columnconfigure(0, weight=1)
        
        # Panel title
        title = ctk.CTkLabel(
            filter_frame, 
            text="🔍 Filters",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        title.grid(row=0, column=0, pady=15, sticky="ew")
        
        # Scrollable frame with responsive sizing
        scroll_frame = ctk.CTkScrollableFrame(filter_frame)
        scroll_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=5)
        
        # Configure scroll frame grid
        scroll_frame.grid_columnconfigure(0, weight=1)
        
        # Date filter
        self.create_date_filter(scroll_frame)
        
        # Sender filter
        self.create_sender_filter(scroll_frame)
        
        # Message search
        self.create_message_search(scroll_frame)
        
        # Note: Quick filters are integrated in the date filter section above
    
    def create_date_filter(self, parent):
        """Create responsive date filter section with adaptive card layout"""
        date_frame = ctk.CTkFrame(parent)
        date_frame.pack(fill="x", pady=10)
        
        # Configure grid for responsive design
        date_frame.grid_columnconfigure(0, weight=1)
        
        # Header
        label = ctk.CTkLabel(
            date_frame, 
            text="📅 Date & Time Filter", 
            font=ctk.CTkFont(weight="bold")
        )
        label.grid(row=0, column=0, pady=(10, 5), sticky="w", padx=10)
        
        # Create a responsive container for date sections
        date_container = ctk.CTkFrame(date_frame)
        date_container.grid(row=1, column=0, sticky="ew", padx=10, pady=5)
        date_container.grid_columnconfigure(0, weight=1)
        date_container.grid_columnconfigure(1, weight=1)
        
        # Store reference for responsive behavior
        self.date_container = date_container
        
        # From date section (responsive card)
        from_section = ctk.CTkFrame(date_container)
        from_section.grid(row=0, column=0, sticky="ew", padx=(0, 5), pady=5)
        from_section.grid_columnconfigure(0, weight=1)
        
        ctk.CTkLabel(from_section, text="📅 From:", font=ctk.CTkFont(size=14, weight="bold")).grid(row=0, column=0, sticky="w", padx=5, pady=(5, 0))
        
        # Date picker with responsive width
        date_frame_from = ctk.CTkFrame(from_section)
        date_frame_from.grid(row=1, column=0, sticky="ew", padx=5, pady=2)
        date_frame_from.grid_columnconfigure(0, weight=1)
        
        # Date entry with responsive width and improved calendar behavior
        self.from_date = DateEntry(
            date_frame_from,
            width=12,  # Reduced width for better responsiveness
            background='#1a1a1a',
            foreground='white',
            borderwidth=2,
            headersbackground='#2d2d2d',
            headersforeground='white',
            selectbackground='#0078d4',
            selectforeground='white',
            normalbackground='#2d2d2d',
            normalforeground='white',
            weekendbackground='#404040',
            weekendforeground='white',
            othermonthforeground='#808080',
            othermonthbackground='#1a1a1a',
            date_pattern='dd/mm/yyyy',
            showweeknumbers=False,
            showothermonthdays=True,
            state="readonly",  # Changed to readonly to prevent typing issues
            cursor="hand2"     # Better cursor for calendar
        )
        self.from_date.grid(row=0, column=0, sticky="w", padx=2)
        
        # Responsive time selectors for FROM date
        time_from_frame = ctk.CTkFrame(from_section)
        time_from_frame.grid(row=2, column=0, sticky="ew", padx=5, pady=2)
        time_from_frame.grid_columnconfigure(1, weight=1)
        time_from_frame.grid_columnconfigure(3, weight=1)
        
        ctk.CTkLabel(time_from_frame, text="🕐", font=ctk.CTkFont(weight="bold")).grid(row=0, column=0, padx=3)
        
        # Hour input field (direct entry)
        self.from_hour = ctk.CTkEntry(
            time_from_frame,
            width=45,
            height=28,
            justify="center",
            font=ctk.CTkFont(size=11, weight="bold"),
            placeholder_text="00"
        )
        self.from_hour.insert(0, "00")
        self.from_hour.grid(row=0, column=1, padx=2, sticky="ew")
        
        ctk.CTkLabel(time_from_frame, text=":", font=ctk.CTkFont(size=14, weight="bold")).grid(row=0, column=2)
        
        # Minute input field (direct entry)
        self.from_minute = ctk.CTkEntry(
            time_from_frame,
            width=45,
            height=28,
            justify="center",
            font=ctk.CTkFont(size=11, weight="bold"),
            placeholder_text="00"
        )
        self.from_minute.insert(0, "00")
        self.from_minute.grid(row=0, column=3, padx=2, sticky="ew")
        
        # To date section (responsive card)
        to_section = ctk.CTkFrame(date_container)
        to_section.grid(row=0, column=1, sticky="ew", padx=(5, 0), pady=5)
        to_section.grid_columnconfigure(0, weight=1)
        
        ctk.CTkLabel(to_section, text="📅 To:", font=ctk.CTkFont(size=14, weight="bold")).grid(row=0, column=0, sticky="w", padx=5, pady=(5, 0))
        
        # Date picker with responsive width
        date_frame_to = ctk.CTkFrame(to_section)
        date_frame_to.grid(row=1, column=0, sticky="ew", padx=5, pady=2)
        date_frame_to.grid_columnconfigure(0, weight=1)
        
        # Date entry with responsive width and improved calendar behavior
        self.to_date = DateEntry(
            date_frame_to,
            width=12,  # Reduced width for better responsiveness
            background='#1a1a1a',
            foreground='white',
            borderwidth=2,
            headersbackground='#2d2d2d',
            headersforeground='white',
            selectbackground='#0078d4',
            selectforeground='white',
            normalbackground='#2d2d2d',
            normalforeground='white',
            weekendbackground='#404040',
            weekendforeground='white',
            othermonthforeground='#808080',
            othermonthbackground='#1a1a1a',
            date_pattern='dd/mm/yyyy',
            showweeknumbers=False,
            showothermonthdays=True,
            state="readonly",  # Changed to readonly to prevent typing issues
            cursor="hand2"     # Better cursor for calendar
        )
        self.to_date.grid(row=0, column=0, sticky="w", padx=2)
        
        # Responsive time selectors for TO date
        time_to_frame = ctk.CTkFrame(to_section)
        time_to_frame.grid(row=2, column=0, sticky="ew", padx=5, pady=2)
        time_to_frame.grid_columnconfigure(1, weight=1)
        time_to_frame.grid_columnconfigure(3, weight=1)
        
        ctk.CTkLabel(time_to_frame, text="🕐", font=ctk.CTkFont(weight="bold")).grid(row=0, column=0, padx=3)
        
        # Hour input field (direct entry)
        self.to_hour = ctk.CTkEntry(
            time_to_frame,
            width=45,
            height=28,
            justify="center",
            font=ctk.CTkFont(size=11, weight="bold"),
            placeholder_text="23"
        )
        self.to_hour.insert(0, "23")
        self.to_hour.grid(row=0, column=1, padx=2, sticky="ew")
        
        ctk.CTkLabel(time_to_frame, text=":", font=ctk.CTkFont(size=14, weight="bold")).grid(row=0, column=2)
        
        # Minute input field (direct entry)
        self.to_minute = ctk.CTkEntry(
            time_to_frame,
            width=45,
            height=28,
            justify="center",
            font=ctk.CTkFont(size=11, weight="bold"),
            placeholder_text="59"
        )
        self.to_minute.insert(0, "59")
        self.to_minute.grid(row=0, column=3, padx=2, sticky="ew")
        
        # Responsive quick presets section
        presets_frame = ctk.CTkFrame(date_frame)
        presets_frame.grid(row=2, column=0, sticky="ew", padx=10, pady=8)
        presets_frame.grid_columnconfigure(0, weight=1)
        
        ctk.CTkLabel(presets_frame, text="⚡ Quick Date Presets:", font=ctk.CTkFont(size=13, weight="bold")).grid(row=0, column=0, sticky="w", padx=8, pady=(8, 4))
        
        # Responsive preset buttons container
        preset_buttons_frame = ctk.CTkFrame(presets_frame)
        preset_buttons_frame.grid(row=1, column=0, sticky="ew", padx=5, pady=5)
        
        # Configure responsive grid for preset buttons (2x2 layout for better readability)
        for i in range(2):
            preset_buttons_frame.grid_columnconfigure(i, weight=1)
        for i in range(2):
            preset_buttons_frame.grid_rowconfigure(i, weight=1)
        
        # Preset buttons with improved styling and text
        presets = [
            ("🌅 Today", lambda: (self.set_date_preset("today"), self.apply_filters())),
            ("🌆 Yesterday", lambda: (self.set_date_preset("yesterday"), self.apply_filters())),
            ("� Last Week", lambda: (self.set_date_preset("week"), self.apply_filters())),
            ("� Last Month", lambda: (self.set_date_preset("month"), self.apply_filters()))
        ]
        
        # Arrange buttons in 2x2 grid for better spacing and readability
        positions = [(0, 0), (0, 1), (1, 0), (1, 1)]
        
        for i, (text, command) in enumerate(presets):
            row, col = positions[i]
            btn = ctk.CTkButton(
                preset_buttons_frame,
                text=text,
                command=command,
                height=38,
                font=ctk.CTkFont(size=12, weight="bold"),
                corner_radius=10,
                hover_color=("gray70", "gray30")
            )
            btn.grid(row=row, column=col, sticky="ew", padx=3, pady=3)
        
        # Clear button spanning both columns at the bottom
        clear_btn = ctk.CTkButton(
            preset_buttons_frame,
            text="🗑️ Reset All Filters",
            command=self.clear_filters,
            height=38,
            font=ctk.CTkFont(size=12, weight="bold"),
            corner_radius=10,
            fg_color=("red", "darkred"),
            hover_color=("darkred", "red"),
            border_width=0
        )
        clear_btn.grid(row=2, column=0, columnspan=2, sticky="ew", padx=3, pady=(6, 3))
        
        # Improved apply button with better styling
        apply_btn = ctk.CTkButton(
            date_frame,
            text="🔍 Apply All Filters",
            command=self.apply_filters,
            height=42,
            font=ctk.CTkFont(size=14, weight="bold"),
            corner_radius=12,
            fg_color=("green", "darkgreen"),
            hover_color=("darkgreen", "green")
        )
        apply_btn.grid(row=3, column=0, sticky="ew", padx=10, pady=12)
    
    def create_sender_filter(self, parent):
        """Create responsive sender filter section"""
        sender_frame = ctk.CTkFrame(parent)
        sender_frame.pack(fill="x", pady=10)
        
        # Configure responsive grid
        sender_frame.grid_columnconfigure(0, weight=1)
        
        label = ctk.CTkLabel(
            sender_frame, 
            text="👤 Sender Filter", 
            font=ctk.CTkFont(weight="bold")
        )
        label.grid(row=0, column=0, sticky="w", padx=10, pady=(10, 5))
        
        # Responsive sender dropdown
        self.sender_var = ctk.StringVar(value="All Senders")
        self.sender_dropdown = ctk.CTkComboBox(
            sender_frame,
            variable=self.sender_var,
            values=["All Senders"],
            command=lambda *_: self.apply_filters(),
            height=35
        )
        self.sender_dropdown.grid(row=1, column=0, sticky="ew", padx=10, pady=5)
    
    def create_message_search(self, parent):
        """Create responsive message search section"""
        search_frame = ctk.CTkFrame(parent)
        search_frame.pack(fill="x", pady=10)
        
        # Configure responsive grid
        search_frame.grid_columnconfigure(0, weight=1)
        
        label = ctk.CTkLabel(
            search_frame, 
            text="🔍 Message Search", 
            font=ctk.CTkFont(weight="bold")
        )
        label.grid(row=0, column=0, sticky="w", padx=10, pady=(10, 5))
        
        # Responsive search entry
        self.search_var = ctk.StringVar()
        self.search_entry = ctk.CTkEntry(
            search_frame,
            textvariable=self.search_var,
            placeholder_text="Search messages...",
            height=35
        )
        self.search_entry.grid(row=1, column=0, sticky="ew", padx=10, pady=5)
        # Bind Enter key to unified filter application
        self.search_entry.bind("<Return>", lambda e: self.apply_filters())

        # Search button with responsive width
        search_btn = ctk.CTkButton(
            search_frame,
            text="🔍 Search",
            command=self.apply_filters,
            height=35,
            font=ctk.CTkFont(size=12, weight="bold")
        )
        search_btn.grid(row=2, column=0, sticky="ew", padx=10, pady=5)
    
    def create_quick_filters(self, parent):
        """Create responsive quick filter buttons with adaptive layout"""
        quick_frame = ctk.CTkFrame(parent)
        quick_frame.pack(fill="x", pady=10)
        
        # Configure responsive grid
        quick_frame.grid_columnconfigure(0, weight=1)
        
        label = ctk.CTkLabel(
            quick_frame, 
            text="⚡ Quick Filters", 
            font=ctk.CTkFont(weight="bold")
        )
        label.grid(row=0, column=0, sticky="w", padx=10, pady=(10, 5))
        
        # Responsive button container
        buttons_container = ctk.CTkFrame(quick_frame)
        buttons_container.grid(row=1, column=0, sticky="ew", padx=10, pady=5)
        
        # Configure responsive grid for buttons
        for i in range(3):
            buttons_container.grid_columnconfigure(i, weight=1)
        
        # Improved quick filter buttons with better styling
        quick_filters = [
            ("🌅 Today's Messages", lambda: (self.set_date_preset("today"), self.apply_filters())),
            ("� This Week", lambda: (self.set_date_preset("week"), self.apply_filters())),
            ("� This Month", lambda: (self.set_date_preset("month"), self.apply_filters()))
        ]
        
        for i, (text, command) in enumerate(quick_filters):
            btn = ctk.CTkButton(
                buttons_container,
                text=text,
                command=command,
                height=40,
                font=ctk.CTkFont(size=12, weight="bold"),
                corner_radius=12,
                hover_color=("gray70", "gray30"),
                fg_color=("blue", "darkblue")
            )
            btn.grid(row=0, column=i, sticky="ew", padx=3, pady=3)
    
    def create_chat_panel(self, parent):
        """Create responsive middle chat display panel"""
        chat_frame = ctk.CTkFrame(parent)
        chat_frame.grid(row=0, column=1, sticky="nsew", padx=2, pady=5)
        
        # Configure responsive grid
        chat_frame.grid_rowconfigure(2, weight=1)  # Chat display expands
        chat_frame.grid_columnconfigure(0, weight=1)
        
        # Header with responsive controls
        header_frame = ctk.CTkFrame(chat_frame)
        header_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=10)
        header_frame.grid_columnconfigure(1, weight=1)
        
        header = ctk.CTkLabel(
            header_frame,
            text="💬 Chat Messages",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        header.grid(row=0, column=0, sticky="w", padx=5)
        
        # Improved and organized display controls
        controls_frame = ctk.CTkFrame(header_frame, corner_radius=8)
        controls_frame.grid(row=0, column=1, sticky="e", padx=5)
        
        # Display limit section with better styling
        limit_section = ctk.CTkFrame(controls_frame, corner_radius=6)
        limit_section.pack(side="left", padx=3, pady=3)
        
        ctk.CTkLabel(
            limit_section, 
            text="📄 Show:",
            font=ctk.CTkFont(size=11, weight="bold")
        ).pack(side="left", padx=(8, 4), pady=5)
        
        self.display_limit_var = ctk.StringVar(value="1000")
        limit_dropdown = ctk.CTkComboBox(
            limit_section,
            variable=self.display_limit_var,
            values=["500", "1000", "2000", "5000", "All"],
            width=80,
            height=28,
            font=ctk.CTkFont(size=10, weight="bold"),
            command=self.update_display_limit
        )
        limit_dropdown.pack(side="left", padx=(0, 8), pady=5)
        
        # Font size section with better styling
        font_section = ctk.CTkFrame(controls_frame, corner_radius=6)
        font_section.pack(side="left", padx=3, pady=3)
        
        ctk.CTkLabel(
            font_section, 
            text="🔤 Font:",
            font=ctk.CTkFont(size=11, weight="bold")
        ).pack(side="left", padx=(8, 4), pady=5)
        
        self.font_size_var = ctk.StringVar(value="12")
        font_dropdown = ctk.CTkComboBox(
            font_section,
            variable=self.font_size_var,
            values=["10", "11", "12", "13", "14", "16"],
            width=60,
            height=28,
            font=ctk.CTkFont(size=10, weight="bold"),
            command=self.update_font_size
        )
        font_dropdown.pack(side="left", padx=(0, 8), pady=5)
        
        # Export section with improved button
        export_section = ctk.CTkFrame(controls_frame, corner_radius=6)
        export_section.pack(side="left", padx=3, pady=3)
        
        export_visible_btn = ctk.CTkButton(
            export_section,
            text="💾 Export",
            command=self.export_visible_messages,
            width=80,
            height=28,
            font=ctk.CTkFont(size=10, weight="bold"),
            corner_radius=6,
            fg_color=("gray", "darkgray"),
            hover_color=("lightgray", "gray")
        )
        export_visible_btn.pack(padx=6, pady=5)
        
        # Progress bar for large files with responsive positioning
        self.progress_frame = ctk.CTkFrame(chat_frame)
        self.progress_frame.grid(row=1, column=0, sticky="ew", padx=10, pady=2)
        self.progress_frame.grid_forget()  # Hidden initially
        self.progress_frame.grid_columnconfigure(0, weight=1)
        
        # Progress label
        self.progress_label = ctk.CTkLabel(
            self.progress_frame,
            text="Loading...",
            font=ctk.CTkFont(size=12, weight="bold")
        )
        self.progress_label.grid(row=0, column=0, pady=5)
        
        # Progress bar
        self.progress_bar = ctk.CTkProgressBar(self.progress_frame)
        self.progress_bar.grid(row=1, column=0, sticky="ew", padx=20, pady=(0, 10))
        
        # Progress percentage
        self.progress_percentage = ctk.CTkLabel(
            self.progress_frame,
            text="0%",
            font=ctk.CTkFont(size=10)
        )
        self.progress_percentage.grid(row=2, column=0, pady=(0, 5))
        
        # Responsive status bar
        self.status_frame = ctk.CTkFrame(chat_frame, height=25)
        self.status_frame.grid(row=3, column=0, sticky="ew", padx=10, pady=2)
        self.status_frame.grid_columnconfigure(0, weight=1)
        
        self.status_label = ctk.CTkLabel(
            self.status_frame,
            text="No data loaded",
            font=ctk.CTkFont(size=10)
        )
        self.status_label.pack(side="left", padx=5)
        
        self.performance_label = ctk.CTkLabel(
            self.status_frame,
            text="",
            font=ctk.CTkFont(size=10)
        )
        self.performance_label.pack(side="right", padx=5)
        
        # Enhanced responsive chat display
        self.chat_display = ctk.CTkTextbox(
            chat_frame,
            font=("Consolas", 12),  # Use tuple format instead of CTkFont for compatibility
            wrap="word"
        )
        self.chat_display.grid(row=2, column=0, sticky="nsew", padx=10, pady=(5, 10))
        
        # Configure text tags for better formatting and sender differentiation
        try:
            # Common styles
            self.chat_display.tag_config("timestamp", foreground="#888888", font=("Consolas", 10))
            self.chat_display.tag_config("highlight", background="#FFE082", foreground="#000000")
            
            # Sender differentiation styles
            self.chat_display.tag_config("sender_user", 
                                       foreground="#4CAF50", 
                                       font=("Consolas", 12, "bold"))
            self.chat_display.tag_config("sender_other", 
                                       foreground="#FF9800", 
                                       font=("Consolas", 12, "bold"))
            
            # Message bubble styles
            self.chat_display.tag_config("message_user", 
                                       foreground="#E8F5E8",
                                       background="#1B5E20",
                                       relief="raised",
                                       borderwidth=1)
            self.chat_display.tag_config("message_other", 
                                       foreground="#FFF3E0",
                                       background="#E65100",
                                       relief="raised", 
                                       borderwidth=1)
            
            # System messages
            self.chat_display.tag_config("system", 
                                       foreground="#FFD700", 
                                       font=("Consolas", 11, "italic"))
        except:
            # Fallback if tag config fails
            self.chat_display.tag_config("timestamp", foreground="#888888")
            self.chat_display.tag_config("sender", foreground="#4CAF50")
            self.chat_display.tag_config("message", foreground="#FFFFFF")
    
    def create_quick_stats_panel(self, parent):
        """Create responsive right statistics panel"""
        stats_frame = ctk.CTkFrame(parent)
        stats_frame.grid(row=0, column=2, sticky="nsew", padx=(2, 5), pady=5)
        
        # Configure responsive grid
        stats_frame.grid_rowconfigure(1, weight=1)
        stats_frame.grid_columnconfigure(0, weight=1)
        
        # Header
        header = ctk.CTkLabel(
            stats_frame,
            text="📊 Quick Stats",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        header.grid(row=0, column=0, pady=15)
        
        # Responsive stats display
        self.stats_display = ctk.CTkTextbox(
            stats_frame,
            font=ctk.CTkFont(size=11),
            wrap="word"
        )
        self.stats_display.grid(row=1, column=0, sticky="nsew", padx=10, pady=(0, 10))
    
    def create_ai_tab(self, parent):
        """Create AI analysis tab"""
        ai_container = ctk.CTkFrame(parent)
        ai_container.pack(fill="both", expand=True, padx=5, pady=5)
        
        # AI Controls
        control_frame = ctk.CTkFrame(ai_container, height=80)
        control_frame.pack(fill="x", padx=10, pady=10)
        control_frame.pack_propagate(False)
        
        # AI Status
        self.ai_status_label = ctk.CTkLabel(
            control_frame,
            text="🤖 AI Status: Ready",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        self.ai_status_label.pack(side="left", padx=20, pady=20)
        
        # Analyze button
        self.analyze_btn = ctk.CTkButton(
            control_frame,
            text="🔍 Analyze Chat",
            command=self.run_ai_analysis,
            width=150,
            height=40
        )
        self.analyze_btn.pack(side="right", padx=20, pady=20)
        
        # AI Progress bar for analysis (initially hidden)
        self.ai_progress_frame = ctk.CTkFrame(ai_container)
        self.ai_progress_frame.pack(fill="x", padx=10, pady=2)
        self.ai_progress_frame.pack_forget()  # Hidden initially
        
        # AI Progress label
        self.ai_progress_label = ctk.CTkLabel(
            self.ai_progress_frame,
            text="AI Analysis in progress...",
            font=ctk.CTkFont(size=12, weight="bold")
        )
        self.ai_progress_label.pack(pady=5)
        
        # AI Progress bar
        self.ai_progress_bar = ctk.CTkProgressBar(self.ai_progress_frame)
        self.ai_progress_bar.pack(fill="x", padx=20, pady=(0, 10))
        
        # AI Progress percentage
        self.ai_progress_percentage = ctk.CTkLabel(
            self.ai_progress_frame,
            text="0%",
            font=ctk.CTkFont(size=10)
        )
        self.ai_progress_percentage.pack(pady=(0, 5))
        
        # Content area
        content_frame = ctk.CTkFrame(ai_container)
        content_frame.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        
        # Left - AI Chat
        self.create_ai_chat_interface(content_frame)
        
        # Right - Analysis Results
        self.create_analysis_results_panel(content_frame)
    
    def create_ai_chat_interface(self, parent):
        """Create AI chat interface"""
        chat_frame = ctk.CTkFrame(parent)
        chat_frame.pack(side="left", fill="both", expand=True, padx=(0, 5))
        
        # Header
        header = ctk.CTkLabel(
            chat_frame,
            text="🗣️ Ask AI About Your Chat",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        header.pack(pady=10)
        
        # Chat display
        self.ai_chat_display = ctk.CTkTextbox(
            chat_frame,
            font=ctk.CTkFont(size=11),
            wrap="word"
        )
        self.ai_chat_display.pack(fill="both", expand=True, padx=10, pady=5)
        
        # Input area
        input_frame = ctk.CTkFrame(chat_frame)
        input_frame.pack(fill="x", padx=10, pady=10)
        
        self.ai_question_entry = ctk.CTkEntry(
            input_frame,
            placeholder_text="Ask here"
        )
        self.ai_question_entry.pack(fill="x", side="left", padx=(0, 5))
        self.ai_question_entry.bind("<Return>", lambda e: self.ask_ai_question())
        
        ask_btn = ctk.CTkButton(
            input_frame,
            text="Ask",
            command=self.ask_ai_question,
            width=80
        )
        ask_btn.pack(side="right")
        
        # Suggested questions with scrollable frame
        suggestions_frame = ctk.CTkFrame(chat_frame)
        suggestions_frame.pack(fill="x", padx=10, pady=(0, 10))
        
        ctk.CTkLabel(
            suggestions_frame,
            text="💡 Suggested Questions:",
            font=ctk.CTkFont(weight="bold")
        ).pack(pady=5)
        
        # Create scrollable frame for suggestions
        self.suggestions_scroll_frame = ctk.CTkScrollableFrame(
            suggestions_frame,
            height=100,  # Height for exactly 3 questions
            fg_color="transparent"
        )
        self.suggestions_scroll_frame.pack(fill="x", padx=5, pady=5)
        
        suggestions = [
            "Who sent the most messages?",
            "What are the main topics discussed?",
            "Show me positive messages",
            "What's the most active time period?",
            "How are the relationship dynamics?",
            "What's the overall mood like?",
            "How have topics evolved over time?",
            "What are the key conversation summaries?",
            "Are there any interesting patterns?",
            "What insights can you provide?"
        ]
        
        for suggestion in suggestions:
            btn = ctk.CTkButton(
                self.suggestions_scroll_frame,
                text=suggestion,
                command=lambda q=suggestion: self.ask_suggested_question(q),
                height=30,
                fg_color="gray40"
            )
            btn.pack(fill="x", padx=2, pady=2)
    
    def create_analysis_results_panel(self, parent):
        """Enhanced analysis results panel with new AI features"""
        results_frame = ctk.CTkFrame(parent)
        results_frame.pack(side="right", fill="both", expand=True, padx=(5, 0))
        
        # Header
        header = ctk.CTkLabel(
            results_frame,
            text="📈 Enhanced AI Analysis Results",
            font=ctk.CTkFont(size=14, weight="bold")
        )
        header.pack(pady=10)
        
        # Results display with enhanced tabs
        self.results_tab_view = ctk.CTkTabview(results_frame)
        self.results_tab_view.pack(fill="both", expand=True, padx=10, pady=5)
        
        # Sentiment tab
        sentiment_tab = self.results_tab_view.add("😊 Sentiment")
        self.sentiment_display = ctk.CTkTextbox(
            sentiment_tab,
            font=ctk.CTkFont(size=10),
            wrap="word"
        )
        self.sentiment_display.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Topics tab
        topics_tab = self.results_tab_view.add("📝 Topics")
        self.topics_display = ctk.CTkTextbox(
            topics_tab,
            font=ctk.CTkFont(size=10),
            wrap="word"
        )
        self.topics_display.pack(fill="both", expand=True, padx=5, pady=5)
        
        # NEW: Summaries tab
        summaries_tab = self.results_tab_view.add("📋 Summaries")
        self.summaries_display = ctk.CTkTextbox(
            summaries_tab,
            font=ctk.CTkFont(size=10),
            wrap="word"
        )
        self.summaries_display.pack(fill="both", expand=True, padx=5, pady=5)
        
        # NEW: Relationship Dynamics tab
        relationships_tab = self.results_tab_view.add("💕 Relationships")
        self.relationships_display = ctk.CTkTextbox(
            relationships_tab,
            font=ctk.CTkFont(size=10),
            wrap="word"
        )
        self.relationships_display.pack(fill="both", expand=True, padx=5, pady=5)
        
        # NEW: Topic Evolution tab
        evolution_tab = self.results_tab_view.add("📈 Topic Evolution")
        self.evolution_display = ctk.CTkTextbox(
            evolution_tab,
            font=ctk.CTkFont(size=10),
            wrap="word"
        )
        self.evolution_display.pack(fill="both", expand=True, padx=5, pady=5)
        
        # NEW: Mood Tracking tab
        mood_tab = self.results_tab_view.add("🎭 Mood Tracking")
        self.mood_display = ctk.CTkTextbox(
            mood_tab,
            font=ctk.CTkFont(size=10),
            wrap="word"
        )
        self.mood_display.pack(fill="both", expand=True, padx=5, pady=5)
        
        # NEW: AI Insights tab
        insights_tab = self.results_tab_view.add("🧠 AI Insights")
        self.insights_display = ctk.CTkTextbox(
            insights_tab,
            font=ctk.CTkFont(size=10),
            wrap="word"
        )
        self.insights_display.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Patterns tab (existing)
        patterns_tab = self.results_tab_view.add("🔄 Patterns")
        self.patterns_display = ctk.CTkTextbox(
            patterns_tab,
            font=ctk.CTkFont(size=10),
            wrap="word"
        )
        self.patterns_display.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Behavior tab (existing)
        behavior_tab = self.results_tab_view.add("👥 Behavior")
        self.behavior_display = ctk.CTkTextbox(
            behavior_tab,
            font=ctk.CTkFont(size=10),
            wrap="word"
        )
        self.behavior_display.pack(fill="both", expand=True, padx=5, pady=5)
    
    def create_statistics_tab(self, parent):
        """Create detailed statistics tab with improved formatting"""
        stats_container = ctk.CTkFrame(parent)
        stats_container.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Header
        header_frame = ctk.CTkFrame(stats_container)
        header_frame.pack(fill="x", padx=10, pady=(10, 5))
        
        header = ctk.CTkLabel(
            header_frame,
            text="📊 Detailed Statistics & Analytics",
            font=ctk.CTkFont(size=18, weight="bold")
        )
        header.pack(pady=15)
        
        # Refresh button
        refresh_btn = ctk.CTkButton(
            header_frame,
            text="🔄 Refresh Statistics",
            command=self.update_detailed_stats,
            height=30,
            width=150
        )
        refresh_btn.pack(pady=5)
        
        # Statistics display with proper styling
        self.detailed_stats_display = ctk.CTkTextbox(
            stats_container,
            font=ctk.CTkFont(size=11, family="Consolas"),
            wrap="word",
            text_color=("gray10", "gray90"),  # Dark text on light, light text on dark
            fg_color=("gray95", "gray10")     # Light background on light theme, dark on dark theme
        )
        self.detailed_stats_display.pack(fill="both", expand=True, padx=20, pady=(5, 20))
        
        # Initialize with placeholder text
        self.detailed_stats_display.insert("end", 
            "📊 Welcome to Detailed Statistics!\n\n"
            "Import a WhatsApp chat file and this section will show:\n"
            "• Comprehensive message statistics\n"
            "• User activity analysis\n"
            "• Time-based insights\n"
            "• Message pattern analysis\n\n"
            "Click 'Import Chat' to get started!"
        )
    
    # Import and File Handling Methods
    def import_chat_file(self):
        """Import WhatsApp chat file"""
        file_path = filedialog.askopenfilename(
            title="Select WhatsApp Chat Export",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        
        if not file_path:
            return
        
        # Parse file in background
        self.parse_chat_file_threaded(file_path)
    
    def parse_chat_file_threaded(self, file_path):
        """Parse chat file in background thread with progress tracking"""
        import time
        
        self.file_info_label.configure(text="Loading...")
        self.root.configure(cursor="wait")
        
        # Show progress for large files
        file_size = os.path.getsize(file_path)
        file_size_mb = file_size / (1024 * 1024)
        if file_size > 5 * 1024 * 1024:  # 5MB+
            self.show_progress(True, f"📂 Loading large file ({file_size_mb:.1f}MB)...")
            self.update_status("Loading large file... Please wait")
        
        start_time = time.time()
        
        def parse_worker():
            try:
                # Enhanced progress callback
                def progress_callback(progress_pct, messages_found):
                    progress_val = progress_pct / 100
                    task_desc = f"📄 Parsing chat file"
                    additional_info = f"Found {messages_found:,} messages"
                    
                    self.root.after(0, lambda: self.update_progress(
                        progress_val, task_desc, additional_info
                    ))
                    self.root.after(0, lambda: self.update_status(
                        f"Processing... Found {messages_found:,} messages", 
                        f"{progress_pct:.1f}%"
                    ))
                
                # Parse with progress tracking
                self.chat_data = self.chat_parser.parse_chat_file(file_path)
                validation = self.chat_parser.validate_chat_data()
                
                # Calculate performance metrics
                end_time = time.time()
                parse_time = end_time - start_time
                
                performance_info = {
                    'parse_time': parse_time,
                    'file_size': file_size,
                    'messages_per_sec': len(self.chat_data) / max(parse_time, 0.001),
                    'mb_per_sec': (file_size / 1024 / 1024) / max(parse_time, 0.001)
                }
                
                if validation['valid']:
                    self.root.after(0, lambda: self.finalize_enhanced_import(file_path, validation, performance_info))
                else:
                    self.root.after(0, lambda: self.show_import_error(validation['error']))
                    
            except Exception as e:
                self.root.after(0, lambda: self.show_import_error(str(e)))
        
        threading.Thread(target=parse_worker, daemon=True).start()
    
    def finalize_enhanced_import(self, file_path, validation, performance_info):
        """Finalize import with enhanced feedback and database storage"""
        self.current_file = file_path
        self.filtered_data = []
        self.stats_cache_valid = False
        
        # NEW: Store in database for fast querying
        try:
            self.update_status("💾 Storing in database for fast access...")
            chat_id = self.chat_db.load_chat(file_path, self.chat_data)
            self.update_status(f"✅ Stored in database (Chat ID: {chat_id})")
        except Exception as e:
            print(f"Database storage error: {e}")
            # Continue even if database storage fails
        
        # Hide progress bar
        self.show_progress(False)
        
        # Update UI
        self.root.configure(cursor="")
        filename = os.path.basename(file_path)
        file_size_mb = os.path.getsize(file_path) / 1024 / 1024
        
        self.file_info_label.configure(
            text=f"📁 {filename} ({len(self.chat_data):,} messages, {file_size_mb:.1f}MB)"
        )
        
        # Update sender dropdown
        self.update_sender_dropdown()
        
        # Display data with performance info
        display_start = time.time()
        self.display_messages_optimized()
        display_time = time.time() - display_start
        
        # Update stats
        self.update_enhanced_stats()
        
        # Show performance summary
        perf_text = (f"Parse: {performance_info['parse_time']:.2f}s "
                    f"({performance_info['messages_per_sec']:.0f} msg/s, "
                    f"{performance_info['mb_per_sec']:.1f} MB/s)")
        
        self.update_status(f"Loaded {len(self.chat_data):,} messages", perf_text)
        
        # Enhanced success message
        success_msg = (f"{validation['message']}\n\n"
                      f"📈 Performance Details:\n"
                      f"• Parse Time: {performance_info['parse_time']:.2f} seconds\n"
                      f"• Processing Speed: {performance_info['messages_per_sec']:.0f} messages/sec\n"
                      f"• Display Time: {display_time:.2f} seconds\n"
                      f"• File Size: {file_size_mb:.1f} MB")
        
        messagebox.showinfo("Import Successful", success_msg)
    
    def finalize_import(self, file_path, validation):
        """Finalize import in main thread"""
        self.current_file = file_path
        self.filtered_data = []
        self.stats_cache_valid = False
        
        # Update UI
        self.root.configure(cursor="")
        filename = os.path.basename(file_path)
        self.file_info_label.configure(
            text=f"📁 {filename} ({len(self.chat_data)} messages)"
        )
        
        # Update sender dropdown
        self.update_sender_dropdown()
        
        # Display data
        self.display_messages()
        self.update_quick_stats()
        self.update_detailed_stats()
        
        messagebox.showinfo("Success", validation['message'])
    
    def show_import_error(self, error_message):
        """Show import error"""
        self.root.configure(cursor="")
        self.file_info_label.configure(text="Import failed")
        messagebox.showerror("Import Error", f"Failed to import chat file:\\n{error_message}")
    
    def update_sender_dropdown(self):
        """Update sender dropdown with available senders"""
        if not self.chat_data:
            return
        
        senders = sorted(set(msg['sender'] for msg in self.chat_data))
        self.sender_dropdown.configure(values=["All Senders"] + senders)
    
    # Filter Methods
    def apply_filters(self):
        """Apply combined date, sender, and message filters"""
        if not self.chat_data:
            messagebox.showwarning("Warning", "No chat data loaded!")
            return
        # Start with full dataset
        data = self.chat_data
        # Date & Time filtering with input validation
        try:
            # Get and validate hour/minute inputs
            from_hour_val = self.from_hour.get().strip()
            from_minute_val = self.from_minute.get().strip()
            to_hour_val = self.to_hour.get().strip()
            to_minute_val = self.to_minute.get().strip()
            
            # Validate and convert to integers
            from_hour = max(0, min(23, int(from_hour_val) if from_hour_val.isdigit() else 0))
            from_minute = max(0, min(59, int(from_minute_val) if from_minute_val.isdigit() else 0))
            to_hour = max(0, min(23, int(to_hour_val) if to_hour_val.isdigit() else 23))
            to_minute = max(0, min(59, int(to_minute_val) if to_minute_val.isdigit() else 59))
            
            from_dt = datetime.combine(
                self.from_date.get_date(),
                datetime.min.time().replace(hour=from_hour, minute=from_minute)
            )
            to_dt = datetime.combine(
                self.to_date.get_date(),
                datetime.min.time().replace(hour=to_hour, minute=to_minute)
            )
            data = [msg for msg in data if from_dt <= msg['timestamp'] <= to_dt]
        except Exception as e:
            # If date/time parsing fails, show error but continue with other filters
            messagebox.showwarning("Time Input Error", f"Invalid time format. Please use numbers 0-23 for hours, 0-59 for minutes.\nError: {str(e)}")
            pass
        # Sender filter
        sender = self.sender_var.get()
        if sender != "All Senders":
            data = [msg for msg in data if msg['sender'] == sender]
        # Message search filter
        term = self.search_var.get().lower().strip()
        if term:
            data = [msg for msg in data if term in msg['message'].lower()]
        self.filtered_data = data
        self.display_messages_optimized()
        self.update_enhanced_stats()
        messagebox.showinfo(
            "Filters Applied",
            f"Showing {len(data):,} of {len(self.chat_data):,} messages"
        )
    
    # sender and message search integrated in apply_filters
    
    
    # quick date presets integrated in apply_filters via set_date_preset then calling apply_filters
    
    def clear_filters(self):
        """Reset filter UI and clear all filters"""
        # Clear UI fields
        self.sender_var.set("All Senders")
        self.search_var.set("")
        # Reset date/time to full range
        dates = [msg['timestamp'] for msg in self.chat_data]
        if dates:
            min_dt = min(dates)
            max_dt = max(dates)
            self.from_date.set_date(min_dt.date())
            self.to_date.set_date(max_dt.date())
            
            # Update time entry fields
            self.from_hour.delete(0, 'end')
            self.from_hour.insert(0, f"{min_dt.hour:02d}")
            self.from_minute.delete(0, 'end')
            self.from_minute.insert(0, f"{min_dt.minute:02d}")
            self.to_hour.delete(0, 'end')
            self.to_hour.insert(0, f"{max_dt.hour:02d}")
            self.to_minute.delete(0, 'end')
            self.to_minute.insert(0, f"{max_dt.minute:02d}")
        # Apply
        self.apply_filters()
    
    def set_date_preset(self, preset_type):
        """Set date range based on preset"""
        today = datetime.now()
        
        if preset_type == "today":
            start_date = today.date()
            end_date = today.date()
            self.from_hour.delete(0, 'end')
            self.from_hour.insert(0, "00")
            self.from_minute.delete(0, 'end')
            self.from_minute.insert(0, "00")
            self.to_hour.delete(0, 'end')
            self.to_hour.insert(0, "23")
            self.to_minute.delete(0, 'end')
            self.to_minute.insert(0, "59")
        elif preset_type == "yesterday":
            yesterday = today - timedelta(days=1)
            start_date = yesterday.date()
            end_date = yesterday.date()
            self.from_hour.delete(0, 'end')
            self.from_hour.insert(0, "00")
            self.from_minute.delete(0, 'end')
            self.from_minute.insert(0, "00")
            self.to_hour.delete(0, 'end')
            self.to_hour.insert(0, "23")
            self.to_minute.delete(0, 'end')
            self.to_minute.insert(0, "59")
        elif preset_type == "week":
            start_date = (today - timedelta(days=7)).date()
            end_date = today.date()
            self.from_hour.delete(0, 'end')
            self.from_hour.insert(0, "00")
            self.from_minute.delete(0, 'end')
            self.from_minute.insert(0, "00")
            self.to_hour.delete(0, 'end')
            self.to_hour.insert(0, "23")
            self.to_minute.delete(0, 'end')
            self.to_minute.insert(0, "59")
        elif preset_type == "month":
            start_date = (today - timedelta(days=30)).date()
            end_date = today.date()
            self.from_hour.delete(0, 'end')
            self.from_hour.insert(0, "00")
            self.from_minute.delete(0, 'end')
            self.from_minute.insert(0, "00")
            self.to_hour.delete(0, 'end')
            self.to_hour.insert(0, "23")
            self.to_minute.delete(0, 'end')
            self.to_minute.insert(0, "59")
        
        # Update date pickers
        self.from_date.set_date(start_date)
        self.to_date.set_date(end_date)
    
    def clear_date_filters(self):
        """Clear date and time filters to show all data"""
        if not self.chat_data:
            messagebox.showwarning("Warning", "No chat data loaded!")
            return
            
        # Reset to show all data
        if self.chat_data:
            # Get the full date range from chat data
            dates = [msg['timestamp'].date() for msg in self.chat_data if 'timestamp' in msg]
            if dates:
                min_date = min(dates)
                max_date = max(dates)
                
                # Set date pickers to full range
                self.from_date.set_date(min_date)
                self.to_date.set_date(max_date)
                
                # Set time to full range using Entry methods
                self.from_hour.delete(0, 'end')
                self.from_hour.insert(0, "00")
                self.from_minute.delete(0, 'end')
                self.from_minute.insert(0, "00")
                self.to_hour.delete(0, 'end')
                self.to_hour.insert(0, "23")
                self.to_minute.delete(0, 'end')
                self.to_minute.insert(0, "59")
                
                # Apply unified filters to refresh the display
                self.apply_filters()
    
    
    # Performance-optimized display methods
    def display_messages_optimized(self):
        """Display messages with advanced optimizations for very large datasets (200MB+ files)"""
        self.chat_display.delete("1.0", "end")
        
        data = self.filtered_data if self.filtered_data else self.chat_data
        
        if not data:
            self.chat_display.insert("end", "No messages to display.\n")
            return
        
        total_messages = len(data)
        
        # Show loading message for large datasets
        if total_messages > 10000:
            self.chat_display.insert("end", f"📱 Loading {total_messages:,} messages...\n\n")
            self.root.update()
        
        # Adaptive display limits based on dataset size
        if total_messages < 1000:
            page_size = total_messages
            batch_size = 50
        elif total_messages < 10000:
            page_size = min(self.display_limit, 3000)
            batch_size = 100
        elif total_messages < 50000:
            page_size = min(self.display_limit, 2000)
            batch_size = 150
        else:  # Very large datasets (100k+ messages)
            page_size = min(self.display_limit, 1500)
            batch_size = 200
        
        display_data = data[:page_size]
        
        # Show progress for very large rendering
        if len(display_data) > 5000:
            self.show_progress(True, f"🎨 Rendering {len(display_data):,} messages with enhanced styling...")
        
        # Get unique senders to assign consistent colors
        unique_senders = list(set(msg['sender'] for msg in self.chat_data if self.chat_data))
        sender_colors = {}
        
        # Assign colors to senders (alternating between user and other styles)
        for i, sender in enumerate(unique_senders):
            if i % 2 == 0:
                sender_colors[sender] = ("sender_user", "message_user")
            else:
                sender_colors[sender] = ("sender_other", "message_other")
        
        # Use efficient batch insertion with progress tracking
        batch_elements = []  # Store tuples of (text, tags)
        total_batches = (len(display_data) + batch_size - 1) // batch_size
        
        start_time = time.time()
        
        for i, message in enumerate(display_data):
            # Optimize message formatting for performance
            timestamp_str = message['timestamp'].strftime("%d/%m/%Y %H:%M")
            
            # Truncate long sender names and messages for performance
            sender_name = message['sender']
            if len(sender_name) > 25:
                sender_name = sender_name[:22] + "..."
            
            message_text = message['message']
            if len(message_text) > 300:  # Reduced from 500 for better performance
                message_text = message_text[:297] + "..."
            
            # Get sender's assigned colors
            sender_tag, message_tag = sender_colors.get(sender_name, ("sender_user", "message_user"))
            
            # Build formatted message with visual separation
            formatted_msg = f"[{timestamp_str}] {sender_name}: 💬 {message_text}\n" + "─" * 50 + "\n"
            batch_elements.append(formatted_msg)
            
            # Insert in optimized batches
            if (i + 1) % batch_size == 0 or i == len(display_data) - 1:
                # Insert batch text
                batch_text = "".join(batch_elements)
                self.chat_display.insert("end", batch_text)
                batch_elements = []
                
                # Update progress for large datasets
                current_batch = (i + 1) // batch_size + 1
                if len(display_data) > 5000:
                    progress = (i + 1) / len(display_data)
                    task_desc = f"🎨 Rendering enhanced messages"
                    additional_info = f"Batch {current_batch}/{total_batches} ({i+1:,}/{len(display_data):,} messages)"
                    
                    self.update_progress(progress, task_desc, additional_info)
                    self.update_status(
                        f"🎨 Rendering enhanced messages... {current_batch}/{total_batches} batches", 
                        f"{i+1:,}/{len(display_data):,} messages ({progress*100:.1f}%)"
                    )
                
                # Keep UI responsive with minimal updates
                if i % (batch_size * 3) == 0:  # Update every 3 batches
                    self.root.update_idletasks()
        
        # Hide progress bar
        self.show_progress(False)
        
        # Show comprehensive pagination info
        if total_messages > page_size:
            pagination_info = f"\n{'='*60}\n"
            pagination_info += f"📄 PAGINATION INFO\n"
            pagination_info += f"{'='*60}\n"
            pagination_info += f"📊 Showing: {page_size:,} of {total_messages:,} messages ({(page_size/total_messages)*100:.1f}%)\n"
            pagination_info += f"⚡ Rendering time: {time.time() - start_time:.2f} seconds\n"
            pagination_info += f"💡 Tip: Use more specific filters to see all results\n"
            pagination_info += f"🔧 Adjust display limit in controls above\n"
            pagination_info += f"{'='*60}\n"
            self.chat_display.insert("end", pagination_info)
        
        # Update performance status
        render_time = time.time() - start_time
        messages_per_sec = len(display_data) / max(render_time, 0.001)
        self.update_status(
            f"Displayed {len(display_data):,}/{total_messages:,} messages", 
            f"Render: {render_time:.2f}s ({messages_per_sec:.0f} msg/s)"
        )
    
    def update_enhanced_stats(self):
        """Update statistics with enhanced performance"""
        data = self.filtered_data if self.filtered_data else self.chat_data
        
        if not data:
            self.stats_display.delete("1.0", "end")
            self.stats_display.insert("end", "No data available for statistics.")
            return
        
        # Use caching for better performance
        cache_key = f"{len(data)}_{hash(str(data[:10]) + str(data[-10:]) if len(data) > 20 else str(data))}"
        
        if hasattr(self, '_stats_cache') and cache_key in self._stats_cache:
            stats_text = self._stats_cache[cache_key]
        else:
            stats_text = self._calculate_enhanced_stats(data)
            if not hasattr(self, '_stats_cache'):
                self._stats_cache = {}
            self._stats_cache[cache_key] = stats_text
        
        self.stats_display.delete("1.0", "end")
        self.stats_display.insert("end", stats_text)
    
    def _calculate_enhanced_stats(self, data):
        """Calculate enhanced statistics efficiently"""
        stats = []
        
        # Basic stats
        total_messages = len(data)
        stats.append(f"📊 CHAT STATISTICS")
        stats.append(f"{'='*30}")
        stats.append(f"📝 Total Messages: {total_messages:,}")
        
        if not data:
            return "\n".join(stats)
        
        # Date range
        dates = [msg['timestamp'] for msg in data]
        date_range = f"{min(dates).strftime('%d/%m/%Y')} - {max(dates).strftime('%d/%m/%Y')}"
        stats.append(f"📅 Date Range: {date_range}")
        
        # Time span
        time_span = max(dates) - min(dates)
        stats.append(f"⏱️ Time Span: {time_span.days} days")
        
        # Sender statistics (optimized)
        sender_counts = Counter(msg['sender'] for msg in data)
        stats.append(f"\n👥 TOP SENDERS:")
        stats.append(f"{'-'*20}")
        for sender, count in sender_counts.most_common(5):
            percentage = (count / total_messages) * 100
            stats.append(f"• {sender}: {count:,} ({percentage:.1f}%)")
        
        # Message length statistics
        message_lengths = [len(msg['message']) for msg in data]
        avg_length = sum(message_lengths) / len(message_lengths)
        stats.append(f"\n📏 MESSAGE LENGTH:")
        stats.append(f"{'-'*20}")
        stats.append(f"• Average: {avg_length:.1f} characters")
        stats.append(f"• Longest: {max(message_lengths)} characters")
        stats.append(f"• Shortest: {min(message_lengths)} characters")
        
        # Time-based analysis (hourly activity)
        hour_counts = Counter(msg['timestamp'].hour for msg in data)
        most_active_hour = hour_counts.most_common(1)[0] if hour_counts else (0, 0)
        stats.append(f"\n🕐 ACTIVITY PATTERNS:")
        stats.append(f"{'-'*20}")
        stats.append(f"• Most Active Hour: {most_active_hour[0]:02d}:00 ({most_active_hour[1]:,} messages)")
        
        # Day of week analysis
        weekday_counts = Counter(msg['timestamp'].strftime('%A') for msg in data)
        most_active_day = weekday_counts.most_common(1)[0] if weekday_counts else ("Unknown", 0)
        stats.append(f"• Most Active Day: {most_active_day[0]} ({most_active_day[1]:,} messages)")
        
        # Emoji analysis (if available)
        try:
            all_messages_text = " ".join(msg['message'] for msg in data)
            emoji_count = sum(1 for char in all_messages_text if char in emoji.UNICODE_EMOJI['en'])
            stats.append(f"\n😊 CONTENT ANALYSIS:")
            stats.append(f"{'-'*20}")
            stats.append(f"• Total Emojis: {emoji_count:,}")
            if total_messages > 0:
                stats.append(f"• Emojis per Message: {emoji_count/total_messages:.2f}")
        except:
            pass
        
        return "\n".join(stats)
    
    # Display Methods
    def display_messages(self):
        """Display chat messages with enhanced visual differentiation between senders"""
        self.chat_display.delete("1.0", "end")
        
        data = self.filtered_data if self.filtered_data else self.chat_data
        
        if not data:
            self.chat_display.insert("end", "No messages to display.\n")
            return
        
        # Limit display for performance
        display_data = data[:self.display_limit]
        
        # Get unique senders to assign consistent colors
        unique_senders = list(set(msg['sender'] for msg in self.chat_data))
        sender_colors = {}
        
        # Assign colors to senders (alternating between user and other styles)
        for i, sender in enumerate(unique_senders):
            if i % 2 == 0:
                sender_colors[sender] = ("sender_user", "message_user")
            else:
                sender_colors[sender] = ("sender_other", "message_other")
        
        for i, message in enumerate(display_data):
            timestamp_str = message['timestamp'].strftime("%d/%m/%Y %H:%M")
            sender_name = message['sender']
            message_text = message['message']
            
            # Get sender's assigned colors
            sender_tag, message_tag = sender_colors.get(sender_name, ("sender_user", "message_user"))
            
            # Insert timestamp
            timestamp_start = self.chat_display.index("end-1c")
            self.chat_display.insert("end", f"[{timestamp_str}] ")
            timestamp_end = self.chat_display.index("end-1c")
            self.chat_display.tag_add("timestamp", timestamp_start, timestamp_end)
            
            # Insert sender name with appropriate styling
            sender_start = self.chat_display.index("end-1c")
            self.chat_display.insert("end", f"{sender_name}")
            sender_end = self.chat_display.index("end-1c")
            self.chat_display.tag_add(sender_tag, sender_start, sender_end)
            
            # Insert separator
            self.chat_display.insert("end", ": ")
            
            # Insert message with bubble-like styling
            message_start = self.chat_display.index("end-1c")
            
            # Handle system messages (like "Messages and calls are end-to-end encrypted")
            if "end-to-end encrypted" in message_text.lower() or \
               "security code changed" in message_text.lower() or \
               "added" in message_text.lower() and "group" in message_text.lower():
                self.chat_display.insert("end", f"📱 {message_text}")
                message_end = self.chat_display.index("end-1c")
                self.chat_display.tag_add("system", message_start, message_end)
            else:
                self.chat_display.insert("end", f"💬 {message_text}")
                message_end = self.chat_display.index("end-1c")
                self.chat_display.tag_add(message_tag, message_start, message_end)
            
            self.chat_display.insert("end", "\n" + "─" * 50 + "\n")
        
        if len(data) > self.display_limit:
            remaining_start = self.chat_display.index("end-1c")
            self.chat_display.insert("end", f"\n📊 ... and {len(data) - self.display_limit:,} more messages\n")
            remaining_end = self.chat_display.index("end-1c")
            self.chat_display.tag_add("system", remaining_start, remaining_end)
    
    def update_quick_stats(self):
        """Update quick statistics display"""
        self.stats_display.delete("1.0", "end")
        
        data = self.filtered_data if self.filtered_data else self.chat_data
        
        if not data:
            self.stats_display.insert("end", "No data available")
            return
        
        # Calculate stats
        total_messages = len(data)
        unique_senders = len(set(msg['sender'] for msg in data))
        
        # Message lengths
        message_lengths = [len(msg['message']) for msg in data]
        avg_length = sum(message_lengths) / len(message_lengths) if message_lengths else 0
        
        # Top senders
        sender_counts = Counter(msg['sender'] for msg in data)
        top_senders = sender_counts.most_common(3)
        
        # Display stats
        stats_text = f"""QUICK STATISTICS
================

📊 Overview:
• Total Messages: {total_messages:,}
• Unique Senders: {unique_senders}
• Avg Message Length: {avg_length:.1f} chars

👤 Top Senders:
"""
        
        for sender, count in top_senders:
            percentage = (count / total_messages) * 100
            stats_text += f"• {sender}: {count} ({percentage:.1f}%)\\n"
        
        # Date range
        if data:
            dates = [msg['timestamp'].date() for msg in data]
            stats_text += f"""
📅 Date Range:
• From: {min(dates)}
• To: {max(dates)}
• Duration: {(max(dates) - min(dates)).days + 1} days
"""
        
        self.stats_display.insert("end", stats_text)
    
    def update_detailed_stats(self):
        """Update detailed statistics with proper formatting"""
        self.detailed_stats_display.delete("1.0", "end")
        
        if not self.chat_data:
            self.detailed_stats_display.insert("end", "No data available for detailed statistics.\n\nPlease import a WhatsApp chat file to view detailed statistics.")
            return
        
        try:
            data = self.chat_data
            
            # Comprehensive statistics
            total_messages = len(data)
            unique_senders = len(set(msg['sender'] for msg in data))
            
            # Message analysis
            message_lengths = [len(msg['message']) for msg in data]
            total_chars = sum(message_lengths)
            avg_length = total_chars / len(message_lengths) if message_lengths else 0
            
            # Time analysis
            timestamps = [msg['timestamp'] for msg in data]
            date_range = max(timestamps) - min(timestamps)
            
            # Sender analysis
            sender_stats = {}
            for msg in data:
                sender = msg['sender']
                if sender not in sender_stats:
                    sender_stats[sender] = {
                        'messages': 0,
                        'chars': 0,
                        'avg_length': 0
                    }
                sender_stats[sender]['messages'] += 1
                sender_stats[sender]['chars'] += len(msg['message'])
            
            # Calculate averages
            for sender in sender_stats:
                stats = sender_stats[sender]
                stats['avg_length'] = stats['chars'] / stats['messages']
            
            # Format detailed stats with better structure
            stats_text = f"""📊 DETAILED CHAT STATISTICS
{"=" * 50}

� OVERVIEW
{"-" * 20}
Total Messages: {total_messages:,}
Unique Participants: {unique_senders}
Total Characters: {total_chars:,}
Average Message Length: {avg_length:.1f} characters

📅 TIME ANALYSIS
{"-" * 20}
Chat Duration: {date_range.days} days
Start Date: {min(timestamps).strftime('%d/%m/%Y %H:%M')}
End Date: {max(timestamps).strftime('%d/%m/%Y %H:%M')}
Messages per Day: {total_messages / max(1, date_range.days):.1f}

👥 SENDER STATISTICS
{"-" * 25}
"""
            
            # Sort senders by message count
            sorted_senders = sorted(sender_stats.items(), key=lambda x: x[1]['messages'], reverse=True)
            
            for i, (sender, stats) in enumerate(sorted_senders, 1):
                percentage = (stats['messages'] / total_messages) * 100
                stats_text += f"""
{i}. {sender}:
   • Messages: {stats['messages']:,} ({percentage:.1f}%)
   • Characters: {stats['chars']:,}
   • Avg Length: {stats['avg_length']:.1f} chars
   • Activity Level: {'High' if percentage > 40 else 'Medium' if percentage > 20 else 'Low'}
"""
            
            # Additional insights
            stats_text += f"""
{"-" * 50}
📋 ADDITIONAL INSIGHTS
{"-" * 25}
• Most Active User: {sorted_senders[0][0]} ({sorted_senders[0][1]['messages']:,} messages)
• Longest Message: {max(message_lengths)} characters
• Shortest Message: {min(message_lengths)} characters
• Average Daily Activity: {total_messages / max(1, date_range.days):.1f} messages/day
"""
            
            self.detailed_stats_display.insert("end", stats_text)
            
        except Exception as e:
            error_text = f"""Error generating detailed statistics:
{str(e)}

Please try reloading your chat file or contact support if the problem persists."""
            self.detailed_stats_display.insert("end", error_text)
    
    # AI Methods
    def run_ai_analysis(self):
        """Run AI analysis on chat data with enhanced progress tracking"""
        if not self.chat_data:
            messagebox.showwarning("Warning", "Please load a chat file first!")
            return
        
        # Show AI-specific progress in the AI tab
        total_messages = len(self.chat_data)
        self.show_ai_progress(True, f"🤖 Starting AI Analysis of {total_messages:,} messages...")
        
        # Update status
        self.ai_status_label.configure(text="🤖 AI Status: Analyzing...")
        self.analyze_btn.configure(state="disabled", text="🔄 Analyzing...")
        self.update_status("Starting AI analysis...", f"{total_messages:,} messages")
        self.root.update()
        
        def analysis_worker():
            try:
                # Create enhanced progress callback for AI tab
                def progress_callback(step, total_steps, current_task):
                    progress = step / total_steps
                    percentage_str = f"{int(progress*100)}%"
                    step_info = f"Step {step}/{total_steps}"
                    
                    self.root.after(0, lambda: self.update_ai_progress(
                        progress, 
                        f"🧠 AI Analysis: {current_task}", 
                        f"{step_info} ({percentage_str})"
                    ))
                    self.root.after(0, lambda: self.update_status(
                        f"🤖 AI Analysis: {current_task}", 
                        f"{step_info} - {percentage_str} complete"
                    ))
                
                # Run analysis with enhanced progress tracking
                self.analysis_results = self.ai_analyzer.analyze_chat_with_progress(
                    self.chat_data, progress_callback
                )
                self.root.after(0, self.display_analysis_results)
            except Exception as e:
                self.root.after(0, lambda: self.show_analysis_error(str(e)))
        
        threading.Thread(target=analysis_worker, daemon=True).start()
    
    def display_analysis_results(self):
        """Display enhanced AI analysis results with all new features"""
        # Hide AI-specific progress bar
        self.show_ai_progress(False)
        
        self.ai_status_label.configure(text="🤖 AI Status: ✅ Analysis Complete")
        self.analyze_btn.configure(state="normal", text="🔍 Re-analyze Chat")
        
        if 'error' in self.analysis_results:
            self.show_analysis_error(self.analysis_results['error'])
            return
        
        # Display results in respective tabs
        self.display_sentiment_analysis()
        self.display_topics_analysis()
        self.display_patterns_analysis()
        self.display_behavior_analysis()
        
        # NEW: Display enhanced AI features
        self.display_summaries_analysis()
        self.display_relationships_analysis()
        self.display_evolution_analysis()
        self.display_mood_tracking_analysis()
        self.display_ai_insights_analysis()
        
        # Add AI message
        self.add_ai_message("✅ Enhanced AI analysis complete! You can now ask me questions about your chat, including relationship dynamics, mood patterns, topic evolution, and get automated insights.")
        
        # Update status with completion info
        total_messages = len(self.chat_data)
        features_analyzed = len([k for k in self.analysis_results.keys() if k not in ['metadata', 'error']])
        self.update_status(
            "🎉 Enhanced AI analysis completed successfully", 
            f"✅ {total_messages:,} messages analyzed across {features_analyzed} AI features - Ready for questions"
        )
    
    def display_sentiment_analysis(self):
        """Display sentiment analysis results"""
        self.sentiment_display.delete("1.0", "end")
        
        sentiments = self.analysis_results.get('sentiments', [])
        if not sentiments:
            self.sentiment_display.insert("end", "No sentiment analysis available.")
            return
        
        # Calculate sentiment distribution
        categories = [s['category'] for s in sentiments]
        sentiment_counts = Counter(categories)
        total = len(sentiments)
        
        result_text = f"""😊 SENTIMENT ANALYSIS
====================

📊 Overall Distribution:
• Positive: {sentiment_counts.get('positive', 0)} ({sentiment_counts.get('positive', 0)/total*100:.1f}%)
• Neutral: {sentiment_counts.get('neutral', 0)} ({sentiment_counts.get('neutral', 0)/total*100:.1f}%)
• Negative: {sentiment_counts.get('negative', 0)} ({sentiment_counts.get('negative', 0)/total*100:.1f}%)

📝 Sample Messages:
"""
        
        # Show sample messages from each category
        for category in ['positive', 'negative', 'neutral']:
            category_messages = [s for s in sentiments[:20] if s['category'] == category]
            if category_messages:
                result_text += f"\\n{category.upper()} Examples:\\n"
                for msg in category_messages[:3]:
                    result_text += f"• {msg['message']} (score: {msg['sentiment']:.2f})\\n"
        
        self.sentiment_display.insert("end", result_text)
    
    def display_topics_analysis(self):
        """Display topic analysis results"""
        self.topics_display.delete("1.0", "end")
        
        topics = self.analysis_results.get('topics', [])
        if not topics:
            self.topics_display.insert("end", "No topic analysis available.")
            return
        
        result_text = """📝 TOPIC ANALYSIS
=================

🎯 Main Discussion Topics:
"""
        
        for i, topic in enumerate(topics):
            result_text += f"\\nTopic {i+1} ({topic['size']} messages):\\n"
            keywords = ", ".join(topic['keywords'][:8])
            result_text += f"Keywords: {keywords}\\n"
        
        self.topics_display.insert("end", result_text)
    
    def display_patterns_analysis(self):
        """Display patterns analysis results"""
        self.patterns_display.delete("1.0", "end")
        
        patterns = self.analysis_results.get('patterns', {})
        if not patterns or 'error' in patterns:
            self.patterns_display.insert("end", "No pattern analysis available.")
            return
        
        result_text = """🔄 CONVERSATION PATTERNS
========================

"""
        
        # Active hours
        if 'active_hours' in patterns:
            active_hours = patterns['active_hours']
            peak_hour = max(active_hours, key=active_hours.get)
            result_text += f"⏰ Most active hour: {peak_hour}:00 ({active_hours[peak_hour]} messages)\\n\\n"
        
        # Active days
        if 'active_days' in patterns:
            active_days = patterns['active_days']
            peak_day = max(active_days, key=active_days.get)
            result_text += f"📅 Most active day: {peak_day} ({active_days[peak_day]} messages)\\n\\n"
        
        # Response patterns
        if 'response_patterns' in patterns:
            response = patterns['response_patterns']
            if 'avg_response_time' in response:
                result_text += f"⚡ Average response time: {response['avg_response_time']:.1f} minutes\\n"
                result_text += f"Quick responses (<5 min): {response.get('quick_responses', 0)}\\n\\n"
        
        self.patterns_display.insert("end", result_text)
    
    def display_behavior_analysis(self):
        """Display user behavior analysis"""
        self.behavior_display.delete("1.0", "end")
        
        behavior = self.analysis_results.get('user_behavior', {})
        if not behavior or 'error' in behavior:
            self.behavior_display.insert("end", "No user behavior analysis available.")
            return
        
        result_text = """👥 USER BEHAVIOR ANALYSIS
=========================

"""
        
        for user, stats in behavior.items():
            result_text += f"👤 {user}:\\n"
            result_text += f"  📝 Messages: {stats.get('total_messages', 0)}\\n"
            result_text += f"  📏 Avg Length: {stats.get('avg_message_length', 0):.1f} chars\\n"
            result_text += f"  😊 Emojis: {stats.get('emoji_usage', 0)}\\n"
            
            # Top words
            top_words = stats.get('most_used_words', {})
            if top_words:
                words = list(top_words.items())[:5]
                word_list = ", ".join([f"{word}({count})" for word, count in words])
                result_text += f"  🔤 Top words: {word_list}\\n"
            
            result_text += "\\n"
        
        self.behavior_display.insert("end", result_text)
    
    # ================ NEW ENHANCED AI DISPLAY METHODS ================
    
    def display_summaries_analysis(self):
        """Display conversation summaries analysis"""
        self.summaries_display.delete("1.0", "end")
        
        summaries = self.analysis_results.get('summaries', {})
        if not summaries or 'error' in summaries:
            self.summaries_display.insert("end", "No summaries analysis available.")
            return
        
        result_text = """📋 CONVERSATION SUMMARIES
=========================

"""
        
        # Daily summaries
        if 'daily_summaries' in summaries:
            daily_summaries = summaries['daily_summaries']
            result_text += f"📅 Daily Summaries ({len(daily_summaries)} days):\\n\\n"
            
            # Show recent daily summaries
            sorted_days = sorted(daily_summaries.items())[-5:]  # Last 5 days
            for date, summary in sorted_days:
                result_text += f"📆 {date} ({summary['message_count']} messages):\\n"
                result_text += f"   {summary['summary']}\\n"
                if summary['top_keywords']:
                    keywords = ", ".join(summary['top_keywords'])
                    result_text += f"   🔑 Keywords: {keywords}\\n"
                result_text += "\\n"
        
        # Conversation segments
        if 'conversation_segments' in summaries:
            segments = summaries['conversation_segments']
            result_text += f"\\n💬 Conversation Segments ({len(segments)} segments):\\n\\n"
            
            for i, segment in enumerate(segments[:3]):  # Show first 3 segments
                duration = segment.get('duration_minutes', 0)
                result_text += f"Segment {i+1} ({duration:.1f} minutes, {segment['message_count']} messages):\\n"
                result_text += f"   {segment['summary']}\\n"
                participants = ", ".join(segment['participants'])
                result_text += f"   👥 Participants: {participants}\\n\\n"
        
        # Key moments
        if 'key_moments' in summaries:
            key_moments = summaries['key_moments']
            if key_moments:
                result_text += f"\\n⭐ Key Moments ({len(key_moments)} events):\\n\\n"
                for moment in key_moments[:3]:
                    result_text += f"📍 {moment['timestamp']}: {moment['description']}\\n"
                    result_text += f"   👥 {', '.join(moment['participants'])}\\n\\n"
        
        self.summaries_display.insert("end", result_text)
    
    def display_relationships_analysis(self):
        """Display relationship dynamics analysis"""
        self.relationships_display.delete("1.0", "end")
        
        relationships = self.analysis_results.get('relationship_dynamics', {})
        if not relationships or 'error' in relationships:
            self.relationships_display.insert("end", "No relationship analysis available.")
            return
        
        result_text = """💕 RELATIONSHIP DYNAMICS
========================

"""
        
        # Relationship strength
        if 'relationship_strength' in relationships:
            strengths = relationships['relationship_strength']
            result_text += "💪 Relationship Strength:\\n\\n"
            
            for pair, strength in strengths.items():
                strength_score = strength.get('strength_score', 0)
                response_rate = strength.get('response_rate', 0)
                balance = strength.get('message_balance', 0)
                
                if strength_score > 0.7:
                    status = "🟢 Strong"
                elif strength_score > 0.4:
                    status = "🟡 Moderate"
                else:
                    status = "🔴 Weak"
                
                result_text += f"{pair.replace('-', ' ↔ ')}: {status}\\n"
                result_text += f"   Strength: {strength_score:.2f} | Response Rate: {response_rate:.2f} | Balance: {balance:.2f}\\n\\n"
        
        # Communication styles
        if 'communication_styles' in relationships:
            styles = relationships['communication_styles']
            result_text += "\\n🗣️ Communication Styles:\\n\\n"
            
            for participant, style in styles.items():
                avg_length = style.get('avg_message_length', 0)
                emoji_freq = style.get('emoji_frequency', 0)
                question_freq = style.get('question_frequency', 0)
                response_speed = style.get('response_speed', 0)
                
                result_text += f"👤 {participant}:\\n"
                result_text += f"   📏 Avg Message Length: {avg_length:.1f} chars\\n"
                result_text += f"   😊 Emoji Usage: {emoji_freq:.3f}\\n"
                result_text += f"   ❓ Question Frequency: {question_freq:.2f}\\n"
                result_text += f"   ⚡ Avg Response Time: {response_speed:.1f} minutes\\n\\n"
        
        # Conversation balance
        if 'conversation_balance' in relationships:
            balance = relationships['conversation_balance']
            result_text += f"\\n⚖️ Conversation Balance:\\n\\n"
            result_text += f"Balance Score: {balance.get('balance_score', 0):.2f}\\n"
            result_text += f"Most Active: {balance.get('dominant_speaker', 'N/A')}\\n"
            result_text += f"Least Active: {balance.get('quiet_speaker', 'N/A')}\\n"
            result_text += f"Dominance Ratio: {balance.get('dominance_ratio', 1):.2f}\\n"
        
        self.relationships_display.insert("end", result_text)
    
    def display_evolution_analysis(self):
        """Display topic evolution analysis"""
        self.evolution_display.delete("1.0", "end")
        
        evolution = self.analysis_results.get('topic_evolution', {})
        if not evolution or 'error' in evolution:
            self.evolution_display.insert("end", "No topic evolution analysis available.")
            return
        
        result_text = """📈 TOPIC EVOLUTION ANALYSIS
===========================

"""
        
        # Topic timeline
        if 'topic_timeline' in evolution:
            timeline = evolution['topic_timeline']
            result_text += f"⏰ Topic Timeline ({len(timeline)} periods):\\n\\n"
            
            # Show recent periods
            for period in timeline[-5:]:  # Last 5 periods
                start_date = period.get('start_date', 'N/A')
                topics = period.get('topics', [])
                dominant_topic = period.get('dominant_topic', {})
                
                result_text += f"📅 Week of {start_date} ({period.get('message_count', 0)} messages):\\n"
                if dominant_topic and dominant_topic.get('keywords'):
                    keywords = ", ".join(dominant_topic['keywords'][:3])
                    result_text += f"   🎯 Dominant Topic: {keywords}\\n"
                result_text += f"   📊 Total Topics: {len(topics)}\\n\\n"
        
        # Trending topics
        if 'trending_topics' in evolution:
            trending = evolution['trending_topics']
            
            if trending.get('rising'):
                result_text += "📈 Rising Topics:\\n"
                for topic in trending['rising'][:5]:
                    result_text += f"   ⬆️ {topic['keyword']} (growth: {topic['growth']:.1f}x)\\n"
                result_text += "\\n"
            
            if trending.get('declining'):
                result_text += "📉 Declining Topics:\\n"
                for topic in trending['declining'][:3]:
                    result_text += f"   ⬇️ {topic['keyword']} (decline: {topic['decline']:.1f}x)\\n"
                result_text += "\\n"
            
            if trending.get('consistent'):
                result_text += "📊 Consistent Topics:\\n"
                for topic in trending['consistent'][:3]:
                    result_text += f"   ➡️ {topic['keyword']} (stability: {topic['stability']:.2f})\\n"
                result_text += "\\n"
        
        # Topic lifecycle
        if 'topic_lifecycle' in evolution:
            lifecycle = evolution['topic_lifecycle']
            result_text += f"🔄 Topic Lifecycle:\\n"
            result_text += f"   Birth Rate: {lifecycle.get('birth_rate', 0):.2f} new topics/period\\n"
            result_text += f"   Death Rate: {lifecycle.get('death_rate', 0):.2f} topics end/period\\n"
            result_text += f"   Avg Lifespan: {lifecycle.get('avg_lifespan', 0):.1f} periods\\n"
        
        self.evolution_display.insert("end", result_text)
    
    def display_mood_tracking_analysis(self):
        """Display mood tracking analysis"""
        self.mood_display.delete("1.0", "end")
        
        mood_tracking = self.analysis_results.get('mood_tracking', {})
        if not mood_tracking or 'error' in mood_tracking:
            self.mood_display.insert("end", "No mood tracking analysis available.")
            return
        
        result_text = """🎭 MOOD TRACKING ANALYSIS
=========================

"""
        
        # Overall mood trends
        if 'mood_trends' in mood_tracking:
            trends = mood_tracking['mood_trends']
            overall_trend = trends.get('overall_trend', 'stable')
            weekly_avg = trends.get('weekly_mood_avg', 0)
            volatility = trends.get('mood_volatility', 0)
            
            trend_emoji = "📈" if overall_trend == "improving" else "📉" if overall_trend == "declining" else "➡️"
            result_text += f"📊 Overall Mood Trend: {trend_emoji} {overall_trend.title()}\\n"
            result_text += f"📋 Average Mood Score: {weekly_avg:.2f}\\n"
            result_text += f"📊 Mood Volatility: {volatility:.2f}\\n\\n"
        
        # Participant mood patterns
        if 'participant_moods' in mood_tracking:
            participant_moods = mood_tracking['participant_moods']
            result_text += f"👥 Individual Mood Patterns:\\n\\n"
            
            for participant, mood_data in participant_moods.items():
                avg_sentiment = mood_data.get('average_sentiment', 0)
                volatility = mood_data.get('mood_volatility', 0)
                positive_ratio = mood_data.get('positive_ratio', 0)
                
                mood_emoji = "😊" if avg_sentiment > 0.1 else "😐" if avg_sentiment > -0.1 else "😔"
                stability = "Stable" if volatility < 0.3 else "Variable" if volatility < 0.6 else "Volatile"
                
                result_text += f"{mood_emoji} {participant}:\\n"
                result_text += f"   Avg Sentiment: {avg_sentiment:.2f}\\n"
                result_text += f"   Mood Stability: {stability} ({volatility:.2f})\\n"
                result_text += f"   Positive Messages: {positive_ratio*100:.1f}%\\n"
                
                best_day = mood_data.get('most_positive_day', 'N/A')
                worst_day = mood_data.get('most_negative_day', 'N/A')
                result_text += f"   Best Day: {best_day}\\n"
                result_text += f"   Challenging Day: {worst_day}\\n\\n"
        
        # Hourly patterns
        if 'hourly_patterns' in mood_tracking:
            hourly = mood_tracking['hourly_patterns']
            result_text += "⏰ Best Times for Positive Conversations:\\n"
            
            # Find top 3 most positive hours
            sorted_hours = sorted(hourly.items(), key=lambda x: x[1].get('average_sentiment', 0), reverse=True)
            for hour, data in sorted_hours[:3]:
                sentiment = data.get('average_sentiment', 0)
                result_text += f"   {hour:02d}:00 - Mood Score: {sentiment:.2f}\\n"
            result_text += "\\n"
        
        # Emotional events
        if 'emotional_events' in mood_tracking:
            events = mood_tracking['emotional_events']
            if events:
                result_text += f"⚡ Significant Emotional Events ({len(events)}):\\n\\n"
                for event in events[:3]:
                    event_emoji = "🎉" if event['type'] == 'very_positive' else "⚠️"
                    result_text += f"{event_emoji} {event['date']} - {event['type'].replace('_', ' ').title()}\\n"
                    result_text += f"   Sentiment Score: {event['sentiment_score']:.2f}\\n"
                    result_text += f"   Messages: {event['message_count']}\\n\\n"
        
        # Mood synchronization
        if 'mood_synchronization' in mood_tracking:
            sync = mood_tracking['mood_synchronization']
            if sync:
                result_text += "🔗 Mood Synchronization Between Participants:\\n\\n"
                for pair, sync_data in sync.items():
                    correlation = sync_data.get('correlation', 0)
                    strength = sync_data.get('sync_strength', 'low')
                    
                    sync_emoji = "🟢" if strength == 'high' else "🟡" if strength == 'medium' else "🔴"
                    result_text += f"{sync_emoji} {pair.replace('-', ' ↔ ')}: {strength.title()} sync\\n"
                    result_text += f"   Correlation: {correlation:.2f}\\n\\n"
        
        self.mood_display.insert("end", result_text)
    
    def display_ai_insights_analysis(self):
        """Display automated AI insights with improved formatting"""
        self.insights_display.delete("1.0", "end")
        
        insights = self.analysis_results.get('automated_insights', {})
        if not insights or 'error' in insights:
            self.insights_display.insert("end", "No automated insights available.")
            return
        
        result_text = """╔═══════════════════════════════════════╗
║            🧠 AI INSIGHTS             ║
╚═══════════════════════════════════════╝

"""
        
        # Key findings
        if 'key_findings' in insights and insights['key_findings']:
            result_text += "🔍 KEY FINDINGS\n"
            result_text += "─" * 50 + "\n\n"
            for i, finding in enumerate(insights['key_findings'][:5], 1):
                result_text += f"  {i}. {finding}\n\n"
            result_text += "\n"
        
        # Behavioral insights
        if 'behavioral_insights' in insights and insights['behavioral_insights']:
            result_text += "👤 USER BEHAVIOR PATTERNS\n"
            result_text += "─" * 50 + "\n\n"
            for insight in insights['behavioral_insights'][:3]:
                result_text += f"  • {insight}\n\n"
            result_text += "\n"
        
        # Relationship insights
        if 'relationship_insights' in insights and insights['relationship_insights']:
            result_text += "💕 RELATIONSHIP DYNAMICS\n"
            result_text += "─" * 50 + "\n\n"
            for insight in insights['relationship_insights'][:3]:
                result_text += f"  • {insight}\n\n"
            result_text += "\n"
        
        # Temporal insights
        if 'temporal_insights' in insights and insights['temporal_insights']:
            result_text += "⏰ TIME-BASED PATTERNS\n"
            result_text += "─" * 50 + "\n\n"
            for insight in insights['temporal_insights'][:3]:
                result_text += f"  • {insight}\n\n"
            result_text += "\n"
        
        # Communication insights
        if 'communication_insights' in insights and insights['communication_insights']:
            result_text += "💬 COMMUNICATION STYLE\n"
            result_text += "─" * 50 + "\n\n"
            for insight in insights['communication_insights'][:3]:
                result_text += f"  • {insight}\n\n"
            result_text += "\n"
        
        # Summary scores
        if 'summary_score' in insights:
            scores = insights['summary_score']
            result_text += "📊 OVERALL ASSESSMENT\n"
            result_text += "─" * 50 + "\n\n"
            
            for metric, score in scores.items():
                percentage = score * 100
                if percentage >= 80:
                    status = "🟢 EXCELLENT"
                    bar = "████████████████████"
                elif percentage >= 60:
                    status = "🟡 GOOD"
                    bar = "████████████████░░░░"
                elif percentage >= 40:
                    status = "🟠 FAIR"
                    bar = "████████████░░░░░░░░"
                else:
                    status = "🔴 NEEDS ATTENTION"
                    bar = "████████░░░░░░░░░░░░"
                
                metric_name = metric.replace('_', ' ').title()
                result_text += f"  {metric_name}: {status}\n"
                result_text += f"  [{bar}] {percentage:.1f}%\n\n"
            result_text += "\n"
        
        # Recommendations
        if 'recommendations' in insights and insights['recommendations']:
            result_text += "💡 AI RECOMMENDATIONS\n"
            result_text += "─" * 50 + "\n\n"
            for i, rec in enumerate(insights['recommendations'][:3], 1):
                result_text += f"  {i}. {rec}\n\n"
            result_text += "\n"
        
        # Anomalies
        if 'anomalies' in insights and insights['anomalies']:
            result_text += f"⚠️  DETECTED ANOMALIES ({len(insights['anomalies'])})\n"
            result_text += "─" * 50 + "\n\n"
            for i, anomaly in enumerate(insights['anomalies'][:3], 1):
                description = anomaly.get('description', 'Unknown anomaly')
                result_text += f"  {i}. {description}\n\n"
        
        result_text += "\n" + "═" * 55 + "\n"
        result_text += "📝 Note: This analysis is based on automated AI processing\n"
        result_text += "   and provides insights into communication patterns.\n"
        
        self.insights_display.insert("end", result_text)
    
    def show_analysis_error(self, error_message):
        """Show analysis error"""
        self.ai_status_label.configure(text="🤖 AI Status: Error")
        self.analyze_btn.configure(state="normal", text="🔍 Analyze Chat")
        messagebox.showerror("AI Analysis Error", f"Error during analysis:\\n{error_message}")
    
    def ask_ai_question(self):
        """Enhanced AI question handling with support for new features"""
        question = self.ai_question_entry.get().strip()
        if not question:
            return
        
        if not self.chat_data:
            messagebox.showwarning("Warning", "Please load a chat file first!")
            return
        
        # Add user message to display
        self.add_user_message(question)
        self.ai_question_entry.delete(0, "end")
        
        # Get AI response with enhanced question handling
        try:
            response = self.get_enhanced_ai_response(question)
            self.add_ai_message(response)
        except Exception as e:
            self.add_ai_message(f"Error processing question: {str(e)}")
    
    def get_enhanced_ai_response(self, question: str) -> str:
        """Get enhanced AI response that can handle questions about new features"""
        question_lower = question.lower()
        
        # If analysis hasn't been run yet
        if not hasattr(self, 'analysis_results') or not self.analysis_results:
            return "Please run the AI analysis first by clicking the '🤖 AI Analysis' button, then ask your question!"
        
        # Handle specific question types about new features
        if any(keyword in question_lower for keyword in ['relationship', 'dynamics', 'interaction']):
            return self._answer_relationship_question(question)
        
        elif any(keyword in question_lower for keyword in ['mood', 'emotion', 'feeling', 'sentiment over time']):
            return self._answer_mood_question(question)
        
        elif any(keyword in question_lower for keyword in ['summary', 'summarize', 'key moments']):
            return self._answer_summary_question(question)
        
        elif any(keyword in question_lower for keyword in ['topic evolution', 'trending', 'topics over time']):
            return self._answer_evolution_question(question)
        
        elif any(keyword in question_lower for keyword in ['insight', 'recommendation', 'findings']):
            return self._answer_insights_question(question)
        
        elif any(keyword in question_lower for keyword in ['pattern', 'anomaly', 'unusual']):
            return self._answer_patterns_question(question)
        
        # For general questions, use the original AI method
        try:
            return self.ai_analyzer.ask_question(question, self.chat_data)
        except Exception:
            return "I had trouble processing that question. Could you try rephrasing it or ask about specific aspects like relationships, mood, summaries, or insights?"
    
    def _answer_relationship_question(self, question: str) -> str:
        """Answer questions about relationship dynamics with improved formatting"""
        relationships = self.analysis_results.get('relationship_dynamics', {})
        if not relationships or 'error' in relationships:
            return "❌ No relationship analysis data available.\n\nPlease ensure the AI analysis completed successfully by clicking the '🤖 AI Analysis' button."
        
        response = """╔════════════════════════════════════════╗
║        � RELATIONSHIP ANALYSIS        ║
╚════════════════════════════════════════╝

"""
        
        # Relationship strengths
        if 'relationship_strength' in relationships:
            strengths = relationships['relationship_strength']
            response += "💪 RELATIONSHIP STRENGTH\n"
            response += "─" * 40 + "\n\n"
            
            for pair, strength in strengths.items():
                strength_score = strength.get('strength_score', 0)
                if strength_score > 0.7:
                    status = "🟢 STRONG"
                    bar = "████████████████████"
                elif strength_score > 0.4:
                    status = "🟡 MODERATE"
                    bar = "████████████░░░░░░░░"
                else:
                    status = "🟠 DEVELOPING"
                    bar = "████████░░░░░░░░░░░░"
                
                pair_display = pair.replace('-', ' ↔ ')
                response += f"  👥 {pair_display}\n"
                response += f"     Status: {status}\n"
                response += f"     [{bar}] {strength_score:.1%}\n\n"
            response += "\n"
        
        # Communication balance
        if 'conversation_balance' in relationships:
            balance = relationships['conversation_balance']
            response += "⚖️ CONVERSATION BALANCE\n"
            response += "─" * 40 + "\n\n"
            
            balance_score = balance.get('balance_score', 0)
            if balance_score > 0.8:
                balance_status = "🟢 WELL BALANCED"
            elif balance_score > 0.6:
                balance_status = "🟡 MODERATELY BALANCED"
            else:
                balance_status = "🟠 IMBALANCED"
            
            response += f"  Balance Score: {balance_status}\n"
            response += f"  Score: {balance_score:.1%}\n"
            response += f"  Most Active: {balance.get('dominant_speaker', 'N/A')}\n\n"
        
        response += "═" * 45 + "\n"
        response += "💡 This analysis shows relationship strength and communication patterns."
        
        return response
    
    def _answer_mood_question(self, question: str) -> str:
        """Answer questions about mood tracking with improved formatting"""
        mood_tracking = self.analysis_results.get('mood_tracking', {})
        if not mood_tracking or 'error' in mood_tracking:
            return "❌ No mood tracking data available.\n\nPlease ensure the AI analysis completed successfully by clicking the '🤖 AI Analysis' button."
        
        response = """╔════════════════════════════════════════╗
║          🎭 MOOD ANALYSIS              ║
╚════════════════════════════════════════╝

"""
        
        # Overall trends
        if 'mood_trends' in mood_tracking:
            trends = mood_tracking['mood_trends']
            trend_direction = trends.get('overall_trend', 'stable')
            avg_mood = trends.get('weekly_mood_avg', 0)
            
            if trend_direction == "improving":
                trend_emoji = "� IMPROVING"
                trend_color = "🟢"
            elif trend_direction == "declining":
                trend_emoji = "📉 DECLINING"
                trend_color = "🔴"
            else:
                trend_emoji = "➡️ STABLE"
                trend_color = "🟡"
            
            response += "📊 OVERALL MOOD TREND\n"
            response += "─" * 40 + "\n\n"
            response += f"  Direction: {trend_color} {trend_emoji}\n"
            response += f"  Average Score: {avg_mood:.1f}/5.0\n\n"
        
        # Individual participants
        if 'participant_moods' in mood_tracking:
            response += "👥 INDIVIDUAL MOOD PATTERNS\n"
            response += "─" * 40 + "\n\n"
            
            for participant, mood_data in mood_tracking['participant_moods'].items():
                avg_sentiment = mood_data.get('average_sentiment', 0)
                positive_ratio = mood_data.get('positive_ratio', 0)
                
                # Create mood bar visualization
                if avg_sentiment > 0.3:
                    mood_status = "😊 POSITIVE"
                    mood_bar = "████████████████████"
                elif avg_sentiment > 0:
                    mood_status = "😐 NEUTRAL"
                    mood_bar = "██████████░░░░░░░░░░"
                else:
                    mood_status = "😔 NEGATIVE"
                    mood_bar = "████░░░░░░░░░░░░░░░░"
                
                response += f"  👤 {participant}\n"
                response += f"     Mood: {mood_status}\n"
                response += f"     [{mood_bar}] {avg_sentiment:.1f}\n"
                response += f"     Positive Messages: {positive_ratio:.1%}\n\n"
        
        # Best conversation times
        if 'hourly_patterns' in mood_tracking:
            response += "⏰ OPTIMAL CONVERSATION TIMES\n"
            response += "─" * 40 + "\n\n"
            
            hourly = mood_tracking['hourly_patterns']
            best_hour = max(hourly.items(), key=lambda x: x[1].get('average_sentiment', 0))
            response += f"  🌟 Most Positive Hour: {best_hour[0]:02d}:00\n"
            response += f"     Sentiment Score: {best_hour[1].get('average_sentiment', 0):.2f}\n\n"
        
        response += "═" * 45 + "\n"
        response += "💡 This analysis tracks emotional patterns and conversation mood."
        
        return response
    
    def _answer_summary_question(self, question: str) -> str:
        """Answer questions about conversation summaries with improved formatting"""
        summaries = self.analysis_results.get('summaries', {})
        if not summaries or 'error' in summaries:
            return "❌ No conversation summaries available.\n\nPlease ensure the AI analysis completed successfully by clicking the '🤖 AI Analysis' button."
        
        response = """╔════════════════════════════════════════╗
║       📋 CONVERSATION SUMMARIES        ║
╚════════════════════════════════════════╝

"""
        
        # Recent daily summaries
        if 'daily_summaries' in summaries:
            daily_summaries = summaries['daily_summaries']
            response += f"📅 DAILY ACTIVITY SUMMARY\n"
            response += "─" * 40 + "\n\n"
            response += f"  📊 Total Days Analyzed: {len(daily_summaries)}\n\n"
            
            # Show last 3 days
            sorted_days = sorted(daily_summaries.items())[-3:]
            for i, (date, summary) in enumerate(sorted_days, 1):
                response += f"  {i}. 📅 {date}\n"
                response += f"     Messages: {summary['message_count']}\n"
                response += f"     Summary: {summary['summary']}\n\n"
        
        # Key moments
        if 'key_moments' in summaries and summaries['key_moments']:
            response += "⭐ KEY CONVERSATION MOMENTS\n"
            response += "─" * 40 + "\n\n"
            
            for i, moment in enumerate(summaries['key_moments'][:3], 1):
                response += f"  {i}. {moment['description']}\n\n"
        
        response += "═" * 45 + "\n"
        response += "💡 This shows important conversation highlights and daily patterns."
        
        return response
    
    def _answer_evolution_question(self, question: str) -> str:
        """Answer questions about topic evolution"""
        evolution = self.analysis_results.get('topic_evolution', {})
        if not evolution or 'error' in evolution:
            return "No topic evolution data available. Please ensure the AI analysis completed successfully."
        
        response = "📈 **Topic Evolution Analysis:**\\n\\n"
        
        # Trending topics
        if 'trending_topics' in evolution:
            trending = evolution['trending_topics']
            
            if trending.get('rising'):
                response += "📈 **Rising Topics:**\\n"
                for topic in trending['rising'][:3]:
                    response += f"• {topic['keyword']} (growth: {topic['growth']:.1f}x)\\n"
                response += "\\n"
            
            if trending.get('declining'):
                response += "📉 **Declining Topics:**\\n"
                for topic in trending['declining'][:2]:
                    response += f"• {topic['keyword']}\\n"
                response += "\\n"
        
        # Topic lifecycle
        if 'topic_lifecycle' in evolution:
            lifecycle = evolution['topic_lifecycle']
            response += f"🔄 **Topic Lifecycle:**\\n"
            response += f"• Average topic lifespan: {lifecycle.get('avg_lifespan', 0):.1f} periods\\n"
            response += f"• New topics emerging: {lifecycle.get('birth_rate', 0):.2f} per period\\n"
        
        return response
    
    def _answer_insights_question(self, question: str) -> str:
        """Answer questions about AI insights"""
        insights = self.analysis_results.get('automated_insights', {})
        if not insights or 'error' in insights:
            return "No automated insights available. Please ensure the AI analysis completed successfully."
        
        response = "🧠 **AI-Generated Insights:**\\n\\n"
        
        # Key findings
        if 'key_findings' in insights and insights['key_findings']:
            response += "🔍 **Key Findings:**\\n"
            for i, finding in enumerate(insights['key_findings'][:3], 1):
                response += f"{i}. {finding}\\n"
            response += "\\n"
        
        # Recommendations
        if 'recommendations' in insights and insights['recommendations']:
            response += "💡 **Recommendations:**\\n"
            for rec in insights['recommendations'][:2]:
                response += f"• {rec}\\n"
            response += "\\n"
        
        # Summary scores
        if 'summary_score' in insights:
            scores = insights['summary_score']
            response += "📊 **Overall Assessment:**\\n"
            for metric, score in scores.items():
                percentage = score * 100
                metric_name = metric.replace('_', ' ').title()
                response += f"• {metric_name}: {percentage:.1f}%\\n"
        
        return response
    
    def _answer_patterns_question(self, question: str) -> str:
        """Answer questions about patterns and anomalies"""
        patterns = self.analysis_results.get('patterns', {})
        insights = self.analysis_results.get('automated_insights', {})
        
        response = "🔄 **Patterns & Anomalies:**\\n\\n"
        
        # Conversation patterns
        if patterns and 'active_hours' in patterns:
            active_hours = patterns['active_hours']
            peak_hour = max(active_hours, key=active_hours.get)
            response += f"⏰ **Peak Activity:** {peak_hour}:00 ({active_hours[peak_hour]} messages)\\n\\n"
        
        # Anomalies from insights
        if insights and 'anomalies' in insights and insights['anomalies']:
            response += "⚠️ **Detected Anomalies:**\\n"
            for anomaly in insights['anomalies'][:2]:
                response += f"• {anomaly.get('description', 'Unusual pattern detected')}\\n"
            response += "\\n"
        
        return response if len(response) > 50 else "No specific patterns or anomalies detected in the current analysis."
    
    def ask_suggested_question(self, question):
        """Ask a suggested question"""
        self.ai_question_entry.delete(0, "end")
        self.ai_question_entry.insert(0, question)
        self.ask_ai_question()
    
    def add_user_message(self, message):
        """Add user message to AI chat display"""
        self.ai_chat_display.insert("end", f"👤 You: {message}\\n\\n")
        self.ai_chat_display.see("end")
    
    def add_ai_message(self, message):
        """Add AI message to chat display"""
        self.ai_chat_display.insert("end", f"🤖 AI: {message}\\n\\n")
        self.ai_chat_display.see("end")
    
    # Utility Methods
    def toggle_theme(self):
        """Toggle between light and dark themes with smooth transition"""
        try:
            # Show loading cursor during theme change
            self.root.configure(cursor="wait")
            self.root.update()
            
            if self.current_theme == "dark":
                ctk.set_appearance_mode("light")
                self.theme_btn.configure(
                    text="☀️ Light Mode",
                    fg_color=("orange", "darkorange"),
                    hover_color=("gold", "orange")
                )
                self.current_theme = "light"
            else:
                ctk.set_appearance_mode("dark")
                self.theme_btn.configure(
                    text="🌙 Dark Mode",
                    fg_color=("navy", "darkblue"),
                    hover_color=("blue", "navy")
                )
                self.current_theme = "dark"
            
            # Force UI refresh
            self.root.update_idletasks()
            
            # Reset cursor
            self.root.configure(cursor="")
            
        except Exception as e:
            # Reset cursor in case of error
            self.root.configure(cursor="")
            print(f"Theme toggle error: {e}")
    
    def export_data(self):
        """Export current data"""
        if not self.chat_data:
            messagebox.showwarning("Warning", "No data to export!")
            return
        
        file_path = filedialog.asksaveasfilename(
            title="Export Chat Data",
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        
        if file_path:
            try:
                data_to_export = self.filtered_data if self.filtered_data else self.chat_data
                
                # Convert datetime objects to strings
                export_data = []
                for msg in data_to_export:
                    export_msg = msg.copy()
                    export_msg['timestamp'] = msg['timestamp'].isoformat()
                    export_data.append(export_msg)
                
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(export_data, f, indent=2, ensure_ascii=False)
                
                messagebox.showinfo("Success", f"Exported {len(export_data)} messages to {file_path}")
                
            except Exception as e:
                messagebox.showerror("Error", f"Export failed: {str(e)}")
    
    # UI Helper Methods
    def update_display_limit(self, selected=None):
        """Update message display limit"""
        try:
            limit_str = self.display_limit_var.get()
            if limit_str == "All":
                self.display_limit = float('inf')
            else:
                self.display_limit = int(limit_str)
            
            # Refresh display
            self.display_messages_optimized()
            self.update_status(f"Display limit: {limit_str} messages")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to update display limit: {str(e)}")
    
    def update_font_size(self, selected=None):
        """Update chat display font size"""
        try:
            font_size = int(self.font_size_var.get())
            self.chat_display.configure(font=("Consolas", font_size))  # Use tuple format
            self.update_status(f"Font size: {font_size}pt")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to update font size: {str(e)}")
    
    def export_visible_messages(self):
        """Export currently visible messages"""
        data = self.filtered_data if self.filtered_data else self.chat_data
        if not data:
            messagebox.showwarning("Warning", "No messages to export!")
            return
        
        # Get visible messages based on current display limit
        if self.display_limit == float('inf'):
            visible_data = data
        else:
            visible_data = data[:min(len(data), int(self.display_limit))]
        
        file_path = filedialog.asksaveasfilename(
            title="Export Visible Messages",
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("JSON files", "*.json"), ("All files", "*.*")]
        )
        
        if file_path:
            try:
                if file_path.endswith('.json'):
                    export_data = []
                    for msg in visible_data:
                        export_msg = msg.copy()
                        export_msg['timestamp'] = msg['timestamp'].isoformat()
                        export_data.append(export_msg)
                    
                    with open(file_path, 'w', encoding='utf-8') as f:
                        json.dump(export_data, f, indent=2, ensure_ascii=False)
                else:
                    with open(file_path, 'w', encoding='utf-8') as f:
                        for msg in visible_data:
                            timestamp_str = msg['timestamp'].strftime("%d/%m/%Y %H:%M:%S")
                            f.write(f"[{timestamp_str}] {msg['sender']}: {msg['message']}\n")
                
                messagebox.showinfo("Success", f"Exported {len(visible_data)} visible messages")
                
            except Exception as e:
                messagebox.showerror("Error", f"Export failed: {str(e)}")
    
    def update_status(self, message, performance_info=""):
        """Update status bar"""
        self.status_label.configure(text=message)
        if performance_info:
            self.performance_label.configure(text=performance_info)
    
    def show_progress(self, show=True, task_name="Processing..."):
        """Show or hide enhanced progress bar with task description"""
        if show:
            self.progress_frame.pack(fill="x", padx=10, pady=5, before=self.status_frame)
            self.progress_bar.set(0)
            self.progress_label.configure(text=task_name)
            self.progress_percentage.configure(text="0%")
        else:
            self.progress_frame.pack_forget()
    
    def show_ai_progress(self, show=True, task_name="AI Analysis in progress..."):
        """Show or hide AI analysis progress bar"""
        if show:
            self.ai_progress_frame.pack(fill="x", padx=10, pady=5)
            self.ai_progress_bar.set(0)
            self.ai_progress_label.configure(text=task_name)
            self.ai_progress_percentage.configure(text="0%")
        else:
            self.ai_progress_frame.pack_forget()
    
    def update_ai_progress(self, value, task_name=None, additional_info=None):
        """Update AI progress bar value (0-1) with optional task description"""
        self.ai_progress_bar.set(value)
        percentage = int(value * 100)
        self.ai_progress_percentage.configure(text=f"{percentage}%")
        
        if task_name:
            if additional_info:
                self.ai_progress_label.configure(text=f"{task_name} - {additional_info}")
            else:
                self.ai_progress_label.configure(text=task_name)
        
        self.root.update_idletasks()
    
    def update_progress(self, value, task_name=None, additional_info=None):
        """Update progress bar value (0-1) with optional task description"""
        self.progress_bar.set(value)
        percentage = int(value * 100)
        self.progress_percentage.configure(text=f"{percentage}%")
        
        if task_name:
            if additional_info:
                self.progress_label.configure(text=f"{task_name} - {additional_info}")
            else:
                self.progress_label.configure(text=task_name)
        
        self.root.update_idletasks()
    
    def toggle_theme(self):
        """Toggle between light and dark themes"""
        if self.current_theme == "dark":
            ctk.set_appearance_mode("light")
            self.current_theme = "light"
            self.theme_btn.configure(text="🌞 Light Theme")
        else:
            ctk.set_appearance_mode("dark")
            self.current_theme = "dark"
            self.theme_btn.configure(text="🌙 Dark Theme")
        
        # Update bubble view theme if exists
        if self.bubble_view:
            self.bubble_view.set_theme(self.current_theme)
        
        # Update status
        self.update_status(f"Switched to {self.current_theme} theme")
    
    def focus_search(self):
        """Focus on search box (Ctrl+F)"""
        try:
            if hasattr(self, 'search_entry'):
                self.search_entry.focus()
                self.update_status("🔍 Search focused - Type to search messages")
        except:
            pass
    
    def export_to_pdf(self):
        """Export chat to PDF (Ctrl+P)"""
        if not self.filtered_data:
            messagebox.showwarning("No Data", "Please import and filter chat data first")
            return
        
        # Ask for save location
        filename = filedialog.asksaveasfilename(
            defaultextension=".pdf",
            filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")],
            title="Export to PDF"
        )
        
        if not filename:
            return
        
        try:
            self.update_status("📄 Generating PDF report...")
            
            # Calculate stats
            stats = {
                'total_messages': len(self.filtered_data),
                'total_senders': len(set(m['sender'] for m in self.filtered_data)),
                'date_range_start': self.filtered_data[0]['timestamp'] if self.filtered_data else 'N/A',
                'date_range_end': self.filtered_data[-1]['timestamp'] if self.filtered_data else 'N/A',
                'avg_message_length': sum(len(m['message']) for m in self.filtered_data) / len(self.filtered_data) if self.filtered_data else 0,
                'total_words': sum(len(m['message'].split()) for m in self.filtered_data)
            }
            
            # Get sender stats from database
            sender_stats = self.chat_db.get_sender_stats() if self.chat_db.current_chat_id else []
            
            # Create exporter
            exporter = PDFExporter(filename, theme="professional")
            
            # Generate comprehensive report
            success = exporter.export_comprehensive_report(
                self.filtered_data,
                stats,
                sender_stats,
                self.analysis_results
            )
            
            if success:
                self.update_status(f"✅ PDF exported successfully: {os.path.basename(filename)}")
                messagebox.showinfo("Success", f"Chat exported to PDF:\n{filename}")
            else:
                self.update_status("❌ PDF export failed")
                messagebox.showerror("Error", "Failed to generate PDF")
                
        except Exception as e:
            self.update_status(f"❌ PDF export error: {str(e)}")
            messagebox.showerror("Export Error", f"Error exporting to PDF:\n{str(e)}")
    
    def refresh_view(self):
        """Refresh current view (F5)"""
        if self.filtered_data:
            self.apply_filters()
            self.update_status("🔄 View refreshed")
    
    def show_visualization_dashboard(self):
        """Show visualization dashboard with charts"""
        if not self.filtered_data:
            messagebox.showwarning("No Data", "Please import chat data first")
            return
        
        # Create new window for dashboard
        viz_window = ctk.CTkToplevel(self.root)
        viz_window.title("Visual Analytics Dashboard")
        viz_window.geometry("1200x800")
        
        # Create dashboard
        dashboard = VisualizationDashboard(viz_window, theme=self.current_theme)
        dashboard.create_comprehensive_dashboard(self.filtered_data, self.analysis_results)
        
        self.update_status("📊 Visualization dashboard opened")
    
    def switch_to_bubble_view(self):
        """Switch chat display to bubble view"""
        if not hasattr(self, 'chat_text_frame'):
            return
        
        # Hide text view
        self.chat_text.pack_forget()
        
        # Create or show bubble view
        if not self.bubble_view:
            self.bubble_view = ChatBubbleView(self.chat_text_frame, theme=self.current_theme)
        
        self.bubble_view.load_messages(self.filtered_data, 
                                       search_term=self.search_entry.get() if hasattr(self, 'search_entry') else None)
        
        self.update_status("💬 Switched to bubble view")
    
    def switch_to_text_view(self):
        """Switch chat display to text view"""
        if not hasattr(self, 'chat_text'):
            return
        
        # Hide bubble view
        if self.bubble_view:
            self.bubble_view.clear()
        
        # Show text view
        self.chat_text.pack(fill="both", expand=True)
        self.display_messages()
        
        self.update_status("📝 Switched to text view")
    
    def show_plugin_manager(self):
        """Show plugin manager window"""
        plugin_window = ctk.CTkToplevel(self.root)
        plugin_window.title("Plugin Manager")
        plugin_window.geometry("800x600")
        
        # Title
        title = ctk.CTkLabel(
            plugin_window,
            text="🔌 Plugin Manager",
            font=ctk.CTkFont(size=20, weight="bold")
        )
        title.pack(pady=20)
        
        # Get plugin info
        plugin_info = self.plugin_manager.get_plugin_info()
        
        # Create tabbed view
        tab_view = ctk.CTkTabview(plugin_window)
        tab_view.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Analyzer plugins tab
        analyzer_tab = tab_view.add("Analyzers")
        self._create_plugin_list(analyzer_tab, plugin_info['analyzers'])
        
        # Export plugins tab
        export_tab = tab_view.add("Exporters")
        self._create_plugin_list(export_tab, plugin_info['exporters'])
        
        # Visualization plugins tab
        viz_tab = tab_view.add("Visualizations")
        self._create_plugin_list(viz_tab, plugin_info['visualizations'])
        
        self.update_status("🔌 Plugin manager opened")
    
    def _create_plugin_list(self, parent, plugins):
        """Create plugin list display"""
        scroll_frame = ctk.CTkScrollableFrame(parent)
        scroll_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        if not plugins:
            label = ctk.CTkLabel(
                scroll_frame,
                text="No plugins loaded",
                font=ctk.CTkFont(size=14)
            )
            label.pack(pady=20)
            return
        
        for plugin in plugins:
            plugin_frame = ctk.CTkFrame(scroll_frame)
            plugin_frame.pack(fill="x", padx=5, pady=5)
            
            name_label = ctk.CTkLabel(
                plugin_frame,
                text=f"📦 {plugin.get('name', 'Unknown')}",
                font=ctk.CTkFont(size=13, weight="bold")
            )
            name_label.pack(anchor="w", padx=10, pady=5)
            
            if 'description' in plugin:
                desc_label = ctk.CTkLabel(
                    plugin_frame,
                    text=plugin['description'],
                    font=ctk.CTkFont(size=11)
                )
                desc_label.pack(anchor="w", padx=20, pady=2)
            
            if 'version' in plugin:
                version_label = ctk.CTkLabel(
                    plugin_frame,
                    text=f"Version: {plugin['version']}",
                    font=ctk.CTkFont(size=10),
                    text_color="gray"
                )
                version_label.pack(anchor="w", padx=20, pady=2)
    
    def run(self):
        """Start the application"""
        self.root.mainloop()


if __name__ == "__main__":
    app = WhatsAppChatViewer()
    app.run()

