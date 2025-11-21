/**
 * SENTIMENT ANALYSIS PRO - Premium Edition
 * Advanced Analytics Dashboard with Comment Review
 */

let selectedFile = null;
let outputFilename = null;
let statusCheckInterval = null;
let startTime = null;
let charts = {};
let currentPage = 1;
let totalPages = 1;
let allComments = [];

// DOM Elements
const fileInput = document.getElementById('fileInput');
const uploadZone = document.getElementById('uploadZone');
const fileInfo = document.getElementById('fileInfo');
const fileName = document.getElementById('fileName');
const fileSize = document.getElementById('fileSize');
const removeFile = document.getElementById('removeFile');
const analyzeBtn = document.getElementById('analyzeBtn');

const uploadSection = document.getElementById('uploadSection');
const processingSection = document.getElementById('processingSection');
const resultsSection = document.getElementById('resultsSection');
const errorSection = document.getElementById('errorSection');

// ============================================================
// FILE UPLOAD HANDLERS
// ============================================================

uploadZone.addEventListener('click', () => fileInput.click());

uploadZone.addEventListener('dragover', (e) => {
    e.preventDefault();
    uploadZone.classList.add('drag-over');
});

uploadZone.addEventListener('dragleave', () => {
    uploadZone.classList.remove('drag-over');
});

uploadZone.addEventListener('drop', (e) => {
    e.preventDefault();
    uploadZone.classList.remove('drag-over');
    
    const files = e.dataTransfer.files;
    if (files.length > 0) {
        handleFileSelect(files[0]);
    }
});

fileInput.addEventListener('change', (e) => {
    if (e.target.files.length > 0) {
        handleFileSelect(e.target.files[0]);
    }
});

removeFile.addEventListener('click', (e) => {
    e.stopPropagation();
    clearFile();
});

function handleFileSelect(file) {
    if (!file.name.match(/\.(xlsx|xls)$/i)) {
        showToast('Please select an Excel file (.xlsx or .xls)', 'error');
        return;
    }
    
    if (file.size > 200 * 1024 * 1024) {
        showToast('File size exceeds 200MB limit', 'error');
        return;
    }
    
    selectedFile = file;
    fileName.textContent = file.name;
    fileSize.textContent = formatFileSize(file.size);
    
    fileInfo.style.display = 'flex';
    document.querySelector('.upload-text').style.display = 'none';
    document.querySelector('.upload-icon').style.display = 'none';
    
    analyzeBtn.disabled = false;
    
    showToast('File ready for analysis', 'success');
}

function clearFile() {
    selectedFile = null;
    fileInput.value = '';
    fileInfo.style.display = 'none';
    document.querySelector('.upload-text').style.display = 'block';
    document.querySelector('.upload-icon').style.display = 'block';
    analyzeBtn.disabled = true;
}

function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return Math.round((bytes / Math.pow(k, i)) * 100) / 100 + ' ' + sizes[i];
}

// ============================================================
// ANALYSIS START
// ============================================================

analyzeBtn.addEventListener('click', async () => {
    if (!selectedFile) return;
    
    const formData = new FormData();
    formData.append('file', selectedFile);
    
    analyzeBtn.disabled = true;
    analyzeBtn.innerHTML = '<span class="spinner"></span> Uploading...';
    
    try {
        const response = await fetch('/upload', {
            method: 'POST',
            body: formData
        });
        
        const data = await response.json();
        
        if (response.ok) {
            outputFilename = data.filename;
            startTime = Date.now();
            
            uploadSection.classList.add('hidden');
            processingSection.classList.remove('hidden');
            
            startProgressMonitoring();
            showToast('Processing started successfully', 'success');
        } else {
            showToast(data.error || 'Upload failed', 'error');
            analyzeBtn.disabled = false;
            analyzeBtn.innerHTML = '<span class="btn-icon">⚡</span><span class="btn-text">Start Analysis</span>';
        }
    } catch (error) {
        showToast('Network error: ' + error.message, 'error');
        analyzeBtn.disabled = false;
        analyzeBtn.innerHTML = '<span class="btn-icon">⚡</span><span class="btn-text">Start Analysis</span>';
    }
});

// ============================================================
// PROGRESS MONITORING (Real-time Updates)
// ============================================================

function startProgressMonitoring() {
    statusCheckInterval = setInterval(checkStatus, 500);
}

async function checkStatus() {
    try {
        const response = await fetch('/status');
        const status = await response.json();
        
        updateProgress(status);
        
        if (!status.is_processing && status.progress > 0 && !status.error) {
            clearInterval(statusCheckInterval);
            await showResults(status);
        }
        
        if (status.error) {
            clearInterval(statusCheckInterval);
            showError(status.error);
        }
        
    } catch (error) {
        console.error('Error checking status:', error);
    }
}

function updateProgress(status) {
    if (status.total > 0) {
        const percentage = Math.round((status.progress / status.total) * 100);
        
        document.getElementById('progressPercent').textContent = percentage + '%';
        const circle = document.getElementById('progressCircle');
        const circumference = 2 * Math.PI * 70;
        const offset = circumference - (percentage / 100) * circumference;
        circle.style.strokeDashoffset = offset;
        
        document.getElementById('progressCount').textContent = 
            `${status.progress.toLocaleString()} / ${status.total.toLocaleString()}`;
        
        document.getElementById('processingSpeed').textContent = 
            `${status.processing_speed || 0} reviews/sec`;
        
        if (status.eta_seconds > 0) {
            const minutes = Math.floor(status.eta_seconds / 60);
            const seconds = status.eta_seconds % 60;
            document.getElementById('etaTime').textContent = 
                minutes > 0 ? `${minutes}m ${seconds}s` : `${seconds}s`;
        }
        
        updateLiveCount('livePositive', status.positive_count);
        updateLiveCount('liveNegative', status.negative_count);
        updateLiveCount('liveNeutral', status.neutral_count);
    }
}

