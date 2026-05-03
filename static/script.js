// ── ArcSync Frontend Controller ─────────────────────────────────────────────
const API_BASE = window.location.origin;

// ── State ───────────────────────────────────────────────────────────────────
let selectedRepo = null;
let repos = [];
let isGenerating = false;
let lastGeneratedSpec = null;

// ── Global Error Handler ────────────────────────────────────────────────────
window.addEventListener('unhandledrejection', (e) => {
    console.error('Unhandled promise rejection:', e.reason);
    showToast('Unexpected error occurred. Please try again.', 'error');
});

// ── Initialization ──────────────────────────────────────────────────────────
document.addEventListener('DOMContentLoaded', async () => {
    await loadRepos();
    await checkHealth();
    restoreState();
});

// ── State Persistence ───────────────────────────────────────────────────────
function saveState() {
    try {
        const state = {
            featureName: document.getElementById('feature-name-input')?.value || '',
            intent: document.getElementById('intent-input')?.value || '',
            selectedRepoIndex: repos.findIndex(r => r.path === selectedRepo?.path)
        };
        localStorage.setItem('arcsync_state', JSON.stringify(state));
    } catch (e) {
        console.warn('Failed to save state:', e);
    }
}

function restoreState() {
    try {
        const saved = localStorage.getItem('arcsync_state');
        if (!saved) return;
        
        const state = JSON.parse(saved);
        const featureInput = document.getElementById('feature-name-input');
        const intentInput = document.getElementById('intent-input');
        
        if (featureInput && state.featureName) featureInput.value = state.featureName;
        if (intentInput && state.intent) intentInput.value = state.intent;
        
        if (state.selectedRepoIndex >= 0 && state.selectedRepoIndex < repos.length) {
            selectRepo(state.selectedRepoIndex);
        }
    } catch (e) {
        console.warn('Failed to restore state:', e);
    }
}

// Auto-save on input
document.addEventListener('input', (e) => {
    if (e.target.id === 'feature-name-input' || e.target.id === 'intent-input') {
        saveState();
    }
});

async function loadRepos() {
    try {
        const res = await fetch(`${API_BASE}/api/v1/repos`);
        repos = await res.json();
        selectedRepo = repos[0];
        renderRepoSelector();
    } catch (e) {
        console.error('Failed to load repos:', e);
    }
}

// ── Upload Repository ───────────────────────────────────────────────────────
async function uploadRepository() {
    const input = document.createElement('input');
    input.type = 'file';
    input.accept = '.zip';
    
    input.onchange = async (e) => {
        const file = e.target.files[0];
        if (!file) return;
        
        // Validate file size (50MB)
        if (file.size > 50 * 1024 * 1024) {
            showToast('File too large. Maximum size is 50MB', 'error');
            return;
        }
        
        const formData = new FormData();
        formData.append('file', file);
        
        showToast('📤 Uploading repository...', 'info');
        
        try {
            const res = await fetch(`${API_BASE}/api/v1/upload-repo`, {
                method: 'POST',
                body: formData
            });
            
            if (!res.ok) {
                const err = await res.json();
                throw new Error(err.detail || 'Upload failed');
            }
            
            const data = await res.json();
            repos.push(data);
            renderRepoSelector();
            selectRepo(repos.length - 1);
            
            showToast('✓ Repository uploaded successfully!', 'success');
        } catch (err) {
            console.error('Upload error:', err);
            showToast(`Upload failed: ${err.message}`, 'error');
        }
    };
    
    input.click();
}

async function deleteUploadedRepo(repoIndex) {
    const repo = repos[repoIndex];
    if (!repo.uploaded) {
        showToast('Can only delete uploaded repositories', 'warning');
        return;
    }
    
    if (!confirm(`Delete "${repo.name}"? This cannot be undone.`)) {
        return;
    }
    
    try {
        const repoId = repo.path.split('/').pop();
        const res = await fetch(`${API_BASE}/api/v1/repos/${repoId}`, {
            method: 'DELETE'
        });
        
        if (!res.ok) throw new Error('Delete failed');
        
        repos.splice(repoIndex, 1);
        renderRepoSelector();
        if (selectedRepo === repo) {
            selectRepo(0);
        }
        
        showToast('✓ Repository deleted', 'success');
    } catch (err) {
        showToast(`Delete failed: ${err.message}`, 'error');
    }
}

