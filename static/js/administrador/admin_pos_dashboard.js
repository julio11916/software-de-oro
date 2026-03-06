// Variables globales que serán inicializadas desde el HTML
let CURRENCY_CODE;
let catalog;
let filteredCatalog = [];
let cart = [];

// Elementos DOM
let catalogBody;
let cartBody;
let cartEmpty;
let itemsJson;
let totalItems;
let totalAmount;
let searchInput;
let checkoutForm;
let imagePreviewModal;
let imagePreviewTarget;
let imagePreviewTitle;

// Inicializar el sistema POS
function initPOS(currencyCode, productos) {
    CURRENCY_CODE = currencyCode;
    catalog = productos;
    filteredCatalog = [...catalog];
    
    // Obtener elementos DOM
    catalogBody = document.getElementById('catalogBody');
    cartBody = document.getElementById('cartBody');
    cartEmpty = document.getElementById('cartEmpty');
    itemsJson = document.getElementById('itemsJson');
    totalItems = document.getElementById('totalItems');
    totalAmount = document.getElementById('totalAmount');
    searchInput = document.getElementById('searchInput');
    checkoutForm = document.getElementById('checkoutForm');
    imagePreviewModal = new bootstrap.Modal(document.getElementById('imagePreviewModal'));
    imagePreviewTarget = document.getElementById('imagePreviewTarget');
    imagePreviewTitle = document.getElementById('imagePreviewTitle');
    
    // Configurar event listeners
    searchInput.addEventListener('input', handleSearch);
    checkoutForm.addEventListener('submit', handleCheckout);
    
    // Renderizar inicial
    renderCatalog();
    renderCart();
}

function money(v) {
    const amount = Number(v || 0).toLocaleString('es-CO', {
        minimumFractionDigits: 2,
        maximumFractionDigits: 2
    });
    return `${CURRENCY_CODE} ${amount}`;
}

function renderCatalog() {
    if (!filteredCatalog.length) {
        catalogBody.innerHTML = '<tr><td colspan="7" class="text-center text-muted py-3">No hay productos para mostrar.</td></tr>';
        return;
    }

    catalogBody.innerHTML = filteredCatalog.map(p => {
        const disabled = Number(p.stock) <= 0 ? 'disabled' : '';
        const badge = Number(p.stock) > 0 ? 'bg-success-subtle text-success' : 'bg-danger-subtle text-danger';
        const imageCell = p.imagen_url
            ? `<img src="/static/${p.imagen_url}" alt="${p.nombre}" class="pos-thumb"
                onclick="openImagePreview('/static/${p.imagen_url}', '${String(p.nombre).replace(/'/g, "\\'")}')">`
            : '<span class="pos-thumb-placeholder">SIN IMG</span>';
        return `
            <tr class="product-row">
                <td>${p.id_producto}</td>
                <td>${imageCell}</td>
                <td>${p.nombre}</td>
                <td>${money(p.precio)}</td>
                <td><span class="badge ${badge} stock-badge">${Number(p.stock)}</span></td>
                <td>
                    <input id="qty-${p.id_producto}" type="number" class="form-control form-control-sm"
                        min="1" max="${Number(p.stock)}" value="1" ${disabled}>
                </td>
                <td>
                    <button type="button" class="btn btn-sm btn-outline-primary" ${disabled}
                        onclick="addToCart(${p.id_producto})">Agregar</button>
                </td>
            </tr>
        `;
    }).join('');
}

function renderCart() {
    if (!cart.length) {
        cartBody.innerHTML = '';
        cartEmpty.style.display = 'block';
    } else {
        cartEmpty.style.display = 'none';
        cartBody.innerHTML = cart.map(item => `
            <tr>
                <td>
                    ${item.imagen_url
                        ? `<img src="/static/${item.imagen_url}" alt="${item.nombre}" class="pos-thumb"
                            onclick="openImagePreview('/static/${item.imagen_url}', '${String(item.nombre).replace(/'/g, "\\'")}')">`
                        : '<span class="pos-thumb-placeholder">SIN IMG</span>'}
                </td>
                <td>${item.nombre}</td>
                <td>
                    <input type="number" class="form-control form-control-sm"
                        min="1" max="${item.stock}" value="${item.cantidad}"
                        onchange="updateQty(${item.id_producto}, this.value)">
                </td>
                <td>${money(item.cantidad * item.precio)}</td>
                <td class="text-end">
                    <button type="button" class="btn btn-sm btn-outline-danger"
                        onclick="removeFromCart(${item.id_producto})">Quitar</button>
                </td>
            </tr>
        `).join('');
    }

    const items = cart.reduce((acc, it) => acc + Number(it.cantidad), 0);
    const total = cart.reduce((acc, it) => acc + (Number(it.cantidad) * Number(it.precio)), 0);

    totalItems.textContent = items;
    totalAmount.textContent = money(total);
    itemsJson.value = JSON.stringify(cart.map(({ id_producto, cantidad }) => ({ id_producto, cantidad })));
}

function addToCart(idProducto) {
    const product = catalog.find(p => Number(p.id_producto) === Number(idProducto));
    if (!product) return;

    const qtyInput = document.getElementById(`qty-${idProducto}`);
    const qty = Number(qtyInput ? qtyInput.value : 1);
    if (!qty || qty < 1) return;

    const existing = cart.find(i => Number(i.id_producto) === Number(idProducto));
    if (existing) {
        const newQty = Number(existing.cantidad) + qty;
        existing.cantidad = Math.min(newQty, Number(existing.stock));
    } else {
        cart.push({
            id_producto: Number(product.id_producto),
            nombre: product.nombre,
            imagen_url: product.imagen_url || '',
            precio: Number(product.precio),
            stock: Number(product.stock),
            cantidad: Math.min(qty, Number(product.stock))
        });
    }
    renderCart();
}

function updateQty(idProducto, value) {
    const item = cart.find(i => Number(i.id_producto) === Number(idProducto));
    if (!item) return;
    const qty = Number(value);
    if (!qty || qty < 1) {
        item.cantidad = 1;
    } else if (qty > Number(item.stock)) {
        item.cantidad = Number(item.stock);
    } else {
        item.cantidad = qty;
    }
    renderCart();
}

function removeFromCart(idProducto) {
    cart = cart.filter(i => Number(i.id_producto) !== Number(idProducto));
    renderCart();
}

function openImagePreview(src, title) {
    imagePreviewTarget.src = src;
    imagePreviewTitle.textContent = title || 'Vista previa';
    imagePreviewModal.show();
}

function handleSearch(e) {
    const term = e.target.value.trim().toLowerCase();
    filteredCatalog = catalog.filter(p =>
        String(p.id_producto).includes(term) ||
        String(p.nombre).toLowerCase().includes(term)
    );
    renderCatalog();
}

function handleCheckout(e) {
    if (!cart.length) {
        e.preventDefault();
        alert('Debes agregar al menos un producto.');
    }
}
