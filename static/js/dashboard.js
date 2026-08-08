/**
 * static/js/dashboard.js — Dashboard Charts & Statistics
 * ========================================================
 * WHY THIS FILE EXISTS:
 *     Powers the dynamic dashboard with:
 *     - Real-time statistics (fetched from /api/dashboard/stats)
 *     - Chart.js bar chart for feature usage
 *     - Recent activity feed rendering
 *
 *     Data is loaded via AJAX (fetch API), making the dashboard
 *     dynamic — it updates every time you visit without a full
 *     page reload of the data.
 */

document.addEventListener('DOMContentLoaded', function () {
    loadDashboardStats();
});

async function loadDashboardStats() {
    try {
        const response = await fetch('/api/dashboard/stats');
        const data = await response.json();

        // Update stat cards with animated counting
        animateCounter('statChats', data.total_chats || 0);
        animateCounter('statResumes', data.total_resumes || 0);
        animateCounter('statInterviews', data.feature_counts?.interview || 0);
        animateCounter('statRoadmaps', data.feature_counts?.roadmap || 0);

        // Render feature usage chart
        renderFeatureChart(data.feature_counts || {});

        // Render recent activity
        renderRecentActivity(data.recent_activity || []);

    } catch (error) {
        console.error('Failed to load dashboard stats:', error);
    }
}

/**
 * Animate a number counting up from 0 to target.
 * Makes the dashboard feel alive and dynamic.
 */
function animateCounter(elementId, target) {
    const element = document.getElementById(elementId);
    if (!element) return;

    const duration = 1000; // 1 second
    const start = 0;
    const startTime = performance.now();

    function update(currentTime) {
        const elapsed = currentTime - startTime;
        const progress = Math.min(elapsed / duration, 1);

        // Ease-out curve for smooth deceleration
        const eased = 1 - Math.pow(1 - progress, 3);
        const current = Math.round(start + (target - start) * eased);

        element.textContent = current;

        if (progress < 1) {
            requestAnimationFrame(update);
        }
    }

    requestAnimationFrame(update);
}

/**
 * Render the feature usage bar chart using Chart.js.
 */
function renderFeatureChart(featureCounts) {
    const ctx = document.getElementById('featureChart');
    if (!ctx) return;

    new Chart(ctx, {
        type: 'bar',
        data: {
            labels: ['Chat', 'Resume', 'Interview', 'Roadmap'],
            datasets: [{
                label: 'Usage Count',
                data: [
                    featureCounts.chat || 0,
                    featureCounts.resume || 0,
                    featureCounts.interview || 0,
                    featureCounts.roadmap || 0
                ],
                backgroundColor: [
                    'rgba(99, 102, 241, 0.6)',
                    'rgba(16, 185, 129, 0.6)',
                    'rgba(245, 158, 11, 0.6)',
                    'rgba(239, 68, 68, 0.6)'
                ],
                borderColor: [
                    'rgba(99, 102, 241, 1)',
                    'rgba(16, 185, 129, 1)',
                    'rgba(245, 158, 11, 1)',
                    'rgba(239, 68, 68, 1)'
                ],
                borderWidth: 2,
                borderRadius: 8,
                borderSkipped: false
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { display: false }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: {
                        color: 'rgba(255,255,255,0.5)',
                        stepSize: 1
                    },
                    grid: {
                        color: 'rgba(255,255,255,0.05)'
                    }
                },
                x: {
                    ticks: { color: 'rgba(255,255,255,0.7)' },
                    grid: { display: false }
                }
            }
        }
    });
}

/**
 * Render the recent activity feed.
 */
function renderRecentActivity(activities) {
    const container = document.getElementById('recentActivity');
    if (!container) return;

    if (activities.length === 0) {
        container.innerHTML = `
            <div class="text-center py-4 text-muted">
                <i class="bi bi-inbox" style="font-size:2rem"></i>
                <p class="mt-2">No activity yet. Start chatting to see your history here!</p>
            </div>
        `;
        return;
    }

    const featureIcons = {
        chat: { icon: 'bi-chat-dots-fill', color: 'primary' },
        resume: { icon: 'bi-file-earmark-check-fill', color: 'success' },
        interview: { icon: 'bi-question-circle-fill', color: 'warning' },
        roadmap: { icon: 'bi-map-fill', color: 'danger' }
    };

    let html = '<div class="list-group list-group-flush">';

    activities.forEach(activity => {
        const feature = featureIcons[activity.feature] || featureIcons.chat;
        const timeAgo = getTimeAgo(new Date(activity.created_at));

        html += `
            <div class="list-group-item bg-transparent border-secondary px-0 py-3">
                <div class="d-flex align-items-start gap-3">
                    <div class="feature-icon bg-${feature.color} bg-opacity-10 text-${feature.color}"
                         style="width:36px;height:36px;font-size:0.9rem">
                        <i class="bi ${feature.icon}"></i>
                    </div>
                    <div class="flex-grow-1">
                        <p class="mb-1 text-truncate" style="max-width:500px">
                            ${escapeHtml(activity.content)}
                        </p>
                        <small class="text-muted">
                            <span class="badge bg-${feature.color} bg-opacity-20 text-${feature.color} me-2">
                                ${activity.feature}
                            </span>
                            ${timeAgo}
                        </small>
                    </div>
                </div>
            </div>
        `;
    });

    html += '</div>';
    container.innerHTML = html;
}

/**
 * Convert a date to a "time ago" string (e.g., "5 minutes ago").
 */
function getTimeAgo(date) {
    const seconds = Math.floor((new Date() - date) / 1000);

    if (seconds < 60) return 'Just now';
    if (seconds < 3600) return `${Math.floor(seconds / 60)} min ago`;
    if (seconds < 86400) return `${Math.floor(seconds / 3600)} hours ago`;
    return `${Math.floor(seconds / 86400)} days ago`;
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}
