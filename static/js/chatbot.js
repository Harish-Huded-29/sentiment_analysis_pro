/**
 * AI CHATBOT FOR SENTIMENT ANALYSIS
 * Provides intelligent insights based on sentiment data
 */

let chatbotOpen = false;
let currentSentiment = 'negative';
let sentimentBriefSummary = null;
let chatHistory = [];

// DOM Elements
const chatFab = document.getElementById('chatFab');
const chatbotContainer = document.getElementById('chatbotContainer');
const chatbotClose = document.getElementById('chatbotClose');
const chatbotSentimentSelect = document.getElementById('chatbotSentimentSelect');
const chatbotMessages = document.getElementById('chatbotMessages');
const chatbotInput = document.getElementById('chatbotInput');
const chatbotSend = document.getElementById('chatbotSend');
const summaryLoadingOverlay = document.getElementById('summaryLoadingOverlay');

// ============================================================
// CHATBOT TOGGLE
// ============================================================

chatFab.addEventListener('click', openChatbot);
chatbotClose.addEventListener('click', closeChatbot);

function openChatbot() {
    if (!allComments || allComments.length === 0) {
        showToast('Please complete an analysis first before using the chatbot', 'info');
        return;
    }

    chatbotOpen = true;
    chatFab.classList.add('hidden');
    chatbotContainer.classList.remove('hidden');
    
    // Initialize chatbot if first time
    if (chatHistory.length === 0) {
        initializeChatbot();
    }
}

function closeChatbot() {
    chatbotOpen = false;
    chatFab.classList.remove('hidden');
    chatbotContainer.classList.add('hidden');
}

// ============================================================
// CHATBOT INITIALIZATION
// ============================================================

async function initializeChatbot() {
    // Show welcome message
    addWelcomeMessage();
    
    // Load initial sentiment summary
    await loadSentimentSummary(currentSentiment);
}

function addWelcomeMessage() {
    const welcomeHTML = `
        <div class="chat-message bot">
            <div class="message-avatar bot">🤖</div>
            <div class="message-content bot welcome-message">
                <h4>👋 Welcome to AI Insights!</h4>
                <p>I'm your intelligent assistant for sentiment analysis. I can help you navigate the app and answer questions about your reviews!</p>
                
                <p style="margin-top: 0.75rem; font-size: 0.9rem;">
                    <strong>🎯 Smart Navigation - Try saying:</strong><br>
                    • "Generate a negative summary"<br>
                    • "Show me individual comment analysis"<br>
                    • "Take me to downloads"<br>
                    • "Create a positive summary"
                </p>
                
                <p style="margin-top: 0.75rem; font-size: 0.9rem;">
                    <strong>💡 Analysis Questions:</strong><br>
                    • "What can I improve?"<br>
                    • "What are the main complaints?"<br>
                    • "Give me 3 action items"
                </p>
            </div>
        </div>
    `;
    
    chatbotMessages.innerHTML = welcomeHTML;
    chatHistory.push({ role: 'bot', content: 'Welcome message', type: 'welcome' });
}

// ============================================================
// SENTIMENT SUMMARY LOADING
// ============================================================

chatbotSentimentSelect.addEventListener('change', async (e) => {
    currentSentiment = e.target.value;
    await loadSentimentSummary(currentSentiment);
});

async function loadSentimentSummary(sentiment) {
    // Show loading overlay
    summaryLoadingOverlay.classList.remove('hidden');
    
    try {
        // Filter comments by sentiment
        const filteredComments = allComments.filter(c => c.sentiment === sentiment);
        
        if (filteredComments.length === 0) {
            sentimentBriefSummary = `No ${sentiment} reviews found in the dataset.`;
            summaryLoadingOverlay.classList.add('hidden');
            addBotMessage(`I've switched to ${sentiment} reviews, but there are no reviews in this category.`);
            return;
        }
        
        // Generate brief summary (compressed format)
        const briefSummary = await generateBriefSummary(filteredComments, sentiment);
        sentimentBriefSummary = briefSummary;
        
        summaryLoadingOverlay.classList.add('hidden');
        
        // Add confirmation message
        addBotMessage(`I've loaded ${filteredComments.length} ${sentiment} reviews. I'm ready to answer your questions! 💡`);
        
    } catch (error) {
        console.error('Error loading sentiment summary:', error);
        summaryLoadingOverlay.classList.add('hidden');
        addBotMessage('Sorry, I encountered an error while loading the reviews. Please try again.');
    }
}

