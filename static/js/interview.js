/**
 * static/js/interview.js — Interview Questions Generator Logic
 * ==============================================================
 * WHY THIS FILE EXISTS:
 *     Handles the interview prep feature:
 *     - Collects job role, experience level, question count
 *     - Sends to /api/interview/generate
 *     - Renders formatted interview questions
 */

async function generateInterviewQuestions() {
    const role = document.getElementById('interviewRole').value.trim();
    const level = document.getElementById('interviewLevel').value;
    const count = parseInt(document.getElementById('interviewCount').value);
    const resultDiv = document.getElementById('interviewResult');
    const generateBtn = document.getElementById('generateInterviewBtn');

    if (!role) {
        alert('Please enter a job role.');
        return;
    }

    // Show loading state
    generateBtn.disabled = true;
    generateBtn.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Generating...';
    resultDiv.innerHTML = `
        <div class="text-center py-5">
            <div class="typing-indicator justify-content-center">
                <span></span><span></span><span></span>
            </div>
            <p class="text-muted mt-3">Generating ${count} interview questions for ${role}...</p>
        </div>
    `;

    try {
        const response = await fetch('/api/interview/generate', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ role, level, count })
        });

        const data = await response.json();

        if (response.ok) {
            if (typeof marked !== 'undefined') {
                resultDiv.innerHTML = marked.parse(data.questions);
            } else {
                resultDiv.innerText = data.questions;
            }
        } else {
            resultDiv.innerHTML = `<p class="text-danger">❌ ${data.error || 'Generation failed. Please try again.'}</p>`;
        }
    } catch (error) {
        resultDiv.innerHTML = '<p class="text-danger">❌ Network error. Please check your connection.</p>';
        console.error('Interview generation error:', error);
    } finally {
        generateBtn.disabled = false;
        generateBtn.innerHTML = '<i class="bi bi-magic me-2"></i>Generate';
    }
}
