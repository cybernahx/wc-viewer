"""
Visualization Dashboard - Charts and graphs for chat analytics
"""

try:
    import customtkinter as ctk
except ImportError:
    print("Warning: customtkinter not installed")
    ctk = None

try:
    import matplotlib.pyplot as plt
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
    from matplotlib.figure import Figure
    import matplotlib.dates as mdates
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    print("Warning: matplotlib not installed. Charts will not be available.")
    MATPLOTLIB_AVAILABLE = False
    
from datetime import datetime, timedelta
from typing import List, Dict
try:
    import numpy as np
except ImportError:
    print("Warning: numpy not installed")
    np = None
from collections import Counter


class VisualizationDashboard:
    """Dashboard for displaying chat analytics with charts"""
    
    def __init__(self, parent, theme: str = "dark"):
        """Initialize visualization dashboard"""
        self.parent = parent
        self.theme = theme
        self.figures = []
        
        # Set matplotlib style based on theme
        self._set_matplotlib_style()
        
        # Create scrollable container
        self.scroll_frame = ctk.CTkScrollableFrame(parent)
        self.scroll_frame.pack(fill="both", expand=True, padx=10, pady=10)
    
    def _set_matplotlib_style(self):
        """Configure matplotlib for dark/light theme"""
        if self.theme == "dark":
            plt.style.use('dark_background')
            self.bg_color = '#2b2b2b'
            self.text_color = 'white'
        else:
            plt.style.use('default')
            self.bg_color = 'white'
            self.text_color = 'black'
    
    def clear(self):
        """Clear all visualizations"""
        for fig in self.figures:
            plt.close(fig)
        self.figures.clear()
        
        for widget in self.scroll_frame.winfo_children():
            widget.destroy()
    
    def create_activity_timeline(self, messages: List[Dict], title: str = "Message Activity Over Time"):
        """Create timeline chart showing message activity"""
        # Extract dates from messages
        dates = []
        for msg in messages:
            try:
                timestamp = msg.get('timestamp', '')
                # Try to parse date
                for fmt in ["%Y-%m-%d %H:%M:%S", "%d/%m/%Y, %H:%M", "%m/%d/%y, %I:%M %p"]:
                    try:
                        dt = datetime.strptime(timestamp, fmt)
                        dates.append(dt.date())
                        break
                    except:
                        continue
            except:
                continue
        
        if not dates:
            return
        
        # Count messages per day
        date_counts = Counter(dates)
        sorted_dates = sorted(date_counts.keys())
        counts = [date_counts[d] for d in sorted_dates]
        
        # Create figure
        fig = Figure(figsize=(10, 4), facecolor=self.bg_color)
        ax = fig.add_subplot(111)
        
        ax.plot(sorted_dates, counts, linewidth=2, color='#0084FF', marker='o', markersize=4)
        ax.fill_between(sorted_dates, counts, alpha=0.3, color='#0084FF')
        
        ax.set_title(title, color=self.text_color, fontsize=14, fontweight='bold', pad=20)
        ax.set_xlabel('Date', color=self.text_color, fontsize=11)
        ax.set_ylabel('Messages', color=self.text_color, fontsize=11)
        ax.grid(True, alpha=0.3, linestyle='--')
        
        # Format x-axis
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%m/%d'))
        fig.autofmt_xdate()
        
        ax.set_facecolor(self.bg_color)
        ax.tick_params(colors=self.text_color)
        
        self._add_figure_to_view(fig, title)
    
    def create_sender_distribution(self, messages: List[Dict], title: str = "Messages per Sender"):
        """Create pie chart showing sender distribution"""
        # Count messages per sender
        senders = [msg.get('sender', 'Unknown') for msg in messages]
        sender_counts = Counter(senders)
        
        # Get top 10 senders
        top_senders = sender_counts.most_common(10)
        labels = [s[0] for s in top_senders]
        sizes = [s[1] for s in top_senders]
        
        # Create figure
        fig = Figure(figsize=(8, 6), facecolor=self.bg_color)
        ax = fig.add_subplot(111)
        
        colors = ['#0084FF', '#34B7F1', '#25D366', '#8B5CF6', '#EF4444', 
                  '#F59E0B', '#10B981', '#EC4899', '#6366F1', '#14B8A6']
        
        wedges, texts, autotexts = ax.pie(
            sizes, 
            labels=labels, 
            autopct='%1.1f%%',
            colors=colors[:len(labels)],
            startangle=90,
            textprops={'color': self.text_color}
        )
        
        # Make percentage text bold
        for autotext in autotexts:
            autotext.set_color('white')
            autotext.set_fontweight('bold')
            autotext.set_fontsize(10)
        
        ax.set_title(title, color=self.text_color, fontsize=14, fontweight='bold', pad=20)
        
        self._add_figure_to_view(fig, title)
    
    def create_hourly_activity(self, messages: List[Dict], title: str = "Activity by Hour of Day"):
        """Create bar chart showing activity by hour"""
        hours = []
        for msg in messages:
            try:
                timestamp = msg.get('timestamp', '')
                for fmt in ["%Y-%m-%d %H:%M:%S", "%d/%m/%Y, %H:%M", "%m/%d/%y, %I:%M %p"]:
                    try:
                        dt = datetime.strptime(timestamp, fmt)
                        hours.append(dt.hour)
                        break
                    except:
                        continue
            except:
                continue
        
        if not hours:
            return
        
        # Count messages per hour
        hour_counts = Counter(hours)
        hour_range = range(24)
        counts = [hour_counts.get(h, 0) for h in hour_range]
        
        # Create figure
        fig = Figure(figsize=(10, 4), facecolor=self.bg_color)
        ax = fig.add_subplot(111)
        
        bars = ax.bar(hour_range, counts, color='#34B7F1', alpha=0.8, edgecolor='white', linewidth=0.5)
        
        # Highlight peak hours
        max_count = max(counts) if counts else 0
        for i, bar in enumerate(bars):
            if counts[i] == max_count and max_count > 0:
                bar.set_color('#EF4444')
        
        ax.set_title(title, color=self.text_color, fontsize=14, fontweight='bold', pad=20)
        ax.set_xlabel('Hour of Day', color=self.text_color, fontsize=11)
        ax.set_ylabel('Messages', color=self.text_color, fontsize=11)
        ax.set_xticks(hour_range)
        ax.set_xticklabels([f'{h:02d}:00' for h in hour_range], rotation=45, ha='right')
        ax.grid(True, alpha=0.3, linestyle='--', axis='y')
        
        ax.set_facecolor(self.bg_color)
        ax.tick_params(colors=self.text_color)
        
        self._add_figure_to_view(fig, title)
    
    def create_sentiment_chart(self, analysis_results: Dict, title: str = "Sentiment Distribution"):
        """Create sentiment distribution chart"""
        if 'sentiments' not in analysis_results:
            return
        
        sentiments = analysis_results['sentiments']
        categories = [s.get('category', 'neutral') for s in sentiments]
        category_counts = Counter(categories)
        
        labels = list(category_counts.keys())
        sizes = list(category_counts.values())
        colors_map = {'positive': '#10B981', 'negative': '#EF4444', 'neutral': '#6B7280'}
        colors = [colors_map.get(label, '#6B7280') for label in labels]
        
        # Create figure
        fig = Figure(figsize=(8, 5), facecolor=self.bg_color)
        ax = fig.add_subplot(111)
        
        bars = ax.bar(labels, sizes, color=colors, alpha=0.8, edgecolor='white', linewidth=1.5)
        
        # Add value labels on bars
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                   f'{int(height)}',
                   ha='center', va='bottom', color=self.text_color, fontweight='bold')
        
        ax.set_title(title, color=self.text_color, fontsize=14, fontweight='bold', pad=20)
        ax.set_ylabel('Count', color=self.text_color, fontsize=11)
        ax.grid(True, alpha=0.3, linestyle='--', axis='y')
        
        ax.set_facecolor(self.bg_color)
        ax.tick_params(colors=self.text_color)
        
        self._add_figure_to_view(fig, title)
    
    def create_message_length_distribution(self, messages: List[Dict], 
                                          title: str = "Message Length Distribution"):
        """Create histogram of message lengths"""
        lengths = [len(msg.get('message', '')) for msg in messages]
        
        if not lengths:
            return
        
        # Create figure
        fig = Figure(figsize=(10, 4), facecolor=self.bg_color)
        ax = fig.add_subplot(111)
        
        ax.hist(lengths, bins=50, color='#8B5CF6', alpha=0.7, edgecolor='white', linewidth=0.5)
        
        # Add mean line
        mean_length = np.mean(lengths)
        ax.axvline(mean_length, color='#EF4444', linestyle='--', linewidth=2, 
                   label=f'Mean: {mean_length:.1f}')
        
        ax.set_title(title, color=self.text_color, fontsize=14, fontweight='bold', pad=20)
        ax.set_xlabel('Message Length (characters)', color=self.text_color, fontsize=11)
        ax.set_ylabel('Frequency', color=self.text_color, fontsize=11)
        ax.legend(facecolor=self.bg_color, edgecolor='white', 
                 labelcolor=self.text_color, framealpha=0.9)
        ax.grid(True, alpha=0.3, linestyle='--', axis='y')
        
        ax.set_facecolor(self.bg_color)
        ax.tick_params(colors=self.text_color)
        
        self._add_figure_to_view(fig, title)
    
    def create_response_time_chart(self, messages: List[Dict], 
                                   title: str = "Response Time Patterns"):
        """Create chart showing response time patterns between users"""
        # Group messages by sender
        sender_times = {}
        
        for msg in messages:
            sender = msg.get('sender', 'Unknown')
            timestamp = msg.get('timestamp', '')
            
            try:
                for fmt in ["%Y-%m-%d %H:%M:%S", "%d/%m/%Y, %H:%M", "%m/%d/%y, %I:%M %p"]:
                    try:
                        dt = datetime.strptime(timestamp, fmt)
                        if sender not in sender_times:
                            sender_times[sender] = []
                        sender_times[sender].append(dt)
                        break
                    except:
                        continue
            except:
                continue
        
        if len(sender_times) < 2:
            return
        
        # Calculate average response times between consecutive messages
        senders = list(sender_times.keys())[:5]  # Top 5 senders
        avg_gaps = []
        
        for sender in senders:
            times = sorted(sender_times[sender])
            gaps = [(times[i+1] - times[i]).total_seconds() / 60 for i in range(len(times)-1)]
            if gaps:
                avg_gaps.append(np.mean(gaps))
            else:
                avg_gaps.append(0)
        
        # Create figure
        fig = Figure(figsize=(10, 4), facecolor=self.bg_color)
        ax = fig.add_subplot(111)
        
        bars = ax.barh(senders, avg_gaps, color='#F59E0B', alpha=0.8, edgecolor='white', linewidth=1)
        
        ax.set_title(title, color=self.text_color, fontsize=14, fontweight='bold', pad=20)
        ax.set_xlabel('Average Gap Between Messages (minutes)', color=self.text_color, fontsize=11)
        ax.grid(True, alpha=0.3, linestyle='--', axis='x')
        
        ax.set_facecolor(self.bg_color)
        ax.tick_params(colors=self.text_color)
        
        self._add_figure_to_view(fig, title)
    
    def create_comprehensive_dashboard(self, messages: List[Dict], analysis_results: Dict = None):
        """Create comprehensive dashboard with multiple charts"""
        self.clear()
        
        # Create section header
        header = ctk.CTkLabel(
            self.scroll_frame,
            text="📊 Visual Analytics Dashboard",
            font=ctk.CTkFont(size=20, weight="bold")
        )
        header.pack(pady=20)
        
        # Create all charts
        self.create_activity_timeline(messages)
        self.create_sender_distribution(messages)
        self.create_hourly_activity(messages)
        
        if analysis_results:
            self.create_sentiment_chart(analysis_results)
        
        self.create_message_length_distribution(messages)
        self.create_response_time_chart(messages)
    
    def _add_figure_to_view(self, fig: Figure, title: str):
        """Add matplotlib figure to the view"""
        # Create frame for this chart
        chart_frame = ctk.CTkFrame(self.scroll_frame, corner_radius=10)
        chart_frame.pack(fill="x", padx=10, pady=15)
        
        # Add canvas
        canvas = FigureCanvasTkAgg(fig, master=chart_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True, padx=10, pady=10)
        
        # Store figure reference
        self.figures.append(fig)
    
    def export_charts_as_images(self, export_dir: str):
        """Export all charts as PNG images"""
        import os
        os.makedirs(export_dir, exist_ok=True)
        
        for i, fig in enumerate(self.figures):
            filename = os.path.join(export_dir, f"chart_{i+1}.png")
            fig.savefig(filename, dpi=300, bbox_inches='tight', 
                       facecolor=self.bg_color, edgecolor='none')
        
        return len(self.figures)
