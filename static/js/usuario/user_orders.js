// Toggle del menú de usuario
document.querySelector('.user-dropdown-btn').addEventListener('click', function () {
    document.getElementById('userDropdown').classList.toggle('show');
});

// Cerrar dropdown al hacer clic fuera
window.addEventListener('click', function (e) {
    if (!e.target.matches('.user-dropdown-btn') && !e.target.closest('.user-dropdown')) {
        var dropdown = document.getElementById('userDropdown');
        if (dropdown.classList.contains('show')) {
            dropdown.classList.remove('show');
        }
    }
});