function updateLiveCount(elementId, newValue) {
    const element = document.getElementById(elementId);
    const currentValue = parseInt(element.textContent) || 0;
    
    if (newValue !== currentValue) {
        element.textContent = newValue.toLocaleString();
        element.style.transform = 'scale(1.2)';
        setTimeout(() => {
            element.style.transform = 'scale(1)';
        }, 200);
    }
}

// ============================================================
// RESULTS DISPLAY
// ============================================================

async function showResults(status) {
    processingSection.classList.add('hidden');
    resultsSection.classList.remove('hidden');
    
    const total = status.total;
    const positive = status.positive_count;
    const negative = status.negative_count;
    const neutral = status.neutral_count;
    
    const posPercent = (positive / total * 100).toFixed(1);
    const negPercent = (negative / total * 100).toFixed(1);
    const neuPercent = (neutral / total * 100).toFixed(1);
    
    const processingTime = ((Date.now() - startTime) / 1000).toFixed(1);
    const avgSpeed = (total / processingTime).toFixed(1);
    
    animateValue('positiveCount', positive);
    animateValue('negativeCount', negative);
    animateValue('neutralCount', neutral);
    animateValue('totalCount', total);
    
    document.getElementById('positivePercent').textContent = posPercent + '%';
    document.getElementById('negativePercent').textContent = negPercent + '%';
    document.getElementById('neutralPercent').textContent = neuPercent + '%';
    
    setTimeout(() => {
        document.getElementById('positiveBar').style.width = posPercent + '%';
        document.getElementById('negativeBar').style.width = negPercent + '%';
        document.getElementById('neutralBar').style.width = neuPercent + '%';
    }, 300);
    
    document.getElementById('processingTime').textContent = processingTime + 's';
    document.getElementById('avgSpeed').textContent = avgSpeed + '/s';
    
    document.getElementById('positiveFileCount').textContent = `${positive.toLocaleString()} reviews`;
    document.getElementById('negativeFileCount').textContent = `${negative.toLocaleString()} reviews`;
    document.getElementById('neutralFileCount').textContent = `${neutral.toLocaleString()} reviews`;
    
    // Generate AI-powered comprehensive report
    generateComprehensiveReport(status);
    
    allComments = status.all_comments || [];
    
    setupDownloadButtons();
    setupCommentReviewButton();
    
    await createCharts(status);
    
    showToast('Analysis complete!', 'success');
}

// ============================================================
// COMPREHENSIVE ANALYSIS REPORT GENERATION
// ============================================================


async function generateComprehensiveReport(status) {
    const summaryElement = document.getElementById('detailedSummary');
    summaryElement.innerHTML = `
        <div style="text-align: center; padding: 2rem;">
            <div class="loading-spinner"></div>
            <p style="margin-top: 1rem; color: var(--text-secondary);">Generating comprehensive analysis report...</p>
        </div>
    `;
    
    try {
        const total = status.total;
        const positive = status.positive_count;
        const negative = status.negative_count;
        const neutral = status.neutral_count;
        
        const posPercent = (positive / total * 100).toFixed(1);
        const negPercent = (negative / total * 100).toFixed(1);
        const neuPercent = (neutral / total * 100).toFixed(1);
        
        // Get top keywords
        const topPosKeywords = status.top_keywords?.positive?.slice(0, 5).map(k => k.word).join(', ') || 'various aspects';
        const topNegKeywords = status.top_keywords?.negative?.slice(0, 5).map(k => k.word).join(', ') || 'various aspects';
        
        const prompt = `You are a professional business analyst. Create a comprehensive sentiment analysis report.

DATA:
- Total Reviews: ${total}
- Positive: ${positive} (${posPercent}%)
- Negative: ${negative} (${negPercent}%)
- Neutral: ${neutral} (${neuPercent}%)
- Top Positive Keywords: ${topPosKeywords}
- Top Negative Keywords: ${topNegKeywords}

Write a professional analysis report (400-500 words) with EXACTLY these 5 sections:

SECTION 1 - Dataset Overview
Start with "Our analysis of ${total.toLocaleString()} customer reviews reveals..."
Describe the overall sentiment distribution and what it means

SECTION 2 - Positive Insights
Start with "The ${posPercent}% positive feedback highlights..."
Discuss what customers appreciate (keywords: ${topPosKeywords})
Explain the competitive advantages

SECTION 3 - Areas of Concern  
Start with "The ${negPercent}% negative reviews indicate..."
Discuss customer complaints (keywords: ${topNegKeywords})
Explain the critical issues

SECTION 4 - Neutral Zone Analysis
Start with "The ${neuPercent}% neutral reviews suggest..."
Discuss opportunities for improvement

SECTION 5 - Strategic Recommendations
Start with "Based on this analysis, we recommend..."
Provide 3-4 clear actionable steps

IMPORTANT FORMATTING:
- Start each section on a new line
- Keep sections clearly separated
- Use professional, executive language
- Each section should be 80-120 words
- Total length: 400-500 words

Write the report now:`;

        const report = await callSummaryAPI(prompt, 800);
        
        // Format the report with proper structure
        summaryElement.innerHTML = formatComprehensiveReport(report);
        
    } catch (error) {
        console.error('Report generation error:', error);
        summaryElement.innerHTML = generateBasicReport(status);
        showToast('Could not generate AI report, showing basic summary', 'info');
    }
}

