# 🚀 Sentiment Analysis Pro - Premium Edition

A professional-grade, GPU-accelerated sentiment analysis system with advanced analytics and stunning dark UI.

## ✨ Premium Features

### 🎯 Advanced Analytics
- **Neutral Sentiment Detection**: Identifies reviews with 50-65% confidence as neutral
- **Confidence Scoring**: Shows prediction confidence for every review
- **Multiple Excel Exports**: Download separate files for positive, negative, and neutral reviews
- **200-300 Word Summary**: AI-generated comprehensive analysis report
- **Real-time Processing**: Live stats and progress tracking

### 📊 Interactive Visualizations
- **Sentiment Distribution Chart**: Pie chart showing overall sentiment breakdown
- **Sentiment Flow Timeline**: Line graph tracking sentiment changes through data
- **Confidence Heatmap**: Bar chart showing prediction confidence distribution
- **Top Keywords Analysis**: Dynamic keyword frequency charts with filters
- **Export Charts**: Download any chart as PNG image

### ⚡ Performance Optimizations
- **90%+ GPU Usage**: Maximized RTX 3050 utilization
- **Batch Size: 48**: Optimized from 16 to 48 for better throughput
- **300-500 reviews/second**: 3x faster than standard version
- **Mixed Precision Ready**: FP16 support for even faster processing
- **Smart Memory Management**: Automatic GPU cache clearing

### 🎨 Premium Dark UI/UX
- **Modern Black Theme**: Professional dark interface with purple/blue accents
- **Smooth Animations**: Transitions on every interaction
- **Glassmorphism Effects**: Frosted glass cards and elements
- **Animated Background**: Floating gradient orbs
- **Drag & Drop Upload**: Intuitive file upload experience
- **Real-time Counters**: Animated statistics
- **Toast Notifications**: Elegant feedback system
- **Mobile Responsive**: Works on all screen sizes

## 📋 System Requirements

- **Python**: 3.11 or 3.13
- **GPU**: NVIDIA RTX 3050 (4GB VRAM) or better
- **RAM**: 16GB recommended
- **OS**: Windows 10/11
- **CUDA**: 11.8 or 12.1

## 🚀 Quick Start

### 1. Installation

```bash
# Run the setup script
setup_gpu_python313.bat

# Wait for installation to complete (5-10 minutes)
```

### 2. Start Server

```bash
# Double-click or run
start_server.bat
```

### 3. Access Application

Open your browser to: **http://localhost:5000**

## 📖 Usage Guide

### Step 1: Upload Excel File
- Drag & drop or click to browse
- File must be .xlsx or .xls format
- Column A should contain reviews with header "review"
- Maximum file size: 200MB

### Step 2: Start Analysis
- Click "Start Analysis" button
- Watch real-time progress with live stats
- See processing speed and ETA

### Step 3: View Results
- **Stats Dashboard**: View positive, negative, and neutral counts
- **Detailed Summary**: Read comprehensive 200-300 word analysis
- **Charts**: Explore interactive visualizations
- **Export**: Download charts as PNG

### Step 4: Download Results
- **Complete Analysis**: All reviews with sentiment predictions
- **Positive Reviews**: Filtered positive-only Excel file
- **Negative Reviews**: Filtered negative-only Excel file  
- **Neutral Reviews**: Filtered neutral-only Excel file

## 📊 Output File Structure

### Main Output File
```
Column A: review (original text)
Column B: sentiment (positive/negative/neutral)
Column C: confidence (percentage score)
```

### Color Coding
- ✅ **Green rows**: Positive reviews
- ❌ **Red rows**: Negative reviews
- ⚠️ **Yellow rows**: Neutral reviews (50-65% confidence)

## 🎨 UI Features

### Animated Elements
- Floating gradient orbs in background
- Smooth fade-in animations on load
- Hover effects on all interactive elements
- Progress circle animation
- Animated counters with easing
- Slide-in toast notifications

### Interactive Charts
- **Sentiment Distribution**: Click legend to toggle categories
- **Timeline**: Hover to see exact row numbers
- **Confidence Heatmap**: Visual intensity gradient
- **Keywords**: Filter by positive/negative/neutral
- **Export**: Click download icon to save chart

