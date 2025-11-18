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
                <p>I'm your AI assistant, ready to help you understand your customer feedback better. Select a sentiment category above and ask me anything about the reviews!</p>
                <p style="margin-top: 0.75rem; font-size: 0.85rem; opacity: 0.8;">
                    <strong>Try asking:</strong><br>
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

async function getAIResponse(userQuestion) {
    // Build comprehensive prompt
    const prompt = buildAIPrompt(userQuestion);
    
    try {
        const response = await fetch('/api/chat-query', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                prompt: prompt,
                max_tokens: 200 // Limit response to 2-3 lines
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