function formatComprehensiveReport(report) {
    // Split into sections and format
    let formattedReport = report;
    
    // Add section headers with styling
    formattedReport = formattedReport
        .replace(/(SECTION 1 - Dataset Overview|Dataset Overview)/gi, '<h3 style="color: var(--accent-primary); margin-top: 1.5rem; margin-bottom: 0.75rem; font-size: 1.2rem; font-weight: 600;">📊 Dataset Overview</h3>')
        .replace(/(SECTION 2 - Positive Insights|Positive Insights)/gi, '<h3 style="color: var(--positive); margin-top: 1.5rem; margin-bottom: 0.75rem; font-size: 1.2rem; font-weight: 600;">✅ Positive Insights</h3>')
        .replace(/(SECTION 3 - Areas of Concern|Areas of Concern)/gi, '<h3 style="color: var(--negative); margin-top: 1.5rem; margin-bottom: 0.75rem; font-size: 1.2rem; font-weight: 600;">⚠️ Areas of Concern</h3>')
        .replace(/(SECTION 4 - Neutral Zone Analysis|Neutral Zone Analysis)/gi, '<h3 style="color: var(--neutral); margin-top: 1.5rem; margin-bottom: 0.75rem; font-size: 1.2rem; font-weight: 600;">⚖️ Neutral Zone Analysis</h3>')
        .replace(/(SECTION 5 - Strategic Recommendations|Strategic Recommendations)/gi, '<h3 style="color: var(--accent-secondary); margin-top: 1.5rem; margin-bottom: 0.75rem; font-size: 1.2rem; font-weight: 600;">🎯 Strategic Recommendations</h3>');
    
    // Format paragraphs
    formattedReport = formattedReport
        .replace(/\n\n+/g, '</p><p style="margin-bottom: 1rem; line-height: 1.8;">')
        .replace(/\n/g, '<br>');
    
    // Wrap in paragraph tags
    formattedReport = `<p style="margin-bottom: 1rem; line-height: 1.8;">${formattedReport}</p>`;
    
    return formattedReport;
}

function generateBasicReport(status) {
    const total = status.total;
    const positive = status.positive_count;
    const negative = status.negative_count;
    const neutral = status.neutral_count;
    
    const posPercent = (positive / total * 100).toFixed(1);
    const negPercent = (negative / total * 100).toFixed(1);
    const neuPercent = (neutral / total * 100).toFixed(1);
    
    return `
        <h3 style="color: var(--accent-primary); margin-bottom: 1rem; font-size: 1.2rem;">📊 Analysis Summary</h3>
        <p style="margin-bottom: 1rem; line-height: 1.8;">
            Analysis of <strong>${total.toLocaleString()}</strong> customer reviews reveals 
            <strong style="color: var(--positive);">${positive.toLocaleString()} positive (${posPercent}%)</strong>, 
            <strong style="color: var(--negative);">${negative.toLocaleString()} negative (${negPercent}%)</strong>, and 
            <strong style="color: var(--neutral);">${neutral.toLocaleString()} neutral (${neuPercent}%)</strong> reviews.
        </p>
        <p style="margin-bottom: 1rem; line-height: 1.8; color: var(--text-secondary);">
            <em>AI-powered detailed analysis temporarily unavailable. Please check the charts below for visual insights.</em>
        </p>
    `;
}

function setupDownloadButtons() {
    // Existing Excel download buttons
    document.getElementById('downloadComplete').onclick = () => {
        window.location.href = `/download/${outputFilename}`;
        showToast('Downloading complete analysis', 'success');
    };
    
    document.getElementById('downloadPositive').onclick = () => {
        window.location.href = `/download/${outputFilename.replace('.xlsx', '_positive.xlsx')}`;
        showToast('Downloading positive reviews', 'success');
    };
    
    document.getElementById('downloadNegative').onclick = () => {
        window.location.href = `/download/${outputFilename.replace('.xlsx', '_negative.xlsx')}`;
        showToast('Downloading negative reviews', 'success');
    };
    
    document.getElementById('downloadNeutral').onclick = () => {
        window.location.href = `/download/${outputFilename.replace('.xlsx', '_neutral.xlsx')}`;
        showToast('Downloading neutral reviews', 'success');
    };
    
    // NEW: PDF download buttons
    document.getElementById('downloadPdfExecutive').onclick = () => {
        showToast('Generating executive summary PDF...', 'info');
        window.location.href = '/generate-pdf-executive';
        setTimeout(() => {
            showToast('Executive summary downloaded!', 'success');
        }, 2000);
    };
    
    // Find this part in setupDownloadButtons():
document.getElementById('downloadPdfDetailed').onclick = () => {
    // Show warning that it takes time
    if (confirm('⏰ This will generate a comprehensive report with AI summaries for positive and negative reviews.\n\nThis may take 2-3 minutes. Continue?')) {
        showToast('Generating detailed report with AI summaries... This may take 2-3 minutes', 'info');
        
        // Disable button to prevent multiple clicks
        const btn = document.getElementById('downloadPdfDetailed');
        const originalText = btn.innerHTML;
        btn.disabled = true;
        btn.innerHTML = '<span class="spinner"></span> Generating AI Report...';
        
        window.location.href = '/generate-pdf-detailed';
        
        // Re-enable button after 3 minutes
        setTimeout(() => {
            btn.disabled = false;
            btn.innerHTML = originalText;
            showToast('Detailed report downloaded!', 'success');
        }, 180000); // 3 minutes
    }
};
}

