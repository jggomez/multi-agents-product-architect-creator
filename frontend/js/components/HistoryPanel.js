/**
 * History Panel Component
 * Displays a slide-over list of previous orchestrations.
 */

export const HistoryPanel = {
    render(container, history, onSelect) {
        let panel = document.getElementById('history-panel');
        
        if (!panel) {
            panel = document.createElement('div');
            panel.id = 'history-panel';
            panel.className = 'fixed inset-y-0 right-0 w-80 bg-slate-950/80 backdrop-blur-xl border-l border-white/10 z-50 transform translate-x-full transition-transform duration-300 shadow-2xl overflow-hidden flex flex-col';
            document.body.appendChild(panel);
        }

        panel.innerHTML = `
            <div class="p-6 border-b border-white/5 flex items-center justify-between bg-white/5">
                <h3 class="text-lg font-semibold flex items-center gap-2">
                    <i data-lucide="history" class="w-5 h-5 text-indigo-400"></i>
                    Session History
                </h3>
                <button id="close-history" class="p-2 hover:bg-white/5 rounded-full transition-colors">
                    <i data-lucide="x" class="w-5 h-5"></i>
                </button>
            </div>
            <div class="flex-1 overflow-y-auto p-4 space-y-3" id="history-items">
                ${history.length === 0 ? `
                    <div class="text-center py-12 text-slate-500 text-sm italic">
                        No previous sessions found.
                    </div>
                ` : history.map((session, index) => `
                    <button class="history-item w-full text-left p-4 rounded-xl glass-card hover:bg-white/5 transition-all group" data-index="${index}">
                        <div class="flex flex-col gap-1">
                            <span class="text-xs text-slate-500">${new Date(session.timestamp).toLocaleString()}</span>
                            <span class="text-sm font-medium text-slate-300 group-hover:text-indigo-400 truncate">
                                ${session.report ? session.report.split('\n')[0].replace(/#/g, '').trim() : 'Unnamed Session'}
                            </span>
                            <div class="flex items-center gap-2 mt-2">
                                <span class="text-[10px] uppercase tracking-wider text-slate-600 bg-slate-900 px-2 py-0.5 rounded">
                                    ${session.artifacts ? session.artifacts.length : 0} Artifacts
                                </span>
                            </div>
                        </div>
                    </button>
                `).join('')}
            </div>
        `;

        // Re-initialize icons
        if (window.lucide) {
            lucide.createIcons({
                attrs: {
                    class: 'lucide'
                },
                portal: panel
            });
        }

        // Bind Events
        panel.querySelector('#close-history').onclick = () => this.toggle(false);
        
        panel.querySelectorAll('.history-item').forEach(item => {
            item.onclick = () => {
                const index = item.getAttribute('data-index');
                onSelect(history[index]);
                this.toggle(false);
            };
        });
    },

    toggle(show) {
        const panel = document.getElementById('history-panel');
        if (panel) {
            if (show) {
                panel.classList.remove('translate-x-full');
            } else {
                panel.classList.add('translate-x-full');
            }
        }
    }
};
