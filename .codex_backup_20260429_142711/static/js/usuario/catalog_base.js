function toggleUserMenu() {
    const dropdown = document.getElementById("userDropdown");
    if (!dropdown) return;
    dropdown.classList.toggle("show");
}

function closeUserMenu() {
    const dropdown = document.getElementById("userDropdown");
    if (!dropdown) return;
    dropdown.classList.remove("show");
}

window.addEventListener("click", function (e) {
    const dropdown = document.getElementById("userDropdown");
    if (!dropdown) return;
    if (!e.target.closest(".user-dropdown")) {
        dropdown.classList.remove("show");
    }
});