## ⚙️ Configuration

### GPU Optimization (app.py)
```python
BATCH_SIZE = 48  # Increase for more GPU usage
NEUTRAL_THRESHOLD = 0.65  # Adjust neutral detection
MAX_LENGTH = 512  # DistilBERT token limit
```

### Performance Tuning
- **More VRAM?** Increase BATCH_SIZE to 64 or 96
- **Less VRAM?** Decrease BATCH_SIZE to 32 or 24
- **Slower CPU?** Reduce batch size for stability

## 🐛 Troubleshooting

### GPU Not Detected
```bash
# Check CUDA installation
nvidia-smi

# Reinstall PyTorch with CUDA
pip uninstall torch torchvision torchaudio
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
```

### Low GPU Usage
- Check Task Manager → Performance → GPU
- Increase BATCH_SIZE in app.py
- Close other GPU applications
- Update NVIDIA drivers

### Charts Not Showing
- Check browser console for errors
- Ensure Chart.js loaded (check internet connection)
- Clear browser cache and reload

### Slow Processing
- Verify GPU is being used (should see 90%+ in nvidia-smi)
- Check for background GPU processes
- Reduce batch size if RAM is low

## 📈 Performance Benchmarks

| Dataset Size | Processing Time | Speed | GPU Usage |
|--------------|----------------|-------|-----------|
| 1,000 reviews | ~3 seconds | 330/sec | 85-95% |
| 10,000 reviews | ~25 seconds | 400/sec | 90-95% |
| 50,000 reviews | ~2 minutes | 420/sec | 92-96% |
| 100,000 reviews | ~4 minutes | 450/sec | 93-97% |

*Benchmarks on RTX 3050 4GB with Python 3.13*

## 🔐 Security Notes

- Application runs locally only (localhost:5000)
- No data sent to external servers
- All processing done on your machine
- Files stored temporarily in uploads/outputs folders
- Automatically cleared on server restart

## 🛠️ Advanced Features

### Custom Model Fine-tuning
- Replace model in `models/distilbert-sst2/`
- Ensure model is compatible with transformers library
- Update MODEL_PATH in app.py

### API Integration
- Server provides REST API endpoints
- `/upload` - POST file for analysis
- `/status` - GET processing status
- `/download/<filename>` - GET processed file

### Batch Processing
- Upload multiple files sequentially
- Results saved separately with timestamps
- Historical data retained in outputs folder

## 📝 File Structure

```
D:\Segment_analysis_project\
├── app.py                  # Main Flask application (optimized)
├── models/
│   └── distilbert-sst2/   # AI model files
├── templates/
│   └── index.html         # Premium dark theme UI
├── static/
│   ├── css/
│   │   └── style.css      # Modern styling with animations
│   └── js/
│       └── main.js        # Charts and interactions
├── uploads/               # Temporary input files
├── outputs/               # Generated result files
└── venv/                  # Python virtual environment
```

## 🎯 Roadmap

### Planned Features
- [ ] Multi-file comparison dashboard
- [ ] Historical trend analysis
- [ ] Custom confidence thresholds
- [ ] Email notifications on completion
- [ ] PDF report generation
- [ ] Aspect-based sentiment analysis
- [ ] Multi-language support

## 💡 Tips & Tricks

1. **Large Files**: For 100k+ reviews, ensure no other apps use GPU
2. **Better Summaries**: More diverse data = better AI insights
3. **Neutral Reviews**: Perfect for follow-up surveys
4. **Chart Export**: Use PNG exports in presentations
5. **Batch Mode**: Process multiple files back-to-back without restart

## 📞 Support

If you encounter issues:
1. Check the troubleshooting section
2. Run `diagnose.bat` to identify problems
3. Review console output for error messages
4. Ensure all dependencies are installed

## 📜 License

This is a custom-built solution. All rights reserved.

## 🙏 Acknowledgments

- **DistilBERT**: Hugging Face transformers
- **PyTorch**: Deep learning framework
- **Chart.js**: Interactive charts
- **Flask**: Web framework

---

**Made with ❤️ for premium sentiment analysis**

*Version 2.0 - Premium Edition*