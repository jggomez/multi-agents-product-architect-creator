/**
 * Report Viewer Component
 */
export const ReportViewer = {
    render(container, report, artifacts) {
        if (!report) return;

        container.innerHTML = `
            <div class="animate-in fade-in zoom-in-95 duration-500 h-full overflow-y-auto">
                <div class="p-8 prose prose-invert prose-indigo max-w-none prose-headings:font-bold prose-a:text-indigo-400">
                    ${marked.parse(report)}
                </div>
                
                ${artifacts && artifacts.length > 0 ? `
                    <div class="mt-12 p-8 border-t border-white/5 bg-white/2">
                        <div class="flex items-center gap-3 mb-6">
                            <div class="p-2 bg-indigo-500/20 rounded-lg">
                                <i data-lucide="layers" class="w-5 h-5 text-indigo-400"></i>
                            </div>
                            <h4 class="text-sm font-bold text-slate-300 uppercase tracking-widest">
                                Generated Artifacts
                            </h4>
                        </div>
                        
                        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                            ${artifacts.map(art => `
                                <a href="${art.url}" target="_blank" 
                                   class="group flex items-center justify-between p-4 glass-card hover:bg-white/5 transition-all">
                                    <div class="flex items-center gap-4 overflow-hidden">
                                        <div class="p-3 bg-slate-900 rounded-xl group-hover:bg-indigo-500/20 transition-colors">
                                            <i data-lucide="${this.getArtifactIcon(art.name)}" class="w-5 h-5 text-slate-400 group-hover:text-indigo-400"></i>
                                        </div>
                                        <div class="overflow-hidden">
                                            <p class="text-sm font-medium text-slate-200 truncate">${art.name}</p>
                                            <p class="text-[10px] text-slate-500 uppercase tracking-tighter">Click to open</p>
                                        </div>
                                    </div>
                                    <i data-lucide="chevron-right" class="w-4 h-4 text-slate-600 group-hover:text-indigo-400 transform group-hover:translate-x-1 transition-all"></i>
                                </a>
                            `).join('')}
                        </div>
                    </div>
                ` : ''}
                
                <!-- Floating Action Bar -->
                <div class="sticky bottom-6 left-0 right-0 px-8">
                    <div class="glass-card p-2 flex items-center justify-center gap-2 bg-slate-900/80 backdrop-blur-xl border-white/10 shadow-2xl">
                        <button id="copy-report" class="flex items-center gap-2 px-4 py-2 hover:bg-white/5 rounded-lg text-sm font-medium transition-colors">
                            <i data-lucide="copy" class="w-4 h-4"></i>
                            Copy Markdown
                        </button>
                        <div class="w-px h-6 bg-slate-800 mx-2"></div>
                        <button id="download-report" class="btn-primary py-2 px-4 text-sm flex items-center gap-2">
                            <i data-lucide="download" class="w-4 h-4"></i>
                            Download Report (.md)
                        </button>
                    </div>
                </div>
            </div>
        `;

        lucide.createIcons();
        this.bindEvents(report);
    },

    bindEvents(report) {
        const copyBtn = document.getElementById('copy-report');
        if (copyBtn) {
            copyBtn.addEventListener('click', () => {
                navigator.clipboard.writeText(report);
                const originalHTML = copyBtn.innerHTML;
                copyBtn.innerHTML = '<i data-lucide="check" class="w-4 h-4 text-emerald-400"></i> Copied!';
                lucide.createIcons();
                setTimeout(() => {
                    copyBtn.innerHTML = originalHTML;
                    lucide.createIcons();
                }, 2000);
            });
        }
    },

    getArtifactIcon(filename) {
        if (filename.includes('stitch') || filename.includes('ux')) return 'monitor';
        if (filename.includes('json')) return 'code-2';
        if (filename.includes('report') || filename.includes('final')) return 'file-text';
        return 'package';
    }
};
