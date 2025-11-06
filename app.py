"""
Segment Analysis System - OPTIMIZED FAST STARTUP Edition
Enhanced with Real-time Updates and Comment Details
OPTIMIZED: Removed auto-tuning for instant startup
"""

from flask import Flask, render_template, request, jsonify, send_file
from pdf_generator import generate_executive_summary, generate_detailed_report_with_ai
import os
import sys
import json

print("\n" + "="*70)
print("🚀 SEGMENT ANALYSIS SYSTEM - OPTIMIZED EDITION")
print("="*70)
print(f"Python: {sys.version.split()[0]}")
print(f"Working Directory: {os.getcwd()}")

# Import with error handling
try:
    import torch
    print(f"PyTorch: {torch.__version__}")
    
    # GPU Configuration
    if torch.cuda.is_available():
        DEVICE = torch.device('cuda:0')
        torch.cuda.set_device(0)
        
        # Enable all optimizations
        torch.backends.cuda.matmul.allow_tf32 = True
        torch.backends.cudnn.allow_tf32 = True
        torch.backends.cudnn.benchmark = True
        torch.backends.cudnn.deterministic = False
        
        # Aggressive memory settings
        torch.cuda.empty_cache()
        os.environ['PYTORCH_CUDA_ALLOC_CONF'] = 'max_split_size_mb:256,expandable_segments:True'
        
        gpu_name = torch.cuda.get_device_name(0)
        gpu_memory = torch.cuda.get_device_properties(0).total_memory / 1024**3
        
        print(f"✓ GPU: {gpu_name}")
        print(f"✓ GPU Memory: {gpu_memory:.2f} GB")
        print("✓ GPU acceleration enabled")
    else:
        DEVICE = torch.device('cpu')
        print("⚠ WARNING: GPU not available, using CPU")
except ImportError as e:
    print(f"✗ ERROR: PyTorch not installed: {e}")
    sys.exit(1)

try:
    from transformers import AutoTokenizer, AutoModelForSequenceClassification
    import numpy as np
except ImportError as e:
    print(f"✗ ERROR: {e}")
    sys.exit(1)

try:
    from openpyxl import load_workbook, Workbook
    from openpyxl.styles import PatternFill, Font, Alignment
except ImportError as e:
    print(f"✗ ERROR: OpenPyXL not installed: {e}")
    sys.exit(1)

import threading
import time
from datetime import datetime
import traceback
from collections import Counter
from concurrent.futures import ThreadPoolExecutor, as_completed
import queue
from dotenv import load_dotenv
import requests

# Load environment variables
load_dotenv()

# Flask app
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['OUTPUT_FOLDER'] = 'outputs'
app.config['MAX_CONTENT_LENGTH'] = 200 * 1024 * 1024  # 200MB

for folder in [app.config['UPLOAD_FOLDER'], app.config['OUTPUT_FOLDER'], 'templates', 'static/css', 'static/js']:
    os.makedirs(folder, exist_ok=True)

# Global status with comment storage
processing_status = {
    'is_processing': False,
    'progress': 0,
    'total': 0,
    'current_file': '',
    'positive_count': 0,
    'negative_count': 0,
    'neutral_count': 0,
    'summary': '',
    'detailed_summary': '',
    'error': None,
    'sentiment_timeline': [],
    'confidence_distribution': [],
    'top_keywords': {'positive': [], 'negative': [], 'neutral': []},
    'processing_speed': 0,
    'eta_seconds': 0,
    'all_comments': []
}

# OPTIMIZED CONFIGURATION - NO AUTO-TUNING ON STARTUP
MODEL_PATH = r"D:\Segement_analysis_project\models\distilbert-sst2"
MAX_LENGTH = 128
NEUTRAL_THRESHOLD = 0.65

# Pre-configured optimal batch size (adjust based on your GPU)
# RTX 3050 4GB: 96-128
# RTX 3060 12GB: 256-384
# RTX 3070 8GB: 192-256
# RTX 3080 10GB: 256-384
OPTIMAL_BATCH_SIZE = 128  # Optimized for RTX 3050 4GB

print(f"\n{'='*70}")
print(f"Loading model from: {MODEL_PATH}")
print(f"Using pre-configured batch size: {OPTIMAL_BATCH_SIZE}")

if not os.path.exists(MODEL_PATH):
    print(f"✗ ERROR: Model not found at {MODEL_PATH}")
    sys.exit(1)

