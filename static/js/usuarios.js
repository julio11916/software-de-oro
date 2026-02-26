document.addEventListener("DOMContentLoaded", function () {

    const toggleBtn = document.getElementById("toggleSidebar");
    const sidebar = document.getElementById("sidebar");
    const content = document.getElementById("content");

    toggleBtn.addEventListener("click", function () {
        sidebar.classList.toggle("active");
        content.classList.toggle("shift");
    });

});