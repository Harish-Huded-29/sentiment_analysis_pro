# 🚀 Sentiment Analysis Pro - GPU Accelerated

A professional-grade sentiment analysis system powered by DistilBERT AI with GPU acceleration, real-time analytics, and comprehensive PDF reporting capabilities.

[![Python](https://img.shields.io/badge/Python-3.11%2B-blue.svg)](https://www.python.org/)
[![PyTorch](https://img.shields.io/badge/PyTorch-2.0%2B-red.svg)](https://pytorch.org/)
[![CUDA](https://img.shields.io/badge/CUDA-11.8%2F12.1-green.svg)](https://developer.nvidia.com/cuda-downloads)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

## ✨ Key Features

- **🎯 Advanced Sentiment Detection**: Positive, Negative, and Neutral classification with confidence scores
- **⚡ GPU Accelerated**: Optimized for NVIDIA GPUs (RTX 3050/3060/3070/3080)
- **📊 Interactive Dashboard**: Real-time progress tracking and live statistics
- **🤖 AI-Powered Summaries**: Local LLM integration for detailed review analysis
- **📄 PDF Report Generation**: Executive summaries and comprehensive reports
- **💾 Multiple Export Formats**: Separate Excel files for each sentiment category
- **🔍 Comment Review System**: Detailed inspection with AI-powered insights
- **📈 Visual Analytics**: Interactive charts and trend analysis

---

## 📋 Prerequisites

### System Requirements
- **OS**: Windows 10/11 (64-bit)
- **RAM**: 16GB minimum (32GB recommended)
- **GPU**: NVIDIA GPU with 4GB+ VRAM (RTX 3050 or better)
- **Storage**: 10GB free space
- **Python**: 3.11 or 3.13

### NVIDIA Requirements
- NVIDIA GPU Drivers (latest version)
- CUDA Toolkit 11.8 or 12.1
- cuDNN 8.x

---

## 🛠️ Installation Guide

### Step 1: Install CUDA Toolkit

Download and install CUDA from [NVIDIA CUDA Downloads](https://developer.nvidia.com/cuda-downloads)

```bash
# Verify CUDA installation
nvcc --version
nvidia-smi
```

### Step 2: Clone Repository

```bash
git clone https://github.com/yourusername/sentiment-analysis-pro.git
cd sentiment-analysis-pro
```

### Step 3: Download DistilBERT Model

Install Hugging Face CLI:

```bash
pip install huggingface-hub
```

Download the model with GPU support:

```bash
# Login to Hugging Face (optional, for gated models)
huggingface-cli login

# Download DistilBERT-SST2 model
huggingface-cli download distilbert-base-uncased-finetuned-sst-2-english --local-dir models/distilbert-sst2 --local-dir-use-symlinks False
```

**Alternative: Download via Python**

```python
from transformers import AutoTokenizer, AutoModelForSequenceClassification

model_name = "distilbert-base-uncased-finetuned-sst-2-english"
save_path = "models/distilbert-sst2"

# Download model and tokenizer
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForSequenceClassification.from_pretrained(model_name)

# Save locally
tokenizer.save_pretrained(save_path)
model.save_pretrained(save_path)

print(f"✓ Model downloaded to {save_path}")
```

### Step 4: Create Virtual Environment

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate

# Linux/Mac:
source venv/bin/activate
```

### Step 5: Install PyTorch with CUDA Support

**For CUDA 11.8:**
```bash
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
```

**For CUDA 12.1:**
```bash
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
```

**Verify GPU Installation:**
```python
python -c "import torch; print(f'CUDA Available: {torch.cuda.is_available()}'); print(f'GPU: {torch.cuda.get_device_name(0) if torch.cuda.is_available() else \"None\"}')"
```

### Step 6: Install Required Libraries

```bash
# Upgrade pip and setuptools
python -m pip install --upgrade pip setuptools wheel

# Install core dependencies
pip install flask transformers accelerate
pip install openpyxl pandas numpy
pip install python-dotenv requests

# Install PDF generation libraries
pip install reportlab pillow

# Install optional dependencies for better performance
pip install scikit-learn sentencepiece
```

**Note**: PyTorch installation with CUDA support may take 5-10 minutes and requires building wheels. Ensure you have a stable internet connection.

### Step 7: Configure Environment Variables

Create a `.env` file in the project root:

```env
# Local Summary Model API Configuration
# Generated from "Immortal's Slave" application
SUMMARY_API_KEY=your_api_key_here
SUMMARY_API_URL=http://127.0.0.1:7860/api/v1/chat
```

**To generate an API key:**
1. Run your "Immortal's Slave" LLM application
2. Navigate to API settings
3. Generate a new API key
4. Copy the key to `.env` file

---

## 📁 Project Structure

```
sentiment-analysis-pro/
│
├── app.py                      # Main Flask application
├── pdf_generator.py            # PDF report generation
├── download_model.py           # Model download utility
├── .env                        # Environment configuration
├── requirements.txt            # Python dependencies
├── README.md                   # This file
│
├── models/
│   └── distilbert-sst2/       # Downloaded DistilBERT model
│       ├── config.json
│       ├── pytorch_model.bin
│       ├── tokenizer.json
│       └── vocab.txt
│
├── templates/
│   └── index.html             # Main web interface
│
├── static/
│   ├── css/
│   │   ├── style.css          # Main stylesheet
│   │   └── modal.css          # Modal styles
│   └── js/
│       └── main.js            # Frontend JavaScript
│
├── uploads/                    # Auto-created: Uploaded files (temporary)
├── outputs/                    # Auto-created: Generated reports
│
├── venv/                       # Virtual environment
└── __pycache__/               # Auto-created: Python cache files
```

### Automatically Created Folders

The following folders are created automatically when you run the application:

- `uploads/` - Stores uploaded Excel files temporarily
- `outputs/` - Stores generated analysis files (Excel & PDF)
- `templates/` - HTML templates (if missing)
- `static/css/` - CSS files (if missing)
- `static/js/` - JavaScript files (if missing)
- `__pycache__/` - Python bytecode cache (can be ignored)

---

## 🚀 Quick Start

### 1. Start the Application

```bash
# Activate virtual environment
venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/Mac

# Run the application
python app.py
```

### 2. Access the Web Interface

Open your browser and navigate to:
```
http://localhost:5000
```

### 3. Start the Local LLM (Optional)

For AI-powered summaries, ensure "Immortal's Slave" is running:

```bash
# In a separate terminal
cd path/to/immortals-slave
python app.py  # Or your LLM application startup command
```

The LLM should be accessible at `http://127.0.0.1:7860/api/v1/chat`

---

## 📖 Usage Guide

### Step 1: Upload Excel File

1. **Prepare Your Data**:
   - Excel file (.xlsx or .xls)
   - Column A should contain reviews
   - Header row: "review" (case-insensitive)
   - Maximum file size: 200MB

2. **Upload**:
   - Drag & drop file onto upload zone, OR
   - Click to browse and select file

### Step 2: Start Analysis

1. Click **"Start Analysis"** button
2. Monitor real-time progress:
   - Processing speed (reviews/second)
   - Live sentiment counts
   - Estimated time remaining (ETA)
   - GPU utilization

### Step 3: Review Results

**Statistics Dashboard:**
- Total reviews analyzed
- Positive/Negative/Neutral counts and percentages
- Processing time and average speed

**Comprehensive Analysis Report:**
- AI-generated insights (200-300 words)
- Dataset overview
- Positive insights and areas of concern
- Neutral zone analysis
- Strategic recommendations

**Interactive Visualizations:**
- 🥧 Sentiment Distribution (Pie Chart)
- 📈 Sentiment Flow Timeline (Line Chart)
- 🔥 Confidence Heatmap (Bar Chart)
- 🔑 Top Keywords Analysis (Horizontal Bar Chart)

### Step 4: Review Comments in Detail

1. Click **"Review All Comments in Detail"** button
2. Browse paginated comments table
3. Click **"🤖 Summarize"** on any comment for:
   - Detailed summary
   - Key words and phrases
   - Sentiment classification reasoning
   - Sentiment indicator breakdown

### Step 5: Generate Batch Summaries

**For Positive or Negative Reviews:**
1. Select sentiment type (Positive/Negative)
2. Click **"Generate Summary"**
3. Wait 30-60 seconds for AI processing
4. Review comprehensive summary with:
   - Overview
   - Key themes
   - Critical insights
   - Recommendations

### Step 6: Download Results

**Excel Files:**
- ✅ Complete Analysis (all reviews with predictions)
- 😊 Positive Reviews Only
- 😞 Negative Reviews Only
- 😐 Neutral Reviews Only

**PDF Reports:**
- 📄 **Executive Summary** (1-page overview)
- 📕 **Detailed Report** (Multi-page with AI insights)
  - ⏰ Takes 2-3 minutes to generate
  - Contains AI summaries for all sentiments

---

## ⚙️ Configuration

### Adjust GPU Batch Size (app.py)

```python
# Line ~85
OPTIMAL_BATCH_SIZE = 128  # Default for RTX 3050 4GB

# Recommended batch sizes:
# RTX 3050 4GB: 96-128
# RTX 3060 12GB: 256-384
# RTX 3070 8GB: 192-256
# RTX 3080 10GB: 256-384
```

### Adjust Neutral Detection Threshold (app.py)

```python
# Line ~86
NEUTRAL_THRESHOLD = 0.65  # 50-65% confidence = neutral

# Higher value = stricter neutral detection
# Lower value = more reviews classified as neutral
```

### Configure Max Sequence Length (app.py)

```python
# Line ~84
MAX_LENGTH = 128  # DistilBERT tokens

# Increase for longer reviews (max 512)
# Decrease for faster processing
```

---

## 🔧 Troubleshooting

### GPU Not Detected

**Check CUDA Installation:**
```bash
nvidia-smi
nvcc --version
```

**Reinstall PyTorch:**
```bash
pip uninstall torch torchvision torchaudio
pip cache purge
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
```

**Verify GPU in Python:**
```python
import torch
print(torch.cuda.is_available())  # Should be True
print(torch.cuda.get_device_name(0))
```

### Low GPU Usage (<50%)

1. **Increase batch size** in `app.py`
2. **Close other GPU applications** (Chrome, games, etc.)
3. **Update NVIDIA drivers**
4. **Check GPU utilization**:
   ```bash
   nvidia-smi -l 1  # Monitor GPU every 1 second
   ```

### Slow Processing Speed

1. **Verify GPU is being used**:
   - Check console output for "✓ GPU acceleration enabled"
   - Run `nvidia-smi` to see GPU memory usage (should be 3-4GB)

2. **Optimize settings**:
   - Reduce `MAX_LENGTH` to 64 or 96
   - Adjust `OPTIMAL_BATCH_SIZE` based on available VRAM

3. **Check for bottlenecks**:
   - CPU usage (should be low)
   - RAM usage (should not exceed 80%)
   - Disk I/O (use SSD if possible)

### ModuleNotFoundError

```bash
# Ensure virtual environment is activated
venv\Scripts\activate

# Reinstall missing package
pip install <package_name>

# Or reinstall all dependencies
pip install -r requirements.txt
```

### API Connection Errors (AI Summaries)

1. **Verify LLM is running**:
   ```bash
   curl http://127.0.0.1:7860/api/v1/chat
   ```

2. **Check `.env` configuration**:
   - Correct API key
   - Correct API URL
   - No extra spaces

3. **Test API manually**:
   ```python
   import requests
   
   response = requests.post(
       'http://127.0.0.1:7860/api/v1/chat',
       headers={'X-API-Key': 'your_key'},
       json={'prompt': 'Test', 'max_tokens': 50}
   )
   print(response.json())
   ```

### Charts Not Displaying

1. **Clear browser cache**: Ctrl+Shift+Delete
2. **Check browser console**: F12 → Console tab
3. **Verify Chart.js loaded**: Should see no errors
4. **Try different browser**: Chrome/Firefox/Edge

### Out of Memory Errors

**Reduce batch size:**
```python
OPTIMAL_BATCH_SIZE = 64  # or 32 for 2GB VRAM
```

**Enable memory optimization:**
```python
# Add to app.py after model loading
torch.backends.cudnn.benchmark = False
torch.backends.cudnn.deterministic = True
```

**Clear GPU cache periodically:**
```python
torch.cuda.empty_cache()
```

---

## 📊 Performance Benchmarks

| Dataset Size | Processing Time | Speed | GPU Usage | VRAM |
|--------------|----------------|-------|-----------|------|
| 1,000 reviews | ~3 seconds | 330/sec | 85-95% | 3.2GB |
| 10,000 reviews | ~25 seconds | 400/sec | 90-95% | 3.5GB |
| 50,000 reviews | ~2 minutes | 420/sec | 92-96% | 3.8GB |
| 100,000 reviews | ~4 minutes | 450/sec | 93-97% | 3.9GB |

*Benchmarks on RTX 3050 4GB with Python 3.13 and CUDA 11.8*

---

## 🐍 Python Cache Files

### What is `__pycache__`?

Python automatically creates `__pycache__` directories containing bytecode-compiled `.pyc` files. These files speed up module loading but can be safely deleted.

### Managing Cache Files

**Add to `.gitignore`:**
```gitignore
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python

# Virtual Environment
venv/
env/
ENV/

# IDE
.vscode/
.idea/
*.swp
*.swo

# Application
uploads/
outputs/*.xlsx
outputs/*.pdf
.env
```

**Clean cache manually:**
```bash
# Windows
del /s /q __pycache__
for /d /r . %d in (__pycache__) do @if exist "%d" rd /s /q "%d"

# Linux/Mac
find . -type d -name __pycache__ -exec rm -r {} +
find . -type f -name "*.pyc" -delete
```

**Prevent cache creation (not recommended):**
```bash
python -B app.py  # Runs without generating .pyc files
```

---

## 🔒 Security Notes

- **Local Processing**: All analysis runs locally, no data sent to external servers
- **API Security**: Use strong API keys for LLM integration
- **File Validation**: Only Excel files accepted, size limits enforced
- **Environment Variables**: Keep `.env` file secure, never commit to Git
- **Temporary Files**: Automatically cleaned on server restart

---

## 📦 Creating requirements.txt

Generate a `requirements.txt` file:

```bash
pip freeze > requirements.txt
```

**Recommended `requirements.txt`:**

```txt
torch>=2.0.0
torchvision>=0.15.0
torchaudio>=2.0.0
transformers>=4.30.0
accelerate>=0.20.0
flask>=2.3.0
openpyxl>=3.1.0
pandas>=2.0.0
numpy>=1.24.0
python-dotenv>=1.0.0
requests>=2.31.0
reportlab>=4.0.0
pillow>=10.0.0
scikit-learn>=1.3.0
sentencepiece>=0.1.99
```

Install from `requirements.txt`:

```bash
pip install -r requirements.txt
```

---

## 🤝 Contributing

We welcome contributions! Please follow these guidelines:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- **DistilBERT**: Hugging Face Transformers team
- **PyTorch**: Facebook AI Research
- **Flask**: Pallets Projects
- **Chart.js**: Chart.js contributors
- **ReportLab**: ReportLab team

---

## 📧 Support

- **Issues**: [GitHub Issues](https://github.com/yourusername/sentiment-analysis-pro/issues)
- **Discussions**: [GitHub Discussions](https://github.com/yourusername/sentiment-analysis-pro/discussions)
- **Email**: your.email@example.com

---

## 🗺️ Roadmap

- [ ] Multi-language support (Spanish, French, German)
- [ ] Real-time streaming analysis
- [ ] Cloud deployment support (AWS, Azure, GCP)
- [ ] Mobile app (iOS/Android)
- [ ] Advanced analytics dashboard
- [ ] Custom model fine-tuning interface
- [ ] Batch file processing
- [ ] Email notifications
- [ ] Historical trend comparison
- [ ] API rate limiting and authentication

---

## 💡 Tips & Best Practices

1. **Large Datasets**: For 100k+ reviews, ensure no other GPU applications are running
2. **Model Warm-up**: First analysis may be slower (2-3 seconds) due to GPU initialization
3. **Memory Management**: Close application between large file analyses to free VRAM
4. **Backup Data**: Keep original Excel files as backup before analysis
5. **API Limits**: Monitor LLM API usage for batch summaries (typically 10-20 requests)
6. **PDF Generation**: Detailed reports take 2-3 minutes due to AI summary generation
7. **Browser Compatibility**: Chrome and Edge offer best performance for charts
8. **Network Stability**: Ensure stable connection when using AI summary features

---

**Made with ❤️ for premium sentiment analysis by immortal**

*Version 2.0 - GPU Accelerated Edition*

*Last Updated: November 2024*
