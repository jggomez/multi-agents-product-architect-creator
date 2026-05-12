/**
 * Agentic Studio - App Entry Point
 */

import { UI } from './ui.js';
import { API } from './api.js';

class App {
    constructor() {
        this.state = {
            status: 'IDLE', // IDLE, UPLOADING, PROCESSING, COMPLETED, ERROR
            file: null,
            events: [],
            report: null,
            artifacts: []
        };

        this.init();
    }

    async init() {
        console.log('🚀 Agentic Studio initializing...');
        
        // Load history
        this.loadHistory();

        // Initialize UI components
        UI.init(this);
        
        // Check orchestrator health
        this.checkHealth();
    }

    async checkHealth() {
        try {
            const isHealthy = await API.healthCheck();
            UI.updateSystemStatus(isHealthy);
        } catch (error) {
            console.error('Failed to connect to orchestrator:', error);
            UI.updateSystemStatus(false);
        }
    }

    loadHistory() {
        const history = localStorage.getItem('agentic_studio_history');
        this.history = history ? JSON.parse(history) : [];
    }

    saveToHistory(session) {
        this.history = [session, ...this.history].slice(0, 10);
        localStorage.setItem('agentic_studio_history', JSON.stringify(this.history));
    }

    setState(newState) {
        const oldStatus = this.state.status;
        this.state = { ...this.state, ...newState };
        UI.render(this.state);

        if (this.state.status === 'COMPLETED' && oldStatus !== 'COMPLETED') {
            this.saveToHistory({
                timestamp: new Date(),
                report: this.state.report,
                artifacts: this.state.artifacts
            });
        }
    }

    async startOrchestration(fileContent) {
        this.setState({ 
            status: 'PROCESSING', 
            events: [{ type: 'SYSTEM', message: 'Initiating orchestration chain...', timestamp: new Date() }],
            report: null
        });

        try {
            const result = await API.triggerOrchestration(fileContent, (event) => {
                this.addEvent(event);
            });
            
            this.setState({ 
                status: 'COMPLETED', 
                report: result.report,
                artifacts: result.artifacts || []
            });
        } catch (error) {
            console.error('Orchestration failed:', error);
            this.setState({ status: 'ERROR' });
            this.addEvent({ type: 'ERROR', message: `Failure: ${error.message}` });
        }
    }

    addEvent(event) {
        const events = [...this.state.events, { ...event, timestamp: new Date() }];
        this.setState({ events });
    }
}

// Global app instance
window.app = new App();
