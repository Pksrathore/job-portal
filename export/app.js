// Job Search Portal - Frontend Application

let allJobs = [];
let filteredJobs = [];
let jobApplications = {};
let currentJobId = null;

// Initialize the app
document.addEventListener('DOMContentLoaded', () => {
    loadJobs();
    loadApplications();
});

// Load jobs from JSON file
async function loadJobs() {
    try {
        const response = await fetch('jobs.json');
        const data = await response.json();

        allJobs = data.jobs || [];
        document.getElementById('last-updated').textContent =
            `Last updated: ${formatDate(data.exported_at)}`;

        filterJobs();
    } catch (error) {
        console.error('Error loading jobs:', error);
        document.getElementById('jobs-container').innerHTML = `
            <div class="text-center py-12">
                <div class="text-red-500">Error loading jobs. Make sure jobs.json exists.</div>
                <p class="text-gray-500 mt-2">${error.message}</p>
            </div>
        `;
    }
}

// Load application tracking from localStorage
function loadApplications() {
    const stored = localStorage.getItem('jobApplications');
    if (stored) {
        jobApplications = JSON.parse(stored);
    }
    updateStats();
}

// Save application tracking to localStorage
function saveApplications() {
    localStorage.setItem('jobApplications', JSON.stringify(jobApplications));
    updateStats();
}

// Filter and sort jobs
function filterJobs() {
    const searchTerm = document.getElementById('search-input').value.toLowerCase();
    const locationFilter = document.getElementById('location-filter').value;
    const sourceFilter = document.getElementById('source-filter').value;
    const statusFilter = document.getElementById('status-filter').value;
    const sortMode = document.getElementById('sort-select').value;

    filteredJobs = allJobs.filter(job => {
        // Search filter
        if (searchTerm) {
            const searchMatch =
                job.title.toLowerCase().includes(searchTerm) ||
                job.company.toLowerCase().includes(searchTerm) ||
                job.description.toLowerCase().includes(searchTerm);
            if (!searchMatch) return false;
        }

        // Location filter
        if (locationFilter) {
            if (locationFilter === 'remote' && !job.is_remote) return false;
            if (locationFilter !== 'remote' &&
                !job.location.toLowerCase().includes(locationFilter)) return false;
        }

        // Source filter
        if (sourceFilter && job.provider !== sourceFilter) return false;

        // Status filter
        if (statusFilter) {
            const jobStatus = jobApplications[job.id]?.status;
            if (jobStatus !== statusFilter) return false;
        }

        return true;
    });

    // Sort jobs
    filteredJobs.sort((a, b) => {
        switch (sortMode) {
            case 'newest':
                return (b.timestamp || 0) - (a.timestamp || 0);
            case 'oldest':
                return (a.timestamp || 0) - (b.timestamp || 0);
            case 'company':
                return a.company.localeCompare(b.company);
            default:
                return 0;
        }
    });

    renderJobs();
}

// Render jobs to the DOM
function renderJobs() {
    const container = document.getElementById('jobs-container');
    document.getElementById('job-count').textContent = filteredJobs.length;

    if (filteredJobs.length === 0) {
        container.innerHTML = `
            <div class="text-center py-12 bg-white rounded-lg shadow">
                <div class="text-gray-400 text-lg">No jobs found</div>
                <p class="text-gray-500 mt-2">Try adjusting your filters</p>
            </div>
        `;
        return;
    }

    container.innerHTML = filteredJobs.map(job => {
        const status = jobApplications[job.id]?.status || null;
        const statusClass = status ? `status-${status}` : '';
        const statusLabel = status ? status.charAt(0).toUpperCase() + status.slice(1) : '';

        return `
            <article class="job-card bg-white rounded-lg shadow p-5 ${statusClass}" data-job-id="${job.id}">
                <div class="flex items-start justify-between">
                    <div class="flex-1">
                        <h3 class="font-semibold text-lg text-gray-900">${escapeHtml(job.title)}</h3>
                        <p class="text-gray-600">${escapeHtml(job.company)}</p>
                    </div>
                    ${status ? `<span class="px-2 py-1 rounded text-xs font-medium">${statusLabel}</span>` : ''}
                </div>

                <div class="flex flex-wrap gap-2 mt-3 text-sm text-gray-500">
                    <span class="flex items-center gap-1">
                        <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z"/>
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 11a3 3 0 11-6 0 3 3 0 016 0z"/>
                        </svg>
                        ${escapeHtml(job.location)}
                    </span>
                    <span class="flex items-center gap-1">
                        <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"/>
                        </svg>
                        ${formatRelativeTime(job.timestamp)}
                    </span>
                    <span class="flex items-center gap-1">
                        <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10"/>
                        </svg>
                        ${escapeHtml(job.source)}
                    </span>
                </div>

                <div class="flex gap-2 mt-4 job-card-actions">
                    <button onclick="openJobModal('${job.id}')" class="flex-1 px-4 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 transition">
                        View Details
                    </button>
                    <button onclick="quickApply('${job.id}')" class="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition">
                        ${status ? 'Update Status' : 'Mark Applied'}
                    </button>
                </div>
            </article>
        `;
    }).join('');
}

