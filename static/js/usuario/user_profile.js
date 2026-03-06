function toggleUserMenu() {
    document.getElementById('userDropdown').classList.toggle('show');
}

// Cerrar dropdown al hacer clic fuera
window.addEventListener('click', function (e) {
    if (!e.target.matches('.user-dropdown-btn') && !e.target.closest('.user-dropdown')) {
        var dropdown = document.getElementById('userDropdown');
        if (dropdown.classList.contains('show')) {
            dropdown.classList.remove('show');
        }
    }
});

// Funciones de Verificación de Email
function showMessage(message, type) {
    const container = document.getElementById('messageContainer');
    const alertClass = type === 'success' ? 'alert-success' : 'alert-danger';
    const icon = type === 'success' ? 'fa-check-circle' : 'fa-exclamation-circle';

    container.innerHTML = `
        <div class="alert ${alertClass} alert-dismissible fade show" role="alert">
            <i class="fas ${icon} me-2"></i>${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        </div>
    `;
}

function enviarCodigoVerificacion() {
    const btn = document.getElementById('btnEnviarCodigo');
    btn.disabled = true;
    btn.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Enviando...';

    fetch('/user/send-verification-code', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        }
    })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                // Mostrar el paso 2
                document.getElementById('stepSendCode').style.display = 'none';
                document.getElementById('stepVerifyCode').style.display = 'block';
                showMessage(data.message, 'success');
            } else {
                showMessage(data.message, 'error');
                btn.disabled = false;
                btn.innerHTML = '<i class="fas fa-paper-plane me-2"></i>Enviar Código';
            }
        })
        .catch(error => {
            console.error('Error:', error);
            showMessage('Error al enviar el código. Intenta nuevamente.', 'error');
            btn.disabled = false;
            btn.innerHTML = '<i class="fas fa-paper-plane me-2"></i>Enviar Código';
        });
}

function verificarCodigo(event) {
    event.preventDefault();

    // Obtener código y eliminar todos los espacios
    const codigoInput = document.getElementById('codigoVerificacion');
    const codigo = codigoInput.value.replace(/\s/g, '').trim();

    // Validar que tenga exactamente 6 dígitos
    if (codigo.length !== 6 || !/^\d{6}$/.test(codigo)) {
        showMessage('El código debe tener exactamente 6 dígitos', 'error');
        return;
    }

    const btn = document.getElementById('btnVerificar');

    btn.disabled = true;
    btn.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Verificando...';

    fetch('/user/verify-email', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ code: codigo })
    })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                showMessage(data.message, 'success');
                setTimeout(() => {
                    location.reload();
                }, 1500);
            } else {
                showMessage(data.message, 'error');
                btn.disabled = false;
                btn.innerHTML = '<i class="fas fa-check me-2"></i>Verificar';
                codigoInput.value = '';
            }
        })
        .catch(error => {
            console.error('Error:', error);
            showMessage('Error al verificar el código. Intenta nuevamente.', 'error');
            btn.disabled = false;
            btn.innerHTML = '<i class="fas fa-check me-2"></i>Verificar';
        });
}

function reenviarCodigo() {
    document.getElementById('codigoVerificacion').value = '';
    document.getElementById('messageContainer').innerHTML = '';
    enviarCodigoVerificacion();
}

// Resetear el modal cuando se cierra
document.getElementById('modalVerificacion').addEventListener('hidden.bs.modal', function () {
    document.getElementById('stepSendCode').style.display = 'block';
    document.getElementById('stepVerifyCode').style.display = 'none';
    document.getElementById('codigoVerificacion').value = '';
    document.getElementById('messageContainer').innerHTML = '';
    document.getElementById('btnEnviarCodigo').disabled = false;
    document.getElementById('btnEnviarCodigo').innerHTML = '<i class="fas fa-paper-plane me-2"></i>Enviar Código';
});

// Configurar el campo de código cuando el modal se muestra
document.getElementById('modalVerificacion').addEventListener('shown.bs.modal', function () {
    setupCodigoInput();
});

// Función para configurar el input del código
function setupCodigoInput() {
    const codigoInput = document.getElementById('codigoVerificacion');

    // Limpiar eventos previos
    codigoInput.removeEventListener('input', handleCodigoInput);
    codigoInput.removeEventListener('paste', handleCodigoPaste);
    codigoInput.removeEventListener('keypress', handleCodigoKeypress);

    // Agregar eventos
    codigoInput.addEventListener('input', handleCodigoInput);
    codigoInput.addEventListener('paste', handleCodigoPaste);
    codigoinput.addEventListener('keypress', handleCodigoKeypress);
}

// Manejar entrada de texto
function handleCodigoInput(e) {
    let value = e.target.value.replace(/\D/g, ''); // Solo números
    if (value.length > 6) {
        value = value.substring(0, 6);
    }
    e.target.value = value;
}

// Manejar pegado
function handleCodigoPaste(e) {
    e.preventDefault();
    const pastedText = (e.clipboardData || window.clipboardData).getData('text');
    const cleanedText = pastedText.replace(/\D/g, '').substring(0, 6);
    e.target.value = cleanedText;
}

// Manejar teclas presionadas
function handleCodigoKeypress(e) {
    // Solo permitir números
    const charCode = (e.which) ? e.which : e.keyCode;
    if (charCode > 31 && (charCode < 48 || charCode > 57)) {
        e.preventDefault();
        return false;
    }
    return true;
}

// Inicializar cuando carga la página
document.addEventListener('DOMContentLoaded', function () {
    setupCodigoInput();
});
