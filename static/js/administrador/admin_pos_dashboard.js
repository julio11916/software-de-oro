let CURRENCY_CODE;
let catalog;
let filteredCatalog = [];
let cart = [];
let tallasCatalog = [];

let catalogGrid;
let catalogEmpty;
let cartEmpty;
let itemsJson;
let totalItems;
let totalAmount;
let selectedPreview;
let searchInput;
let forceFilter;
let searchBtn;
let checkoutForm;
let clienteNombreInput;
let clienteCorreoInput;
let clienteDocumentoInput;
let clienteTelefonoInput;
let imagePreviewModal;
let imagePreviewTarget;
let imagePreviewTitle;
const EMAIL_REGEX = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
const NAME_REGEX = /^[A-Za-zÁÉÍÓÚáéíóúÑñÜü\s]+$/;
const INTENDENCIAS_SIN_TALLA = new Set([
    'pañoleta', 'pañoletas',
    'panoleta', 'panoletas',
    'gorra', 'gorras',
    'colcha', 'colchas',
    'tendido', 'tendidos',
    'chuspa para ropa sucia', 'chuspas para ropa sucia',
    'funda para almohadas', 'fundas para almohadas',
    'accesorio', 'accesorios',
    'presilla', 'presillas'
]);

function money(value) {
    const amount = Number(value || 0).toLocaleString('es-CO', {
        minimumFractionDigits: 2,
        maximumFractionDigits: 2
    });
    return `${CURRENCY_CODE} ${amount}`;
}

