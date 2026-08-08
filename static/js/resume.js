/**
 * static/js/resume.js — Resume Analyzer Logic
 * ==============================================
 * WHY THIS FILE EXISTS:
 *     Handles the resume analysis feature:
 *     - Captures resume text from the textarea
 *     - Sends it to /api/resume/analyze
 *     - Renders the AI analysis (with markdown)
 *     - Shows loading state
 */

async function analyzeResume() {
    const resumeText = document.getElementById('resumeInput').value.trim();
    const resultDiv = document.getElementById('analysisResult');
    const analyzeBtn = document.getElementById('analyzeBtn');

    if (!resumeText) {
        alert('Please paste your resume text first.');
        return;
    }

    // Show loading state
    analyzeBtn.disabled = true;
    analyzeBtn.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Analyzing...';
    resultDiv.innerHTML = `
        <div class="text-center py-5">
            <div class="typing-indicator justify-content-center">
                <span></span><span></span><span></span>
            </div>
            <p class="text-muted mt-3">AI is analyzing your resume...</p>
        </div>
    `;

    try {
        const response = await fetch('/api/resume/analyze', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ resume_text: resumeText })
        });

        const data = await response.json();

        if (response.ok) {
            // Render markdown result
            if (typeof marked !== 'undefined') {
                resultDiv.innerHTML = marked.parse(data.analysis);
            } else {
                resultDiv.innerText = data.analysis;
            }
        } else {
            resultDiv.innerHTML = `<p class="text-danger">❌ ${data.error || 'Analysis failed. Please try again.'}</p>`;
        }
    } catch (error) {
        resultDiv.innerHTML = '<p class="text-danger">❌ Network error. Please check your connection.</p>';
        console.error('Resume analysis error:', error);
    } finally {
        analyzeBtn.disabled = false;
        analyzeBtn.innerHTML = '<i class="bi bi-magic me-2"></i>Analyze Resume';
    }
}
