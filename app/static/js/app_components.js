/**
 * Componentes de UI Interactiva - Las Encinas de Fraijanes
 * 1. MultiImageUploader: Carga acumulativa de múltiples imágenes, arrastrar y soltar, vista previa y eliminación.
 * 2. ResidentSearchPicker: Buscador predictivo multicampo para selección de residentes.
 */

// Normalización de texto sin acentos
function normalizeSearchText(str) {
    if (!str) return '';
    return str.toString()
        .toLowerCase()
        .normalize('NFD')
        .replace(/[\u0300-\u036f]/g, '')
        .trim();
}

/**
 * --------------------------------------------------------------------------
 * 1. MultiImageUploader
 * Permite seleccionar varias imágenes en una sola tanda o en múltiples selecciones
 * acumulativas, arrastrar y soltar, con vista previa y botón de eliminación individual.
 * --------------------------------------------------------------------------
 */
class MultiImageUploader {
    constructor(container) {
        this.container = container;
        this.inputName = container.dataset.inputName || 'evidencias';
        this.maxFiles = parseInt(container.dataset.maxFiles || '10', 10);
        this.maxSizeMB = parseInt(container.dataset.maxSizeMb || '16', 10);
        this.accept = container.dataset.accept || 'image/png, image/jpeg, image/jpg, image/webp';
        this.stagedFiles = [];

        this.initDOM();
        this.bindEvents();
    }

    initDOM() {
        this.container.innerHTML = `
            <div class="multi-upload-wrapper">
                <input type="file" class="d-none multi-real-input" name="${this.inputName}" multiple accept="${this.accept}">
                
                <div class="multi-dropzone border border-2 border-dashed rounded-3 p-3 text-center bg-light cursor-pointer transition-all" style="cursor: pointer; border-color: #cbd5e1 !important;">
                    <div class="dropzone-content py-2">
                        <div class="mb-2 text-primary fs-2">
                            <i class="bi bi-cloud-arrow-up-fill"></i>
                        </div>
                        <div class="fw-semibold text-dark mb-1">
                            Arrastra tus fotos aquí o <span class="text-primary text-decoration-underline">haz clic para examinar</span>
                        </div>
                        <div class="small text-muted">
                            Puedes seleccionar múltiples imágenes a la vez (JPG, PNG, WebP &bull; máx. ${this.maxSizeMB}MB c/u)
                        </div>
                    </div>
                </div>

                <div class="multi-preview-section mt-3" style="display: none;">
                    <div class="d-flex align-items-center justify-content-between mb-2">
                        <span class="badge bg-primary-subtle text-primary border border-primary-subtle px-2 py-1 count-badge">
                            <i class="bi bi-images me-1"></i><span class="count-num">0</span> fotos seleccionadas
                        </span>
                        <button type="button" class="btn btn-sm btn-outline-primary btn-add-more py-1 px-2">
                            <i class="bi bi-plus-circle me-1"></i>Añadir más fotos
                        </button>
                    </div>
                    <div class="row g-2 multi-preview-grid"></div>
                </div>
            </div>
        `;

        this.realInput = this.container.querySelector('.multi-real-input');
        this.dropzone = this.container.querySelector('.multi-dropzone');
        this.previewSection = this.container.querySelector('.multi-preview-section');
        this.previewGrid = this.container.querySelector('.multi-preview-grid');
        this.countNum = this.container.querySelector('.count-num');
        this.btnAddMore = this.container.querySelector('.btn-add-more');
    }

    bindEvents() {
        // Clic en dropzone abre selector de archivos
        this.dropzone.addEventListener('click', () => {
            this.openFileDialog();
        });

        // Botón añadir más
        this.btnAddMore.addEventListener('click', (e) => {
            e.stopPropagation();
            this.openFileDialog();
        });

        // Drag & Drop
        ['dragenter', 'dragover'].forEach(eventName => {
            this.dropzone.addEventListener(eventName, (e) => {
                e.preventDefault();
                e.stopPropagation();
                this.dropzone.classList.add('bg-primary-subtle', 'border-primary');
            }, false);
        });

        ['dragleave', 'drop'].forEach(eventName => {
            this.dropzone.addEventListener(eventName, (e) => {
                e.preventDefault();
                e.stopPropagation();
                this.dropzone.classList.remove('bg-primary-subtle', 'border-primary');
            }, false);
        });

        this.dropzone.addEventListener('drop', (e) => {
            const dt = e.dataTransfer;
            if (dt && dt.files && dt.files.length) {
                this.handleFiles(dt.files);
            }
        });

        // Cambio en el input auxiliar
        this.fileHelperInput = document.createElement('input');
        this.fileHelperInput.type = 'file';
        this.fileHelperInput.multiple = true;
        this.fileHelperInput.accept = this.accept;
        this.fileHelperInput.style.display = 'none';
        document.body.appendChild(this.fileHelperInput);

        this.fileHelperInput.addEventListener('change', () => {
            if (this.fileHelperInput.files && this.fileHelperInput.files.length) {
                this.handleFiles(this.fileHelperInput.files);
            }
            this.fileHelperInput.value = '';
        });
    }