// ============================================================
// COMMENT REVIEW MODAL - FIXED
// ============================================================

function setupCommentReviewButton() {
    const viewCommentsBtn = document.getElementById('viewCommentsBtn');
    viewCommentsBtn.onclick = openCommentModal;
}

function openCommentModal() {
    const modal = document.getElementById('commentModal');
    modal.classList.remove('hidden');
    currentPage = 1;
    loadComments(1);
}

function closeCommentModal() {
    const modal = document.getElementById('commentModal');
    modal.classList.add('hidden');
}

async function loadComments(page) {
    try {
        const response = await fetch(`/api/comments?page=${page}`);
        const data = await response.json();
        
        if (data.comments) {
            displayComments(data.comments);
            setupPagination(data.page, data.total_pages);
            currentPage = data.page;
            totalPages = data.total_pages;
        }
    } catch (error) {
        console.error('Error loading comments:', error);
        showToast('Failed to load comments', 'error');
    }
}

function displayComments(comments) {
    const tbody = document.getElementById('commentsTableBody');
    tbody.innerHTML = '';
    
    comments.forEach(comment => {
        const tr = document.createElement('tr');
        
        // Create cells
        const numberCell = document.createElement('td');
        numberCell.innerHTML = `<span class="comment-number">${comment.id}</span>`;
        
        const commentCell = document.createElement('td');
        const commentDiv = document.createElement('div');
        commentDiv.className = 'comment-text';
        commentDiv.textContent = comment.comment;
        commentCell.appendChild(commentDiv);
        
        const sentimentCell = document.createElement('td');
        sentimentCell.innerHTML = `<span class="sentiment-badge ${comment.sentiment}">${comment.sentiment.toUpperCase()}</span>`;
        
        const actionCell = document.createElement('td');
        const summarizeBtn = document.createElement('button');
        summarizeBtn.className = 'btn-summarize';
        summarizeBtn.textContent = '🤖 Summarize';
        
        // Store data attributes instead of using onclick with parameters
        summarizeBtn.dataset.commentId = comment.id;
        summarizeBtn.dataset.sentiment = comment.sentiment;
        summarizeBtn.dataset.confidence = comment.confidence;
        summarizeBtn.dataset.comment = comment.comment;
        
        // Use addEventListener instead of onclick
        summarizeBtn.addEventListener('click', function() {
            const id = this.dataset.commentId;
            const commentText = this.dataset.comment;
            const sentiment = this.dataset.sentiment;
            const confidence = parseFloat(this.dataset.confidence);
            summarizeComment(id, commentText, sentiment, confidence);
        });
        
        actionCell.appendChild(summarizeBtn);
        
        tr.appendChild(numberCell);
        tr.appendChild(commentCell);
        tr.appendChild(sentimentCell);
        tr.appendChild(actionCell);
        
        tbody.appendChild(tr);
    });
}

function setupPagination(currentPage, totalPages) {
    const paginationNumbers = document.getElementById('paginationNumbers');
    paginationNumbers.innerHTML = '';
    
    document.getElementById('prevPage').disabled = currentPage === 1;
    document.getElementById('nextPage').disabled = currentPage === totalPages;
    
    const maxVisible = 7;
    let startPage = Math.max(1, currentPage - Math.floor(maxVisible / 2));
    let endPage = Math.min(totalPages, startPage + maxVisible - 1);
    
    if (endPage - startPage < maxVisible - 1) {
        startPage = Math.max(1, endPage - maxVisible + 1);
    }
    
    if (startPage > 1) {
        addPageNumber(1);
        if (startPage > 2) {
            addEllipsis();
        }
    }
    
    for (let i = startPage; i <= endPage; i++) {
        addPageNumber(i, i === currentPage);
    }
    
    if (endPage < totalPages) {
        if (endPage < totalPages - 1) {
            addEllipsis();
        }
        addPageNumber(totalPages);
    }
}

function addPageNumber(pageNum, isActive = false) {
    const paginationNumbers = document.getElementById('paginationNumbers');
    const pageBtn = document.createElement('button');
    pageBtn.className = 'page-number' + (isActive ? ' active' : '');
    pageBtn.textContent = pageNum;
    pageBtn.onclick = () => loadComments(pageNum);
    paginationNumbers.appendChild(pageBtn);
}

function addEllipsis() {
    const paginationNumbers = document.getElementById('paginationNumbers');
    const ellipsis = document.createElement('span');
    ellipsis.className = 'page-ellipsis';
    ellipsis.textContent = '...';
    paginationNumbers.appendChild(ellipsis);
}

function changePage(direction) {
    const newPage = currentPage + direction;
    if (newPage >= 1 && newPage <= totalPages) {
        loadComments(newPage);
    }
}

// ============================================================
// COMMENT SUMMARIZATION - FIXED
// ============================================================