function escapeHtml(value) {
    return String(value ?? '')
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;')
        .replace(/'/g, '&#39;');
}

function staticImagePath(relativePath) {
    return `/static/${String(relativePath || '').replace(/^\/+/, '')}`;
}

function normalizeText(value) {
    return String(value || '').trim().toLowerCase().replace(/\s+/g, ' ');
}

function requiresSize(product) {
    if (typeof product?.requiere_talla === 'boolean') {
        return product.requiere_talla;
    }
    const intendencia = normalizeText(product?.intendencia);
    return !INTENDENCIAS_SIN_TALLA.has(intendencia);
}

function applyFilters() {
    const term = String(searchInput.value || '').trim().toLowerCase();
    const selectedForce = String(forceFilter.value || '').trim().toLowerCase();

    filteredCatalog = catalog.filter((product) => {
        const idText = String(product.id_producto || '').toLowerCase();
        const nameText = String(product.nombre || '').toLowerCase();
        const descText = String(product.descripcion || '').toLowerCase();
        const forceText = String(product.fuerza || '').toLowerCase();

        const matchesTerm = !term ||
            idText.includes(term) ||
            nameText.includes(term) ||
            descText.includes(term);

        const matchesForce = !selectedForce || forceText === selectedForce;
        return matchesTerm && matchesForce;
    });

    renderCatalog();
}

function renderCatalog() {
    if (!filteredCatalog.length) {
        catalogGrid.innerHTML = '';
        catalogEmpty.classList.remove('d-none');
        return;
    }

    catalogEmpty.classList.add('d-none');
    catalogGrid.innerHTML = filteredCatalog.map((product) => {
        const stock = Number(product.stock || 0);
        const basePrice = Number(product.precio_original ?? product.precio ?? 0);
        const salePrice = Number(product.precio_venta ?? product.precio_con_descuento ?? product.precio ?? 0);
        const hasPromo = Boolean(product.promo_activa) && salePrice < basePrice;
        const productRequiresSize = requiresSize(product);
        const disabled = stock <= 0 ? 'disabled' : '';
        const imageMarkup = product.imagen_url
            ? `<img
                    src="${escapeHtml(staticImagePath(product.imagen_url))}"
                    alt="${escapeHtml(product.nombre)}"
                    class="catalog-image js-image-preview"
                    data-src="${escapeHtml(staticImagePath(product.imagen_url))}"
                    data-title="${escapeHtml(product.nombre)}"
               >`
            : '<div class="catalog-image-placeholder">Sin imagen</div>';
        const priceMarkup = hasPromo
            ? `
                <p class="catalog-price mb-0">${money(salePrice)}</p>
                <p class="catalog-price-original mb-1">${money(basePrice)}</p>
                <p class="catalog-promo-name mb-0">${escapeHtml(product.promo_nombre || 'Descuento activo')}</p>
            `
            : `<p class="catalog-price mb-1">${money(salePrice)}</p>`;
        const tallasOptions = tallasCatalog.map((talla) => {
            const tallaTxt = String(talla || '').trim().toUpperCase();
            return `<option value="${escapeHtml(tallaTxt)}">${escapeHtml(tallaTxt)}</option>`;
        }).join('');
        const sizeFieldMarkup = productRequiresSize
            ? `
                <select id="size-${Number(product.id_producto)}" class="form-select form-select-sm" ${disabled}>
                    ${tallasOptions}
                </select>
              `
            : `
                <input type="hidden" id="size-${Number(product.id_producto)}" value="">
                <div class="form-control form-control-sm text-center text-muted">Sin talla</div>
              `;

        return `
            <article class="catalog-card">
                <span class="catalog-top-badge">Producto</span>
                <div class="catalog-image-wrap">${imageMarkup}</div>
                <div class="catalog-body">
                    <h6 class="catalog-name">${escapeHtml(product.nombre)}</h6>
                    ${priceMarkup}
                    <p class="catalog-stock mb-0">Stock: ${stock}</p>
                    <div class="catalog-actions mt-2">
                        <input
                            id="qty-${Number(product.id_producto)}"
                            type="number"
                            class="form-control form-control-sm"
                            min="1"
                            max="${stock}"
                            value="1"
                            ${disabled}
                        >
                        ${sizeFieldMarkup}
                        <button
                            type="button"
                            class="btn btn-primary btn-sm btn-add-pos js-add-to-cart"
                            data-product-id="${Number(product.id_producto)}"
                            ${disabled}
                        >Agregar</button>
                    </div>
                </div>
            </article>
        `;
    }).join('');

    catalogGrid.querySelectorAll('.js-add-to-cart').forEach((button) => {
        button.addEventListener('click', () => {
            addToCart(Number(button.dataset.productId));
        });
    });

    catalogGrid.querySelectorAll('.js-image-preview').forEach((image) => {
        image.addEventListener('click', () => {
            openImagePreview(image.dataset.src || '', image.dataset.title || 'Vista previa');
        });
    });
}

function renderSummary() {
    const itemsCount = cart.reduce((acc, item) => acc + Number(item.cantidad || 0), 0);
    const total = cart.reduce((acc, item) => acc + (Number(item.cantidad || 0) * Number(item.precio || 0)), 0);

    totalItems.textContent = String(itemsCount);
    totalAmount.textContent = money(total);
    itemsJson.value = JSON.stringify(
        cart.map(({ id_producto, cantidad, talla }) => ({
            id_producto,
            cantidad,
            talla: String(talla || '').toUpperCase().trim()
        }))
    );
    cartEmpty.textContent = itemsCount > 0
        ? `${itemsCount} producto(s) seleccionados.`
        : 'Aún no has agregado productos.';

    renderSelectedPreview();
}

function renderSelectedPreview() {
    if (!selectedPreview) {
        return;
    }

    if (!cart.length) {
        selectedPreview.innerHTML = '<p class="selected-empty mb-0">No hay productos seleccionados.</p>';
        return;
    }

    selectedPreview.innerHTML = cart.map((item) => {
        const imageMarkup = item.imagen_url
            ? `<img src="${escapeHtml(staticImagePath(item.imagen_url))}" alt="${escapeHtml(item.nombre)}" class="selected-thumb">`
            : '<div class="selected-thumb selected-thumb-placeholder">IMG</div>';
        const subtotal = money(Number(item.cantidad || 0) * Number(item.precio || 0));
        const tallaLabel = String(item.talla || '').trim() || 'Sin talla';
        return `
            <div class="selected-item">
                <div class="selected-main">
                    ${imageMarkup}
                    <div class="selected-meta">
                        <div class="selected-name">${escapeHtml(item.nombre)}</div>
                        <div class="selected-detail">Talla: ${escapeHtml(tallaLabel)} | Cant: ${Number(item.cantidad || 0)} | ${subtotal}</div>
                    </div>
                </div>
                <button type="button" class="btn btn-sm btn-outline-danger js-remove-selected"
                    data-product-id="${Number(item.id_producto)}"
                    data-talla="${escapeHtml(item.talla || '')}">Quitar</button>
            </div>
        `;
    }).join('');

    selectedPreview.querySelectorAll('.js-remove-selected').forEach((button) => {
        button.addEventListener('click', () => {
            removeFromCart(Number(button.dataset.productId), String(button.dataset.talla || ''));
        });
    });
}

function addToCart(idProducto) {
    const product = catalog.find((item) => Number(item.id_producto) === Number(idProducto));
    if (!product) {
        return;
    }

    const qtyInput = document.getElementById(`qty-${idProducto}`);
    const qty = Number(qtyInput ? qtyInput.value : 1);
    const sizeInput = document.getElementById(`size-${idProducto}`);
    const productRequiresSize = requiresSize(product);
    let talla = String(sizeInput ? sizeInput.value : '').trim().toUpperCase();
    const stock = Number(product.stock || 0);
    if (!qty || qty < 1 || stock <= 0) {
        return;
    }
    if (productRequiresSize) {
        if (!tallasCatalog.includes(talla)) {
            alert('Selecciona una talla valida.');
            return;
        }
    } else {
        talla = '';
    }
    const salePrice = Number(product.precio_venta ?? product.precio_con_descuento ?? product.precio ?? 0);
    const totalActualMismoProducto = cart.reduce((acc, item) => {
        if (Number(item.id_producto) !== Number(idProducto)) {
            return acc;
        }
        return acc + Number(item.cantidad || 0);
    }, 0);
    const disponibleParaAgregar = stock - totalActualMismoProducto;
    if (disponibleParaAgregar <= 0) {
        alert('No hay mas stock disponible para este producto.');
        return;
    }
    const qtyAAgregar = Math.min(qty, disponibleParaAgregar);

    const existing = cart.find((item) => (
        Number(item.id_producto) === Number(idProducto) &&
        String(item.talla || '').trim().toUpperCase() === talla
    ));
    if (existing) {
        existing.cantidad = Number(existing.cantidad) + qtyAAgregar;
    } else {
        cart.push({
            id_producto: Number(product.id_producto),
            nombre: String(product.nombre || ''),
            imagen_url: String(product.imagen_url || ''),
            precio: salePrice,
            stock,
            cantidad: qtyAAgregar,
            talla
        });
    }

    renderSummary();
}

function removeFromCart(idProducto, talla) {
    const tallaNorm = String(talla || '').trim().toUpperCase();
    cart = cart.filter((item) => !(
        Number(item.id_producto) === Number(idProducto) &&
        String(item.talla || '').trim().toUpperCase() === tallaNorm
    ));
    renderSummary();
}

function openImagePreview(src, title) {
    imagePreviewTarget.src = src;
    imagePreviewTitle.textContent = title || 'Vista previa';
    imagePreviewModal.show();
}

function handleCheckout(event) {
    if (!cart.length) {
        event.preventDefault();
        alert('Debes agregar al menos un producto.');
        return;
    }

    sanitizeNameInput(clienteNombreInput);
    sanitizeNumericInput(clienteDocumentoInput);
    sanitizeNumericInput(clienteTelefonoInput, 10);

    const nombre = String(clienteNombreInput ? clienteNombreInput.value : '').trim();
    const correo = String(clienteCorreoInput ? clienteCorreoInput.value : '').trim();
    const documento = String(clienteDocumentoInput ? clienteDocumentoInput.value : '').trim();
    const telefono = String(clienteTelefonoInput ? clienteTelefonoInput.value : '').trim();

    if (!nombre || !correo || !documento || !telefono) {
        event.preventDefault();
        alert('Debes completar todos los datos del cliente.');
        return;
    }

    if (!NAME_REGEX.test(nombre)) {
        event.preventDefault();
        alert('El nombre solo puede contener letras y espacios.');
        if (clienteNombreInput) {
            clienteNombreInput.focus();
        }
        return;
    }

    if (!EMAIL_REGEX.test(correo)) {
        event.preventDefault();
        alert('Debes ingresar un correo electrónico válido.');
        if (clienteCorreoInput) {
            clienteCorreoInput.focus();
        }
        return;
    }

    if (!/^\d+$/.test(documento)) {
        event.preventDefault();
        alert('La cédula solo puede contener números.');
        if (clienteDocumentoInput) {
            clienteDocumentoInput.focus();
        }
        return;
    }

    if (!/^\d{1,10}$/.test(telefono)) {
        event.preventDefault();
        alert('El teléfono solo puede contener números y máximo 10 dígitos.');
        if (clienteTelefonoInput) {
            clienteTelefonoInput.focus();
        }
    }
}

function sanitizeNumericInput(input, maxLength = null) {
    if (!input) {
        return;
    }
    let cleaned = String(input.value || '').replace(/\D+/g, '');
    if (maxLength && cleaned.length > maxLength) {
        cleaned = cleaned.slice(0, maxLength);
    }
    if (input.value !== cleaned) {
        input.value = cleaned;
    }
}

function sanitizeNameInput(input) {
    if (!input) {
        return;
    }
    let cleaned = String(input.value || '').replace(/[^A-Za-zÁÉÍÓÚáéíóúÑñÜü\s]+/g, '');
    cleaned = cleaned.replace(/\s{2,}/g, ' ');
    if (input.value !== cleaned) {
        input.value = cleaned;
    }
}

function initPOS(currencyCode, productos, tallas) {
    CURRENCY_CODE = currencyCode;
    catalog = Array.isArray(productos) ? productos : [];
    filteredCatalog = [...catalog];
    tallasCatalog = Array.isArray(tallas)
        ? tallas.map((t) => String(t || '').trim().toUpperCase()).filter(Boolean)
        : [];
    if (!tallasCatalog.length) {
        tallasCatalog = ['XS', 'S', 'M', 'L', 'XL', 'XXL', 'XXXL'];
    }

    catalogGrid = document.getElementById('catalogGrid');
    catalogEmpty = document.getElementById('catalogEmpty');
    cartEmpty = document.getElementById('cartEmpty');
    selectedPreview = document.getElementById('selectedPreview');
    itemsJson = document.getElementById('itemsJson');
    totalItems = document.getElementById('totalItems');
    totalAmount = document.getElementById('totalAmount');
    searchInput = document.getElementById('searchInput');
    forceFilter = document.getElementById('forceFilter');
    searchBtn = document.getElementById('searchBtn');
    checkoutForm = document.getElementById('checkoutForm');
    clienteNombreInput = document.getElementById('clienteNombreInput');
    clienteCorreoInput = document.getElementById('clienteCorreoInput');
    clienteDocumentoInput = document.getElementById('clienteDocumentoInput');
    clienteTelefonoInput = document.getElementById('clienteTelefonoInput');
    imagePreviewModal = new bootstrap.Modal(document.getElementById('imagePreviewModal'));
    imagePreviewTarget = document.getElementById('imagePreviewTarget');
    imagePreviewTitle = document.getElementById('imagePreviewTitle');

    searchInput.addEventListener('input', applyFilters);
    forceFilter.addEventListener('change', applyFilters);
    searchBtn.addEventListener('click', applyFilters);
    checkoutForm.addEventListener('submit', handleCheckout);
    if (clienteNombreInput) {
        clienteNombreInput.addEventListener('input', () => sanitizeNameInput(clienteNombreInput));
    }
    if (clienteDocumentoInput) {
        clienteDocumentoInput.addEventListener('input', () => sanitizeNumericInput(clienteDocumentoInput));
    }
    if (clienteTelefonoInput) {
        clienteTelefonoInput.addEventListener('input', () => sanitizeNumericInput(clienteTelefonoInput, 10));
    }

    renderCatalog();
    renderSummary();
}

document.addEventListener('DOMContentLoaded', () => {
    const posData = document.getElementById('posData');
    if (!posData) {
        return;
    }

    const currencyCode = JSON.parse(posData.dataset.currencyCode || '"COP"');
    const productos = JSON.parse(posData.dataset.productos || '[]');
    const tallas = JSON.parse(posData.dataset.tallas || '[]');
    initPOS(currencyCode, productos, tallas);
});