// Open job detail modal
function openJobModal(jobId) {
    const job = allJobs.find(j => j.id === jobId);
    if (!job) return;

    currentJobId = jobId;
    const appData = jobApplications[jobId] || {};

    document.getElementById('modal-title').textContent = job.title;
    document.getElementById('modal-company').textContent = job.company;
    document.getElementById('modal-location').textContent = job.location;
    document.getElementById('modal-source').textContent = job.source;
    document.getElementById('modal-posted').textContent = formatRelativeTime(job.timestamp);
    document.getElementById('modal-description').innerHTML = job.description.replace(/\n/g, '<br>');
    document.getElementById('modal-apply-link').href = job.url || '#';
    document.getElementById('modal-status').value = appData.status || '';
    document.getElementById('modal-notes').value = appData.notes || '';

    document.getElementById('job-modal').classList.remove('hidden');
    document.getElementById('job-modal').classList.add('flex');
}

// Close modal
function closeModal(event) {
    if (!event || event.target === document.getElementById('job-modal')) {
        document.getElementById('job-modal').classList.add('hidden');
        document.getElementById('job-modal').classList.remove('flex');
        currentJobId = null;
    }
}

// Update job status
function updateJobStatus(status) {
    if (!currentJobId) return;

    if (!jobApplications[currentJobId]) {
        jobApplications[currentJobId] = {};
    }
    jobApplications[currentJobId].status = status;
    jobApplications[currentJobId].updatedAt = new Date().toISOString();

    saveApplications();
    filterJobs(); // Re-render to show status badge
}

// Quick apply action
function quickApply(jobId) {
    openJobModal(jobId);
}

// Save notes for a job
function saveNotes() {
    if (!currentJobId) return;

    const notes = document.getElementById('modal-notes').value;
    if (!jobApplications[currentJobId]) {
        jobApplications[currentJobId] = {};
    }
    jobApplications[currentJobId].notes = notes;
    jobApplications[currentJobId].updatedAt = new Date().toISOString();

    saveApplications();
}

// Update stats display
function updateStats() {
    const stats = { saved: 0, applied: 0, interview: 0, offer: 0, rejected: 0 };

    Object.values(jobApplications).forEach(app => {
        if (app.status && stats[app.status] !== undefined) {
            stats[app.status]++;
        }
    });

    document.getElementById('stat-saved').textContent = stats.saved;
    document.getElementById('stat-applied').textContent = stats.applied;
    document.getElementById('stat-interview').textContent = stats.interview;
    document.getElementById('stat-offer').textContent = stats.offer;
    document.getElementById('stat-rejected').textContent = stats.rejected;
}

// Refresh jobs
function refreshJobs() {
    location.reload();
}

// Utility functions
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

function formatDate(isoString) {
    if (!isoString) return 'Unknown';
    const date = new Date(isoString);
    return date.toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    });
}

function formatRelativeTime(timestamp) {
    if (!timestamp) return 'Unknown';

    const now = Date.now();
    const diff = now - (timestamp * 1000);

    const minutes = Math.floor(diff / 60000);
    const hours = Math.floor(diff / 3600000);
    const days = Math.floor(diff / 86400000);

    if (minutes < 60) return `${minutes}m ago`;
    if (hours < 24) return `${hours}h ago`;
    if (days < 7) return `${days}d ago`;
    if (days < 30) return `${Math.floor(days / 7)}w ago`;
    return `${Math.floor(days / 30)}mo ago`;
}

// Keyboard shortcuts
document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') {
        closeModal();
    }
});