async function summarizeComment(id, comment, sentiment, confidence) {
    const modal = document.getElementById('summaryModal');
    const loadingDiv = document.getElementById('summaryLoading');
    const resultDiv = document.getElementById('summaryResult');
    
    console.log('Summarizing comment:', { id, sentiment, confidence, length: comment.length });
    
    modal.classList.remove('hidden');
    
    document.getElementById('summaryOriginalComment').textContent = comment;
    document.getElementById('summarySentiment').textContent = sentiment.toUpperCase();
    document.getElementById('summarySentiment').className = `sentiment-badge ${sentiment}`;
    document.getElementById('summaryConfidence').textContent = `Confidence: ${(confidence * 100).toFixed(1)}%`;
    
    loadingDiv.classList.remove('hidden');
    resultDiv.classList.add('hidden');
    
    try {
        const response = await fetch('/api/summarize', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                comment: comment,
                sentiment: sentiment,
                confidence: confidence
            })
        });
        
        const data = await response.json();
        
        if (response.ok && data.success) {
            const analysisContent = document.getElementById('aiAnalysisContent');
            analysisContent.innerHTML = formatAnalysis(data.summary);
            
            loadingDiv.classList.add('hidden');
            resultDiv.classList.remove('hidden');
            
            console.log('✓ Summary generated successfully');
        } else {
            throw new Error(data.error || 'Summarization failed');
        }
    } catch (error) {
        console.error('Summarization error:', error);
        showToast('Failed to generate summary: ' + error.message, 'error');
        closeSummaryModal();
    }
}

function formatAnalysis(text) {
    let html = text
        .replace(/\n\n/g, '</p><p>')
        .replace(/\n/g, '<br>')
        .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
        .replace(/^(\d+\.)/gm, '<br><strong>$1</strong>');
    
    return `<p>${html}</p>`;
}

function closeSummaryModal() {
    const modal = document.getElementById('summaryModal');
    modal.classList.add('hidden');
}

document.getElementById('commentModal').addEventListener('click', (e) => {
    if (e.target.id === 'commentModal') {
        closeCommentModal();
    }
});

document.getElementById('summaryModal').addEventListener('click', (e) => {
    if (e.target.id === 'summaryModal') {
        closeSummaryModal();
    }
});

// ============================================================
// CHARTS CREATION
// ============================================================

async function createCharts(status) {
    const svg = document.querySelector('.progress-ring');
    if (!svg.querySelector('#progressGradient')) {
        const defs = document.createElementNS('http://www.w3.org/2000/svg', 'defs');
        defs.innerHTML = `
            <linearGradient id="progressGradient" x1="0%" y1="0%" x2="100%" y2="100%">
                <stop offset="0%" style="stop-color:#667eea;stop-opacity:1" />
                <stop offset="100%" style="stop-color:#764ba2;stop-opacity:1" />
            </linearGradient>
        `;
        svg.insertBefore(defs, svg.firstChild);
    }
    
    createSentimentChart(status);
    createTimelineChart(status);
    createConfidenceChart(status);
    createKeywordsChart(status, 'positive');
    
    document.querySelectorAll('.filter-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            document.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            createKeywordsChart(status, btn.dataset.sentiment);
        });
    });
}

function createSentimentChart(status) {
    const ctx = document.getElementById('sentimentChart').getContext('2d');
    
    if (charts.sentiment) charts.sentiment.destroy();
    
    charts.sentiment = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: ['Positive', 'Negative', 'Neutral'],
            datasets: [{
                data: [status.positive_count, status.negative_count, status.neutral_count],
                backgroundColor: ['#10b981', '#ef4444', '#f59e0b'],
                borderWidth: 0,
                hoverOffset: 10
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'bottom',
                    labels: {
                        color: '#a0a0a0',
                        padding: 20,
                        font: { size: 13, weight: '600' }
                    }
                },
                tooltip: {
                    backgroundColor: '#1a1a1a',
                    titleColor: '#ffffff',
                    bodyColor: '#a0a0a0',
                    borderColor: '#2a2a2a',
                    borderWidth: 1,
                    padding: 12,
                    displayColors: false
                }
            }
        }
    });
}