try:
    tokenizer = AutoTokenizer.from_pretrained(MODEL_PATH)
    model = AutoModelForSequenceClassification.from_pretrained(MODEL_PATH)
    
    if torch.cuda.is_available():
        try:
            model = model.half()
            print("✓ Using FP16 (half precision) for 2x speed boost")
        except:
            print("ℹ FP16 not available, using FP32")
    
    model = model.to(DEVICE)
    model.eval()
    torch.set_grad_enabled(False)
    
    print("✓ Model loaded successfully")
    
    # Quick GPU warm-up (reduced from 10 to 3 iterations)
    if torch.cuda.is_available():
        print("⚡ Quick GPU warm-up...")
        warmup_texts = ["test sample review text"] * OPTIMAL_BATCH_SIZE
        
        for i in range(3):
            warmup_input = tokenizer(warmup_texts, return_tensors='pt', padding=True, truncation=True, max_length=MAX_LENGTH)
            warmup_input = {k: v.to(DEVICE) for k, v in warmup_input.items()}
            with torch.inference_mode():
                _ = model(**warmup_input)
        
        torch.cuda.synchronize()
        torch.cuda.empty_cache()
        print("✓ GPU ready")
    
    print(f"✓ Batch size: {OPTIMAL_BATCH_SIZE}")
    print(f"✓ Max sequence length: {MAX_LENGTH}")
    print("="*70 + "\n")
    
except Exception as e:
    print(f"✗ ERROR loading model: {e}")
    traceback.print_exc()
    sys.exit(1)


def predict_sentiment_batch_ultra_fast(texts):
    """
    Ultra-optimized batch prediction with ADVANCED NEUTRAL DETECTION
    Handles: 1) Weak sentiments, 2) Mixed sentiments, 3) Balanced reviews
    NO API CALLS - Pure pattern analysis for speed
    """
    try:
        # FAST PRE-ANALYSIS: Detect neutral patterns before model inference
        neutral_signals = []
        
        for text in texts:
            text_lower = text.lower()
            signal = {
                'weak_score': 0,
                'mixed_score': 0,
                'balanced': False
            }
            
            # ====== PATTERN 1: WEAK/BLAND SENTIMENT ======
            weak_words = ['okay', 'fine', 'average', 'normal', 'usual', 'standard', 'typical',
                         'regular', 'basic', 'acceptable', 'adequate', 'reasonable', 'moderate',
                         'neither', 'nothing', 'same', 'similar', 'plain', 'routine', 'common',
                         'ordinary', 'middling', 'fair', 'decent', 'alright', 'passable']
            
            weak_phrases = ['not bad', 'not great', 'not much', 'nothing special',
                           'nothing new', 'as expected', 'no change', 'no difference',
                           'works fine', 'it works', 'does the job', 'good enough',
                           'could be worse', 'could be better', 'no surprises']
            
            signal['weak_score'] += sum(2 for word in weak_words if f' {word} ' in f' {text_lower} ')
            signal['weak_score'] += sum(3 for phrase in weak_phrases if phrase in text_lower)
            
            # ====== PATTERN 2: MIXED SENTIMENT (positive + negative) ======
            # Contrast connectors indicating mixed feelings
            contrast_words = [' but ', ' however ', ' although ', ' though ', ' yet ',
                            ' except ', ' despite ', ' still ', ' on the other hand',
                            ' at the same time', ' while ']
            
            has_contrast = any(connector in text_lower for connector in contrast_words)
            
            if has_contrast:
                # Check if both positive and negative words exist
                positive_words = ['good', 'great', 'nice', 'excellent', 'amazing', 'love',
                                'best', 'perfect', 'wonderful', 'fantastic', 'awesome',
                                'helpful', 'easy', 'fast', 'smooth', 'pleased', 'happy',
                                'impressed', 'satisfied', 'recommend', 'enjoy']
                
                negative_words = ['bad', 'poor', 'terrible', 'awful', 'horrible', 'worst',
                                'hate', 'disappoint', 'slow', 'difficult', 'hard', 'issue',
                                'problem', 'error', 'fail', 'broken', 'useless', 'annoying',
                                'frustrat', 'confus', 'complicated', 'not good', 'not great',
                                'not working', 'not work', 'didnt work', "didn't work"]
                
                pos_count = sum(1 for word in positive_words if word in text_lower)
                neg_count = sum(1 for word in negative_words if word in text_lower)
                
                # Mixed if both sentiments present
                if pos_count >= 1 and neg_count >= 1:
                    signal['mixed_score'] = 10  # Strong indicator
                    signal['balanced'] = True
            
            # ====== PATTERN 3: BALANCED STATEMENTS ======
            balance_phrases = ['some good some bad', 'pros and cons', 'mixed feelings',
                             'hit or miss', 'half and half', 'fifty fifty', '50/50',
                             'depends', 'sometimes', 'partially', 'somewhat']
            
            if any(phrase in text_lower for phrase in balance_phrases):
                signal['balanced'] = True
                signal['mixed_score'] += 8
            
            # ====== PATTERN 4: LACK OF STRONG SENTIMENT ======
            strong_positive = ['excellent', 'amazing', 'fantastic', 'wonderful', 'perfect',
                             'love', 'best', 'awesome', 'outstanding', 'brilliant', 'incredible']
            strong_negative = ['terrible', 'awful', 'horrible', 'worst', 'hate', 'useless',
                             'broken', 'disaster', 'nightmare', 'garbage', 'pathetic']
            
            has_strong = any(word in text_lower for word in strong_positive + strong_negative)
            if not has_strong and len(text.split()) > 5:  # Longer text without strong words
                signal['weak_score'] += 1
            
            neutral_signals.append(signal)
        
        # ====== MODEL INFERENCE ======
        inputs = tokenizer(
            texts,
            padding=True,
            truncation=True,
            max_length=MAX_LENGTH,
            return_tensors='pt'
        )
        
        inputs = {k: v.to(DEVICE, non_blocking=True) for k, v in inputs.items()}
        
        with torch.inference_mode():
            outputs = model(**inputs)
            probabilities = torch.nn.functional.softmax(outputs.logits, dim=-1)
            confidences, predicted_classes = torch.max(probabilities, dim=-1)
        
        confidences = confidences.cpu().numpy()
        predicted_classes = predicted_classes.cpu().numpy()
        
        # ====== INTELLIGENT DECISION LOGIC ======
        results = []
        for text, conf, pred_class, signal in zip(texts, confidences, predicted_classes, neutral_signals):
            is_neutral = False
            
            # RULE 1: MIXED SENTIMENT (highest priority - overrides model)
            if signal['balanced'] or signal['mixed_score'] >= 8:
                is_neutral = True
            
            # RULE 2: STRONG WEAK SIGNALS (weak words dominate)
            elif signal['weak_score'] >= 4:
                is_neutral = True
            
            # RULE 3: MODEL UNCERTAINTY + WEAK SIGNALS
            elif conf < 0.65 and signal['weak_score'] >= 2:
                is_neutral = True
            
            # RULE 4: MODERATE CONFIDENCE + SOME WEAK SIGNALS
            elif 0.55 <= conf <= 0.72 and signal['weak_score'] >= 1:
                is_neutral = True
            
            # RULE 5: VERY LOW CONFIDENCE (model is confused)
            elif conf < 0.58:
                is_neutral = True
            
            # RULE 6: MIXED SENTIMENT + LOW CONFIDENCE
            elif signal['mixed_score'] >= 5 and conf < 0.75:
                is_neutral = True
            
            # Determine final sentiment
            if is_neutral:
                sentiment = 'neutral'
            else:
                sentiment = 'positive' if pred_class == 1 else 'negative'
            
            results.append({
                'sentiment': sentiment,
                'confidence': float(conf),
                'label': pred_class
            })
        
        return results
        
    except Exception as e:
        print(f"Error in prediction: {e}")
        raise


