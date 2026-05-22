function updateForceArrows() {
    const controlsByTrack = {};
    document.querySelectorAll('.force-arrow[data-track-id]').forEach((button) => {
        const trackId = button.dataset.trackId;
        if (!trackId) {
            return;
        }
        if (!controlsByTrack[trackId]) {
            controlsByTrack[trackId] = {};
        }
        const direction = button.dataset.direction === 'prev' ? 'prev' : 'next';
        controlsByTrack[trackId][direction] = button;
    });

    Object.entries(controlsByTrack).forEach(([trackId, controls]) => {
        const track = document.getElementById(trackId);
        if (!track) {
            return;
        }

        const maxScrollLeft = Math.max(0, track.scrollWidth - track.clientWidth);
        const hasOverflow = maxScrollLeft > 2;
        const prevButton = controls.prev || null;
        const nextButton = controls.next || null;

        if (prevButton) {
            prevButton.disabled = !hasOverflow;
        }
        if (nextButton) {
            nextButton.disabled = !hasOverflow;
        }
    });
}

let forceArrowAnimationFrame = null;
function scheduleForceArrowUpdate() {
    if (forceArrowAnimationFrame !== null) {
        return;
    }

    forceArrowAnimationFrame = window.requestAnimationFrame(() => {
        forceArrowAnimationFrame = null;
        updateForceArrows();
    });
}

const productEditModalState = {
    modal: null,
    element: null,
    staticPrefix: '/static/',
    maxImages: 0,
    activeImages: [],
    activeIndex: 0,
    pendingPreviewUrls: [],
    refs: {},
};

function clearPendingFilePreviews() {
    productEditModalState.pendingPreviewUrls.forEach((url) => {
        URL.revokeObjectURL(url);
    });
    productEditModalState.pendingPreviewUrls = [];
}

function getProductImageUrl(imagePath) {
    const cleanPath = String(imagePath || '').replace(/^\/+/, '');
    return `${productEditModalState.staticPrefix}${cleanPath}`;
}

function updateModalPreview() {
    const { refs, activeImages, activeIndex } = productEditModalState;
    if (!refs.previewImage || !refs.previewEmpty) {
        return;
    }

    const hasImages = Array.isArray(activeImages) && activeImages.length > 0;
    const safeIndex = hasImages ? Math.max(0, Math.min(activeIndex, activeImages.length - 1)) : 0;
    productEditModalState.activeIndex = safeIndex;

    if (!hasImages) {
        refs.previewImage.src = '';
        refs.previewImage.classList.add('d-none');
        refs.previewEmpty.classList.remove('d-none');
    } else {
        refs.previewImage.src = getProductImageUrl(activeImages[safeIndex]);
        refs.previewImage.classList.remove('d-none');
        refs.previewEmpty.classList.add('d-none');
    }

    if (refs.thumbnailGrid) {
        refs.thumbnailGrid.querySelectorAll('.js-modal-thumb').forEach((button) => {
            const thumbIndex = Number.parseInt(button.dataset.index || '0', 10);
            button.classList.toggle('is-active', thumbIndex === safeIndex);
        });
    }
}

function updateModalFilePreview(index = 0) {
    const { refs, pendingPreviewUrls } = productEditModalState;
    if (!refs.previewImage || !refs.previewEmpty || pendingPreviewUrls.length === 0) {
        return;
    }

    const safeIndex = Math.max(0, Math.min(index, pendingPreviewUrls.length - 1));
    productEditModalState.activeIndex = safeIndex;
    refs.previewImage.src = pendingPreviewUrls[safeIndex];
    refs.previewImage.classList.remove('d-none');
    refs.previewEmpty.classList.add('d-none');

    if (refs.thumbnailGrid) {
        refs.thumbnailGrid.querySelectorAll('.js-modal-file-thumb').forEach((button) => {
            const thumbIndex = Number.parseInt(button.dataset.index || '0', 10);
            button.classList.toggle('is-active', thumbIndex === safeIndex);
        });
    }
}

function renderModalFileSelectionPreview(files, labelPrefix) {
    const { refs } = productEditModalState;
    const selectedFiles = Array.from(files || []).filter((file) => file && file.type.startsWith('image/'));

    clearPendingFilePreviews();
    if (!selectedFiles.length) {
        renderModalThumbnails(productEditModalState.activeImages);
        updateModalGalleryMeta(productEditModalState.activeImages);
        updateModalPreview();
        return;
    }

    productEditModalState.pendingPreviewUrls = selectedFiles.map((file) => URL.createObjectURL(file));

    if (refs.thumbnailGrid) {
        refs.thumbnailGrid.innerHTML = '';
        productEditModalState.pendingPreviewUrls.forEach((previewUrl, index) => {
            const button = document.createElement('button');
            button.type = 'button';
            button.className = 'modal-thumb js-modal-file-thumb';
            button.dataset.index = String(index);
            button.innerHTML = `
                <img src="${previewUrl}" alt="${labelPrefix} ${index + 1}">
                <span class="modal-thumb-label">${labelPrefix} ${index + 1}</span>
            `;
            refs.thumbnailGrid.appendChild(button);
        });
    }

    if (refs.galleryCount) {
        refs.galleryCount.textContent = `${labelPrefix}: ${selectedFiles.length}`;
    }

    updateModalFilePreview(0);
}