function createTimelineChart(status) {
    const ctx = document.getElementById('timelineChart').getContext('2d');
    
    if (charts.timeline) charts.timeline.destroy();
    
    const timeline = status.sentiment_timeline || [];
    const step = Math.max(1, Math.floor(timeline.length / 50));
    const sampledData = timeline.filter((_, i) => i % step === 0);
    
    const positiveData = [];
    const negativeData = [];
    const neutralData = [];
    
    sampledData.forEach(point => {
        if (point.sentiment === 'positive') {
            positiveData.push(point.row);
            negativeData.push(null);
            neutralData.push(null);
        } else if (point.sentiment === 'negative') {
            positiveData.push(null);
            negativeData.push(point.row);
            neutralData.push(null);
        } else {
            positiveData.push(null);
            negativeData.push(null);
            neutralData.push(point.row);
        }
    });
    
    charts.timeline = new Chart(ctx, {
        type: 'line',
        data: {
            labels: sampledData.map(p => p.row),
            datasets: [
                {
                    label: 'Positive',
                    data: positiveData,
                    borderColor: '#10b981',
                    backgroundColor: 'rgba(16, 185, 129, 0.1)',
                    pointRadius: 3,
                    pointHoverRadius: 6,
                    borderWidth: 2,
                    tension: 0.4
                },
                {
                    label: 'Negative',
                    data: negativeData,
                    borderColor: '#ef4444',
                    backgroundColor: 'rgba(239, 68, 68, 0.1)',
                    pointRadius: 3,
                    pointHoverRadius: 6,
                    borderWidth: 2,
                    tension: 0.4
                },
                {
                    label: 'Neutral',
                    data: neutralData,
                    borderColor: '#f59e0b',
                    backgroundColor: 'rgba(245, 158, 11, 0.1)',
                    pointRadius: 3,
                    pointHoverRadius: 6,
                    borderWidth: 2,
                    tension: 0.4
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                x: {
                    title: { display: true, text: 'Review Number', color: '#a0a0a0' },
                    ticks: { color: '#6b6b6b' },
                    grid: { color: '#2a2a2a' }
                },
                y: {
                    title: { display: true, text: 'Row Index', color: '#a0a0a0' },
                    ticks: { color: '#6b6b6b' },
                    grid: { color: '#2a2a2a' }
                }
            },
            plugins: {
                legend: {
                    position: 'bottom',
                    labels: {
                        color: '#a0a0a0',
                        padding: 15,
                        font: { size: 12, weight: '600' }
                    }
                },
                tooltip: {
                    backgroundColor: '#1a1a1a',
                    titleColor: '#ffffff',
                    bodyColor: '#a0a0a0',
                    borderColor: '#2a2a2a',
                    borderWidth: 1,
                    padding: 12
                }
            }
        }
    });
}

function createConfidenceChart(status) {
    const ctx = document.getElementById('confidenceChart').getContext('2d');
    
    if (charts.confidence) charts.confidence.destroy();
    
    const distribution = status.confidence_distribution || [0,0,0,0,0,0,0,0,0,0];
    
    charts.confidence = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: ['0-10%', '10-20%', '20-30%', '30-40%', '40-50%', '50-60%', '60-70%', '70-80%', '80-90%', '90-100%'],
            datasets: [{
                label: 'Number of Reviews',
                data: distribution,
                backgroundColor: distribution.map((_, i) => {
                    const intensity = i / 9;
                    const r = Math.round(102 + (118 - 102) * intensity);
                    const g = Math.round(126 + (75 - 126) * intensity);
                    const b = Math.round(234 + (162 - 234) * intensity);
                    return `rgb(${r}, ${g}, ${b})`;
                }),
                borderWidth: 0,
                borderRadius: 8
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                x: {
                    title: { display: true, text: 'Confidence Level', color: '#a0a0a0' },
                    ticks: { color: '#6b6b6b', maxRotation: 45, minRotation: 45 },
                    grid: { display: false }
                },
                y: {
                    title: { display: true, text: 'Count', color: '#a0a0a0' },
                    ticks: { color: '#6b6b6b' },
                    grid: { color: '#2a2a2a' }
                }
            },
            plugins: {
                legend: {
                    display: false
                },
                tooltip: {
                    backgroundColor: '#1a1a1a',
                    titleColor: '#ffffff',
                    bodyColor: '#a0a0a0',
                    borderColor: '#2a2a2a',
                    borderWidth: 1,
                    padding: 12
                }
            }
        }
    });
}

function createKeywordsChart(status, sentiment) {
    const ctx = document.getElementById('keywordsChart').getContext('2d');
    
    if (charts.keywords) charts.keywords.destroy();
    
    const keywords = status.top_keywords?.[sentiment] || [];
    const labels = keywords.map(k => k.word);
    const data = keywords.map(k => k.count);
    
    const colors = {
        positive: '#10b981',
        negative: '#ef4444',
        neutral: '#f59e0b'
    };
    
    charts.keywords = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{
                label: 'Frequency',
                data: data,
                backgroundColor: colors[sentiment],
                borderWidth: 0,
                borderRadius: 8
            }]
        },
        options: {
            indexAxis: 'y',
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                x: {
                    title: { display: true, text: 'Mentions', color: '#a0a0a0' },
                    ticks: { color: '#6b6b6b' },
                    grid: { color: '#2a2a2a' }
                },
                y: {
                    ticks: { color: '#6b6b6b' },
                    grid: { display: false }
                }
            },
            plugins: {
                legend: {
                    display: false
                },
                tooltip: {
                    backgroundColor: '#1a1a1a',
                    titleColor: '#ffffff',
                    bodyColor: '#a0a0a0',
                    borderColor: '#2a2a2a',
                    borderWidth: 1,
                    padding: 12
                }
            }
        }
    });
}

// ============================================================
// CHART EXPORT
// ============================================================

async function exportChart(chartId) {
    const canvas = document.getElementById(chartId);
    const container = canvas.parentElement;
    
    try {
        const dataUrl = await html2canvas(container, {
            backgroundColor: '#1a1a1a',
            scale: 2
        }).then(canvas => canvas.toDataURL('image/png'));
        
        const link = document.createElement('a');
        link.download = `${chartId}_${Date.now()}.png`;
        link.href = dataUrl;
        link.click();
        
        showToast('Chart exported successfully', 'success');
    } catch (error) {
        showToast('Export failed: ' + error.message, 'error');
    }
}

// ============================================================
// UTILITIES
// ============================================================

function animateValue(elementId, endValue, duration = 1500) {
    const element = document.getElementById(elementId);
    const startValue = 0;
    const startTime = performance.now();
    
    function update(currentTime) {
        const elapsed = currentTime - startTime;
        const progress = Math.min(elapsed / duration, 1);
        
        const easeOutQuart = 1 - Math.pow(1 - progress, 4);
        const current = Math.floor(startValue + (endValue - startValue) * easeOutQuart);
        
        element.textContent = current.toLocaleString();
        
        if (progress < 1) {
            requestAnimationFrame(update);
        } else {
            element.textContent = endValue.toLocaleString();
        }
    }
    
    requestAnimationFrame(update);
}

function showToast(message, type = 'info') {
    const toast = document.getElementById('toast');
    const toastIcon = document.getElementById('toastIcon');
    const toastMessage = document.getElementById('toastMessage');
    
    const icons = {
        success: '✓',
        error: '✕',
        info: 'ℹ'
    };
    
    toastIcon.textContent = icons[type] || icons.info;
    toastMessage.textContent = message;
    
    toast.classList.remove('hidden');
    
    setTimeout(() => {
        toast.classList.add('hidden');
    }, 3000);
}

