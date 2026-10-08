function toggleSidebar() {
    var sidebar = document.getElementById('sidebar');
    var overlay = document.getElementById('sidebarOverlay');

    if (window.innerWidth < 992) {
        if (!sidebar) return;
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

document.addEventListener('DOMContentLoaded', function() {
    var sidebar = document.getElementById('sidebar');
    var overlay = document.getElementById('sidebarOverlay');

    // Cerrar sidebar si se pasa a escritorio ancho
    function handleResize() {
        if (window.innerWidth >= 992) {
            closeSidebar();
        }
    }
    window.addEventListener('resize', handleResize);

    // Cerrar al hacer clic en el overlay
    if (overlay) {
        overlay.addEventListener('click', closeSidebar);
    }

    // Cerrar con la tecla Escape
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape') {
            closeSidebar();
        }
    });

    // Cerrar sidebar al hacer click en cualquier enlace interno dentro de la navegación en móvil/tablet
    if (sidebar) {
        sidebar.querySelectorAll('a').forEach(function(link) {
            link.addEventListener('click', function() {
                if (window.innerWidth < 992) {
                    closeSidebar();
                }
            });
        });
    }

    // Auto-hide alerts after 5 seconds
    setTimeout(function() {
        document.querySelectorAll('.alert-dismissible').forEach(function(alert) {
            if (window.bootstrap && bootstrap.Alert) {
                var bsAlert = bootstrap.Alert.getOrCreateInstance(alert);
                bsAlert.close();
            }
        });
    }, 5000);

    // Mover modales a document.body para evitar que queden atrapados detrás del backdrop
    function relocateModals() {
        document.querySelectorAll('.modal').forEach(function(modalEl) {
            if (modalEl.parentElement && modalEl.parentElement !== document.body) {
                document.body.appendChild(modalEl);
            }
        });
    }
    relocateModals();

    // En caso de que se abran modales dinámicos
    document.addEventListener('show.bs.modal', function(e) {
        if (e.target && e.target.parentElement !== document.body) {
            document.body.appendChild(e.target);
        }
    });
});
