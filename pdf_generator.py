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
    """Generate detailed multi-page report with AI summaries for all sentiments"""
    
    print(f"\n{'='*70}")
    print(f"📄 GENERATING DETAILED PDF REPORT WITH AI SUMMARIES")
    print(f"{'='*70}")
    
    pdf = EnhancedPDFReportGenerator(output_path)
    
    # ========================================
    # PAGE 1: HEADER & OVERVIEW
    # ========================================
    
    pdf.add_header(
        "Comprehensive Sentiment Analysis Report",
        f"Detailed Analysis with AI Insights | {datetime.now().strftime('%B %d, %Y')}"
    )
    
    # Metadata
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
    
    # Statistics with chart
    pos_pct = (positive / total * 100) if total > 0 else 0
    neg_pct = (negative / total * 100) if total > 0 else 0
    neu_pct = (neutral / total * 100) if total > 0 else 0
    
    stats = [
        ('Positive', positive, pos_pct),
        ('Negative', negative, neg_pct),
        ('Neutral', neutral, neu_pct),
    ]
    
    pdf.add_statistics_table(stats)
    
    chart_data = [
        ('Positive', positive),
        ('Negative', negative),
        ('Neutral', neutral)
    ]
    pdf.add_pie_chart(chart_data, "Sentiment Distribution Visualization")
    
    # ========================================
    # SECTION 1: COMPREHENSIVE ANALYSIS
    # ========================================
    
    pdf.add_page_break()
    
    comprehensive_summary = status.get('detailed_summary', 'No comprehensive summary available')
    pdf.add_summary_section(
        "Comprehensive Analysis Report",
        comprehensive_summary,
        "📊"
    )
    
    # ========================================
    # SECTION 2: POSITIVE REVIEWS AI ANALYSIS
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
    # SECTION 3: NEGATIVE REVIEWS AI ANALYSIS
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
    # SECTION 4: KEYWORDS & RECOMMENDATIONS
    # ========================================
    
    pdf.add_page_break()
    
    # Keywords
    keywords = status.get('top_keywords', {})
    if keywords:
        pdf.add_keywords_section(keywords)
    
    # Recommendations
    recommendations = []
    
    if pos_pct > 60:
        recommendations.append("Leverage positive sentiment in marketing materials and testimonials")
        recommendations.append("Identify and replicate factors driving customer satisfaction")
    
    if neg_pct > 30:
        recommendations.append("Implement immediate action plan to address critical negative feedback")
        recommendations.append("Establish customer service recovery protocols for dissatisfied customers")
    
    if neg_pct < 20 and pos_pct > 60:
        recommendations.append("Focus on converting neutral customers to promoters")
        recommendations.append("Develop customer loyalty programs to maintain positive momentum")
    
    recommendations.append("Monitor sentiment trends weekly to catch issues early")
    recommendations.append("Create feedback loop to ensure customer concerns are addressed")
    
    pdf.add_recommendations(recommendations)
    
    # Footer
    pdf.add_footer_note()
    
    # Generate
    print(f"\n{'='*70}")
    print("📝 Building final PDF document...")
    pdf.generate()
    print(f"✓ DETAILED REPORT COMPLETED")
    print(f"{'='*70}\n")