function showError(message) {
    uploadSection.classList.add('hidden');
    processingSection.classList.add('hidden');
    resultsSection.classList.add('hidden');
    errorSection.classList.remove('hidden');
    
    document.getElementById('errorMessage').textContent = message;
}

function copySummary() {
    const summary = document.getElementById('detailedSummary').textContent;
    
    navigator.clipboard.writeText(summary).then(() => {
        showToast('Summary copied to clipboard', 'success');
    }).catch(() => {
        showToast('Failed to copy summary', 'error');
    });
}

// ============================================================
// BATCH SUMMARY GENERATION
// ============================================================

let batchSummaryInProgress = false;

document.getElementById('generateBatchSummary').addEventListener('click', async () => {
    if (batchSummaryInProgress) {
        showToast('Summary generation already in progress', 'info');
        return;
    }

    const sentiment = document.getElementById('sentimentSelect').value;
    
    // Filter comments by selected sentiment
    const filteredComments = allComments.filter(c => c.sentiment === sentiment);
    
    if (filteredComments.length === 0) {
        showToast(`No ${sentiment} reviews found`, 'error');
        return;
    }

    await generateBatchSummary(sentiment, filteredComments);
});

async function generateBatchSummary(sentiment, comments) {
    batchSummaryInProgress = true;
    
    const generateBtn = document.getElementById('generateBatchSummary');
    generateBtn.disabled = true;
    generateBtn.innerHTML = '<span class="spinner"></span> Processing...';
    
    const progressContainer = document.getElementById('batchProgressContainer');
    const summaryBox = document.getElementById('generatedSummaryBox');
    
    progressContainer.classList.remove('hidden');
    summaryBox.classList.add('hidden');
    
    // OPTIMIZED: Process in 3 rounds with fewer comments per batch
    const COMMENTS_PER_ROUND = Math.ceil(comments.length / 3); // Divide into 3 parts
    const MAX_COMMENT_LENGTH = 100; // Shorter comments
    
    let roundSummaries = [];
    const startTime = Date.now();
    
    try {
        // Process in 3 rounds
        for (let round = 0; round < 3; round++) {
            const roundStart = round * COMMENTS_PER_ROUND;
            const roundEnd = Math.min(roundStart + COMMENTS_PER_ROUND, comments.length);
            const roundComments = comments.slice(roundStart, roundEnd);
            
            updateBatchProgress(round + 1, 3, 'processing', startTime);
            
            // Take only first 100 chars from each comment
            const roundTexts = roundComments
                .slice(0, 15) // Maximum 15 comments per round
                .map(c => {
                    const text = c.comment.trim();
                    return text.length > MAX_COMMENT_LENGTH 
                        ? text.substring(0, MAX_COMMENT_LENGTH) + '...'
                        : text;
                })
                .join('\n---\n');
            
            const roundSummary = await generateRoundSummary(roundTexts, sentiment, roundComments.length);
            roundSummaries.push(roundSummary);
            
            // Delay between rounds
            await new Promise(resolve => setTimeout(resolve, 200));
        }
        
        // Final comprehensive summary
        updateBatchProgress(3, 3, 'finalizing', startTime);
        
        const finalSummary = await generateFinalSummary(roundSummaries, sentiment, comments.length);
        
        displayBatchSummary(finalSummary, sentiment);
        
        showToast('Summary generated successfully!', 'success');
        
    } catch (error) {
        console.error('Batch summary error:', error);
        showToast('Failed to generate summary: ' + error.message, 'error');
    } finally {
        batchSummaryInProgress = false;
        generateBtn.disabled = false;
        generateBtn.innerHTML = `
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M12 2L2 7l10 5 10-5-10-5z"/>
                <path d="M2 17l10 5 10-5"/>
                <path d="M2 12l10 5 10-5"/>
            </svg>
            Generate Summary
        `;
        progressContainer.classList.add('hidden');
    }
}

async function generateRoundSummary(roundTexts, sentiment, commentCount) {
    const prompt = `You are analyzing ${commentCount} customer ${sentiment} reviews. Sample excerpts:

${roundTexts}

Write exactly 2 sentences (max 50 words) summarizing the main theme.

Focus: ${sentiment === 'positive' ? 'what customers love' : 'main complaints'}

Summary:`;

    const response = await callSummaryAPI(prompt, 100);
    return response.trim();
}

async function generateFinalSummary(roundSummaries, sentiment, totalCount) {
    const allSummaries = roundSummaries.map((s, i) => `Section ${i + 1}: ${s}`).join('\n\n');
    
    const prompt = `Create an executive summary of ${totalCount} ${sentiment.toUpperCase()} customer reviews.

Section insights:
${allSummaries}

Write a structured report (350-450 words) with EXACTLY these 4 sections:

OVERVIEW (80 words)
Start with: "Analysis of ${totalCount} ${sentiment} reviews reveals..."
${sentiment === 'positive' ? 'Describe satisfaction levels and what customers appreciate' : 'Describe dissatisfaction patterns and main complaints'}

KEY THEMES (150 words)
Start with: "Three dominant patterns emerge from the feedback..."
List 3-4 specific themes from the section insights above
${sentiment === 'positive' ? 'What customers consistently praise with examples' : 'What customers consistently complain about with examples'}

CRITICAL INSIGHTS (70 words)
Start with: "The most important takeaway is..."
${sentiment === 'positive' ? 'Competitive advantages and unique strengths' : 'Critical issues requiring immediate action'}

RECOMMENDATIONS (50 words)
Start with: "Based on this analysis..."
${sentiment === 'positive' ? '2-3 ways to leverage these strengths' : '2-3 actionable steps to address concerns'}

FORMATTING RULES:
- Clearly separate each section
- Use professional business language
- Write in clear paragraphs (NO bullet points)
- Total: 350-450 words

Write the executive summary:`;

    const response = await callSummaryAPI(prompt, 700);
    return response.trim();
}