# OPTIONAL: Add API-based fallback for truly ambiguous cases
def predict_with_api_fallback(text, sentiment, confidence, api_key, api_url):
    """
    Use API for secondary classification when DistilBERT is uncertain
    Only call this for borderline cases (confidence 0.50-0.70)
    """
    if not api_key or confidence > 0.70:
        return sentiment  # Trust the model for high confidence
    
    try:
        prompt = f"""Classify this review sentiment in ONE WORD (positive/negative/neutral):

"{text}"

Respond with ONLY ONE WORD: positive, negative, or neutral."""

        headers = {
            "X-API-Key": api_key,
            "Content-Type": "application/json"
        }
        
        payload = {
            "prompt": prompt,
            "max_tokens": 10,
            "temperature": 0.1
        }
        
        response = requests.post(api_url, headers=headers, json=payload, timeout=10)
        
        if response.status_code == 200:
            result = response.json()
            api_sentiment = (result.get('response') or result.get('text') or '').strip().lower()
            
            # Extract sentiment from response
            if 'positive' in api_sentiment:
                return 'positive'
            elif 'negative' in api_sentiment:
                return 'negative'
            elif 'neutral' in api_sentiment:
                return 'neutral'
        
    except Exception as e:
        print(f"API fallback failed: {e}")
    
    return sentiment  # Return original if API fails


def extract_keywords(text, sentiment):
    """Fast keyword extraction"""
    words = text.lower().split()
    stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'is', 'was', 'are', 'were', 'been', 'be', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should', 'may', 'might', 'must', 'can', 'this', 'that', 'these', 'those', 'i', 'you', 'he', 'she', 'it', 'we', 'they', 'my', 'your', 'his', 'her', 'its', 'our', 'their'}
    keywords = [w for w in words if len(w) > 3 and w not in stop_words]
    return keywords[:5]


