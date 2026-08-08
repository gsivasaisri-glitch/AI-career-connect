/**
 * static/js/roadmap.js — Career Roadmap Generator Logic
 * =======================================================
 * WHY THIS FILE EXISTS:
 *     Handles the career roadmap feature:
 *     - Collects current role, target role, and experience years
 *     - Sends to /api/roadmap/generate
 *     - Renders the AI-generated career progression roadmap
 */

async function generateRoadmap() {
    const currentRole = document.getElementById('currentRole').value.trim();
    const targetRole = document.getElementById('targetRole').value.trim();
    const experience = parseInt(document.getElementById('experienceYears').value) || 0;
    const resultDiv = document.getElementById('roadmapResult');
    const generateBtn = document.getElementById('generateRoadmapBtn');

    if (!currentRole || !targetRole) {
        alert('Please enter both your current role and target role.');
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
            <p class="text-muted mt-3">Creating your roadmap: ${currentRole} → ${targetRole}...</p>
        </div>
    `;

    try {
        const response = await fetch('/api/roadmap/generate', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                current_role: currentRole,
                target_role: targetRole,
                experience: experience
            })
        });

        const data = await response.json();

        if (response.ok) {
            if (typeof marked !== 'undefined') {
                resultDiv.innerHTML = marked.parse(data.roadmap);
            } else {
                resultDiv.innerText = data.roadmap;
            }
        } else {
            resultDiv.innerHTML = `<p class="text-danger">❌ ${data.error || 'Generation failed. Please try again.'}</p>`;
        }
    } catch (error) {
        resultDiv.innerHTML = '<p class="text-danger">❌ Network error. Please check your connection.</p>';
        console.error('Roadmap generation error:', error);
    } finally {
        generateBtn.disabled = false;
        generateBtn.innerHTML = '<i class="bi bi-magic me-2"></i>Generate';
    }
}