    openFileDialog() {
        this.fileHelperInput.click();
    }

    handleFiles(newFiles) {
        const allowedTypes = ['image/jpeg', 'image/jpg', 'image/png', 'image/webp'];
        let addedCount = 0;

        for (let i = 0; i < newFiles.length; i++) {
            const file = newFiles[i];

            // Validar tipo
            if (!allowedTypes.includes(file.type.toLowerCase())) {
                alert(`El archivo "${file.name}" no es una imagen válida (JPG, PNG o WebP).`);
                continue;
            }

            // Validar tamaño
            if (file.size > this.maxSizeMB * 1024 * 1024) {
                alert(`La imagen "${file.name}" excede el tamaño máximo permitido de ${this.maxSizeMB}MB.`);
                continue;
            }

            // Evitar duplicados exactos en nombre y tamaño
            const isDuplicate = this.stagedFiles.some(f => f.name === file.name && f.size === file.size);
            if (!isDuplicate) {
                this.stagedFiles.push(file);
                addedCount++;
            }
        }

        this.syncWithRealInput();
        this.renderPreviews();
    }

    removeFile(index) {
        this.stagedFiles.splice(index, 1);
        this.syncWithRealInput();
        this.renderPreviews();
    }

    syncWithRealInput() {
        // Usar DataTransfer para sincronizar con el input real del formulario
        try {
            const dataTransfer = new DataTransfer();
            this.stagedFiles.forEach(file => dataTransfer.items.add(file));
            this.realInput.files = dataTransfer.files;
        } catch (err) {
            console.warn('DataTransfer no soportado por este navegador:', err);
        }
    }

    formatFileSize(bytes) {
        if (bytes < 1024) return bytes + ' B';
        if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB';
        return (bytes / (1024 * 1024)).toFixed(1) + ' MB';
    }

    renderPreviews() {
        this.previewGrid.innerHTML = '';
        const count = this.stagedFiles.length;
        this.countNum.textContent = count;

        if (count === 0) {
            this.previewSection.style.display = 'none';
            return;
        }

        this.previewSection.style.display = 'block';

        this.stagedFiles.forEach((file, index) => {
            const col = document.createElement('div');
            col.className = 'col-6 col-sm-4 col-md-3';

            const card = document.createElement('div');
            card.className = 'card h-100 border shadow-sm position-relative overflow-hidden bg-white';
            card.style.borderRadius = '8px';

            const imgUrl = URL.createObjectURL(file);

            card.innerHTML = `
                <div class="position-relative" style="height: 90px; background-color: #f1f5f9;">
                    <img src="${imgUrl}" class="w-100 h-100 object-fit-cover" alt="preview">
                    <button type="button" class="btn btn-danger btn-sm p-0 d-flex align-items-center justify-content-center position-absolute top-0 end-0 m-1 rounded-circle" style="width: 22px; height: 22px; z-index: 2;" title="Quitar imagen">
                        <i class="bi bi-x fs-6"></i>
                    </button>
                </div>
                <div class="p-1 px-2 text-start">
                    <div class="small fw-semibold text-truncate text-dark" style="font-size: 11px;" title="${file.name}">${file.name}</div>
                    <div class="text-muted" style="font-size: 10px;">${this.formatFileSize(file.size)}</div>
                </div>
            `;

            const btnRemove = card.querySelector('button');
            btnRemove.addEventListener('click', (e) => {
                e.stopPropagation();
                URL.revokeObjectURL(imgUrl);
                this.removeFile(index);
            });

            col.appendChild(card);
            this.previewGrid.appendChild(col);
        });
    }
}

/**
 * --------------------------------------------------------------------------
 * 2. ResidentSearchPicker
 * Convierte un <select class="searchable-resident-select"> en un buscador
 * interactivo predictivo con búsqueda multicampo (nombre, casa, dpi, teléfono, etc.).
 * --------------------------------------------------------------------------
 */
class ResidentSearchPicker {
    constructor(selectElement) {
        this.select = selectElement;
        this.optionsData = [];
        this.selectedValue = this.select.value || '';
        this.init();
    }

    init() {
        this.extractDataFromSelect();
        this.buildUI();
        this.bindEvents();
        this.checkInitialSelection();
    }