function renderModalExistingImagePreview(imagePath) {
    const { refs } = productEditModalState;
    const cleanPath = String(imagePath || '').trim();

    clearPendingFilePreviews();
    if (!cleanPath) {
        renderModalThumbnails(productEditModalState.activeImages);
        updateModalGalleryMeta(productEditModalState.activeImages);
        updateModalPreview();
        return;
    }

    const imageUrl = getProductImageUrl(cleanPath);
    if (refs.thumbnailGrid) {
        refs.thumbnailGrid.innerHTML = `
            <button type="button" class="modal-thumb js-modal-existing-thumb is-active">
                <img src="${imageUrl}" alt="Imagen existente seleccionada">
                <span class="modal-thumb-label">Imagen existente</span>
            </button>
        `;
    }

    if (refs.previewImage && refs.previewEmpty) {
        refs.previewImage.src = imageUrl;
        refs.previewImage.classList.remove('d-none');
        refs.previewEmpty.classList.add('d-none');
    }

    if (refs.galleryCount) {
        refs.galleryCount.textContent = 'Imagen existente';
    }
}

function renderModalThumbnails(images) {
    const { refs } = productEditModalState;
    if (!refs.thumbnailGrid) {
        return;
    }

    refs.thumbnailGrid.innerHTML = '';

    if (!Array.isArray(images) || images.length === 0) {
        const emptyThumb = document.createElement('div');
        emptyThumb.className = 'modal-thumb';
        emptyThumb.innerHTML = `
            <div class="modal-thumb-placeholder">Sin imágenes</div>
            <span class="modal-thumb-label">Galería vacía</span>
        `;
        refs.thumbnailGrid.appendChild(emptyThumb);
        return;
    }

    images.forEach((imagePath, index) => {
        const button = document.createElement('button');
        button.type = 'button';
        button.className = 'modal-thumb js-modal-thumb';
        button.dataset.index = String(index);
        button.innerHTML = `
            <img src="${getProductImageUrl(imagePath)}" alt="Imagen ${index + 1}">
            <span class="modal-thumb-label">Imagen ${index + 1}</span>
        `;
        refs.thumbnailGrid.appendChild(button);
    });
}

function renderModalRemoveOptions(images) {
    const { refs } = productEditModalState;
    if (!refs.removeSelect || !refs.removeButton) {
        return;
    }

    refs.removeSelect.innerHTML = '<option value="">Selecciona imagen a quitar</option>';

    if (!Array.isArray(images) || images.length === 0) {
        refs.removeSelect.disabled = true;
        refs.removeButton.disabled = true;
        return;
    }

    images.forEach((imagePath, index) => {
        const option = document.createElement('option');
        option.value = imagePath;
        option.textContent = `Imagen ${index + 1}`;
        refs.removeSelect.appendChild(option);
    });

    refs.removeSelect.disabled = false;
    refs.removeButton.disabled = false;
}

function updateModalGalleryMeta(images) {
    const { refs, maxImages } = productEditModalState;
    const totalImages = Array.isArray(images) ? images.length : 0;
    const remainingImages = Math.max(0, maxImages - totalImages);
    const canAddMore = totalImages < maxImages;

    if (refs.galleryCount) {
        refs.galleryCount.textContent = `${totalImages}/${maxImages} imágenes`;
    }

    if (refs.addHelp) {
        refs.addHelp.textContent = canAddMore
            ? `Puedes agregar hasta ${remainingImages} imagen(es) más a esta galería.`
            : 'Este producto ya alcanzó el máximo permitido de imágenes.';
    }

    if (refs.addInput) {
        refs.addInput.disabled = !canAddMore;
    }
    if (refs.addButton) {
        refs.addButton.disabled = !canAddMore;
    }
}

