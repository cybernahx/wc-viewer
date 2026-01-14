"""
PDF Export Module - Export chats with formatting and charts
"""

try:
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import letter, A4
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak, Image
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT
    from reportlab.pdfgen import canvas
    REPORTLAB_AVAILABLE = True
except ImportError:
    print("Warning: reportlab not installed. PDF export will not be available.")
    REPORTLAB_AVAILABLE = False
    
from datetime import datetime
from typing import List, Dict
import os
import tempfile


class PDFExporter:
    """Export chat data and analysis to formatted PDF"""
    
    def __init__(self, output_path: str, theme: str = "professional"):
        """
        Initialize PDF exporter
        
        Args:
            output_path: Path for output PDF file
            theme: 'professional', 'modern', or 'minimal'
        """
        if not REPORTLAB_AVAILABLE:
            raise ImportError("reportlab is required for PDF export. Install with: pip install reportlab")
        
        self.output_path = output_path
        self.theme = theme
        self.doc = SimpleDocTemplate(output_path, pagesize=letter)
        self.styles = getSampleStyleSheet()
        self.story = []
        
        self._setup_custom_styles()
    
    def _setup_custom_styles(self):
        """Setup custom paragraph styles"""
        # Title style
        self.styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#0084FF'),
            spaceAfter=30,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        ))
        
        # Subtitle style
        self.styles.add(ParagraphStyle(
            name='CustomSubtitle',
            parent=self.styles['Heading2'],
            fontSize=16,
            textColor=colors.HexColor('#34B7F1'),
            spaceAfter=20,
            spaceBefore=20,
            fontName='Helvetica-Bold'
        ))
        
        # Message sender style
        self.styles.add(ParagraphStyle(
            name='MessageSender',
            parent=self.styles['Normal'],
            fontSize=10,
            textColor=colors.HexColor('#666666'),
            fontName='Helvetica-Bold',
            spaceAfter=2
        ))
        
        # Message text style
        self.styles.add(ParagraphStyle(
            name='MessageText',
            parent=self.styles['Normal'],
            fontSize=11,
            textColor=colors.black,
            spaceAfter=12,
            leftIndent=20
        ))
        
        # Stats style
        self.styles.add(ParagraphStyle(
            name='Stats',
            parent=self.styles['Normal'],
            fontSize=12,
            textColor=colors.HexColor('#333333'),
            spaceAfter=10
        ))
    
    def add_title(self, title: str, subtitle: str = None):
        """Add title page"""
        self.story.append(Spacer(1, 2*inch))
        self.story.append(Paragraph(title, self.styles['CustomTitle']))
        
        if subtitle:
            self.story.append(Spacer(1, 0.3*inch))
            self.story.append(Paragraph(subtitle, self.styles['Heading3']))
        
        # Add generation info
        self.story.append(Spacer(1, 0.5*inch))
        gen_info = f"Generated on {datetime.now().strftime('%B %d, %Y at %I:%M %p')}"
        self.story.append(Paragraph(gen_info, self.styles['Normal']))
        self.story.append(PageBreak())
    
    def add_overview_section(self, stats: Dict):
        """Add overview statistics section"""
        self.story.append(Paragraph("📊 Chat Overview", self.styles['CustomSubtitle']))
        self.story.append(Spacer(1, 0.2*inch))
        
        # Create statistics table
        data = [
            ['Metric', 'Value'],
            ['Total Messages', f"{stats.get('total_messages', 0):,}"],
            ['Total Participants', str(stats.get('total_senders', 0))],
            ['Date Range', f"{stats.get('date_range_start', 'N/A')} to {stats.get('date_range_end', 'N/A')}"],
            ['Average Message Length', f"{stats.get('avg_message_length', 0):.1f} characters"],
            ['Total Words', f"{stats.get('total_words', 0):,}"],
        ]
        
        table = Table(data, colWidths=[3*inch, 3*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#0084FF')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey]),
        ]))
        
        self.story.append(table)
        self.story.append(Spacer(1, 0.5*inch))
    
    def add_sender_statistics(self, sender_stats: List[Dict]):
        """Add sender statistics section"""
        self.story.append(Paragraph("👥 Participant Statistics", self.styles['CustomSubtitle']))
        self.story.append(Spacer(1, 0.2*inch))
        
        # Sort by message count
        sorted_senders = sorted(sender_stats, key=lambda x: x.get('message_count', 0), reverse=True)
        
        # Create table data
        data = [['Participant', 'Messages', 'Avg Length', 'Total Words', 'Emojis']]
        
        for sender in sorted_senders[:10]:  # Top 10 senders
            data.append([
                sender.get('sender_name', 'Unknown'),
                f"{sender.get('message_count', 0):,}",
                f"{sender.get('avg_message_length', 0):.1f}",
                f"{sender.get('total_words', 0):,}",
                str(sender.get('emoji_count', 0))
            ])
        
        table = Table(data, colWidths=[2*inch, 1*inch, 1*inch, 1.2*inch, 0.8*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#34B7F1')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 11),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey]),
        ]))
        
        self.story.append(table)
        self.story.append(Spacer(1, 0.5*inch))
    
    def add_messages_section(self, messages: List[Dict], max_messages: int = 100):
        """Add messages section with formatting"""
        self.story.append(Paragraph(f"💬 Messages (showing {min(len(messages), max_messages)} of {len(messages)})", 
                                   self.styles['CustomSubtitle']))
        self.story.append(Spacer(1, 0.2*inch))
        
        # Add messages
        for i, msg in enumerate(messages[:max_messages]):
            sender = msg.get('sender', 'Unknown')
            message = msg.get('message', '')
            timestamp = msg.get('timestamp', '')
            
            # Sender and timestamp
            header = f"<b>{sender}</b> • {timestamp}"
            self.story.append(Paragraph(header, self.styles['MessageSender']))
            
            # Message text (escape HTML special characters)
            safe_message = message.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
            # Limit message length for PDF
            if len(safe_message) > 500:
                safe_message = safe_message[:500] + "..."
            
            self.story.append(Paragraph(safe_message, self.styles['MessageText']))
            
            # Add page break every 20 messages
            if (i + 1) % 20 == 0 and i < max_messages - 1:
                self.story.append(PageBreak())
    
    def add_sentiment_section(self, analysis_results: Dict):
        """Add sentiment analysis section"""
        if 'sentiments' not in analysis_results:
            return
        
        self.story.append(PageBreak())
        self.story.append(Paragraph("😊 Sentiment Analysis", self.styles['CustomSubtitle']))
        self.story.append(Spacer(1, 0.2*inch))
        
        sentiments = analysis_results['sentiments']
        from collections import Counter
        sentiment_counts = Counter(s.get('category', 'neutral') for s in sentiments)
        
        # Create sentiment summary
        total = len(sentiments)
        data = [['Sentiment', 'Count', 'Percentage']]
        
        for category in ['positive', 'neutral', 'negative']:
            count = sentiment_counts.get(category, 0)
            percentage = (count / total * 100) if total > 0 else 0
            data.append([
                category.capitalize(),
                str(count),
                f"{percentage:.1f}%"
            ])
        
        table = Table(data, colWidths=[2*inch, 2*inch, 2*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#10B981')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 11),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey]),
        ]))
        
        self.story.append(table)
        self.story.append(Spacer(1, 0.3*inch))
    
    def add_chart_image(self, image_path: str, title: str = None, width: float = 6*inch):
        """Add chart image to PDF"""
        if title:
            self.story.append(Paragraph(title, self.styles['CustomSubtitle']))
            self.story.append(Spacer(1, 0.2*inch))
        
        if os.path.exists(image_path):
            img = Image(image_path, width=width, height=width*0.6)
            self.story.append(img)
            self.story.append(Spacer(1, 0.3*inch))
    
    def add_topics_section(self, analysis_results: Dict):
        """Add topics analysis section"""
        if 'topics' not in analysis_results:
            return
        
        topics = analysis_results['topics']
        if not topics:
            return
        
        self.story.append(PageBreak())
        self.story.append(Paragraph("📝 Top Discussion Topics", self.styles['CustomSubtitle']))
        self.story.append(Spacer(1, 0.2*inch))
        
        for i, topic in enumerate(topics[:5], 1):  # Top 5 topics
            keywords = ', '.join(topic.get('keywords', [])[:10])
            size = topic.get('size', 0)
            
            topic_text = f"<b>Topic {i}</b> ({size} messages)<br/>{keywords}"
            self.story.append(Paragraph(topic_text, self.styles['Stats']))
            self.story.append(Spacer(1, 0.1*inch))
    
    def generate(self):
        """Generate the PDF file"""
        try:
            self.doc.build(self.story)
            return True
        except Exception as e:
            print(f"Error generating PDF: {e}")
            return False
    
    def export_comprehensive_report(self, 
                                    messages: List[Dict], 
                                    stats: Dict,
                                    sender_stats: List[Dict],
                                    analysis_results: Dict = None,
                                    chart_images: List[str] = None):
        """
        Export comprehensive chat report
        
        Args:
            messages: List of message dictionaries
            stats: Overall statistics
            sender_stats: Per-sender statistics
            analysis_results: AI analysis results
            chart_images: List of chart image paths
        """
        # Title page
        self.add_title(
            "WhatsApp Chat Analysis Report",
            f"{stats.get('total_messages', 0):,} messages analyzed"
        )
        
        # Overview
        self.add_overview_section(stats)
        
        # Sender statistics
        if sender_stats:
            self.add_sender_statistics(sender_stats)
        
        # Charts
        if chart_images:
            self.story.append(PageBreak())
            self.story.append(Paragraph("📊 Visual Analytics", self.styles['CustomSubtitle']))
            for img_path in chart_images:
                if os.path.exists(img_path):
                    self.add_chart_image(img_path)
        
        # Sentiment analysis
        if analysis_results:
            self.add_sentiment_section(analysis_results)
            self.add_topics_section(analysis_results)
        
        # Messages
        self.add_messages_section(messages, max_messages=100)
        
        # Generate
        return self.generate()


def export_to_pdf(messages: List[Dict], 
                 output_path: str,
                 stats: Dict = None,
                 sender_stats: List[Dict] = None,
                 analysis_results: Dict = None) -> bool:
    """
    Convenience function to export chat to PDF
    
    Args:
        messages: List of message dictionaries
        output_path: Path for output PDF
        stats: Overall statistics
        sender_stats: Per-sender statistics
        analysis_results: AI analysis results
    
    Returns:
        True if successful, False otherwise
    """
    exporter = PDFExporter(output_path)
    
    # Calculate basic stats if not provided
    if stats is None:
        stats = {
            'total_messages': len(messages),
            'total_senders': len(set(m.get('sender', 'Unknown') for m in messages)),
            'date_range_start': messages[0].get('timestamp', 'N/A') if messages else 'N/A',
            'date_range_end': messages[-1].get('timestamp', 'N/A') if messages else 'N/A',
            'avg_message_length': sum(len(m.get('message', '')) for m in messages) / len(messages) if messages else 0,
            'total_words': sum(len(m.get('message', '').split()) for m in messages)
        }
    
    return exporter.export_comprehensive_report(
        messages,
        stats,
        sender_stats or [],
        analysis_results
    )
