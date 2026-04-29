function redirectToLogin(event) {
    event.preventDefault();
    window.location.href = window.location.pathname;
    return false;
}
