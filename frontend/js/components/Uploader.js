/**
 * Uploader Component
 */
export const Uploader = {
    render(container, onUpload) {
        container.innerHTML = `
            <div class="flex flex-col items-center justify-center space-y-6 py-4" id="drop-zone">
                <div class="p-6 bg-indigo-500/10 rounded-full group-hover:bg-indigo-500/20 transition-all duration-500 group-hover:scale-110">
                    <i data-lucide="upload-cloud" class="w-12 h-12 text-indigo-400"></i>
                </div>
                <div class="text-center space-y-2">
                    <p class="text-xl font-semibold text-white">Upload Specification</p>
                    <p class="text-sm text-slate-500">Drag and drop your requirements document here</p>
                </div>
                <div class="flex items-center gap-4 w-full px-8">
                    <div class="h-px bg-slate-800 grow"></div>
                    <span class="text-xs text-slate-600 font-bold uppercase tracking-widest">OR</span>
                    <div class="h-px bg-slate-800 grow"></div>
                </div>
                <label for="file-input" class="btn-primary flex items-center gap-2 cursor-pointer">
                    <i data-lucide="file-plus" class="w-4 h-4"></i>
                    Select File
                </label>
                <input type="file" id="file-input" class="hidden" accept=".md,.txt">
            </div>
            
            <div id="file-preview" class="hidden space-y-6">
                <div class="flex items-center gap-4 p-4 glass-card bg-indigo-500/5">
                    <div class="p-3 bg-indigo-500/20 rounded-lg">
                        <i data-lucide="file-text" class="w-6 h-6 text-indigo-400"></i>
                    </div>
                    <div class="grow min-w-0">
                        <p id="filename" class="font-medium text-slate-200 truncate"></p>
                        <p id="filesize" class="text-xs text-slate-500"></p>
                    </div>
                    <button id="remove-file" class="p-2 hover:bg-rose-500/20 text-slate-500 hover:text-rose-400 rounded-full transition-colors">
                        <i data-lucide="x" class="w-5 h-5"></i>
                    </button>
                </div>
                <button id="start-btn" class="w-full py-4 btn-primary text-lg flex items-center justify-center gap-3">
                    <i data-lucide="play" class="w-5 h-5 fill-current"></i>
                    Start Orchestration
                </button>
            </div>
        `;
        
        lucide.createIcons();
        this.bindEvents(container, onUpload);
    },

    bindEvents(container, onUpload) {
        const dropZone = container.querySelector('#drop-zone');
        const fileInput = container.querySelector('#file-input');
        const filePreview = container.querySelector('#file-preview');
        const filenameLabel = container.querySelector('#filename');
        const filesizeLabel = container.querySelector('#filesize');
        const removeBtn = container.querySelector('#remove-file');
        const startBtn = container.querySelector('#start-btn');

        let selectedFile = null;

        const handleFiles = (files) => {
            if (files.length === 0) return;
            const file = files[0];
            
            // Validation
            if (file.size > 10 * 1024 * 1024) {
                alert('File too large (Max 10MB)');
                return;
            }

            selectedFile = file;
            filenameLabel.textContent = file.name;
            filesizeLabel.textContent = `${(file.size / 1024).toFixed(1)} KB`;
            
            dropZone.classList.add('hidden');
            filePreview.classList.remove('hidden');
            container.classList.remove('border-dashed', 'border-2');
        };

        // Note: selectBtn listener removed as label handles click natively
        fileInput.addEventListener('change', (e) => handleFiles(e.target.files));

        dropZone.addEventListener('dragover', (e) => {
            e.preventDefault();
            container.classList.add('border-indigo-500/50', 'bg-indigo-500/5');
        });

        dropZone.addEventListener('dragleave', () => {
            container.classList.remove('border-indigo-500/50', 'bg-indigo-500/5');
        });

        dropZone.addEventListener('drop', (e) => {
            e.preventDefault();
            container.classList.remove('border-indigo-500/50', 'bg-indigo-500/5');
            handleFiles(e.dataTransfer.files);
        });

        removeBtn.addEventListener('click', () => {
            selectedFile = null;
            fileInput.value = '';
            dropZone.classList.remove('hidden');
            filePreview.classList.add('hidden');
            container.classList.add('border-dashed', 'border-2');
        });

        startBtn.addEventListener('click', async () => {
            if (!selectedFile) return;
            
            const reader = new FileReader();
            reader.onload = (e) => {
                onUpload(e.target.result, selectedFile.name);
            };
            reader.readAsText(selectedFile);
        });
    }
};
