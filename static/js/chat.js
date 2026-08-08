/**
 * static/js/chat.js — AI Chat Page Logic
 * ========================================
 * WHY THIS FILE EXISTS:
 *     Handles all JavaScript logic for the AI chat page:
 *     - Sending messages to the /api/chat endpoint
 *     - Rendering user and AI message bubbles
 *     - Auto-scrolling to latest message
 *     - Markdown rendering for AI responses
 *     - Managing chat sessions
 *     - Auto-resizing textarea
 *
 *     Separated from speech.js because chat logic is
 *     only needed on the chat page, while speech is
 *     shared across all pages.
 */

// Unique session ID for this conversation
let sessionId = crypto.randomUUID();

// ─── DOM Ready ──────────────────────────────────────────────────

document.addEventListener('DOMContentLoaded', function () {
    const chatForm = document.getElementById('chatForm');
    const chatInput = document.getElementById('chatInput');

    // Handle form submission
    chatForm.addEventListener('submit', function (e) {
        e.preventDefault();
        sendMessage();
    });

    // Auto-resize textarea as user types
    chatInput.addEventListener('input', function () {
        this.style.height = 'auto';
        this.style.height = Math.min(this.scrollHeight, 120) + 'px';
    });

    // Send on Enter (Shift+Enter for new line)
    chatInput.addEventListener('keydown', function (e) {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            sendMessage();
        }
    });
});

// ─── Send Message ───────────────────────────────────────────────

async function sendMessage() {
    const chatInput = document.getElementById('chatInput');
    const message = chatInput.value.trim();

    if (!message) return;

    // Clear input and reset height
    chatInput.value = '';
    chatInput.style.height = 'auto';

    // Stop any ongoing speech recording
    if (typeof stopRecording === 'function') stopRecording();

    // Add user message bubble to the chat
    addMessage('user', message);

    // Show typing indicator
    showTypingIndicator();

    // Disable send button while waiting
    const sendBtn = document.getElementById('sendBtn');
    sendBtn.disabled = true;

    try {
        const response = await fetch('/api/chat', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                message: message,
                session_id: sessionId,
                feature: 'chat'
            })
        });

        const data = await response.json();

        // Remove typing indicator
        removeTypingIndicator();

        if (response.ok) {
            addMessage('assistant', data.response);
        } else {
            addMessage('assistant', '❌ ' + (data.error || 'Something went wrong. Please try again.'));
        }
    } catch (error) {
        removeTypingIndicator();
        addMessage('assistant', '❌ Network error. Please check your connection and try again.');
        console.error('Chat error:', error);
    } finally {
        sendBtn.disabled = false;
    }
}

// ─── Add Message Bubble ─────────────────────────────────────────

function addMessage(role, content) {
    const chatMessages = document.getElementById('chatMessages');

    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${role}-message`;

    const avatarIcon = role === 'assistant' ? 'bi-robot' : 'bi-person-fill';

    // Render markdown for AI responses
    let renderedContent;
    if (role === 'assistant' && typeof marked !== 'undefined') {
        renderedContent = marked.parse(content);
    } else {
        renderedContent = `<p>${escapeHtml(content)}</p>`;
    }

    messageDiv.innerHTML = `
        <div class="message-avatar">
            <i class="bi ${avatarIcon}"></i>
        </div>
        <div class="message-bubble">
            ${renderedContent}
            ${role === 'assistant' ? `
                <div class="message-actions">
                    <button class="btn btn-sm btn-outline-secondary" onclick="speakText(this.closest('.message-bubble').innerText)" title="Read aloud">
                        <i class="bi bi-volume-up-fill"></i>
                    </button>
                    <button class="btn btn-sm btn-outline-secondary" onclick="copyToClipboard(this.closest('.message-bubble').innerText)" title="Copy">
                        <i class="bi bi-clipboard"></i>
                    </button>
                </div>
            ` : ''}
        </div>
    `;

    chatMessages.appendChild(messageDiv);
    scrollToBottom();
}

// ─── Typing Indicator ───────────────────────────────────────────

function showTypingIndicator() {
    const chatMessages = document.getElementById('chatMessages');

    const typingDiv = document.createElement('div');
    typingDiv.className = 'message assistant-message';
    typingDiv.id = 'typingIndicator';
    typingDiv.innerHTML = `
        <div class="message-avatar">
            <i class="bi bi-robot"></i>
        </div>
        <div class="message-bubble">
            <div class="typing-indicator">
                <span></span><span></span><span></span>
            </div>
        </div>
    `;

    chatMessages.appendChild(typingDiv);
    scrollToBottom();
}

function removeTypingIndicator() {
    const indicator = document.getElementById('typingIndicator');
    if (indicator) indicator.remove();
}

// ─── Utilities ──────────────────────────────────────────────────

function scrollToBottom() {
    const chatMessages = document.getElementById('chatMessages');
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

function clearChat() {
    const chatMessages = document.getElementById('chatMessages');
    // Keep only the welcome message (first child)
    while (chatMessages.children.length > 1) {
        chatMessages.removeChild(chatMessages.lastChild);
    }
    // New session for fresh context
    sessionId = crypto.randomUUID();
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

function copyToClipboard(text) {
    navigator.clipboard.writeText(text).then(() => {
        // Brief visual feedback could be added here
    }).catch(err => {
        console.error('Copy failed:', err);
    });
}