async function generateBriefSummary(comments, sentiment) {
    // Process in 3 rounds with compressed excerpts
    const COMMENTS_PER_ROUND = Math.ceil(comments.length / 3);
    const MAX_EXCERPT_LENGTH = 80; // Short excerpts
    
    let roundSummaries = [];
    
    for (let round = 0; round < 3; round++) {
        const roundStart = round * COMMENTS_PER_ROUND;
        const roundEnd = Math.min(roundStart + COMMENTS_PER_ROUND, comments.length);
        const roundComments = comments.slice(roundStart, roundEnd);
        
        // Update progress
        updateSummaryProgress(round + 1, 3);
        
        // Take short excerpts (max 10 comments per round)
        const excerpts = roundComments
            .slice(0, 10)
            .map(c => {
                const text = c.comment.trim();
                return text.length > MAX_EXCERPT_LENGTH 
                    ? text.substring(0, MAX_EXCERPT_LENGTH) + '...'
                    : text;
            })
            .join('\n');
        
        // Generate compressed round summary
        const roundSummary = await generateCompressedRoundSummary(excerpts, sentiment, roundComments.length);
        roundSummaries.push(roundSummary);
        
        await new Promise(resolve => setTimeout(resolve, 200));
    }
    
    // Combine all summaries into brief format
    const briefSummary = `
SENTIMENT: ${sentiment.toUpperCase()}
TOTAL REVIEWS: ${comments.length}

KEY POINTS:
${roundSummaries.map((s, i) => `${i + 1}. ${s}`).join('\n')}
`.trim();
    
    return briefSummary;
}

async function generateCompressedRoundSummary(excerpts, sentiment, count) {
    const prompt = `Analyze ${count} ${sentiment} customer reviews. Sample excerpts:

${excerpts}

Write ONLY ONE sentence (max 25 words) capturing the main theme.

Theme:`;

    try {
        const response = await fetch('/api/chat-summary', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                prompt: prompt,
                max_tokens: 50
            })
        });
        
        if (!response.ok) throw new Error('API call failed');
        
        const data = await response.json();
        return data.summary.trim();
        
    } catch (error) {
        console.error('Round summary error:', error);
        return `Issues reported in ${count} reviews`;
    }
}

function updateSummaryProgress(current, total) {
    const percentage = Math.round((current / total) * 100);
    const progressBar = document.querySelector('.summary-progress-bar');
    if (progressBar) {
        progressBar.style.width = percentage + '%';
    }
}

// ============================================================
// MESSAGE HANDLING
// ============================================================

chatbotSend.addEventListener('click', sendMessage);

chatbotInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        sendMessage();
    }
});

async function sendMessage() {
    const message = chatbotInput.value.trim();
    
    if (!message) return;
    
    if (!sentimentBriefSummary) {
        showToast('Please wait while I load the sentiment data...', 'info');
        return;
    }
    
    // Add user message
    addUserMessage(message);
    chatbotInput.value = '';
    
    // Show typing indicator
    showTypingIndicator();
    
    // Get AI response
    try {
        const response = await getAIResponse(message);
        hideTypingIndicator();
        addBotMessage(response);
    } catch (error) {
        hideTypingIndicator();
        addBotMessage('Sorry, I encountered an error. Please try again.');
        console.error('AI response error:', error);
    }
}

function addUserMessage(message) {
    const messageHTML = `
        <div class="chat-message user">
            <div class="message-avatar user">👤</div>
            <div class="message-content user">${escapeHtml(message)}</div>
        </div>
    `;
    
    chatbotMessages.insertAdjacentHTML('beforeend', messageHTML);
    chatHistory.push({ role: 'user', content: message });
    scrollToBottom();
}

