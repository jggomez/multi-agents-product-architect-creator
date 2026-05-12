/**
 * API Communication Layer — SSE streaming for real-time agent updates.
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

        onEvent({ type: 'SYSTEM', message: 'Session established. Starting pipeline...' });

        const response = await fetch(`${BASE_URL}/sessions/${sessionId}/stream`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                message: `Process the following requirements:\n\n${content}`
            })
        });

        if (!response.ok) {
            const error = await response.json().catch(() => ({ detail: 'Orchestration failed' }));
            throw new Error(error.detail || 'Orchestration failed');
        }

        const reader = response.body.getReader();
        const decoder = new TextDecoder();
        let fullReport = '';
        let buffer = '';

        while (true) {
            const { done, value } = await reader.read();
            if (done) break;

            buffer += decoder.decode(value, { stream: true });
            const lines = buffer.split('\n');
            buffer = lines.pop();

            for (const line of lines) {
                if (!line.startsWith('data: ')) continue;
                try {
                    const event = JSON.parse(line.slice(6));

                    if (event.type === 'status') {
                        onEvent({ type: 'STATUS', message: event.message, agent: event.agent });
                    } else if (event.type === 'text') {
                        fullReport += event.text;
                        onEvent({ type: 'TEXT', message: event.text, agent: event.author });
                    } else if (event.type === 'complete') {
                        return { report: fullReport, artifacts: event.artifacts || [] };
                    } else if (event.type === 'error') {
                        throw new Error(event.detail || 'Pipeline error');
                    }
                } catch (parseError) {
                    if (parseError.message === 'Pipeline error' ||
                        parseError.message.includes('Orchestration failed')) {
                        throw parseError;
                    }
                    // Skip JSON parse errors from partial chunks
                }
            }
        }

        return { report: fullReport, artifacts: [] };
    }
};