function renderRepoSelector() {
    const container = document.getElementById('repo-selector');
    if (!container) return;
    container.innerHTML = repos.map((r, i) => `
        <button onclick="selectRepo(${i})" 
                class="repo-btn px-4 py-2 rounded-lg text-sm font-medium transition-all duration-200
                       ${i === 0 ? 'bg-primary text-on-primary shadow-md' : 'bg-slate-100 text-slate-600 hover:bg-slate-200'}"
                id="repo-btn-${i}">
            ${r.name}
        </button>
    `).join('');
}

async function selectRepo(index) {
    selectedRepo = repos[index];
    // Update button states
    document.querySelectorAll('.repo-btn').forEach((btn, i) => {
        if (i === index) {
            btn.className = btn.className.replace(/bg-slate-100 text-slate-600 hover:bg-slate-200/g, '')
                                          .replace(/bg-primary text-on-primary shadow-md/g, '')
                                          + ' bg-primary text-on-primary shadow-md';
        } else {
            btn.className = btn.className.replace(/bg-primary text-on-primary shadow-md/g, '')
                                          .replace(/bg-slate-100 text-slate-600 hover:bg-slate-200/g, '')
                                          + ' bg-slate-100 text-slate-600 hover:bg-slate-200';
        }
    });
    await checkHealth();
}

// ── Health Check ────────────────────────────────────────────────────────────
async function checkHealth() {
    try {
        const params = selectedRepo ? `?repo_path=${encodeURIComponent(selectedRepo.path)}` : '';
        const res = await fetch(`${API_BASE}/api/v1/health${params}`);
        const data = await res.json();
        
        const statusEl = document.getElementById('bob-status');
        const stackEl = document.getElementById('tech-stack-badge');
        const dbEl = document.getElementById('db-badge');
        const filesEl = document.getElementById('files-badge');
        const apiEl = document.getElementById('api-badge');

        if (statusEl) {
            statusEl.innerHTML = data.backend_connected 
                ? '<div class="h-2 w-2 rounded-full bg-emerald-500 animate-pulse"></div><span class="text-emerald-600 text-xs font-medium">Bob Connected</span>'
                : '<div class="h-2 w-2 rounded-full bg-red-500"></div><span class="text-red-600 text-xs font-medium">Disconnected</span>';
        }
        if (stackEl) stackEl.textContent = data.tech_stack || 'Unknown';
        if (dbEl) dbEl.textContent = data.database || 'Unknown';
        if (filesEl) filesEl.textContent = `${data.file_count || 0} files`;
        if (apiEl) apiEl.textContent = `${data.api_endpoints || 0} endpoints`;

    } catch (e) {
        console.error('Health check failed:', e);
    }
}

// ── Generate Specification ──────────────────────────────────────────────────
async function triggerArchSync() {
    if (isGenerating) return;
    
    const textarea = document.getElementById('intent-input');
    const featureInput = document.getElementById('feature-name-input');
    const intent = textarea?.value?.trim();
    const featureName = featureInput?.value?.trim() || 'Feature Specification';

    if (!intent || intent.length < 5) {
        showToast('Please describe the feature in at least a few words.', 'warning');
        return;
    }

    isGenerating = true;
    showLoadingState(true);

    try {
        const response = await fetch(`${API_BASE}/api/v1/generate`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                intent: intent,
                feature_name: featureName,
                repo_path: selectedRepo?.path || null
            })
        });

        if (!response.ok) {
            const err = await response.json();
            throw new Error(err.detail || 'Generation failed');
        }

        const data = await response.json();
        
        // Validate response
        if (!data || !data.specification) {
            throw new Error('Invalid response from server');
        }
        
        lastGeneratedSpec = data.specification;
        renderResults(data);

    } catch (error) {
        console.error('Generation failed:', error);
        showToast(`Error: ${error.message}`, 'error');
    } finally {
        isGenerating = false;
        showLoadingState(false);
    }
}