function addBotMessage(message) {
    const messageHTML = `
        <div class="chat-message bot">
            <div class="message-avatar bot">🤖</div>
            <div class="message-content bot">${escapeHtml(message)}</div>
        </div>
    `;
    
    chatbotMessages.insertAdjacentHTML('beforeend', messageHTML);
    chatHistory.push({ role: 'bot', content: message });
    scrollToBottom();
}

function showTypingIndicator() {
    const typingHTML = `
        <div class="typing-indicator" id="typingIndicator">
            <div class="message-avatar bot">🤖</div>
            <div class="typing-dots">
                <span class="typing-dot"></span>
                <span class="typing-dot"></span>
                <span class="typing-dot"></span>
            </div>
        </div>
    `;
    
    chatbotMessages.insertAdjacentHTML('beforeend', typingHTML);
    scrollToBottom();
}

function hideTypingIndicator() {
    const indicator = document.getElementById('typingIndicator');
    if (indicator) {
        indicator.remove();
    }
}

function scrollToBottom() {
    chatbotMessages.scrollTop = chatbotMessages.scrollHeight;
}

// ============================================================
// AI RESPONSE GENERATION
// ============================================================

// ============================================================
// AI RESPONSE GENERATION WITH INTELLIGENT INTENT DETECTION
// ============================================================

async function getAIResponse(userQuestion) {
    // STEP 1: Ask AI to classify the user's intent
    const intentResult = await detectIntentWithAI(userQuestion);
    
    // STEP 2: If AI detected a navigation intent, handle it
    if (intentResult.isNavigation) {
        return handleNavigationIntent(intentResult.intent);
    }
    
    // STEP 3: Otherwise, answer the question normally
    const prompt = buildAIPrompt(userQuestion);
    
    try {
        const response = await fetch('/api/chat-query', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                prompt: prompt,
                max_tokens: 200
            })
        });
        
        if (!response.ok) {
            throw new Error(`API returned status ${response.status}`);
        }
        
        const data = await response.json();
        
        if (!data.success) {
            throw new Error(data.error || 'Unknown error');
        }
        
        return data.response.trim();
        
    } catch (error) {
        console.error('AI query error:', error);
        throw error;
    }
}

// ============================================================
// NEW: INTELLIGENT INTENT DETECTION USING AI
// ============================================================

async function detectIntentWithAI(userQuestion) {
    const intentPrompt = `You are an intent classifier for a sentiment analysis app.

The app has these capabilities:
1. GENERATE_POSITIVE_SUMMARY - Create AI summary of positive reviews
2. GENERATE_NEGATIVE_SUMMARY - Create AI summary of negative reviews  
3. VIEW_COMMENTS - Browse individual comments with AI analysis
4. DOWNLOAD_REPORTS - Download Excel/PDF files

User said: "${userQuestion}"

INSTRUCTIONS:
- If user wants to generate/create/see a summary of positive reviews, respond: GENERATE_POSITIVE_SUMMARY
- If user wants to generate/create/see a summary of negative reviews, respond: GENERATE_NEGATIVE_SUMMARY
- If user wants to see/view/browse individual comments/reviews, respond: VIEW_COMMENTS
- If user wants to download/export/get files/reports, respond: DOWNLOAD_REPORTS
- If none of above, respond: NO_NAVIGATION

Respond with ONLY ONE WORD from the options above.`;

    try {
        const response = await fetch('/api/chat-query', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                prompt: intentPrompt,
                max_tokens: 10
            })
        });
        
        if (!response.ok) {
            console.warn('Intent detection failed, falling back to keyword matching');
            return { isNavigation: false };
        }
        
        const data = await response.json();
        
        if (!data.success) {
            return { isNavigation: false };
        }
        
        const aiIntent = data.response.trim().toUpperCase();
        
        console.log('🎯 AI detected intent:', aiIntent);
        
        // Validate AI response and map to navigation intents
        const intentMapping = {
            'GENERATE_POSITIVE_SUMMARY': { type: 'generate_summary', sentiment: 'positive' },
            'GENERATE_NEGATIVE_SUMMARY': { type: 'generate_summary', sentiment: 'negative' },
            'VIEW_COMMENTS': { type: 'view_comments' },
            'DOWNLOAD_REPORTS': { type: 'download_report' },
            'NO_NAVIGATION': null
        };
        
        // Check if AI response is valid
        if (intentMapping.hasOwnProperty(aiIntent)) {
            const intent = intentMapping[aiIntent];
            
            if (intent === null) {
                return { isNavigation: false };
            }
            
            return { isNavigation: true, intent: intent };
        }
        
        // If AI gave invalid response, fallback to keyword matching
        console.warn('⚠️ AI gave unexpected response:', aiIntent, '- Using fallback');
        return fallbackKeywordDetection(userQuestion);
        
    } catch (error) {
        console.error('Intent detection error:', error);
        // Fallback to old keyword matching
        return fallbackKeywordDetection(userQuestion);
    }
}

