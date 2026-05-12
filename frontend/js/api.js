/**
 * API Communication Layer
 */
const BASE_URL = window.APP_CONFIG?.ORCHESTRATOR_URL || 'http://localhost:8005';

export const API = {
    async healthCheck() {
        try {
            const response = await fetch(`${BASE_URL}/health`);
            return response.ok;
        } catch (error) {
            return false;
        }
    },

    async createSession() {
        const sessionId = `session_${Date.now()}`;
        const response = await fetch(`${BASE_URL}/sessions/${sessionId}`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' }
        });
        
        if (!response.ok) throw new Error('Failed to create session');
        return sessionId;
    },

    async triggerOrchestration(content, onEvent) {
        const sessionId = await this.createSession();
        
        // Initial feedback
        onEvent({ type: 'SYSTEM', message: 'Session established. Sending document...' });

        const response = await fetch(`${BASE_URL}/sessions/${sessionId}/chat`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                message: `Process the following requirements:\n\n${content}`
            })
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Orchestration failed');
        }

        const data = await response.json();
        
        // Since we don't have a stream endpoint yet in the base ADK runner,
        // we simulate completion. In the future, we'd listen to an SSE stream here.
        return {
            report: data.answer,
            artifacts: data.artifacts || []
        };
    }
};