// ── Loading State ───────────────────────────────────────────────────────────
function showLoadingState(active) {
    const btn = document.getElementById('generate-btn');
    const stepper = document.getElementById('loading-stepper');
    const specPanel = document.getElementById('spec-output');
    const verdictBadge = document.getElementById('verdict-badge');
    const anchorContainer = document.getElementById('anchor-chips');

    if (btn) {
        btn.disabled = active;
        btn.innerHTML = active
            ? '<span class="material-symbols-outlined text-sm animate-spin">progress_activity</span> Generating...'
            : '<span class="material-symbols-outlined text-sm">bolt</span> Process Requirements';
    }

    if (stepper) stepper.style.display = active ? 'block' : 'none';

    if (active) {
        // Show loading skeletons
        if (verdictBadge) verdictBadge.style.display = 'none';
        if (anchorContainer) {
            anchorContainer.innerHTML = `
                <div class="shimmer h-12 rounded-lg mb-2"></div>
                <div class="shimmer h-12 rounded-lg mb-2"></div>
                <div class="shimmer h-12 rounded-lg"></div>
            `;
        }
        if (specPanel) {
            specPanel.innerHTML = `
                <div class="shimmer h-6 w-3/4 rounded mb-4"></div>
                <div class="shimmer h-4 w-full rounded mb-2"></div>
                <div class="shimmer h-4 w-5/6 rounded mb-2"></div>
                <div class="shimmer h-4 w-4/5 rounded mb-4"></div>
                <div class="shimmer h-32 w-full rounded"></div>
            `;
            specPanel.style.display = 'block';
        }
        animateSteps();
    }
}

function animateSteps() {
    const steps = document.querySelectorAll('.step-item');
    steps.forEach((step, i) => {
        setTimeout(() => {
            step.classList.add('step-active');
            if (i > 0) steps[i-1].classList.add('step-done');
        }, i * 2000);
    });
}

// ── Render Results ──────────────────────────────────────────────────────────
function renderResults(data) {
    // Update verdict badge
    const verdictEl = document.getElementById('verdict-badge');
    if (verdictEl) {
        const verdictConfig = {
            'FEASIBLE': { text: '✅ Feasible', cls: 'bg-emerald-100 text-emerald-800 border-emerald-300' },
            'FEASIBLE_WITH_CAVEATS': { text: '⚠️ Feasible with Caveats', cls: 'bg-amber-100 text-amber-800 border-amber-300' },
            'NOT_FEASIBLE': { text: '❌ Not Feasible', cls: 'bg-red-100 text-red-800 border-red-300' },
        };
        const v = verdictConfig[data.verdict] || verdictConfig['FEASIBLE'];
        verdictEl.className = `px-4 py-2 rounded-full text-sm font-bold border ${v.cls} transition-all duration-500`;
        verdictEl.textContent = v.text;
        verdictEl.style.display = 'inline-block';
    }

    // Update complexity gauge
    updateGauge(data.complexity);

    // Update tech/db badges
    const stackEl = document.getElementById('result-stack');
    const dbEl = document.getElementById('result-db');
    if (stackEl) stackEl.textContent = data.tech_stack || 'Unknown';
    if (dbEl) dbEl.textContent = data.database || 'Unknown';

    // Update anchor chips
    const anchorContainer = document.getElementById('anchor-chips');
    if (anchorContainer && data.anchors) {
        anchorContainer.innerHTML = data.anchors.map(anchor => {
            const tagColors = {
                'model': 'bg-purple-500', 'route': 'bg-blue-500', 'auth': 'bg-red-500',
                'middleware': 'bg-amber-500', 'config': 'bg-slate-500', 'database': 'bg-emerald-500',
                'service': 'bg-cyan-500', 'test': 'bg-pink-500', 'source': 'bg-slate-400'
            };
            const dotColor = tagColors[anchor.tags?.[0]] || 'bg-slate-400';
            const tagBadges = (anchor.tags || []).map(t => 
                `<span class="text-[10px] px-1.5 py-0.5 rounded-full bg-slate-100 text-slate-500">${t}</span>`
            ).join('');
            return `
                <div class="px-3 py-2 bg-white border border-slate-200 rounded-lg text-body-sm font-mono 
                            flex items-center gap-2 hover:border-primary hover:shadow-sm cursor-pointer transition-all">
                    <span class="w-2.5 h-2.5 rounded-full ${dotColor} flex-shrink-0"></span>
                    <span class="truncate">${anchor.file}</span>
                    <div class="flex gap-1 ml-auto">${tagBadges}</div>
                </div>`;
        }).join('');
    }

    // Render specification markdown with copy button
    const specPanel = document.getElementById('spec-output');
    if (specPanel && data.specification) {
        const copyBtn = `
            <div class="flex justify-end mb-4">
                <button onclick="copySpecToClipboard()"
                        class="flex items-center gap-2 px-4 py-2 bg-slate-100 hover:bg-slate-200 text-slate-700 rounded-lg text-sm font-medium transition-all">
                    <span class="material-symbols-outlined text-lg">content_copy</span>
                    Copy Specification
                </button>
            </div>
        `;
        specPanel.innerHTML = copyBtn + renderMarkdown(data.specification);
        specPanel.style.display = 'block';
    }

    // Show results panel
    const resultsPanel = document.getElementById('results-panel');
    if (resultsPanel) resultsPanel.style.display = 'block';
}