    extractDataFromSelect() {
        const options = Array.from(this.select.options);
        this.optionsData = options
            .filter(opt => opt.value !== '')
            .map(opt => ({
                id: opt.value,
                text: opt.text.trim(),
                nombre: opt.dataset.nombre || opt.text.trim(),
                casa: opt.dataset.casa || '',
                dpi: opt.dataset.dpi || '',
                telefono: opt.dataset.telefono || '',
                correo: opt.dataset.correo || '',
                familia: opt.dataset.familia || '',
                selected: opt.selected
            }));
    }

    buildUI() {
        // Ocultar el select original manteniendo su presencia para envíos de formularios estándar
        this.select.style.setProperty('display', 'none', 'important');
        this.select.setAttribute('tabindex', '-1');

        this.wrapper = document.createElement('div');
        this.wrapper.className = 'resident-search-picker position-relative mb-1';

        this.wrapper.innerHTML = `
            <!-- Tarjeta de Residente Seleccionado -->
            <div class="resident-selected-card border rounded-3 p-2 bg-success-subtle border-success-subtle d-flex align-items-center justify-content-between" style="display: none;">
                <div class="d-flex align-items-center gap-2 overflow-hidden">
                    <div class="rounded-circle bg-success text-white d-flex align-items-center justify-content-center flex-shrink-0" style="width: 36px; height: 36px; font-size: 16px;">
                        <i class="bi bi-person-check-fill"></i>
                    </div>
                    <div class="min-w-0">
                        <div class="fw-bold text-dark text-truncate resident-card-name" style="font-size: 13.5px;">Residente</div>
                        <div class="text-muted text-truncate resident-card-meta" style="font-size: 11.5px;">Información</div>
                    </div>
                </div>
                <button type="button" class="btn btn-sm btn-outline-success bg-white flex-shrink-0 ms-2 resident-btn-change py-1 px-2" style="font-size: 12px;">
                    <i class="bi bi-arrow-repeat me-1"></i>Cambiar
                </button>
            </div>

            <!-- Caja de Búsqueda Interactiva -->
            <div class="resident-search-box">
                <div class="input-group">
                    <span class="input-group-text bg-white border-end-0 text-muted">
                        <i class="bi bi-search"></i>
                    </span>
                    <input type="text" class="form-control border-start-0 resident-search-input" 
                           placeholder="Buscar por nombre, apellido, casa #, DPI o teléfono..." 
                           autocomplete="off">
                    <button class="btn btn-outline-secondary resident-search-clear border-start-0" type="button" style="display: none;">
                        <i class="bi bi-x-lg"></i>
                    </button>
                </div>
                <!-- Menú flotante de resultados -->
                <div class="resident-search-results shadow-lg border rounded-3 bg-white mt-1 w-100 position-absolute" 
                     style="display: none; max-height: 250px; overflow-y: auto; z-index: 1060; left: 0; right: 0;">
                </div>
            </div>
        `;

        this.select.parentNode.insertBefore(this.wrapper, this.select.nextSibling);

        this.selectedCard = this.wrapper.querySelector('.resident-selected-card');
        this.cardName = this.wrapper.querySelector('.resident-card-name');
        this.cardMeta = this.wrapper.querySelector('.resident-card-meta');
        this.btnChange = this.wrapper.querySelector('.resident-btn-change');

        this.searchBox = this.wrapper.querySelector('.resident-search-box');
        this.searchInput = this.wrapper.querySelector('.resident-search-input');
        this.btnClear = this.wrapper.querySelector('.resident-search-clear');
        this.resultsList = this.wrapper.querySelector('.resident-search-results');
    }

    bindEvents() {
        // Escribir en el input de búsqueda
        this.searchInput.addEventListener('input', () => {
            const query = this.searchInput.value;
            this.btnClear.style.display = query.trim() ? 'block' : 'none';
            this.filterAndRender(query);
        });

        // Foco en input abre resultados si hay texto o muestra los primeros
        this.searchInput.addEventListener('focus', () => {
            this.filterAndRender(this.searchInput.value);
        });

        // Limpiar input con botón X
        this.btnClear.addEventListener('click', () => {
            this.searchInput.value = '';
            this.btnClear.style.display = 'none';
            this.filterAndRender('');
            this.searchInput.focus();
        });

        // Botón "Cambiar" residente
        this.btnChange.addEventListener('click', () => {
            this.selectedCard.style.display = 'none';
            this.searchBox.style.display = 'block';
            this.searchInput.value = '';
            this.btnClear.style.display = 'none';
            this.select.value = '';
            this.select.dispatchEvent(new Event('change', { bubbles: true }));
            this.searchInput.focus();
            this.filterAndRender('');
        });

        // Cerrar resultados al hacer clic fuera
        document.addEventListener('click', (e) => {
            if (!this.wrapper.contains(e.target)) {
                this.resultsList.style.display = 'none';
            }
        });
    }

