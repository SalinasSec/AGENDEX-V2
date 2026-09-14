function toggleSidebar() {
    var sidebar = document.getElementById('sidebar');
    var overlay = document.getElementById('sidebarOverlay');

    if (window.innerWidth <= 767) {
        sidebar.classList.toggle('show');
        if (overlay) overlay.classList.toggle('show', sidebar.classList.contains('show'));
        document.body.style.overflow = sidebar.classList.contains('show') ? 'hidden' : '';
    }
}

document.addEventListener('DOMContentLoaded', function() {
    var sidebar = document.getElementById('sidebar');
    var overlay = document.getElementById('sidebarOverlay');

    // Cerrar sidebar si se pasa a escritorio
    function handleResize() {
        if (window.innerWidth > 767) {
            if (sidebar) sidebar.classList.remove('show');
            if (overlay) overlay.classList.remove('show');
            document.body.style.overflow = '';
        }
    }
    window.addEventListener('resize', handleResize);

    // Cerrar al hacer clic en el overlay
    if (overlay) {
        overlay.addEventListener('click', function() {
            if (sidebar) sidebar.classList.remove('show');
            overlay.classList.remove('show');
            document.body.style.overflow = '';
        });
    }

    // Auto-hide alerts after 5 seconds
    setTimeout(function() {
        document.querySelectorAll('.alert-dismissible').forEach(function(alert) {
            var bsAlert = bootstrap.Alert.getOrCreateInstance(alert);
            bsAlert.close();
        });
    }, 5000);
});
