// AgendEx - JavaScript Principal (UI y Navegación)

function toggleSidebar() {
    var sidebar = document.getElementById('sidebar');
    var overlay = document.getElementById('sidebarOverlay');
    if (window.innerWidth < 992 && sidebar) {
        sidebar.classList.toggle('show');
        var isOpen = sidebar.classList.contains('show');
        if (overlay) overlay.classList.toggle('show', isOpen);
        document.body.style.overflow = isOpen ? 'hidden' : '';
    }
}

function closeSidebar() {
    var sidebar = document.getElementById('sidebar');
    var overlay = document.getElementById('sidebarOverlay');
    if (sidebar) sidebar.classList.remove('show');
    if (overlay) overlay.classList.remove('show');
    document.body.style.overflow = '';
}

document.addEventListener('DOMContentLoaded', function () {
    var overlay = document.getElementById('sidebarOverlay');

    // Cerrar sidebar al redimensionar a pantalla grande
    window.addEventListener('resize', function () {
        if (window.innerWidth >= 992) {
            closeSidebar();
        }
    });

    // Cerrar al hacer clic en fondo oscuro
    if (overlay) {
        overlay.addEventListener('click', closeSidebar);
    }

    // Cerrar con Escape
    document.addEventListener('keydown', function (e) {
        if (e.key === 'Escape') {
            closeSidebar();
        }
    });

    // Auto-ocultar alertas después de 5 segundos
    setTimeout(function () {
        document.querySelectorAll('.alert-dismissible').forEach(function (alert) {
            if (window.bootstrap && bootstrap.Alert) {
                bootstrap.Alert.getOrCreateInstance(alert).close();
            }
        });
    }, 5000);
});
