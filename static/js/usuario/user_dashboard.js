function toggleSidebar() {
    document.getElementById("sidebar").classList.toggle("active");
    document.getElementById("overlay").classList.toggle("active");
    document.body.classList.toggle("sidebar-open");
}

function toggleUserMenu() {
    document.getElementById("userDropdown").classList.toggle("show");
}

function toggleSubmenu(element) {
    element.parentElement.classList.toggle("open");
}

window.onclick = function (e) {

    // Cerrar dropdown usuario
    if (!e.target.closest('.user-dropdown')) {
        document.getElementById("userDropdown").classList.remove("show");
    }

    // Cerrar sidebar si se hace clic fuera
    if (
        !e.target.closest('.sidebar') &&
        !e.target.closest('.menu-toggle') &&
        document.getElementById('sidebar').classList.contains('active')
    ) {
        toggleSidebar();
    }
};