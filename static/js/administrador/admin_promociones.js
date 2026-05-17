function updatePromoForceArrows() {
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

let promoForceArrowAnimationFrame = null;
function schedulePromoForceArrowUpdate() {
    if (promoForceArrowAnimationFrame !== null) {
        return;
    }

    promoForceArrowAnimationFrame = window.requestAnimationFrame(() => {
        promoForceArrowAnimationFrame = null;
        updatePromoForceArrows();
    });
}

const promoModalState = {
    modal: null,
    staticPrefix: '/static/',
    refs: {},
};

function promoImageUrl(imagePath) {
    const cleanPath = String(imagePath || '').replace(/^\/+/, '');
    return `${promoModalState.staticPrefix}${cleanPath}`;
}

function formatPromoPrice(value) {
    const numericValue = Number.parseFloat(value || '0');
    if (Number.isNaN(numericValue)) {
        return '';
    }

    return new Intl.NumberFormat('es-CO', {
        style: 'currency',
        currency: 'COP',
        minimumFractionDigits: 2,
    }).format(numericValue);
}

function fillPromoModal(product) {
    const { refs } = promoModalState;
    if (!refs.form) {
        return;
    }

    refs.form.action = product.postUrl || '#';
    refs.form.dataset.productPrice = String(product.precio || '0');
    refs.productId.value = product.id || '';
    refs.nombre.value = '';
    refs.descripcion.value = '';
    refs.tipo.value = 'porcentaje';
    refs.valor.value = '';
    refs.valor.min = '0.01';
    refs.valor.removeAttribute('max');
    refs.fechaInicio.value = '';
    refs.fechaFin.value = '';
    refs.codigo.value = '';
    refs.activo.checked = true;

    refs.modalProductId.textContent = `Producto ID: ${product.id || ''}`;
    refs.force.textContent = `${product.fuerza || 'Sin fuerza'}${product.id ? ` · ID ${product.id}` : ''}`;
    refs.name.textContent = product.nombre || 'Producto';
    refs.price.textContent = formatPromoPrice(product.precio);
    refs.intendencia.textContent = product.intendencia || 'Sin intendencia';

    if (product.imagen_url) {
        refs.image.src = promoImageUrl(product.imagen_url);
        refs.image.classList.remove('d-none');
        refs.imageEmpty.classList.add('d-none');
    } else {
        refs.image.src = '';
        refs.image.classList.add('d-none');
        refs.imageEmpty.classList.remove('d-none');
    }

    updateDiscountLimits();
}

function updateDiscountLimits() {
    const { refs } = promoModalState;
    if (!refs.tipo || !refs.valor || !refs.form) {
        return;
    }

    const productPrice = Number.parseFloat(refs.form.dataset.productPrice || '0') || 0;
    refs.valor.min = '0.01';
    refs.valor.setCustomValidity('');

    if (refs.tipo.value === 'porcentaje') {
        refs.valor.max = '100';
    } else if (productPrice > 0) {
        refs.valor.max = String(Math.max(0.01, productPrice - 0.01));
    } else {
        refs.valor.removeAttribute('max');
    }
}

function validatePromoForm(event) {
    const { refs } = promoModalState;
    if (!refs.form) {
        return;
    }

    [refs.productId, refs.tipo, refs.valor, refs.fechaInicio, refs.fechaFin, refs.codigo].forEach((field) => {
        if (field) {
            field.setCustomValidity('');
        }
    });

    const productPrice = Number.parseFloat(refs.form.dataset.productPrice || '0') || 0;
    const discountValue = Number.parseFloat(refs.valor.value || '0');
    const startDate = refs.fechaInicio.value;
    const endDate = refs.fechaFin.value;
    const code = (refs.codigo.value || '').trim();

    if (!refs.productId.value) {
        refs.productId.setCustomValidity('Selecciona un producto para crear la promoción.');
    } else if (!discountValue || discountValue <= 0) {
        refs.valor.setCustomValidity('El descuento debe ser mayor a cero.');
    } else if (refs.tipo.value === 'porcentaje' && discountValue > 100) {
        refs.valor.setCustomValidity('El porcentaje no puede superar el 100%.');
    } else if (refs.tipo.value === 'valor_fijo' && productPrice > 0 && discountValue >= productPrice) {
        refs.valor.setCustomValidity('El descuento fijo debe ser inferior al precio de la prenda.');
    } else if (!startDate) {
        refs.fechaInicio.setCustomValidity('La fecha de inicio es obligatoria.');
    } else if (!endDate) {
        refs.fechaFin.setCustomValidity('La fecha de finalización es obligatoria.');
    } else if (startDate > endDate) {
        refs.fechaFin.setCustomValidity('La fecha de fin no puede ser anterior al inicio.');
    } else if (code && !/^[A-Z0-9_-]{3,30}$/i.test(code)) {
        refs.codigo.setCustomValidity('El código debe tener de 3 a 30 caracteres: letras, números, guion o guion bajo.');
    }

    if (!refs.form.checkValidity()) {
        event.preventDefault();
        refs.form.reportValidity();
    }
}

document.addEventListener('click', (event) => {
    const openModalButton = event.target.closest('.js-open-promo-modal');
    if (openModalButton && promoModalState.modal) {
        let product = {};
        try {
            product = JSON.parse(openModalButton.dataset.product || '{}');
        } catch (error) {
            product = {};
        }

        fillPromoModal(product);
        promoModalState.modal.show();
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
        schedulePromoForceArrowUpdate();
        setTimeout(schedulePromoForceArrowUpdate, 240);
        return;
    }

    const navButton = event.target.closest('.image-nav');
    if (!navButton) {
        return;
    }

    const imageWrap = navButton.closest('.promo-image-wrap');
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
        track.addEventListener('scroll', schedulePromoForceArrowUpdate, { passive: true });
    });

    window.addEventListener('resize', schedulePromoForceArrowUpdate);
    window.addEventListener('orientationchange', schedulePromoForceArrowUpdate);

    if ('ResizeObserver' in window) {
        const observer = new ResizeObserver(() => {
            schedulePromoForceArrowUpdate();
        });

        tracks.forEach((track) => observer.observe(track));
        document.querySelectorAll('.force-track-wrap, .promo-panel').forEach((block) => {
            observer.observe(block);
        });
    }

    const modalElement = document.getElementById('promoCreateModal');
    if (modalElement && window.bootstrap) {
        const modalBody = modalElement.querySelector('.modal-body');
        promoModalState.modal = window.bootstrap.Modal.getOrCreateInstance(modalElement);
        promoModalState.staticPrefix = modalBody ? (modalBody.dataset.staticPrefix || '/static/') : '/static/';
        promoModalState.refs = {
            form: document.getElementById('promoCreateForm'),
            productId: document.getElementById('promoProductId'),
            nombre: document.getElementById('promoNombreInput'),
            descripcion: document.getElementById('promoDescripcionInput'),
            tipo: document.getElementById('promoTipoInput'),
            valor: document.getElementById('promoValorInput'),
            fechaInicio: document.getElementById('promoInicioInput'),
            fechaFin: document.getElementById('promoFinInput'),
            codigo: document.getElementById('promoCodigoInput'),
            activo: document.getElementById('promoActivoInput'),
            modalProductId: modalElement.querySelector('.js-promo-modal-product-id'),
            force: modalElement.querySelector('.js-promo-modal-force'),
            name: modalElement.querySelector('.js-promo-modal-name'),
            price: modalElement.querySelector('.js-promo-modal-price'),
            intendencia: modalElement.querySelector('.js-promo-modal-intendencia'),
            image: modalElement.querySelector('.js-promo-modal-image'),
            imageEmpty: modalElement.querySelector('.js-promo-modal-image-empty'),
        };

        modalElement.addEventListener('hidden.bs.modal', () => {
            if (promoModalState.refs.form) {
                promoModalState.refs.form.reset();
                promoModalState.refs.form.dataset.productPrice = '0';
            }
        });

        if (promoModalState.refs.tipo) {
            promoModalState.refs.tipo.addEventListener('change', updateDiscountLimits);
        }
        if (promoModalState.refs.form) {
            promoModalState.refs.form.addEventListener('submit', validatePromoForm);
        }
    }

    schedulePromoForceArrowUpdate();
});