// ============================================================
// FALLBACK: KEYWORD-BASED DETECTION (OLD METHOD)
// ============================================================

function fallbackKeywordDetection(userQuestion) {
    console.log('📋 Using fallback keyword detection');
    
    const question = userQuestion.toLowerCase();
    
    // Intent 1: Generate summary (positive/negative)
    const summaryKeywords = ['generate', 'create', 'make', 'show me', 'give me'];
    const sentimentKeywords = ['positive', 'negative', 'summary', 'analysis', 'insights'];
    
    if (summaryKeywords.some(kw => question.includes(kw)) && 
        sentimentKeywords.some(kw => question.includes(kw))) {
        
        if (question.includes('positive')) {
            return { isNavigation: true, intent: { type: 'generate_summary', sentiment: 'positive' } };
        } else if (question.includes('negative')) {
            return { isNavigation: true, intent: { type: 'generate_summary', sentiment: 'negative' } };
        }
    }
    
    // Intent 2: View individual comments
    const commentKeywords = ['see comments', 'view comments', 'show comments', 'individual', 
                            'single comment', 'detail', 'review details', 'browse'];
    
    if (commentKeywords.some(kw => question.includes(kw))) {
        return { isNavigation: true, intent: { type: 'view_comments' } };
    }
    
    // Intent 3: Download reports
    const downloadKeywords = ['download', 'export', 'get report', 'pdf', 'excel'];
    
    if (downloadKeywords.some(kw => question.includes(kw))) {
        return { isNavigation: true, intent: { type: 'download_report' } };
    }
    
    return { isNavigation: false };
}

function detectNavigationIntent(userQuestion) {
    const question = userQuestion.toLowerCase();
    
    // Intent 1: Generate summary (positive/negative)
    const summaryKeywords = ['generate', 'create', 'make', 'show me'];
    const sentimentKeywords = ['positive summary','positive analysis','positive insights',
                               ,'negative analysis','negative insights','negative summary', 'brief summary', 'comprehensive summary'];
    
    if (summaryKeywords.some(kw => question.includes(kw)) && 
        sentimentKeywords.some(kw => question.includes(kw))) {
        
        // Detect which sentiment
        if (question.includes('positive')) {
            return { type: 'generate_summary', sentiment: 'positive' };
        } else if (question.includes('negative')) {
            return { type: 'generate_summary', sentiment: 'negative' };
        }
    }
    
    // Intent 2: View individual comments
    const commentKeywords = ['see comments', 'view comments', 'show comments', 'individual comments', 
                            'single comment', 'comment analysis', 'detail', 'review details', 
                            'all comments', 'comment by comment'];
    
    if (commentKeywords.some(kw => question.includes(kw))) {
        return { type: 'view_comments' };
    }
    
    // Intent 3: Download reports
    const downloadKeywords = ['download', 'export', 'get report', 'pdf'];
    
    if (downloadKeywords.some(kw => question.includes(kw))) {
        return { type: 'download_report' };
    }
    
    return null; // No navigation intent detected
}

