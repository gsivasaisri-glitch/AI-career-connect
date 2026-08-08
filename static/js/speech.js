/**
 * static/js/speech.js — Speech-to-Text & Text-to-Speech
 * =======================================================
 * WHY THIS FILE EXISTS (inside static/js/):
 *     The static/js/ folder holds all JavaScript files.
 *     Each feature has its OWN JS file (chat.js, resume.js, etc.)
 *     instead of one giant file. This follows 'Separation of Concerns'.
 *
 *     speech.js is SHARED across all pages because voice features
 *     (mic button + speaker button) are used on chat, resume,
 *     interview, and roadmap pages.
 *
 * WHAT IT DOES:
 *     1. Speech-to-Text (STT): Converts spoken words into text
 *        using the browser's Web Speech API (SpeechRecognition).
 *     2. Text-to-Speech (TTS): Reads text aloud using the
 *        browser's SpeechSynthesis API.
 *
 * WHY Web Speech API instead of a Python library?
 *     - No server costs for speech processing
 *     - Zero latency (runs locally in the browser)
 *     - No additional Python packages needed
 *     - Works in Chrome, Edge, and Safari
 */

// ─── Speech-to-Text (STT) ──────────────────────────────────────

let recognition = null;
let isRecording = false;

/**
 * Initialize the SpeechRecognition object.
 * Called once when the user first clicks the mic button.
 */
function initSpeechRecognition() {
    // Browser compatibility check
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;

    if (!SpeechRecognition) {
        alert('Speech recognition is not supported in your browser. Please use Chrome or Edge.');
        return null;
    }

    const recognizer = new SpeechRecognition();
    recognizer.continuous = true;        // Keep listening until stopped
    recognizer.interimResults = true;    // Show words as they're spoken
    recognizer.lang = 'en-US';           // Language

    return recognizer;
}

/**
 * Toggle speech recognition on/off.
 *
 * @param {string} targetInputId - The ID of the input/textarea to fill with speech.
 *                                  Defaults to 'chatInput' for the chat page.
 */
function toggleSpeechRecognition(targetInputId = 'chatInput') {
    if (isRecording) {
        stopRecording();
        return;
    }

    if (!recognition) {
        recognition = initSpeechRecognition();
        if (!recognition) return;
    }

    const targetInput = document.getElementById(targetInputId);
    const micBtn = document.getElementById('micBtn') || document.getElementById('resumeMicBtn');

    // Start recording
    isRecording = true;
    if (micBtn) micBtn.classList.add('recording');

    recognition.onresult = function (event) {
        let transcript = '';
        for (let i = event.resultIndex; i < event.results.length; i++) {
            transcript += event.results[i][0].transcript;
        }
        if (targetInput) {
            targetInput.value = transcript;
            // Trigger input event for auto-resize textareas
            targetInput.dispatchEvent(new Event('input'));
        }
    };

    recognition.onerror = function (event) {
        console.error('Speech recognition error:', event.error);
        stopRecording();
    };

    recognition.onend = function () {
        // If still recording, restart (handles browser auto-stop)
        if (isRecording) {
            try {
                recognition.start();
            } catch (e) {
                stopRecording();
            }
        }
    };

    try {
        recognition.start();
    } catch (e) {
        console.error('Failed to start speech recognition:', e);
        stopRecording();
    }
}

/**
 * Stop speech recording.
 */
function stopRecording() {
    isRecording = false;
    if (recognition) {
        try {
            recognition.stop();
        } catch (e) { /* ignore */ }
    }
    // Remove recording visual indicator from all mic buttons
    document.querySelectorAll('.mic-btn, #resumeMicBtn').forEach(btn => {
        btn.classList.remove('recording');
    });
}


// ─── Text-to-Speech (TTS) ──────────────────────────────────────

let currentUtterance = null;

/**
 * Read text aloud using the browser's speech synthesis.
 *
 * @param {string} text - The text to speak
 */
function speakText(text) {
    // If already speaking, stop
    if (window.speechSynthesis.speaking) {
        window.speechSynthesis.cancel();
        return;
    }

    if (!text || text.trim() === '') return;

    // Clean up markdown/HTML for cleaner speech
    const cleanText = text
        .replace(/#{1,6}\s/g, '')          // Remove markdown headers
        .replace(/\*{1,2}(.*?)\*{1,2}/g, '$1')  // Remove bold/italic markers
        .replace(/`{1,3}.*?`{1,3}/g, '')   // Remove code blocks
        .replace(/\[([^\]]+)\]\([^)]+\)/g, '$1')  // Clean links
        .replace(/<[^>]+>/g, '')            // Remove HTML tags
        .trim();

    currentUtterance = new SpeechSynthesisUtterance(cleanText);
    currentUtterance.rate = 1.0;      // Speech speed (0.1 to 10)
    currentUtterance.pitch = 1.0;     // Voice pitch (0 to 2)
    currentUtterance.volume = 1.0;    // Volume (0 to 1)
    currentUtterance.lang = 'en-US';

    // Use a natural-sounding voice if available
    const voices = window.speechSynthesis.getVoices();
    const preferredVoice = voices.find(v =>
        v.name.includes('Google') || v.name.includes('Natural') || v.name.includes('Samantha')
    );
    if (preferredVoice) {
        currentUtterance.voice = preferredVoice;
    }

    window.speechSynthesis.speak(currentUtterance);
}

/**
 * Stop any ongoing speech.
 */
function stopSpeaking() {
    window.speechSynthesis.cancel();
}

// Pre-load voices (some browsers need this)
if (window.speechSynthesis) {
    window.speechSynthesis.getVoices();
    window.speechSynthesis.onvoiceschanged = function () {
        window.speechSynthesis.getVoices();
    };
}