function populateProductEditModal(product) {
    const { refs } = productEditModalState;
    if (!refs.editForm) {
        return;
    }

    const images = Array.isArray(product.imagenes) ? product.imagenes : [];
    clearPendingFilePreviews();
    productEditModalState.activeImages = images;
    productEditModalState.activeIndex = 0;

    refs.modalTitle.textContent = product.nombre || 'Editar producto';
    refs.modalProductId.textContent = `ID del producto: ${product.id || ''}`;
    refs.nameInput.value = product.nombre || '';
    refs.descriptionInput.value = product.descripcion || '';
    refs.priceInput.value = product.precio ?? '';
    refs.stockInput.value = product.stock ?? '';
    refs.forceSelect.value = product.fuerza || '';
    refs.intendenciaSelect.value = product.intendencia || '';

    refs.editForm.action = product.editUrl || '#';
    refs.replaceForm.action = product.replaceImagesUrl || '#';
    refs.addForm.action = product.addImagesUrl || '#';
    refs.removeForm.action = product.removeImageUrl || '#';
    refs.deleteForm.action = product.deleteUrl || '#';

    refs.replaceForm.reset();
    refs.addForm.reset();
    refs.removeForm.reset();

    renderModalThumbnails(images);
    renderModalRemoveOptions(images);
    updateModalGalleryMeta(images);
    updateModalPreview();
}

document.addEventListener('click', (event) => {
    const openModalButton = event.target.closest('.js-open-product-modal');
    if (openModalButton && productEditModalState.modal) {
        const rawProduct = openModalButton.dataset.product || '{}';
        let product = {};
        try {
            product = JSON.parse(rawProduct);
        } catch (error) {
            product = {};
        }

        populateProductEditModal(product);
        productEditModalState.modal.show();
        return;
    }

    const forceArrow = event.target.closest('.force-arrow');
    if (forceArrow) {
        const trackId = forceArrow.dataset.trackId;
        const direction = forceArrow.dataset.direction === 'prev' ? 'prev' : 'next';
        const track = trackId ? document.getElementById(trackId) : null;
        if (!track) {
            return;
        }

        const item = track.querySelector('.force-product-item');
        const styles = window.getComputedStyle(track);
        const gapRaw = styles.gap || styles.columnGap || '0';
        const gap = Number.parseFloat(gapRaw) || 0;
        const step = item ? (item.getBoundingClientRect().width + gap) : track.clientWidth;
        const maxScrollLeft = Math.max(0, track.scrollWidth - track.clientWidth);
        const maxIndex = step > 0 ? Math.round(maxScrollLeft / step) : 0;
        const currentIndex = step > 0 ? Math.round(track.scrollLeft / step) : 0;

        let targetIndex = currentIndex;
        if (direction === 'next') {
            targetIndex = currentIndex >= maxIndex ? 0 : currentIndex + 1;
        } else {
            targetIndex = currentIndex <= 0 ? maxIndex : currentIndex - 1;
        }

        const targetLeft = Math.max(0, Math.min(maxScrollLeft, targetIndex * step));

        track.scrollTo({ left: targetLeft, behavior: 'smooth' });
        scheduleForceArrowUpdate();
        setTimeout(scheduleForceArrowUpdate, 240);
        return;
    }

    const modalThumb = event.target.closest('.js-modal-thumb');
    if (modalThumb) {
        const nextIndex = Number.parseInt(modalThumb.dataset.index || '0', 10);
        productEditModalState.activeIndex = Number.isNaN(nextIndex) ? 0 : nextIndex;
        updateModalPreview();
        return;
    }

    const modalFileThumb = event.target.closest('.js-modal-file-thumb');
    if (modalFileThumb) {
        const nextIndex = Number.parseInt(modalFileThumb.dataset.index || '0', 10);
        updateModalFilePreview(Number.isNaN(nextIndex) ? 0 : nextIndex);
        return;
    }

    const navButton = event.target.closest('.image-nav');
    if (!navButton) {
        return;
    }

    const imageWrap = navButton.closest('.product-image-wrap');
    if (!imageWrap) {
        return;
    }

    const imageElement = imageWrap.querySelector('.js-product-image');
    if (!imageElement) {
        return;
    }

    let images = [];
    try {
        images = JSON.parse(imageElement.dataset.images || '[]');
    } catch (error) {
        images = [];
    }

    if (!Array.isArray(images) || images.length <= 1) {
        return;
    }

    let currentIndex = Number.parseInt(imageElement.dataset.index || '0', 10);
    if (Number.isNaN(currentIndex)) {
        currentIndex = 0;
    }

    const action = navButton.dataset.action === 'prev' ? 'prev' : 'next';
    if (action === 'next') {
        currentIndex = (currentIndex + 1) % images.length;
    } else {
        currentIndex = (currentIndex - 1 + images.length) % images.length;
    }

    const staticPrefix = imageElement.dataset.staticPrefix || '/static/';
    const nextImagePath = String(images[currentIndex] || '').replace(/^\/+/, '');
    imageElement.src = `${staticPrefix}${nextImagePath}`;
    imageElement.dataset.index = String(currentIndex);

    const counter = imageWrap.querySelector('.js-current-index');
    if (counter) {
        counter.textContent = String(currentIndex + 1);
    }
});