// ── Copy to Clipboard ───────────────────────────────────────────────────────
async function copySpecToClipboard() {
    if (!lastGeneratedSpec) {
        showToast('No specification to copy', 'warning');
        return;
    }
    
    try {
        await navigator.clipboard.writeText(lastGeneratedSpec);
        showToast('✓ Specification copied to clipboard!', 'success');
    } catch (e) {
        // Fallback for older browsers
        const textarea = document.createElement('textarea');
        textarea.value = lastGeneratedSpec;
        textarea.style.position = 'fixed';
        textarea.style.opacity = '0';
        document.body.appendChild(textarea);
        textarea.select();
        try {
            document.execCommand('copy');
            showToast('✓ Specification copied to clipboard!', 'success');
        } catch (err) {
            showToast('Failed to copy. Please select and copy manually.', 'error');
        }
        document.body.removeChild(textarea);
    }
}

function updateGauge(complexityStr) {
    const match = complexityStr?.match(/(\d+)\/(\d+)/);
    if (!match) return;

    const value = parseInt(match[1]);
    const max = parseInt(match[2]);
    const pct = (value / max) * 100;

    const gaugeValue = document.getElementById('complexity-value');
    const gaugeProgress = document.getElementById('gauge-progress');

    if (gaugeValue) gaugeValue.innerHTML = `${value}<span class="text-slate-300">/</span>${max}`;

    if (gaugeProgress) {
        // SVG arc calculation
        const dashLen = (pct / 100) * 125.6; // ~125.6 is the arc length of our semicircle
        gaugeProgress.style.strokeDasharray = `${dashLen} 200`;
        
        // Color based on complexity
        if (value <= 3) gaugeProgress.style.stroke = '#10b981'; // green
        else if (value <= 8) gaugeProgress.style.stroke = '#f59e0b'; // amber
        else gaugeProgress.style.stroke = '#ef4444'; // red
    }
}

