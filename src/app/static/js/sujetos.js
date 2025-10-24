function descargarArchivo() {
    window.location.href = '/api/download-all';
}

// Activate the correct tab if there's a hash in the URL
document.addEventListener('DOMContentLoaded', function () {
    if (window.location.hash) {
        const hash = window.location.hash;
        const tabButton = document.querySelector(`button[data-bs-target="${hash}"]`);
        if (tabButton) {
            const tab = new bootstrap.Tab(tabButton);
            tab.show();
        }
    }
});