function handleNavigationIntent(intent) {
    switch (intent.type) {
        case 'generate_summary':
            navigateToSummaryGenerator(intent.sentiment);
            return `I'm taking you to the AI Summary Generator. I've selected ${intent.sentiment} reviews for you. Just click the "Generate Summary" button to create a comprehensive analysis! 🎯`;
        
        case 'view_comments':
            navigateToCommentReview();
            return `I'm opening the detailed comment review section for you. You can browse through all comments individually and get AI-powered analysis for each one! 📝`;
        
        case 'download_report':
            scrollToDownloadSection();
            return `I've scrolled to the download section for you. You can download Excel files for each sentiment category, or generate comprehensive PDF reports with AI analysis! 📥`;
        
        default:
            return null;
    }
}

function navigateToSummaryGenerator(sentiment) {
    // Close chatbot
    closeChatbot();
    
    // Scroll to batch summary section
    const summarySection = document.querySelector('.batch-summary-section');
    if (summarySection) {
        summarySection.scrollIntoView({ behavior: 'smooth', block: 'center' });
        
        // Set the sentiment dropdown
        setTimeout(() => {
            const sentimentSelect = document.getElementById('sentimentSelect');
            if (sentimentSelect) {
                sentimentSelect.value = sentiment;
                
                // Highlight the section
                summarySection.style.border = '2px solid var(--accent-primary)';
                summarySection.style.boxShadow = '0 0 20px rgba(102, 126, 234, 0.5)';
                
                setTimeout(() => {
                    summarySection.style.border = '';
                    summarySection.style.boxShadow = '';
                }, 3000);
            }
        }, 500);
    }
}

function navigateToCommentReview() {
    // Close chatbot
    closeChatbot();
    
    // Find and click the "Review All Comments" button
    const viewCommentsBtn = document.getElementById('viewCommentsBtn');
    if (viewCommentsBtn) {
        viewCommentsBtn.scrollIntoView({ behavior: 'smooth', block: 'center' });
        
        setTimeout(() => {
            // Highlight the button
            viewCommentsBtn.style.transform = 'scale(1.05)';
            viewCommentsBtn.style.boxShadow = '0 0 30px rgba(102, 126, 234, 0.7)';
            
            setTimeout(() => {
                viewCommentsBtn.click();
                viewCommentsBtn.style.transform = '';
                viewCommentsBtn.style.boxShadow = '';
            }, 800);
        }, 500);
    }
}

function scrollToDownloadSection() {
    // Close chatbot
    closeChatbot();
    
    // Scroll to download section
    const downloadSection = document.querySelector('.download-section');
    if (downloadSection) {
        downloadSection.scrollIntoView({ behavior: 'smooth', block: 'center' });
        
        setTimeout(() => {
            downloadSection.style.border = '2px solid var(--positive)';
            downloadSection.style.boxShadow = '0 0 20px rgba(16, 185, 129, 0.5)';
            
            setTimeout(() => {
                downloadSection.style.border = '';
                downloadSection.style.boxShadow = '';
            }, 3000);
        }, 500);
    }
}


function buildAIPrompt(userQuestion) {
    const prompt = `You are an expert business analyst helping interpret customer sentiment data.

CONTEXT - Customer Reviews Analysis:
${sentimentBriefSummary}

USER QUESTION: "${userQuestion}"

INSTRUCTIONS:
1. Answer in 2-3 clear sentences (max 60 words)
2. Be specific and actionable
3. Use data from the context above
4. If asked about improvements, prioritize top 3 actionable items
5. Be professional but conversational

Your concise answer:`;

    return prompt;
}

// ============================================================
// UTILITY FUNCTIONS
// ============================================================

function escapeHtml(text) {
    const map = {
        '&': '&amp;',
        '<': '&lt;',
        '>': '&gt;',
        '"': '&quot;',
        "'": '&#039;'
    };
    return text.replace(/[&<>"']/g, m => map[m]);
}

// ============================================================
// INITIALIZATION CHECK
// ============================================================

// Check if analysis is complete before showing chat button
function checkChatbotAvailability() {
    if (allComments && allComments.length > 0) {
        chatFab.style.display = 'flex';
    } else {
        chatFab.style.display = 'none';
    }
}

// Monitor when results are loaded
const originalShowResults = window.showResults;
if (typeof originalShowResults === 'function') {
    window.showResults = async function(...args) {
        await originalShowResults.apply(this, args);
        checkChatbotAvailability();
    };
}

console.log('🤖 AI Chatbot initialized');