def process_excel_advanced(input_path, output_path):
    """Maximum GPU saturation Excel processing with comment storage"""
    global processing_status
    
    try:
        start_time = time.time()
        print(f"Loading workbook: {input_path}")
        wb = load_workbook(input_path)
        ws = wb.active
        
        total_rows = ws.max_row - 1
        processing_status['total'] = total_rows
        processing_status['all_comments'] = []
        print(f"Total rows: {total_rows}")
        print(f"Using batch size: {OPTIMAL_BATCH_SIZE}")
        
        all_results = []
        sentiment_timeline = []
        all_keywords = {'positive': [], 'negative': [], 'neutral': []}
        
        wb_positive = Workbook()
        ws_positive = wb_positive.active
        ws_positive.title = "Positive Reviews"
        
        wb_negative = Workbook()
        ws_negative = wb_negative.active
        ws_negative.title = "Negative Reviews"
        
        wb_neutral = Workbook()
        ws_neutral = wb_neutral.active
        ws_neutral.title = "Neutral Reviews"
        
        headers = [ws.cell(1, col).value for col in range(1, ws.max_column + 1)]
        headers.extend(['sentiment', 'confidence'])
        
        for col_idx, header in enumerate(headers, 1):
            ws.cell(1, ws.max_column + 1 if col_idx > len(headers) - 2 else col_idx, value=header)
            ws_positive.cell(1, col_idx, value=header)
            ws_negative.cell(1, col_idx, value=header)
            ws_neutral.cell(1, col_idx, value=header)
        
        positive_count = 0
        negative_count = 0
        neutral_count = 0
        pos_row_idx = 2
        neg_row_idx = 2
        neu_row_idx = 2
        
        batch_texts = []
        batch_rows = []
        batch_data = []
        
        processed_count = 0
        
        print(f"\nStarting optimized processing...")
        print(f"Target GPU Usage: 85-95%")
        print("="*70)
        
        for row_idx in range(2, ws.max_row + 1):
            cell_value = ws.cell(row_idx, 1).value
            
            if cell_value is None or str(cell_value).strip() == '':
                review_text = "No review"
            else:
                review_text = str(cell_value).strip()
            
            batch_texts.append(review_text)
            batch_rows.append(row_idx)
            batch_data.append([ws.cell(row_idx, col).value for col in range(1, ws.max_column + 1)])
            
            if len(batch_texts) >= OPTIMAL_BATCH_SIZE or row_idx == ws.max_row:
                batch_start = time.time()
                
                results = predict_sentiment_batch_ultra_fast(batch_texts)
                
                batch_time = time.time() - batch_start
                speed = len(batch_texts) / batch_time if batch_time > 0 else 0
                processing_status['processing_speed'] = round(speed, 1)
                
                for text, result, r_idx, row_data in zip(batch_texts, results, batch_rows, batch_data):
                    sentiment = result['sentiment']
                    confidence = result['confidence']
                    
                    # Store comment details
                    processing_status['all_comments'].append({
                        'id': processed_count + 1,
                        'comment': text,
                        'sentiment': sentiment,
                        'confidence': confidence
                    })
                    
                    ws.cell(r_idx, ws.max_column - 1, value=sentiment)
                    ws.cell(r_idx, ws.max_column, value=f"{confidence:.2%}")
                    
                    fill_color = "d1fae5" if sentiment == 'positive' else "fee2e2" if sentiment == 'negative' else "fef3c7"
                    row_fill = PatternFill(start_color=fill_color, end_color=fill_color, fill_type="solid")
                    for col in range(1, ws.max_column + 1):
                        ws.cell(r_idx, col).fill = row_fill
                    
                    row_data_full = row_data + [sentiment, f"{confidence:.2%}"]
                    
                    if sentiment == 'positive':
                        positive_count += 1
                        for col_idx, value in enumerate(row_data_full, 1):
                            ws_positive.cell(pos_row_idx, col_idx, value=value)
                        pos_row_idx += 1
                    elif sentiment == 'negative':
                        negative_count += 1
                        for col_idx, value in enumerate(row_data_full, 1):
                            ws_negative.cell(neg_row_idx, col_idx, value=value)
                        neg_row_idx += 1
                    else:
                        neutral_count += 1
                        for col_idx, value in enumerate(row_data_full, 1):
                            ws_neutral.cell(neu_row_idx, col_idx, value=value)
                        neu_row_idx += 1
                    
                    all_results.append(result)
                    if len(sentiment_timeline) < 1000:
                        sentiment_timeline.append({
                            'row': r_idx - 1,
                            'sentiment': sentiment,
                            'confidence': confidence
                        })
                    
                    keywords = extract_keywords(text, sentiment)
                    all_keywords[sentiment].extend(keywords)
                    
                    processed_count += 1
                
                processing_status['progress'] = processed_count
                processing_status['positive_count'] = positive_count
                processing_status['negative_count'] = negative_count
                processing_status['neutral_count'] = neutral_count
                
                elapsed = time.time() - start_time
                if processed_count > 0:
                    eta = (elapsed / processed_count) * (total_rows - processed_count)
                    processing_status['eta_seconds'] = round(eta)
                
                if torch.cuda.is_available():
                    gpu_memory_used = torch.cuda.memory_allocated() / 1024**3
                    gpu_memory_total = torch.cuda.get_device_properties(0).total_memory / 1024**3
                    gpu_usage_percent = (gpu_memory_used / gpu_memory_total) * 100
                    
                    print(f"Batch {processed_count:6d}/{total_rows:6d} | "
                          f"Speed: {speed:6.1f} r/s | "
                          f"GPU: {gpu_usage_percent:5.1f}% | "
                          f"Mem: {gpu_memory_used:.2f}/{gpu_memory_total:.2f} GB")
                else:
                    print(f"Batch {processed_count:6d}/{total_rows:6d} | Speed: {speed:6.1f} r/s")
                
                batch_texts = []
                batch_rows = []
                batch_data = []
        
        print(f"\nSaving files...")
        wb.save(output_path)
        
        positive_path = output_path.replace('.xlsx', '_positive.xlsx')
        negative_path = output_path.replace('.xlsx', '_negative.xlsx')
        neutral_path = output_path.replace('.xlsx', '_neutral.xlsx')
        
        wb_positive.save(positive_path)
        wb_negative.save(negative_path)
        wb_neutral.save(neutral_path)
        
        wb.close()
        wb_positive.close()
        wb_negative.close()
        wb_neutral.close()
        
        processing_status['sentiment_timeline'] = sentiment_timeline[::max(1, len(sentiment_timeline)//100)]
        
        for sentiment_type in ['positive', 'negative', 'neutral']:
            keyword_counts = Counter(all_keywords[sentiment_type])
            processing_status['top_keywords'][sentiment_type] = [
                {'word': word, 'count': count} 
                for word, count in keyword_counts.most_common(10)
            ]
        
        confidence_bins = [0] * 10
        for result in all_results:
            bin_idx = min(int(result['confidence'] * 10), 9)
            confidence_bins[bin_idx] += 1
        
        processing_status['confidence_distribution'] = confidence_bins
        
        processing_time = time.time() - start_time
        avg_speed = total_rows / processing_time
        
        print(f"\n{'='*70}")
        print(f"✓ PROCESSING COMPLETE!")
        print(f"Total time: {processing_time:.1f}s")
        print(f"Average speed: {avg_speed:.1f} reviews/sec")
        print(f"Batch size used: {OPTIMAL_BATCH_SIZE}")
        print(f"Positive: {positive_count}, Negative: {negative_count}, Neutral: {neutral_count}")
        print(f"{'='*70}\n")
        
        torch.cuda.empty_cache()
        
        return positive_count, negative_count, neutral_count
        
    except Exception as e:
        print(f"Error in process_excel_advanced: {e}")
        traceback.print_exc()
        raise


def generate_detailed_summary():
    """Generate comprehensive summary"""
    try:
        total = processing_status['total']
        pos = processing_status['positive_count']
        neg = processing_status['negative_count']
        neu = processing_status['neutral_count']
        
        pos_pct = (pos / total * 100) if total > 0 else 0
        neg_pct = (neg / total * 100) if total > 0 else 0
        neu_pct = (neu / total * 100) if total > 0 else 0
        
        top_pos_words = [kw['word'] for kw in processing_status['top_keywords']['positive'][:5]]
        top_neg_words = [kw['word'] for kw in processing_status['top_keywords']['negative'][:5]]
        
        if pos_pct > 60:
            overall_sentiment = "predominantly positive"
            sentiment_desc = "strong customer satisfaction"
        elif pos_pct > 40:
            overall_sentiment = "mixed with a positive lean"
            sentiment_desc = "generally favorable reception with room for improvement"
        elif neg_pct > 60:
            overall_sentiment = "predominantly negative"
            sentiment_desc = "significant customer dissatisfaction requiring immediate attention"
        elif neg_pct > 40:
            overall_sentiment = "mixed with concerning negative trends"
            sentiment_desc = "notable issues that need addressing"
        else:
            overall_sentiment = "balanced"
            sentiment_desc = "diverse range of customer experiences"
        
        summary = f"""COMPREHENSIVE SENTIMENT ANALYSIS REPORT

Dataset Overview:
Our analysis processed {total:,} customer reviews, revealing {overall_sentiment} sentiment patterns. The distribution shows {pos:,} positive reviews ({pos_pct:.1f}%), {neg:,} negative reviews ({neg_pct:.1f}%), and {neu:,} neutral reviews ({neu_pct:.1f}%), indicating {sentiment_desc}.

Positive Insights:
Customers expressing positive sentiments frequently mentioned: {', '.join(top_pos_words[:3]) if top_pos_words else 'various favorable aspects'}. This suggests strong performance in key areas valued by your customer base. The {pos_pct:.1f}% positive rate {'exceeds industry standards and demonstrates excellent customer satisfaction' if pos_pct > 70 else 'shows solid performance with opportunities for enhancement' if pos_pct > 50 else 'indicates areas needing improvement'}.

Areas of Concern:
Negative feedback centered around: {', '.join(top_neg_words[:3]) if top_neg_words else 'various improvement areas'}. These themes appeared consistently across {neg:,} reviews, representing {neg_pct:.1f}% of all feedback. {'Immediate action is recommended to address these critical issues' if neg_pct > 40 else 'While concerning, these issues affect a manageable portion of customers' if neg_pct > 20 else 'Minor issues that can be addressed through incremental improvements'}.

Neutral Zone Analysis:
{neu:,} reviews ({neu_pct:.1f}%) showed neutral sentiment, suggesting {'significant ambivalence that could swing either way with targeted improvements' if neu_pct > 20 else 'a small segment of undecided customers' if neu_pct > 10 else 'most customers have clear opinions'}.

Strategic Recommendations:
{'Focus on scaling positive aspects while urgently addressing negative feedback to prevent customer churn' if neg_pct > 30 else 'Leverage strong positive sentiment while proactively addressing minor concerns' if pos_pct > 60 else 'Implement balanced improvements across all feedback areas'}. The neutral segment presents {'a significant opportunity' if neu_pct > 15 else 'an opportunity'} for conversion through targeted engagement strategies.

Overall, {'this analysis reveals strong market position with manageable challenges' if pos_pct > 60 else 'this analysis highlights critical areas requiring strategic intervention' if neg_pct > 40 else 'this analysis shows mixed performance requiring focused attention'}."""
        
        return summary
        
    except Exception as e:
        print(f"Error generating summary: {e}")
        return "Summary generation encountered an error."


def process_file_async(input_path, output_path):
    """Background processing thread"""
    global processing_status
    
    try:
        processing_status['is_processing'] = True
        processing_status['progress'] = 0
        processing_status['error'] = None
        
        pos, neg, neu = process_excel_advanced(input_path, output_path)
        
        print("Generating detailed summary...")
        detailed_summary = generate_detailed_summary()
        processing_status['detailed_summary'] = detailed_summary
        
        processing_status['progress'] = processing_status['total']
        processing_status['is_processing'] = False
        
        print("✓ Processing complete!")
        
    except Exception as e:
        processing_status['error'] = str(e)
        processing_status['is_processing'] = False
        print(f"Error: {e}")
        traceback.print_exc()


@app.route('/')
def index():
    api_key = os.getenv('SUMMARY_API_KEY', '')
    api_url = os.getenv('SUMMARY_API_URL', 'http://127.0.0.1:7860/api/v1/chat')
    return render_template('index.html', SUMMARY_API_KEY=api_key, SUMMARY_API_URL=api_url)


@app.route('/upload', methods=['POST'])
def upload_file():
    global processing_status
    
    if processing_status['is_processing']:
        return jsonify({'error': 'Already processing'}), 400
    
    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400
    
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    if not file.filename.lower().endswith(('.xlsx', '.xls')):
        return jsonify({'error': 'Only Excel files allowed'}), 400
    
    try:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"input_{timestamp}.xlsx"
        input_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(input_path)
        
        output_filename = f"output_{timestamp}.xlsx"
        output_path = os.path.join(app.config['OUTPUT_FOLDER'], output_filename)
        
        processing_status = {
            'is_processing': True,
            'progress': 0,
            'total': 0,
            'current_file': output_filename,
            'positive_count': 0,
            'negative_count': 0,
            'neutral_count': 0,
            'summary': '',
            'detailed_summary': '',
            'error': None,
            'sentiment_timeline': [],
            'confidence_distribution': [],
            'top_keywords': {'positive': [], 'negative': [], 'neutral': []},
            'processing_speed': 0,
            'eta_seconds': 0,
            'all_comments': []
        }
        
        thread = threading.Thread(target=process_file_async, args=(input_path, output_path))
        thread.daemon = True
        thread.start()
        
        return jsonify({'message': 'Processing started', 'filename': output_filename}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/status')
def get_status():
    return jsonify(processing_status)


@app.route('/api/comments')
def get_comments():
    """Get paginated comments"""
    try:
        page = int(request.args.get('page', 1))
        per_page = 10
        
        all_comments = processing_status.get('all_comments', [])
        total = len(all_comments)
        
        start = (page - 1) * per_page
        end = start + per_page
        
        comments = all_comments[start:end]
        
        return jsonify({
            'comments': comments,
            'total': total,
            'page': page,
            'per_page': per_page,
            'total_pages': (total + per_page - 1) // per_page
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/summarize', methods=['POST'])
def summarize_comment():
    """Summarize a comment using local model API"""
    try:
        data = request.json
        comment = data.get('comment', '')
        sentiment = data.get('sentiment', '')
        confidence = data.get('confidence', 0)
        
        # Get API configuration from environment
        api_key = os.getenv('SUMMARY_API_KEY')
        api_url = os.getenv('SUMMARY_API_URL', 'http://127.0.0.1:7860/api/v1/chat')
        
        if not api_key:
            return jsonify({'error': 'API key not configured in .env file'}), 500
        
        # Truncate very long comments intelligently
        max_comment_length = 2000
        truncated = False
        original_length = len(comment)
        
        if len(comment) > max_comment_length:
            comment = comment[:1800] + "... [truncated for analysis]"
            truncated = True
            print(f"⚠ Comment truncated from {original_length} to {len(comment)} characters")
        
        # Construct the prompt for summarization
        truncation_note = f"\n\nNote: Original comment was {original_length} characters and has been truncated for analysis." if truncated else ""
        
        prompt = f"""Analyze this customer review in detail:

Review: "{comment}"{truncation_note}

Detected Sentiment: {sentiment.upper()}
Confidence Score: {confidence:.2%}

Please provide a structured analysis with the following sections:

1. DETAILED SUMMARY
Explain what this review is about in 2-3 sentences.

2. KEY WORDS AND PHRASES
List the most important words and phrases used in this review (5-7 key terms).

3. SENTIMENT CLASSIFICATION REASONING
Explain why this review is classified as {sentiment}. What specific language, words, or tone led to this classification?

4. SENTIMENT INDICATOR BREAKDOWN
Provide a percentage breakdown:
- Positive signals: X%
- Negative signals: Y%
- Neutral signals: Z%

Please format your response clearly with headers for each section."""

        # Make API request to local model
        headers = {
            "X-API-Key": api_key,
            "Content-Type": "application/json"
        }
        
        payload = {
            "prompt": prompt,
            "max_tokens": 1500,
            "temperature": 0.3
        }
        
        print(f"\n{'='*70}")
        print("🤖 Sending summarization request to local model...")
        print(f"API URL: {api_url}")
        print(f"Comment length: {len(comment)} characters (original: {original_length})")
        print(f"Sentiment: {sentiment}")
        print(f"Confidence: {confidence:.2%}")
        
        response = requests.post(api_url, headers=headers, json=payload, timeout=60)
        
        print(f"Response status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            
            summary_text = (
                result.get('response') or 
                result.get('text') or 
                result.get('output') or 
                result.get('content') or
                str(result)
            )
            
            if not summary_text or summary_text == str(result):
                print(f"⚠ Unusual response format: {result}")
                return jsonify({
                    'error': 'Could not extract summary from API response',
                    'debug': str(result)
                }), 500
            
            print(f"✓ Summary generated ({len(summary_text)} characters)")
            print(f"{'='*70}\n")
            
            return jsonify({
                'summary': summary_text,
                'success': True,
                'truncated': truncated,
                'original_length': original_length if truncated else None
            })
        else:
            error_msg = f"API returned status code {response.status_code}"
            try:
                error_detail = response.json()
                error_msg += f": {error_detail}"
            except:
                error_msg += f": {response.text[:200]}"
            
            print(f"✗ Error: {error_msg}")
            print(f"{'='*70}\n")
            return jsonify({'error': error_msg}), 500
        
    except requests.exceptions.Timeout:
        error_msg = "Request timeout - model took too long to respond (>60s)"
        print(f"✗ Error: {error_msg}")
        return jsonify({'error': error_msg}), 504
        
    except requests.exceptions.ConnectionError:
        error_msg = f"Cannot connect to local model API. Make sure the model server is running at {api_url}"
        print(f"✗ Error: {error_msg}")
        return jsonify({'error': error_msg}), 503
        
    except Exception as e:
        print(f"✗ Summarization error: {e}")
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500
@app.route('/api/batch-summarize', methods=['POST'])
def batch_summarize():
    """Batch summarization endpoint for processing multiple reviews"""
    try:
        data = request.json
        prompt = data.get('prompt', '')
        max_tokens = data.get('max_tokens', 800)
        
        if not prompt:
            return jsonify({'error': 'No prompt provided', 'success': False}), 400
        
        # Get API configuration from environment
        api_key = os.getenv('SUMMARY_API_KEY')
        api_url = os.getenv('SUMMARY_API_URL', 'http://127.0.0.1:7860/api/v1/chat')
        
        if not api_key:
            return jsonify({'error': 'API key not configured in .env file', 'success': False}), 500
        
        print(f"\n{'='*70}")
        print(f"🤖 Batch Summarization Request")
        print(f"API URL: {api_url}")
        print(f"Prompt length: {len(prompt)} characters")
        print(f"Max tokens: {max_tokens}")
        
        # Make API request to local model
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
        
        print(f"Response status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            
            summary_text = (
                result.get('response') or 
                result.get('text') or 
                result.get('output') or 
                result.get('content') or
                str(result)
            )
            
            if not summary_text or summary_text == str(result):
                print(f"⚠ Unusual response format: {result}")
                return jsonify({
                    'error': 'Could not extract summary from API response',
                    'debug': str(result),
                    'success': False
                }), 500
            
            print(f"✓ Summary generated ({len(summary_text)} characters)")
            print(f"{'='*70}\n")
            
            return jsonify({
                'summary': summary_text,
                'success': True
            })
        else:
            error_msg = f"API returned status code {response.status_code}"
            try:
                error_detail = response.json()
                error_msg += f": {error_detail}"
            except:
                error_msg += f": {response.text[:200]}"
            
            print(f"✗ Error: {error_msg}")
            print(f"{'='*70}\n")
            return jsonify({'error': error_msg, 'success': False}), 500
        
    except requests.exceptions.Timeout:
        error_msg = "Request timeout - model took too long to respond (>120s)"
        print(f"✗ Error: {error_msg}")
        return jsonify({'error': error_msg, 'success': False}), 504
        
    except requests.exceptions.ConnectionError:
        error_msg = f"Cannot connect to local model API at {api_url}"
        print(f"✗ Error: {error_msg}")
        return jsonify({'error': error_msg, 'success': False}), 503
        
    except Exception as e:
        print(f"✗ Batch summarization error: {e}")
        traceback.print_exc()
        return jsonify({'error': str(e), 'success': False}), 500

@app.route('/download/<filename>')
def download_file(filename):
    try:
        file_path = os.path.join(app.config['OUTPUT_FOLDER'], filename)
        if os.path.exists(file_path):
            return send_file(file_path, as_attachment=True)
        return jsonify({'error': 'File not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
@app.route('/generate-pdf-executive')
def generate_pdf_executive():
    """Generate executive summary PDF"""
    try:
        if not processing_status.get('total', 0) > 0:
            return jsonify({'error': 'No analysis data available'}), 400
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"executive_summary_{timestamp}.pdf"
        output_path = os.path.join(app.config['OUTPUT_FOLDER'], filename)
        
        # Add processing time to status
        processing_status['processing_time'] = 0  # You can calculate actual time
        
        generate_executive_summary(processing_status, output_path)
        
        return send_file(output_path, as_attachment=True)
        
    except Exception as e:
        print(f"Error generating executive PDF: {e}")
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500


@app.route('/generate-pdf-detailed')
def generate_pdf_detailed():
    """Generate detailed report PDF with AI summaries"""
    try:
        if not processing_status.get('total', 0) > 0:
            return jsonify({'error': 'No analysis data available'}), 400
        
        # Get API configuration
        api_key = os.getenv('SUMMARY_API_KEY')
        api_url = os.getenv('SUMMARY_API_URL', 'http://127.0.0.1:7860/api/v1/chat')
        
        if not api_key:
            return jsonify({'error': 'API key not configured in .env file'}), 500
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"detailed_report_{timestamp}.pdf"
        output_path = os.path.join(app.config['OUTPUT_FOLDER'], filename)
        
        # This will take time as it generates AI summaries
        print("\n" + "="*70)
        print("🤖 Starting detailed PDF generation with AI summaries...")
        print("⏰ This will take 2-3 minutes to generate all AI summaries")
        print("="*70)
        
        generate_detailed_report_with_ai(processing_status, output_path, api_key, api_url)
        
        return send_file(output_path, as_attachment=True)
        
    except Exception as e:
        print(f"Error generating detailed PDF: {e}")
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    print("\n" + "="*70)
    print("✅ SENTIMENT ANALYSIS SYSTEM READY")
    print("="*70)
    print(f"Device: {DEVICE}")
    print(f"Batch Size: {OPTIMAL_BATCH_SIZE}")
    print(f"Max Sequence Length: {MAX_LENGTH}")
    if torch.cuda.is_available():
        gpu_name = torch.cuda.get_device_name(0)
        print(f"GPU: {gpu_name}")
        print(f"Expected Speed: 100-200 reviews/second")
    else:
        print("Running on CPU")
    print("="*70)
    print("\n🌐 Starting server at http://localhost:5000")
    print("ℹ  Press Ctrl+C to stop\n")
    
    app.run(debug=False, host='0.0.0.0', port=5000, threaded=True)