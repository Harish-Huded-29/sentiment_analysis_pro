"""
ENHANCED PDF Report Generator for Sentiment Analysis
Creates professional PDF reports with AI-generated summaries for all sentiments
"""

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.graphics.shapes import Drawing, Rect
from reportlab.graphics.charts.piecharts import Pie
from reportlab.graphics.charts.barcharts import VerticalBarChart
from datetime import datetime
import os
import requests


class EnhancedPDFReportGenerator:
    """Generate professional PDF reports with AI summaries"""
    
    def __init__(self, output_path):
        self.output_path = output_path
        self.doc = SimpleDocTemplate(output_path, pagesize=letter)
        self.styles = getSampleStyleSheet()
        self.story = []
        self.width, self.height = letter
        
        # Custom styles
        self.title_style = ParagraphStyle(
            'CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#667eea'),
            spaceAfter=30,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        )
        
        self.heading_style = ParagraphStyle(
            'CustomHeading',
            parent=self.styles['Heading2'],
            fontSize=16,
            textColor=colors.HexColor('#667eea'),
            spaceAfter=12,
            spaceBefore=12,
            fontName='Helvetica-Bold'
        )
        
        self.subheading_style = ParagraphStyle(
            'CustomSubHeading',
            parent=self.styles['Heading3'],
            fontSize=13,
            textColor=colors.HexColor('#764ba2'),
            spaceAfter=10,
            spaceBefore=10,
            fontName='Helvetica-Bold'
        )
        
        self.body_style = ParagraphStyle(
            'CustomBody',
            parent=self.styles['Normal'],
            fontSize=11,
            textColor=colors.HexColor('#333333'),
            spaceAfter=10,
            leading=16
        )
        
        self.footer_style = ParagraphStyle(
            'CustomFooter',
            parent=self.styles['Normal'],
            fontSize=9,
            textColor=colors.HexColor('#666666'),
            alignment=TA_CENTER
        )
    
    def add_page_break(self):
        """Add page break"""
        self.story.append(PageBreak())
    
    def add_header(self, title, subtitle=None):
        """Add report header"""
        self.story.append(Paragraph(title, self.title_style))
        
        if subtitle:
            subtitle_style = ParagraphStyle(
                'Subtitle',
                parent=self.styles['Normal'],
                fontSize=12,
                textColor=colors.HexColor('#764ba2'),
                alignment=TA_CENTER,
                spaceAfter=20
            )
            self.story.append(Paragraph(subtitle, subtitle_style))
        
        self.story.append(Spacer(1, 0.3 * inch))
    
    def add_metadata_table(self, metadata):
        """Add metadata information table"""
        data = []
        for key, value in metadata.items():
            data.append([
                Paragraph(f"<b>{key}</b>", self.body_style),
                Paragraph(str(value), self.body_style)
            ])
        
        table = Table(data, colWidths=[2.5*inch, 4*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#f8f9fa')),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.HexColor('#333333')),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
            ('TOPPADDING', (0, 0), (-1, -1), 12),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#e0e0e0'))
        ]))
        
        self.story.append(table)
        self.story.append(Spacer(1, 0.3 * inch))
    
    def add_statistics_table(self, stats):
        """Add sentiment statistics table"""
        self.story.append(Paragraph("Sentiment Distribution", self.heading_style))
        
        data = [
            [
                Paragraph("<b>Sentiment</b>", self.body_style),
                Paragraph("<b>Count</b>", self.body_style),
                Paragraph("<b>Percentage</b>", self.body_style)
            ]
        ]
        
        colors_map = {
            'Positive': colors.HexColor('#d1fae5'),
            'Negative': colors.HexColor('#fee2e2'),
            'Neutral': colors.HexColor('#fef3c7')
        }
        
        for sentiment, count, percentage in stats:
            data.append([
                Paragraph(f"<b>{sentiment}</b>", self.body_style),
                Paragraph(f"{count:,}", self.body_style),
                Paragraph(f"{percentage:.1f}%", self.body_style)
            ])
        
        table = Table(data, colWidths=[2*inch, 2*inch, 2*inch])
        
        style_commands = [
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#667eea')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('TOPPADDING', (0, 0), (-1, 0), 12),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#e0e0e0'))
        ]
        
        for i, (sentiment, _, _) in enumerate(stats, 1):
            bg_color = colors_map.get(sentiment, colors.white)
            style_commands.append(('BACKGROUND', (0, i), (-1, i), bg_color))
        
        table.setStyle(TableStyle(style_commands))
        
        self.story.append(table)
        self.story.append(Spacer(1, 0.3 * inch))
    
    def add_pie_chart(self, data, title):
        """Add pie chart for sentiment distribution"""
        self.story.append(Paragraph(title, self.heading_style))
        
        drawing = Drawing(400, 200)
        pie = Pie()
        pie.x = 150
        pie.y = 50
        pie.width = 120
        pie.height = 120
        
        pie.data = [d[1] for d in data]
        pie.labels = [d[0] for d in data]
        
        pie.slices[0].fillColor = colors.HexColor('#10b981')  # Positive
        pie.slices[1].fillColor = colors.HexColor('#ef4444')  # Negative
        pie.slices[2].fillColor = colors.HexColor('#f59e0b')  # Neutral
        
        drawing.add(pie)
        
        self.story.append(drawing)
        self.story.append(Spacer(1, 0.3 * inch))
    
    def add_timeline_chart(self, timeline_data):
        """Add line chart showing sentiment flow over time"""
        from reportlab.graphics.charts.linecharts import HorizontalLineChart
        
        drawing = Drawing(500, 250)
        chart = HorizontalLineChart()
        chart.x = 50
        chart.y = 50
        chart.width = 400
        chart.height = 150
        
        # Sample data (take max 50 points for clarity)
        step = max(1, len(timeline_data) // 50)
        sampled = timeline_data[::step][:50]
        
        # Prepare data
        positive_points = []
        negative_points = []
        neutral_points = []
        
        for point in sampled:
            if point['sentiment'] == 'positive':
                positive_points.append(point['row'])
            else:
                positive_points.append(None)
                
            if point['sentiment'] == 'negative':
                negative_points.append(point['row'])
            else:
                negative_points.append(None)
                
            if point['sentiment'] == 'neutral':
                neutral_points.append(point['row'])
            else:
                neutral_points.append(None)
        
        chart.data = [positive_points, negative_points, neutral_points]
        chart.categoryAxis.categoryNames = [str(p['row']) for p in sampled]
        
        # Styling
        chart.lines[0].strokeColor = colors.HexColor('#10b981')  # Positive
        chart.lines[0].strokeWidth = 2
        chart.lines[1].strokeColor = colors.HexColor('#ef4444')  # Negative
        chart.lines[1].strokeWidth = 2
        chart.lines[2].strokeColor = colors.HexColor('#f59e0b')  # Neutral
        chart.lines[2].strokeWidth = 2
        
        # Axes
        chart.valueAxis.valueMin = 0
        chart.valueAxis.valueMax = max([p['row'] for p in sampled]) + 50
        chart.categoryAxis.labels.angle = 45
        chart.categoryAxis.labels.fontSize = 6
        
        drawing.add(chart)
        
        self.story.append(drawing)
        self.story.append(Spacer(1, 0.3 * inch))
    
    def add_confidence_chart(self, confidence_data):
        """Add bar chart showing confidence distribution"""
        drawing = Drawing(500, 250)
        chart = VerticalBarChart()
        chart.x = 50
        chart.y = 50
        chart.width = 400
        chart.height = 150
        
        chart.data = [confidence_data]
        chart.categoryAxis.categoryNames = [
            '0-10%', '10-20%', '20-30%', '30-40%', '40-50%',
            '50-60%', '60-70%', '70-80%', '80-90%', '90-100%'
        ]
        
        # Color gradient from light to dark purple
        colors_list = [
            colors.HexColor('#e9d5ff'),
            colors.HexColor('#d8b4fe'),
            colors.HexColor('#c084fc'),
            colors.HexColor('#a855f7'),
            colors.HexColor('#9333ea'),
            colors.HexColor('#7e22ce'),
            colors.HexColor('#6b21a8'),
            colors.HexColor('#581c87'),
            colors.HexColor('#4c1d95'),
            colors.HexColor('#3b0764'),
        ]
        
        for i in range(len(confidence_data)):
            chart.bars[0].fillColor = colors_list[i]
        
        chart.valueAxis.valueMin = 0
        chart.categoryAxis.labels.angle = 45
        chart.categoryAxis.labels.fontSize = 8
        
        drawing.add(chart)
        
        self.story.append(drawing)
        self.story.append(Spacer(1, 0.3 * inch))
    
    def add_keywords_bar_chart(self, keywords_data, sentiment_type):
        """Add horizontal bar chart for keywords"""
        drawing = Drawing(500, 200)
        chart = VerticalBarChart()
        chart.x = 50
        chart.y = 30
        chart.width = 400
        chart.height = 140
        
        # Take top 10 keywords
        top_keywords = keywords_data[:10]
        
        chart.data = [[kw['count'] for kw in top_keywords]]
        chart.categoryAxis.categoryNames = [kw['word'] for kw in top_keywords]
        
        # Color based on sentiment
        if sentiment_type == 'positive':
            chart.bars[0].fillColor = colors.HexColor('#10b981')
        elif sentiment_type == 'negative':
            chart.bars[0].fillColor = colors.HexColor('#ef4444')
        else:
            chart.bars[0].fillColor = colors.HexColor('#f59e0b')
        
        chart.valueAxis.valueMin = 0
        chart.categoryAxis.labels.angle = 45
        chart.categoryAxis.labels.fontSize = 8
        chart.valueAxis.labels.fontSize = 8
        
        drawing.add(chart)
        
        self.story.append(drawing)
        self.story.append(Spacer(1, 0.2 * inch))
    def add_summary_section(self, title, summary_text, icon="📋"):
        """Add formatted summary section"""
        self.story.append(Paragraph(f"{icon} {title}", self.heading_style))
        
        # Parse and format the summary
        lines = summary_text.split('\n')
        current_section = []
        
        for line in lines:
            line = line.strip()
            if not line:
                if current_section:
                    self.story.append(Paragraph(' '.join(current_section), self.body_style))
                    current_section = []
                continue
            
            # Check if line is a section header
            if any(keyword in line for keyword in ['Overview', 'OVERVIEW', 'Themes', 'THEMES', 'Insights', 'INSIGHTS', 'Recommendations', 'RECOMMENDATIONS', 'Dataset Overview', 'Positive Insights', 'Areas of Concern', 'Neutral Zone', 'Strategic']):
                if current_section:
                    self.story.append(Paragraph(' '.join(current_section), self.body_style))
                    current_section = []
                self.story.append(Paragraph(line, self.subheading_style))
            else:
                current_section.append(line)
        
        if current_section:
            self.story.append(Paragraph(' '.join(current_section), self.body_style))
        
        self.story.append(Spacer(1, 0.3 * inch))
    
    def add_keywords_section(self, keywords_dict):
        """Add top keywords section"""
        self.story.append(Paragraph("🔑 Key Themes & Keywords", self.heading_style))
        
        for sentiment, keywords in keywords_dict.items():
            if keywords:
                sentiment_style = ParagraphStyle(
                    f'{sentiment}Style',
                    parent=self.body_style,
                    fontSize=12,
                    textColor=colors.HexColor('#667eea'),
                    fontName='Helvetica-Bold'
                )
                
                icon = "😊" if sentiment == "positive" else "😞" if sentiment == "negative" else "😐"
                self.story.append(Paragraph(f"{icon} {sentiment.capitalize()} Reviews:", sentiment_style))
                
                keyword_list = ", ".join([f"{kw['word']} ({kw['count']})" for kw in keywords[:10]])
                self.story.append(Paragraph(keyword_list, self.body_style))
                self.story.append(Spacer(1, 0.15 * inch))
        
        self.story.append(Spacer(1, 0.2 * inch))
    
    def add_recommendations(self, recommendations):
        """Add actionable recommendations"""
        self.story.append(Paragraph("🎯 Actionable Recommendations", self.heading_style))
        
        for i, recommendation in enumerate(recommendations, 1):
            bullet_style = ParagraphStyle(
                'BulletStyle',
                parent=self.body_style,
                leftIndent=20,
                bulletIndent=10,
                spaceAfter=8
            )
            self.story.append(Paragraph(f"{i}. {recommendation}", bullet_style))
        
        self.story.append(Spacer(1, 0.3 * inch))
    
    def add_footer_note(self):
        """Add footer note"""
        footer_text = f"""
        <para alignment="center">
        Generated by Sentiment Analysis Pro | {datetime.now().strftime('%B %d, %Y at %I:%M %p')}<br/>
        Powered by DistilBERT AI | GPU Accelerated Processing
        </para>
        """
        self.story.append(Spacer(1, 0.5 * inch))
        self.story.append(Paragraph(footer_text, self.footer_style))
    
    def generate(self):
        """Build the PDF document"""
        self.doc.build(self.story)
        print(f"✓ PDF report generated: {self.output_path}")


def generate_executive_summary(status, output_path):
    """Generate 1-page executive summary"""
    
    pdf = EnhancedPDFReportGenerator(output_path)
    
    # Header
    pdf.add_header(
        "Sentiment Analysis Executive Summary",
        f"Analysis Date: {datetime.now().strftime('%B %d, %Y')}"
    )
    
    # Metadata
    total = status['total']
    positive = status['positive_count']
    negative = status['negative_count']
    neutral = status['neutral_count']
    
    metadata = {
        "Total Reviews Analyzed": f"{total:,}",
        "Processing Speed": f"{status.get('processing_speed', 0):.1f} reviews/second",
        "Analysis Duration": "Completed successfully"
    }
    
    pdf.add_metadata_table(metadata)
    
    # Statistics
    pos_pct = (positive / total * 100) if total > 0 else 0
    neg_pct = (negative / total * 100) if total > 0 else 0
    neu_pct = (neutral / total * 100) if total > 0 else 0
    
    stats = [
        ('Positive', positive, pos_pct),
        ('Negative', negative, neg_pct),
        ('Neutral', neutral, neu_pct),
    ]
    
    pdf.add_statistics_table(stats)
    
    # Pie chart
    chart_data = [
        ('Positive', positive),
        ('Negative', negative),
        ('Neutral', neutral)
    ]
    pdf.add_pie_chart(chart_data, "Visual Distribution")
    
    # Key insights
    key_insights = []
    
    if pos_pct > 60:
        key_insights.append("Strong positive sentiment indicates high customer satisfaction")
    elif pos_pct > 40:
        key_insights.append("Mixed sentiment with positive lean suggests room for improvement")
    
    if neg_pct > 30:
        key_insights.append("Significant negative feedback requires immediate attention")
    
    if neu_pct > 20:
        key_insights.append("Large neutral segment presents conversion opportunity")
    
    pdf.add_recommendations(key_insights)
    
    # Footer
    pdf.add_footer_note()
    
    # Generate
    pdf.generate()


def generate_ai_sentiment_summary(comments, sentiment, api_key, api_url):
    """Generate AI summary for specific sentiment using the same logic as frontend"""
    
    print(f"\n{'='*70}")
    print(f"🤖 Generating {sentiment.upper()} summary for PDF...")
    print(f"Total {sentiment} comments: {len(comments)}")
    
    # Filter comments by sentiment
    filtered_comments = [c for c in comments if c.get('sentiment') == sentiment]
    
    if len(filtered_comments) == 0:
        return f"No {sentiment} reviews found in the dataset."
    
    # Process in 3 rounds (same as frontend)
    COMMENTS_PER_ROUND = max(1, len(filtered_comments) // 3)
    MAX_COMMENT_LENGTH = 100
    
    round_summaries = []
    
    try:
        # Process 3 rounds
        for round_num in range(3):
            round_start = round_num * COMMENTS_PER_ROUND
            round_end = min(round_start + COMMENTS_PER_ROUND, len(filtered_comments))
            round_comments = filtered_comments[round_start:round_end]
            
            if not round_comments:
                break
            
            print(f"  Round {round_num + 1}/3: Processing {len(round_comments)} comments...")
            
            # Take first 100 chars from each comment (max 15 comments)
            round_texts = []
            for c in round_comments[:15]:
                text = c.get('comment', '').strip()
                if len(text) > MAX_COMMENT_LENGTH:
                    text = text[:MAX_COMMENT_LENGTH] + '...'
                round_texts.append(text)
            
            round_text = '\n---\n'.join(round_texts)
            
            # Generate round summary
            round_prompt = f"""You are analyzing {len(round_comments)} customer {sentiment} reviews. Sample excerpts:

{round_text}

Write exactly 2 sentences (max 50 words) summarizing the main theme.

Focus: {sentiment == 'positive' and 'what customers love' or 'main complaints'}

Summary:"""
            
            round_summary = call_summary_api(round_prompt, 100, api_key, api_url)
            if round_summary:
                round_summaries.append(round_summary.strip())
        
        if not round_summaries:
            return f"Unable to generate summary for {sentiment} reviews."
        
        # Generate final comprehensive summary
        print(f"  Generating final comprehensive summary...")
        
        all_summaries = '\n\n'.join([f"Section {i + 1}: {s}" for i, s in enumerate(round_summaries)])
        
        final_prompt = f"""Create an executive summary of {len(filtered_comments)} {sentiment.upper()} customer reviews.

Section insights:
{all_summaries}

Write a structured report (350-450 words) with EXACTLY these 4 sections:

OVERVIEW (80 words)
Start with: "Analysis of {len(filtered_comments)} {sentiment} reviews reveals..."
{sentiment == 'positive' and 'Describe satisfaction levels and what customers appreciate' or 'Describe dissatisfaction patterns and main complaints'}

KEY THEMES (150 words)
Start with: "Three dominant patterns emerge from the feedback..."
List 3-4 specific themes from the section insights above
{sentiment == 'positive' and 'What customers consistently praise with examples' or 'What customers consistently complain about with examples'}

CRITICAL INSIGHTS (70 words)
Start with: "The most important takeaway is..."
{sentiment == 'positive' and 'Competitive advantages and unique strengths' or 'Critical issues requiring immediate action'}

RECOMMENDATIONS (50 words)
Start with: "Based on this analysis..."
{sentiment == 'positive' and '2-3 ways to leverage these strengths' or '2-3 actionable steps to address concerns'}

FORMATTING RULES:
- Clearly separate each section
- Use professional business language
- Write in clear paragraphs (NO bullet points)
- Total: 350-450 words

Write the executive summary:"""
        
        final_summary = call_summary_api(final_prompt, 700, api_key, api_url)
        
        print(f"✓ {sentiment.capitalize()} summary generated successfully")
        print(f"{'='*70}\n")
        
        return final_summary.strip() if final_summary else f"Summary generation completed with {len(round_summaries)} sections."
        
    except Exception as e:
        print(f"✗ Error generating {sentiment} summary: {e}")
        return f"Error generating {sentiment} summary: {str(e)}"


def call_summary_api(prompt, max_tokens, api_key, api_url):
    """Call the summary API"""
    try:
        headers = {
            "X-API-Key": api_key,
            "Content-Type": "application/json"
        }
        
        payload = {
            "prompt": prompt,
            "max_tokens": max_tokens,
            "temperature": 0.3
        }
        
        response = requests.post(api_url, headers=headers, json=payload, timeout=120)
        
        if response.status_code == 200:
            result = response.json()
            summary_text = (
                result.get('response') or 
                result.get('text') or 
                result.get('output') or 
                result.get('content') or
                ''
            )
            return summary_text
        else:
            print(f"  API error: Status {response.status_code}")
            return None
            
    except Exception as e:
        print(f"  API call error: {e}")
        return None


def generate_detailed_report_with_ai(status, output_path, api_key, api_url):
    """Generate detailed multi-page report with AI summaries and ALL charts"""
    
    print(f"\n{'='*70}")
    print(f"📄 GENERATING DETAILED PDF REPORT WITH AI SUMMARIES")
    print(f"{'='*70}")
    
    pdf = EnhancedPDFReportGenerator(output_path)
    
    # ========================================
    # PAGE 1: COVER PAGE WITH METADATA
    # ========================================
    
    pdf.add_header(
        "Comprehensive Sentiment Analysis Report",
        f"Detailed Analysis with AI Insights | {datetime.now().strftime('%B %d, %Y')}"
    )
    
    # Metadata Table
    total = status['total']
    positive = status['positive_count']
    negative = status['negative_count']
    neutral = status['neutral_count']
    
    metadata = {
        "Total Reviews": f"{total:,}",
        "Positive Reviews": f"{positive:,} ({(positive/total*100):.1f}%)",
        "Negative Reviews": f"{negative:,} ({(negative/total*100):.1f}%)",
        "Neutral Reviews": f"{neutral:,} ({(neutral/total*100):.1f}%)",
        "Processing Speed": f"{status.get('processing_speed', 0):.1f} reviews/sec",
        "Analysis Date": datetime.now().strftime('%B %d, %Y at %I:%M %p')
    }
    
    pdf.add_metadata_table(metadata)
    
    # Statistics Table
    pos_pct = (positive / total * 100) if total > 0 else 0
    neg_pct = (negative / total * 100) if total > 0 else 0
    neu_pct = (neutral / total * 100) if total > 0 else 0
    
    stats = [
        ('Positive', positive, pos_pct),
        ('Negative', negative, neg_pct),
        ('Neutral', neutral, neu_pct),
    ]
    
    pdf.add_statistics_table(stats)
    
    # ========================================
    # PAGE 2: SENTIMENT DISTRIBUTION WITH PIE CHART
    # ========================================
    
    pdf.add_page_break()
    
    pdf.story.append(Paragraph("Sentiment Distribution", pdf.heading_style))
    pdf.story.append(Spacer(1, 0.2 * inch))
    
    # Add Pie Chart
    chart_data = [
        ('Positive', positive),
        ('Negative', negative),
        ('Neutral', neutral)
    ]
    pdf.add_pie_chart(chart_data, "Sentiment Distribution Visualization")
    
    # ========================================
    # PAGE 3: SENTIMENT FLOW TIMELINE CHART
    # ========================================
    
    pdf.add_page_break()
    
    pdf.story.append(Paragraph("Sentiment Flow Timeline", pdf.heading_style))
    pdf.story.append(Spacer(1, 0.2 * inch))
    
    # Add Timeline Chart
    timeline_data = status.get('sentiment_timeline', [])
    if timeline_data:
        pdf.add_timeline_chart(timeline_data)
    
    # ========================================
    # PAGE 4: CONFIDENCE DISTRIBUTION CHART
    # ========================================
    
    pdf.add_page_break()
    
    pdf.story.append(Paragraph("Prediction Confidence Heatmap", pdf.heading_style))
    pdf.story.append(Spacer(1, 0.2 * inch))
    
    # Add Confidence Chart
    confidence_data = status.get('confidence_distribution', [])
    if confidence_data:
        pdf.add_confidence_chart(confidence_data)
    
    # ========================================
    # PAGE 5: TOP KEYWORDS CHARTS (All 3 sentiments)
    # ========================================
    
    pdf.add_page_break()
    
    pdf.story.append(Paragraph("Top Keywords Analysis", pdf.heading_style))
    pdf.story.append(Spacer(1, 0.3 * inch))
    
    keywords = status.get('top_keywords', {})
    
    # Positive Keywords Chart
    if keywords.get('positive'):
        pdf.story.append(Paragraph("😊 Positive Keywords", pdf.subheading_style))
        pdf.add_keywords_bar_chart(keywords['positive'], 'positive')
        pdf.story.append(Spacer(1, 0.3 * inch))
    
    # Negative Keywords Chart
    if keywords.get('negative'):
        pdf.story.append(Paragraph("😞 Negative Keywords", pdf.subheading_style))
        pdf.add_keywords_bar_chart(keywords['negative'], 'negative')
        pdf.story.append(Spacer(1, 0.3 * inch))
    
    # Neutral Keywords Chart (if exists)
    if keywords.get('neutral'):
        pdf.story.append(Paragraph("😐 Neutral Keywords", pdf.subheading_style))
        pdf.add_keywords_bar_chart(keywords['neutral'], 'neutral')
    
    # ========================================
    # PAGE 6+: COMPREHENSIVE ANALYSIS REPORT
    # ========================================
    
    pdf.add_page_break()
    
    comprehensive_summary = status.get('detailed_summary', 'No comprehensive summary available')
    pdf.add_summary_section(
        "Comprehensive Analysis Report",
        comprehensive_summary,
        "📊"
    )
    
    # ========================================
    # POSITIVE REVIEWS AI ANALYSIS
    # ========================================
    
    pdf.add_page_break()
    
    print("Generating POSITIVE reviews AI summary...")
    all_comments = status.get('all_comments', [])
    
    positive_summary = generate_ai_sentiment_summary(
        all_comments, 
        'positive', 
        api_key, 
        api_url
    )
    
    pdf.add_summary_section(
        "Positive Reviews - AI Analysis",
        positive_summary,
        "😊"
    )
    
    # ========================================
    # NEGATIVE REVIEWS AI ANALYSIS
    # ========================================
    
    pdf.add_page_break()
    
    print("Generating NEGATIVE reviews AI summary...")
    
    negative_summary = generate_ai_sentiment_summary(
        all_comments, 
        'negative', 
        api_key, 
        api_url
    )
    
    pdf.add_summary_section(
        "Negative Reviews - AI Analysis",
        negative_summary,
        "😞"
    )
    
    # ========================================
    # RECOMMENDATIONS PAGE
    # ========================================
    
    pdf.add_page_break()
    
    pdf.story.append(Paragraph("📋 Strategic Recommendations", pdf.heading_style))
    pdf.story.append(Spacer(1, 0.3 * inch))
    
    # Generate comprehensive recommendations
    recommendations = generate_comprehensive_recommendations(status, pos_pct, neg_pct, neu_pct)
    
    pdf.add_recommendations(recommendations)
    
    # ========================================
    # FINAL PAGE: KEYWORDS SUMMARY & ACTIONS
    # ========================================
    
    pdf.add_page_break()
    
    # Keywords Summary (text format)
    pdf.add_keywords_section(keywords)
    
    pdf.story.append(Spacer(1, 0.5 * inch))
    
    # Quick action items
    quick_actions = [
        "Monitor sentiment trends weekly to identify emerging issues early",
        "Create feedback loops to ensure customer concerns are promptly addressed",
        "Leverage positive sentiment in marketing materials and customer testimonials",
        "Develop targeted improvement plans for critical negative feedback areas"
    ]
    
    pdf.add_recommendations(quick_actions)
    
    # Footer with timestamp and branding
    pdf.add_footer_note()
    
    # Generate
    print(f"\n{'='*70}")
    print("📝 Building final PDF document...")
    pdf.generate()
    print(f"✅ DETAILED REPORT COMPLETED")
    print(f"{'='*70}\n")

def generate_comprehensive_recommendations(status, pos_pct, neg_pct, neu_pct):
    """Generate 10-15 detailed recommendations based on sentiment analysis"""
    
    recommendations = []
    total = status['total']
    
    # Positive sentiment recommendations
    if pos_pct > 60:
        recommendations.extend([
            "Leverage the strong positive sentiment ({}%) by featuring customer testimonials prominently on your website and marketing materials".format(int(pos_pct)),
            "Create case studies from satisfied customers to demonstrate proven value to potential clients",
            "Implement a customer referral program to capitalize on high satisfaction levels",
            "Develop a customer loyalty rewards program to maintain and strengthen positive relationships"
        ])
    elif pos_pct > 40:
        recommendations.extend([
            "Build on the moderate positive sentiment ({}%) by identifying and replicating success factors across all customer touchpoints".format(int(pos_pct)),
            "Conduct in-depth interviews with satisfied customers to understand what drives their positive experience"
        ])
    
    # Negative sentiment recommendations
    if neg_pct > 40:
        recommendations.extend([
            "URGENT: Address the high negative sentiment ({}%) by establishing a rapid response team for critical customer issues".format(int(neg_pct)),
            "Implement immediate quality control measures to prevent recurring problems mentioned in negative reviews",
            "Create a comprehensive customer recovery program with clear escalation procedures",
            "Schedule weekly leadership reviews of negative feedback to ensure accountability",
            "Develop targeted training programs for staff based on specific complaints identified"
        ])
    elif neg_pct > 20:
        recommendations.extend([
            "Analyze negative feedback patterns ({}%) to identify root causes and implement preventive measures".format(int(neg_pct)),
            "Establish a customer feedback response protocol with guaranteed response times",
            "Create a dedicated team to proactively reach out to dissatisfied customers"
        ])
    
    # Neutral sentiment recommendations
    if neu_pct > 15:
        recommendations.extend([
            "Convert neutral customers ({}%) into promoters by implementing personalized follow-up campaigns".format(int(neu_pct)),
            "Conduct surveys with neutral respondents to understand what would improve their experience",
            "Create targeted engagement programs to move neutral customers toward positive sentiment"
        ])
    
    # General operational recommendations
    recommendations.extend([
        "Establish a centralized customer feedback dashboard for real-time sentiment monitoring",
        "Implement AI-powered sentiment analysis on all customer communications for early issue detection",
        "Create monthly sentiment trend reports for executive leadership and board presentations",
        "Develop department-specific action plans based on feedback themes relevant to each team"
    ])
    
    # Data-driven recommendations
    if total > 1000:
        recommendations.append(
            "With {} reviews analyzed, establish this as a baseline for quarterly sentiment tracking".format(total)
        )
    
    return recommendations[:15]  # Return maximum 15 recommendations

def generate_comprehensive_recommendations(status, pos_pct, neg_pct, neu_pct):
    """Generate 10-15 detailed recommendations based on sentiment analysis"""
    
    recommendations = []
    total = status['total']
    
    # Positive sentiment recommendations
    if pos_pct > 60:
        recommendations.extend([
            "Leverage the strong positive sentiment ({}%) by featuring customer testimonials prominently on your website and marketing materials".format(int(pos_pct)),
            "Create case studies from satisfied customers to demonstrate proven value to potential clients",
            "Implement a customer referral program to capitalize on high satisfaction levels",
            "Develop a customer loyalty rewards program to maintain and strengthen positive relationships"
        ])
    elif pos_pct > 40:
        recommendations.extend([
            "Build on the moderate positive sentiment ({}%) by identifying and replicating success factors across all customer touchpoints".format(int(pos_pct)),
            "Conduct in-depth interviews with satisfied customers to understand what drives their positive experience"
        ])
    else:
        recommendations.extend([
            "Address the low positive sentiment ({}%) by identifying and promoting your unique value propositions more effectively".format(int(pos_pct)),
            "Implement a comprehensive customer satisfaction improvement program"
        ])
    
    # Negative sentiment recommendations
    if neg_pct > 40:
        recommendations.extend([
            "URGENT: Address the high negative sentiment ({}%) by establishing a rapid response team for critical customer issues".format(int(neg_pct)),
            "Implement immediate quality control measures to prevent recurring problems mentioned in negative reviews",
            "Create a comprehensive customer recovery program with clear escalation procedures",
            "Schedule weekly leadership reviews of negative feedback to ensure accountability",
            "Develop targeted training programs for staff based on specific complaints identified"
        ])
    elif neg_pct > 20:
        recommendations.extend([
            "Analyze negative feedback patterns ({}%) to identify root causes and implement preventive measures".format(int(neg_pct)),
            "Establish a customer feedback response protocol with guaranteed response times",
            "Create a dedicated team to proactively reach out to dissatisfied customers"
        ])
    else:
        recommendations.append(
            "Maintain low negative sentiment ({}%) through continued focus on quality and customer service excellence".format(int(neg_pct))
        )
    
    # Neutral sentiment recommendations
    if neu_pct > 15:
        recommendations.extend([
            "Convert neutral customers ({}%) into promoters by implementing personalized follow-up campaigns".format(int(neu_pct)),
            "Conduct surveys with neutral respondents to understand what would improve their experience",
            "Create targeted engagement programs to move neutral customers toward positive sentiment"
        ])
    
    # General operational recommendations
    recommendations.extend([
        "Establish a centralized customer feedback dashboard for real-time sentiment monitoring",
        "Implement AI-powered sentiment analysis on all customer communications for early issue detection",
        "Create monthly sentiment trend reports for executive leadership and board presentations",
        "Develop department-specific action plans based on feedback themes relevant to each team",
        "Set up automated alerts for sudden changes in sentiment patterns to enable rapid response"
    ])
    
    # Data-driven recommendations
    if total > 1000:
        recommendations.append(
            "With {} reviews analyzed, establish this as a baseline for quarterly sentiment tracking and competitive benchmarking".format(total)
        )
    
    return recommendations[:15]  # Return maximum 15 recommendations