document.addEventListener('DOMContentLoaded', () => {
    const tracks = Array.from(document.querySelectorAll('.force-track'));
    tracks.forEach((track) => {
        track.addEventListener('scroll', scheduleForceArrowUpdate, { passive: true });
    });

    window.addEventListener('resize', scheduleForceArrowUpdate);
    window.addEventListener('orientationchange', scheduleForceArrowUpdate);

    if ('ResizeObserver' in window) {
        const observer = new ResizeObserver(() => {
            scheduleForceArrowUpdate();
        });

        tracks.forEach((track) => observer.observe(track));
        document.querySelectorAll('.force-track-wrap, .product-panel').forEach((block) => {
            observer.observe(block);
        });
    }

    const modalElement = document.getElementById('productEditModal');
    if (modalElement && window.bootstrap) {
        const modalBody = modalElement.querySelector('.modal-body');
        productEditModalState.element = modalElement;
        productEditModalState.modal = window.bootstrap.Modal.getOrCreateInstance(modalElement);
        productEditModalState.staticPrefix = modalBody ? (modalBody.dataset.staticPrefix || '/static/') : '/static/';
        productEditModalState.maxImages = Number.parseInt(
            modalBody ? (modalBody.dataset.maxImages || '0') : '0',
            10
        ) || 0;
        productEditModalState.refs = {
            modalTitle: modalElement.querySelector('.modal-title'),
            modalProductId: modalElement.querySelector('.js-modal-product-id'),
            editForm: document.getElementById('modalProductEditForm'),
            replaceForm: document.getElementById('modalReplaceImagesForm'),
            addForm: document.getElementById('modalAddImagesForm'),
            removeForm: document.getElementById('modalRemoveImageForm'),
            deleteForm: document.getElementById('modalProductDeleteForm'),
            replaceInput: document.querySelector('#modalReplaceImagesForm input[type="file"]'),
            existingSelect: modalElement.querySelector('.js-modal-existing-image-select'),
            nameInput: document.getElementById('modalProductName'),
            descriptionInput: document.getElementById('modalProductDescription'),
            priceInput: document.getElementById('modalProductPrice'),
            stockInput: document.getElementById('modalProductStock'),
            forceSelect: document.getElementById('modalProductForce'),
            intendenciaSelect: document.getElementById('modalProductIntendencia'),
            previewImage: modalElement.querySelector('.js-modal-preview-image'),
            previewEmpty: modalElement.querySelector('.js-modal-preview-empty'),
            thumbnailGrid: modalElement.querySelector('.js-modal-thumbnail-grid'),
            galleryCount: modalElement.querySelector('.js-modal-gallery-count'),
            addHelp: modalElement.querySelector('.js-modal-add-help'),
            addInput: modalElement.querySelector('.js-modal-add-input'),
            addButton: modalElement.querySelector('.js-modal-add-button'),
            removeSelect: modalElement.querySelector('.js-modal-remove-select'),
            removeButton: modalElement.querySelector('.js-modal-remove-button'),
        };

        if (productEditModalState.refs.replaceInput) {
            productEditModalState.refs.replaceInput.addEventListener('change', (event) => {
                if (productEditModalState.refs.existingSelect) {
                    productEditModalState.refs.existingSelect.value = '';
                }
                renderModalFileSelectionPreview(event.target.files, 'Nueva imagen');
            });
        }

        if (productEditModalState.refs.existingSelect) {
            productEditModalState.refs.existingSelect.addEventListener('change', (event) => {
                if (productEditModalState.refs.replaceInput) {
                    productEditModalState.refs.replaceInput.value = '';
                }
                renderModalExistingImagePreview(event.target.value);
            });
        }

        if (productEditModalState.refs.addInput) {
            productEditModalState.refs.addInput.addEventListener('change', (event) => {
                renderModalFileSelectionPreview(event.target.files, 'Imagen por agregar');
            });
        }

        modalElement.addEventListener('hidden.bs.modal', () => {
            clearPendingFilePreviews();
            productEditModalState.activeImages = [];
            productEditModalState.activeIndex = 0;
            if (productEditModalState.refs.replaceForm) {
                productEditModalState.refs.replaceForm.reset();
            }
            if (productEditModalState.refs.addForm) {
                productEditModalState.refs.addForm.reset();
            }
            if (productEditModalState.refs.removeForm) {
                productEditModalState.refs.removeForm.reset();
            }
        });
    }

    scheduleForceArrowUpdate();
});