// ── Simple Markdown Renderer ────────────────────────────────────────────────
function renderMarkdown(md) {
    // Process tables first (before other replacements)
    md = md.replace(/(\|[^\n]+\|\n\|[-:\s|]+\|\n(?:\|[^\n]+\|\n?)+)/g, (match) => {
        const lines = match.trim().split('\n');
        const headers = lines[0].split('|').filter(c => c.trim()).map(c => c.trim());
        const rows = lines.slice(2); // Skip header and separator
        
        let tableHtml = '<table class="min-w-full my-4 border-collapse">';
        tableHtml += '<thead class="bg-slate-50"><tr>';
        headers.forEach(h => {
            tableHtml += `<th class="px-4 py-2 text-left text-xs font-semibold text-slate-600 uppercase tracking-wider border-b-2 border-slate-200">${h}</th>`;
        });
        tableHtml += '</tr></thead><tbody>';
        
        rows.forEach((row, i) => {
            const cells = row.split('|').filter(c => c.trim()).map(c => c.trim());
            tableHtml += `<tr class="${i % 2 === 0 ? 'bg-white' : 'bg-slate-50'}">`;
            cells.forEach(cell => {
                tableHtml += `<td class="px-4 py-2 text-sm text-slate-700 border-b border-slate-100">${cell}</td>`;
            });
            tableHtml += '</tr>';
        });
        
        tableHtml += '</tbody></table>';
        return tableHtml;
    });

    // Hide technical diff blocks and replace with user-friendly summaries
    md = md.replace(/```diff\n([\s\S]*?)```/g, (match, diffContent) => {
        // Extract file path from diff
        const fileMatch = diffContent.match(/---\s+a\/(.*?)\s+\+\+\+\s+b\/(.*?)\s/);
        const fileName = fileMatch ? fileMatch[1] : 'file';
        
        // Count additions and deletions
        const additions = (diffContent.match(/^\+[^+]/gm) || []).length;
        const deletions = (diffContent.match(/^-[^-]/gm) || []).length;
        
        return `<div class="my-4 p-4 bg-blue-50 border-l-4 border-blue-500 rounded-r">
            <div class="flex items-center gap-2 mb-2">
                <span class="material-symbols-outlined text-blue-600 text-lg">code</span>
                <span class="font-semibold text-blue-900">Code Change: ${fileName}</span>
            </div>
            <div class="text-sm text-blue-700">
                <span class="text-green-600">+${additions} additions</span> ·
                <span class="text-red-600">-${deletions} deletions</span>
            </div>
        </div>`;
    });

    let html = md
        .replace(/^### (.*$)/gm, '<h3 class="text-lg font-bold text-slate-900 mt-6 mb-2 flex items-center gap-2">$1</h3>')
        .replace(/^## (.*$)/gm, '<h2 class="text-xl font-bold text-slate-900 mt-8 mb-3">$1</h2>')
        .replace(/^# (.*$)/gm, '<h1 class="text-2xl font-bold text-slate-900 mt-6 mb-4">$1</h1>')
        .replace(/\*\*(.*?)\*\*/g, '<strong class="font-semibold text-slate-900">$1</strong>')
        .replace(/`([^`]+)`/g, '<code class="bg-slate-100 text-slate-800 px-1.5 py-0.5 rounded text-sm font-mono">$1</code>')
        .replace(/^> (.*$)/gm, '<blockquote class="border-l-4 border-accent pl-4 py-2 my-4 text-slate-600 italic bg-slate-50 rounded-r">$1</blockquote>')
        .replace(/^- (.*$)/gm, '<li class="ml-4 text-slate-700 mb-1 list-disc">$1</li>')
        .replace(/^\d+\.\s+(.*$)/gm, '<li class="ml-4 text-slate-700 mb-2 list-decimal"><strong>$1</strong></li>')
        .replace(/^---$/gm, '<hr class="my-6 border-slate-200">')
        .replace(/\n\n/g, '</p><p class="text-slate-700 mb-3 leading-relaxed">')
        .replace(/```(\w*)\n([\s\S]*?)```/g, (match, lang, code) => {
            // Collapse long code blocks
            const lines = code.trim().split('\n');
            if (lines.length > 10) {
                const preview = lines.slice(0, 5).join('\n');
                return `<details class="my-4">
                    <summary class="cursor-pointer bg-slate-100 px-4 py-2 rounded-t text-sm font-medium text-slate-700 hover:bg-slate-200">
                        📄 View ${lang || 'code'} (${lines.length} lines)
                    </summary>
                    <pre class="bg-slate-900 text-slate-100 rounded-b p-4 overflow-x-auto text-sm font-mono"><code>${code.trim()}</code></pre>
                </details>`;
            }
            return `<pre class="bg-slate-900 text-slate-100 rounded-lg p-4 my-4 overflow-x-auto text-sm font-mono"><code>${code.trim()}</code></pre>`;
        });

    return `<div class="prose max-w-none">${html}</div>`;
}

// ── Export ───────────────────────────────────────────────────────────────────
async function exportBobSession() {
    try {
        const res = await fetch(`${API_BASE}/api/v1/export`);
        const data = await res.json();

        const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `ibm_bob_audit_${new Date().toISOString().slice(0,10)}.json`;
        a.click();
        URL.revokeObjectURL(url);
        showToast('IBM Bob session exported successfully!', 'success');
    } catch (e) {
        showToast('Export failed: ' + e.message, 'error');
    }
}

// ── Toast Notifications ─────────────────────────────────────────────────────
function showToast(message, type = 'info') {
    const toast = document.createElement('div');
    const colors = {
        success: 'bg-emerald-500', error: 'bg-red-500',
        warning: 'bg-amber-500', info: 'bg-blue-500'
    };
    toast.className = `fixed bottom-6 left-1/2 -translate-x-1/2 ${colors[type]} text-white px-6 py-3 rounded-full shadow-lg z-[100] text-sm font-medium transition-all duration-300 opacity-0 translate-y-4`;
    toast.textContent = message;
    document.body.appendChild(toast);
    
    requestAnimationFrame(() => {
        toast.classList.remove('opacity-0', 'translate-y-4');
    });

    setTimeout(() => {
        toast.classList.add('opacity-0', 'translate-y-4');
        setTimeout(() => toast.remove(), 300);
    }, 4000);
}