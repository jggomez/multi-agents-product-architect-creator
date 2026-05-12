/**
 * Activity Log Component
 */
export const ActivityLog = {
    render(container, events) {
        if (events.length === 0) {
            container.innerHTML = `
                <div class="text-center py-12 text-slate-500 italic text-sm">
                    Waiting for orchestration to start...
                </div>
            `;
            return;
        }

        container.innerHTML = events.map(event => this.getEventHTML(event)).join('');
        lucide.createIcons();
        container.scrollTop = container.scrollHeight;
    },

    getEventHTML(event) {
        const color = this.getEventColor(event);
        const icon = this.getEventIcon(event);
        
        return `
            <div class="flex gap-4 p-3 rounded-lg hover:bg-white/5 transition-all group animate-in fade-in slide-in-from-left-2 duration-300">
                <div class="flex flex-col items-center">
                    <div class="w-8 h-8 rounded-lg ${color.bg} flex items-center justify-center shadow-lg shadow-indigo-500/10">
                        <i data-lucide="${icon}" class="w-4 h-4 ${color.text}"></i>
                    </div>
                    <div class="w-px h-full bg-slate-800 mt-2"></div>
                </div>
                <div class="space-y-1 pb-4">
                    <div class="flex items-center gap-2">
                        <span class="text-xs font-bold uppercase tracking-wider ${color.text}">
                            ${event.agent || 'System'}
                        </span>
                        <span class="text-[10px] text-slate-600 font-mono">
                            ${new Date(event.timestamp).toLocaleTimeString([], { hour12: false, hour: '2-digit', minute: '2-digit', second: '2-digit' })}
                        </span>
                    </div>
                    <p class="text-sm text-slate-300 leading-relaxed">${event.message}</p>
                </div>
            </div>
        `;
    },

    getEventColor(event) {
        if (event.type === 'ERROR') return { bg: 'bg-rose-500/20', text: 'text-rose-400' };
        if (event.type === 'SYSTEM') return { bg: 'bg-indigo-500/20', text: 'text-indigo-400' };
        
        const agentColors = {
            'analyst': { bg: 'bg-blue-500/20', text: 'text-blue-400' },
            'architect': { bg: 'bg-purple-500/20', text: 'text-purple-400' },
            'ux_designer': { bg: 'bg-pink-500/20', text: 'text-pink-400' },
            'critic': { bg: 'bg-amber-500/20', text: 'text-amber-400' },
            'orchestrator': { bg: 'bg-emerald-500/20', text: 'text-emerald-400' }
        };

        return agentColors[event.agent] || { bg: 'bg-slate-500/20', text: 'text-slate-400' };
    },

    getEventIcon(event) {
        if (event.type === 'ERROR') return 'alert-circle';
        if (event.type === 'SYSTEM') return 'settings';
        
        const agentIcons = {
            'analyst': 'search',
            'architect': 'layout',
            'ux_designer': 'palette',
            'critic': 'shield-check',
            'orchestrator': 'bot'
        };

        return agentIcons[event.agent] || 'bot';
    }
};
