"""
Message Bubble Widget - iMessage-style chat bubbles with color coding
"""

import tkinter as tk
try:
    import customtkinter as ctk
except ImportError:
    print("Warning: customtkinter not installed. Install with: pip install customtkinter")
    ctk = None
from typing import Dict, List
import hashlib
import re


class MessageBubble:
    """Individual message bubble with styling"""
    
    # Color palette for different users
    USER_COLORS = [
        ("#0084FF", "#FFFFFF"),  # Blue (Facebook Messenger style)
        ("#34B7F1", "#FFFFFF"),  # Light Blue (Telegram style)
        ("#25D366", "#FFFFFF"),  # Green (WhatsApp style)
        ("#8B5CF6", "#FFFFFF"),  # Purple
        ("#EF4444", "#FFFFFF"),  # Red
        ("#F59E0B", "#FFFFFF"),  # Orange
        ("#10B981", "#FFFFFF"),  # Emerald
        ("#EC4899", "#FFFFFF"),  # Pink
        ("#6366F1", "#FFFFFF"),  # Indigo
        ("#14B8A6", "#FFFFFF"),  # Teal
    ]
    
    def __init__(self, parent, message_data: Dict, user_color_map: Dict, 
                 search_term: str = None, current_theme: str = "dark"):
        """
        Initialize message bubble
        
        Args:
            parent: Parent widget
            message_data: Dict with 'sender', 'message', 'timestamp'
            user_color_map: Dict mapping sender names to color indices
            search_term: Optional term to highlight
            current_theme: 'dark' or 'light'
        """
        self.parent = parent
        self.message_data = message_data
        self.user_color_map = user_color_map
        self.search_term = search_term
        self.current_theme = current_theme
        
        self.frame = None
        self.create_bubble()
    
    def create_bubble(self):
        """Create the message bubble UI"""
        sender = self.message_data.get('sender', 'Unknown')
        message = self.message_data.get('message', '')
        timestamp = self.message_data.get('timestamp', '')
        
        # Get color for this sender
        color_idx = self.user_color_map.get(sender, 0)
        bg_color, text_color = self.USER_COLORS[color_idx % len(self.USER_COLORS)]
        
        # Main container frame
        self.frame = ctk.CTkFrame(self.parent, fg_color="transparent")
        self.frame.pack(fill="x", padx=10, pady=5)
        
        # Determine alignment (alternate left/right or use sender hash)
        sender_hash = abs(hash(sender)) % 2
        side = "left" if sender_hash == 0 else "right"
        
        # Create bubble container
        bubble_container = ctk.CTkFrame(self.frame, fg_color="transparent")
        bubble_container.pack(side=side, anchor="w" if side == "left" else "e")
        
        # Sender name label (small, above bubble)
        sender_label = ctk.CTkLabel(
            bubble_container,
            text=sender,
            font=ctk.CTkFont(size=10, weight="bold"),
            text_color=bg_color
        )
        sender_label.pack(anchor="w" if side == "left" else "e", padx=12, pady=(0, 2))
        
        # Message bubble frame
        bubble_frame = ctk.CTkFrame(
            bubble_container,
            fg_color=bg_color,
            corner_radius=15,
            border_width=0
        )
        bubble_frame.pack(anchor="w" if side == "left" else "e")
        
        # Message text with highlighting
        if self.search_term and self.search_term.lower() in message.lower():
            self._create_highlighted_message(bubble_frame, message, text_color, bg_color)
        else:
            message_label = ctk.CTkLabel(
                bubble_frame,
                text=message,
                font=ctk.CTkFont(size=13),
                text_color=text_color,
                wraplength=400,
                justify="left",
                anchor="w"
            )
            message_label.pack(padx=15, pady=10, anchor="w")
        
        # Timestamp label (small, below bubble)
        time_label = ctk.CTkLabel(
            bubble_container,
            text=self._format_timestamp(timestamp),
            font=ctk.CTkFont(size=9),
            text_color="gray"
        )
        time_label.pack(anchor="w" if side == "left" else "e", padx=12, pady=(2, 0))
    
    def _create_highlighted_message(self, parent, message: str, text_color: str, bg_color: str):
        """Create message with search term highlighted"""
        # Use Text widget for highlighting capability
        text_widget = tk.Text(
            parent,
            font=("Segoe UI", 13),
            bg=bg_color,
            fg=text_color,
            wrap="word",
            width=50,
            height=message.count('\n') + 2,
            relief="flat",
            borderwidth=0,
            padx=15,
            pady=10,
            state="normal"
        )
        text_widget.pack(anchor="w")
        
        # Insert message
        text_widget.insert("1.0", message)
        
        # Highlight search term
        if self.search_term:
            search_lower = self.search_term.lower()
            message_lower = message.lower()
            
            start_idx = 0
            while True:
                start_idx = message_lower.find(search_lower, start_idx)
                if start_idx == -1:
                    break
                
                end_idx = start_idx + len(self.search_term)
                
                # Calculate line and column
                lines_before = message[:start_idx].count('\n')
                col_start = start_idx - message[:start_idx].rfind('\n') - 1
                col_end = col_start + len(self.search_term)
                
                # Create tag for highlighting
                tag_name = f"highlight_{start_idx}"
                text_widget.tag_add(tag_name, f"{lines_before + 1}.{col_start}", 
                                   f"{lines_before + 1}.{col_end}")
                text_widget.tag_config(tag_name, background="yellow", foreground="black")
                
                start_idx = end_idx
        
        text_widget.config(state="disabled")
    
    def _format_timestamp(self, timestamp: str) -> str:
        """Format timestamp for display"""
        try:
            from datetime import datetime
            if isinstance(timestamp, str):
                # Try to parse common formats
                for fmt in ["%Y-%m-%d %H:%M:%S", "%d/%m/%Y, %H:%M", "%m/%d/%y, %I:%M %p"]:
                    try:
                        dt = datetime.strptime(timestamp, fmt)
                        return dt.strftime("%I:%M %p")
                    except:
                        continue
            return timestamp
        except:
            return timestamp
    
    def destroy(self):
        """Destroy the bubble widget"""
        if self.frame:
            self.frame.destroy()


