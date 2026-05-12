/**
 * UI Orchestrator
 */
import { Uploader } from './components/Uploader.js';
import { ActivityLog } from './components/ActivityLog.js';
import { ReportViewer } from './components/ReportViewer.js';
import { HistoryPanel } from './components/HistoryPanel.js';

export const UI = {
    init(app) {
        this.app = app;
        this.cacheElements();
        this.bindEvents();
        this.renderInitial();
    },

    cacheElements() {
        this.elements = {
            app: document.getElementById('app'),
            systemStatus: document.getElementById('system-status'),
            uploader: document.getElementById('uploader-container'),
            activityLog: document.getElementById('activity-log'),
            activityCount: document.getElementById('activity-count'),
            resultEmpty: document.getElementById('result-empty'),
            resultView: document.getElementById('result-view')
        };
    },

    bindEvents() {
        const historyToggle = document.getElementById('history-toggle');
        if (historyToggle) {
            historyToggle.addEventListener('click', () => this.toggleHistory());
        }
    },

    toggleHistory() {
        HistoryPanel.render(document.body, this.app.history, (session) => {
            this.loadSession(session);
        });
        HistoryPanel.toggle(true);
    },

    loadSession(session) {
        // Reset and show result view for the historical session
        this.app.setState({
            status: 'COMPLETED',
            report: session.report,
            artifacts: session.artifacts || [],
            events: [{ type: 'SYSTEM', message: 'Restored from history', timestamp: new Date(session.timestamp) }]
        });
    },

    renderInitial() {
        this.renderUploader();
    },

    renderUploader() {
        Uploader.render(this.elements.uploader, (content, name) => {
            this.app.startOrchestration(content);
        });
    },

    updateSystemStatus(isHealthy) {
        const dot = this.elements.systemStatus.querySelector('span:first-child');
        const text = this.elements.systemStatus.querySelector('span:last-child');
        
        if (isHealthy) {
            dot.className = 'status-indicator status-completed';
            text.textContent = 'Orchestrator Online';
        } else {
            dot.className = 'status-indicator status-error';
            text.textContent = 'Orchestrator Offline';
        }
    },

    render(state) {
        // Update Activity Count
        this.elements.activityCount.textContent = `${state.events.length} events`;
        
        // Render Activity Log
        ActivityLog.render(this.elements.activityLog, state.events);
        
        // Handle Status Transitions
        if (state.status === 'PROCESSING') {
            this.showProcessing();
        } else if (state.status === 'COMPLETED') {
            this.showResult();
            ReportViewer.render(this.elements.resultView, state.report, state.artifacts);
        } else if (state.status === 'ERROR') {
            this.showError();
        }
    },

    showProcessing() {
        this.elements.uploader.classList.add('opacity-50', 'pointer-events-none');
        if (!this.elements.uploader.querySelector('.loading-overlay')) {
            const loader = document.createElement('div');
            loader.className = 'loading-overlay absolute inset-0 flex items-center justify-center bg-slate-950/20 rounded-2xl';
            loader.innerHTML = `
                <div class="flex flex-col items-center gap-3">
                    <div class="w-10 h-10 border-4 border-indigo-500/30 border-t-indigo-500 rounded-full animate-spin"></div>
                    <span class="text-xs font-bold text-indigo-400 uppercase tracking-widest">Processing</span>
                </div>
            `;
            this.elements.uploader.style.position = 'relative';
            this.elements.uploader.appendChild(loader);
        }
    },

    showResult() {
        this.elements.uploader.classList.remove('opacity-50', 'pointer-events-none');
        const loader = this.elements.uploader.querySelector('.loading-overlay');
        if (loader) loader.remove();
        
        this.elements.resultEmpty.classList.add('hidden');
        this.elements.resultView.classList.remove('hidden');
    },

    showError() {
        this.elements.uploader.classList.remove('opacity-50', 'pointer-events-none');
        const loader = this.elements.uploader.querySelector('.loading-overlay');
        if (loader) loader.remove();
        
        // Optionally show an error toast or UI state
    }
};