    checkInitialSelection() {
        if (this.selectedValue) {
            const found = this.optionsData.find(item => item.id.toString() === this.selectedValue.toString());
            if (found) {
                this.selectResident(found, false);
            }
        }
    }

    filterAndRender(query) {
        const normalizedQuery = normalizeSearchText(query);
        const tokens = normalizedQuery.split(/\s+/).filter(t => t.length > 0);

        let matches = [];
        if (tokens.length === 0) {
            matches = this.optionsData.slice(0, 10);
        } else {
            matches = this.optionsData.filter(item => {
                const fullText = normalizeSearchText(
                    `${item.nombre} ${item.casa} ${item.dpi} ${item.telefono} ${item.correo} ${item.familia}`
                );
                return tokens.every(token => fullText.includes(token));
            }).slice(0, 15);
        }

        this.renderResults(matches, query);
    }

    renderResults(items, currentQuery) {
        this.resultsList.innerHTML = '';

        if (items.length === 0) {
            this.resultsList.innerHTML = `
                <div class="p-3 text-center text-muted small">
                    <i class="bi bi-person-x fs-4 d-block mb-1 text-secondary"></i>
                    No se encontraron residentes que coincidan con "<strong>${currentQuery}</strong>".
                </div>
            `;
            this.resultsList.style.display = 'block';
            return;
        }

        const listGroup = document.createElement('div');
        listGroup.className = 'list-group list-group-flush';

        items.forEach(item => {
            const btn = document.createElement('button');
            btn.type = 'button';
            btn.className = 'list-group-item list-group-item-action p-2 px-3 border-0 d-flex align-items-center justify-content-between text-start';

            const initials = item.nombre.split(' ').map(w => w[0]).slice(0, 2).join('').toUpperCase();

            let badgesHtml = '';
            if (item.casa) {
                badgesHtml += `<span class="badge bg-light text-dark border me-1"><i class="bi bi-house-door me-1"></i>${item.casa}</span>`;
            }
            if (item.dpi) {
                badgesHtml += `<span class="badge bg-secondary-subtle text-secondary me-1">DPI: ${item.dpi}</span>`;
            }
            if (item.telefono) {
                badgesHtml += `<span class="badge bg-info-subtle text-info"><i class="bi bi-telephone me-1"></i>${item.telefono}</span>`;
            }

            btn.innerHTML = `
                <div class="d-flex align-items-center gap-2 min-w-0">
                    <div class="rounded-circle bg-secondary-subtle text-secondary fw-bold d-flex align-items-center justify-content-center flex-shrink-0" style="width: 32px; height: 32px; font-size: 12px;">
                        ${initials}
                    </div>
                    <div class="min-w-0">
                        <div class="fw-semibold text-dark text-truncate" style="font-size: 13px;">${item.nombre}</div>
                        <div class="mt-1 d-flex flex-wrap gap-1" style="font-size: 11px;">
                            ${badgesHtml || '<span class="text-muted">Residente</span>'}
                        </div>
                    </div>
                </div>
                <i class="bi bi-chevron-right text-muted small ms-2"></i>
            `;

            btn.addEventListener('click', () => {
                this.selectResident(item, true);
            });

            listGroup.appendChild(btn);
        });

        this.resultsList.appendChild(listGroup);
        this.resultsList.style.display = 'block';
    }

    selectResident(item, triggerChangeEvent = true) {
        this.select.value = item.id;
        if (triggerChangeEvent) {
            this.select.dispatchEvent(new Event('change', { bubbles: true }));
        }

        this.cardName.textContent = item.nombre;
        const metaParts = [];
        if (item.casa) metaParts.push(item.casa);
        if (item.dpi) metaParts.push(`DPI: ${item.dpi}`);
        if (item.telefono) metaParts.push(`Tel: ${item.telefono}`);
        this.cardMeta.textContent = metaParts.join(' · ') || 'Residente registrado';

        this.resultsList.style.display = 'none';
        this.searchBox.style.display = 'none';
        this.selectedCard.style.display = 'flex';
    }
}

// Inicialización automática de componentes al cargar el DOM
document.addEventListener('DOMContentLoaded', () => {
    // 1. Inicializar subidores de múltiples imágenes
    document.querySelectorAll('[data-multi-image-uploader]').forEach(el => {
        new MultiImageUploader(el);
    });

    // 2. Inicializar selectores predictivos de residentes
    document.querySelectorAll('.searchable-resident-select').forEach(select => {
        new ResidentSearchPicker(select);
    });
});