class ChatBubbleView:
    """Container for managing multiple message bubbles with virtual scrolling"""
    
    def __init__(self, parent, theme: str = "dark"):
        """Initialize bubble view"""
        self.parent = parent
        self.theme = theme
        self.bubbles = []
        self.user_color_map = {}
        self.current_search = None
        
        # Virtual scrolling parameters
        self.visible_range = (0, 50)  # Show 50 messages at a time
        self.all_messages = []
        
        # Create scrollable frame
        self.scroll_frame = ctk.CTkScrollableFrame(parent)
        self.scroll_frame.pack(fill="both", expand=True)
        
        # Bind scroll events for lazy loading
        self.scroll_frame.bind("<Configure>", self._on_scroll)
    
    def _assign_colors(self, messages: List[Dict]):
        """Assign colors to unique senders"""
        unique_senders = list(set(msg.get('sender', 'Unknown') for msg in messages))
        
        for idx, sender in enumerate(unique_senders):
            if sender not in self.user_color_map:
                self.user_color_map[sender] = idx
    
    def load_messages(self, messages: List[Dict], search_term: str = None):
        """Load messages into bubble view with virtual scrolling"""
        # Clear existing bubbles
        self.clear()
        
        self.all_messages = messages
        self.current_search = search_term
        
        # Assign colors to senders
        self._assign_colors(messages)
        
        # Load initial batch
        self._load_visible_messages()
    
    def _load_visible_messages(self):
        """Load only visible messages for performance"""
        start, end = self.visible_range
        visible_messages = self.all_messages[start:end]
        
        # Create bubbles for visible messages
        for msg_data in visible_messages:
            bubble = MessageBubble(
                self.scroll_frame,
                msg_data,
                self.user_color_map,
                self.current_search,
                self.theme
            )
            self.bubbles.append(bubble)
        
        # Show pagination info
        if len(self.all_messages) > end:
            self._show_load_more_button(end)
    
    def _show_load_more_button(self, current_end: int):
        """Show button to load more messages"""
        remaining = len(self.all_messages) - current_end
        
        load_more_frame = ctk.CTkFrame(self.scroll_frame, fg_color="transparent")
        load_more_frame.pack(fill="x", pady=20)
        
        btn = ctk.CTkButton(
            load_more_frame,
            text=f"📥 Load More ({remaining} messages remaining)",
            command=self._load_next_batch,
            height=40,
            font=ctk.CTkFont(size=13, weight="bold")
        )
        btn.pack(pady=10)
    
    def _load_next_batch(self):
        """Load next batch of messages"""
        start, end = self.visible_range
        new_end = min(end + 50, len(self.all_messages))
        self.visible_range = (start, new_end)
        
        # Reload view
        self.load_messages(self.all_messages, self.current_search)
    
    def _on_scroll(self, event):
        """Handle scroll events for lazy loading"""
        # Could implement auto-loading on scroll here
        pass
    
    def update_search(self, search_term: str):
        """Update search highlighting"""
        self.current_search = search_term
        self.load_messages(self.all_messages, search_term)
    
    def clear(self):
        """Clear all bubbles"""
        for bubble in self.bubbles:
            bubble.destroy()
        self.bubbles.clear()
        
        # Clear scroll frame
        for widget in self.scroll_frame.winfo_children():
            widget.destroy()
    
    def set_theme(self, theme: str):
        """Update theme"""
        self.theme = theme
        # Reload to apply new theme
        if self.all_messages:
            self.load_messages(self.all_messages, self.current_search)
