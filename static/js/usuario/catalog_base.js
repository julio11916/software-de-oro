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

document.addEventListener("DOMContentLoaded", () => {
    document.querySelectorAll(".flash-toast[data-toast-duration]").forEach((toast) => {
        const duration = Number.parseInt(toast.dataset.toastDuration || "0", 10);
        if (!duration || duration < 1) return;

        window.setTimeout(() => {
            toast.remove();
            const stack = document.querySelector(".flash-toast-stack");
            if (stack && !stack.querySelector(".flash-toast")) {
                stack.remove();
            }
        }, duration);
    });
});