async function callSummaryAPI(prompt, maxTokens) {
    const response = await fetch('/api/batch-summarize', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            prompt: prompt,
            max_tokens: maxTokens
        })
    });
    
    if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.error || `API returned status ${response.status}`);
    }
    
    const data = await response.json();
    
    if (!data.success) {
        throw new Error(data.error || 'Unknown error occurred');
    }
    
    return data.summary || '';
}

function updateBatchProgress(current, total, phase, startTime) {
    const percentage = Math.round((current / total) * 100);
    
    document.getElementById('batchProcessed').textContent = current;
    document.getElementById('batchTotal').textContent = total;
    document.getElementById('batchProgressFill').style.width = percentage + '%';
    
    const elapsed = (Date.now() - startTime) / 1000;
    const eta = current < total ? Math.round((elapsed / current) * (total - current)) : 0;
    
    if (eta > 0) {
        const minutes = Math.floor(eta / 60);
        const seconds = eta % 60;
        document.getElementById('batchETA').textContent = 
            minutes > 0 ? `${minutes}m ${seconds}s` : `${seconds}s`;
    } else {
        document.getElementById('batchETA').textContent = 'Finishing...';
    }
    
    const statusText = phase === 'processing' 
        ? `Analyzing section ${current} of ${total}...`
        : 'Creating final comprehensive summary...';
    
    document.getElementById('batchStatusText').textContent = statusText;
}

function displayBatchSummary(summary, sentiment) {
    const summaryBox = document.getElementById('generatedSummaryBox');
    const summaryText = document.getElementById('generatedSummaryText');
    const badge = document.getElementById('summaryTypeBadge');
    
    // Format the summary with proper structure
    let formattedSummary = summary;
    
    // Add section styling based on keywords
    formattedSummary = formattedSummary
        .replace(/(OVERVIEW|Overview)/gi, '<h3 style="color: var(--accent-primary); margin-top: 1.5rem; margin-bottom: 0.75rem; font-size: 1.15rem; font-weight: 600;">📋 Overview</h3>')
        .replace(/(KEY THEMES|Key Themes)/gi, '<h3 style="color: ' + (sentiment === 'positive' ? 'var(--positive)' : 'var(--negative)') + '; margin-top: 1.5rem; margin-bottom: 0.75rem; font-size: 1.15rem; font-weight: 600;">🔍 Key Themes</h3>')
        .replace(/(CRITICAL INSIGHTS|Critical Insights)/gi, '<h3 style="color: var(--accent-secondary); margin-top: 1.5rem; margin-bottom: 0.75rem; font-size: 1.15rem; font-weight: 600;">💡 Critical Insights</h3>')
        .replace(/(RECOMMENDATIONS|Recommendations)/gi, '<h3 style="color: var(--neutral); margin-top: 1.5rem; margin-bottom: 0.75rem; font-size: 1.15rem; font-weight: 600;">🎯 Recommendations</h3>');
    
    // Format paragraphs
    formattedSummary = formattedSummary
        .replace(/\n\n+/g, '</p><p style="margin-bottom: 1rem; line-height: 1.8; color: var(--text-secondary);">')
        .replace(/\n/g, '<br>');
    
    // Wrap in paragraph tags
    formattedSummary = `<p style="margin-bottom: 1rem; line-height: 1.8; color: var(--text-secondary);">${formattedSummary}</p>`;
    
    summaryText.innerHTML = formattedSummary;
    
    badge.textContent = sentiment === 'positive' ? '😊 Positive Summary' : '😞 Negative Summary';
    badge.className = `summary-type-badge ${sentiment}`;
    
    summaryBox.classList.remove('hidden');
    summaryBox.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
}

function copyBatchSummary() {
    const summary = document.getElementById('generatedSummaryText').textContent;
    
    navigator.clipboard.writeText(summary).then(() => {
        showToast('Summary copied to clipboard', 'success');
    }).catch(() => {
        showToast('Failed to copy summary', 'error');
    });
}

function downloadBatchSummary() {
    const summary = document.getElementById('generatedSummaryText').textContent;
    const sentiment = document.getElementById('sentimentSelect').value;
    const timestamp = new Date().toISOString().slice(0, 19).replace(/:/g, '-');
    
    const blob = new Blob([summary], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    
    link.download = `${sentiment}_summary_${timestamp}.txt`;
    link.href = url;
    link.click();
    
    URL.revokeObjectURL(url);
    showToast('Summary downloaded', 'success');
}

// ============================================================
// INITIALIZATION
// ============================================================

console.log('%c🚀 Sentiment Analysis Pro', 'font-size: 20px; font-weight: bold; color: #667eea;');
console.log('%cPremium Edition - GPU Accelerated', 'font-size: 14px; color: #764ba2;');
console.log('');
console.log('Ready to analyze your data!');

fetch('/status')
    .then(r => r.json())
    .then(data => {
        console.log('✓ Backend connected');
    })
    .catch(() => {
        console.warn('⚠ Backend not responding');
    });
