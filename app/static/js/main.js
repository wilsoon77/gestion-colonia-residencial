// Scripts auxiliares para el frontend
document.addEventListener('DOMContentLoaded', () => {
    // Auto-ocultar alertas flash después de 5 segundos
    const alerts = document.querySelectorAll('.alert-dismissible');
    alerts.forEach(alert => {
        setTimeout(() => {
            const bsAlert = bootstrap.Alert.getOrCreateInstance(alert);
            bsAlert.close();
        }, 5000);
    });

    // Control de colapso/despliegue del menú lateral en el panel administrativo
    const appLayout = document.querySelector('.admin-app-layout');
    const toggleBtn = document.getElementById('sidebarToggleBtn');
    const collapseBtn = document.getElementById('sidebarCollapseDesktopBtn');
    const toggleText = document.getElementById('sidebarToggleText');

    function updateToggleText(isCollapsed) {
        if (toggleText) {
            toggleText.textContent = isCollapsed ? 'Expandir Menú' : 'Colapsar Menú';
        }
        if (toggleBtn) {
            toggleBtn.setAttribute('title', isCollapsed ? 'Expandir menú lateral completo' : 'Colapsar a barra de solo iconos');
        }
        if (collapseBtn) {
            collapseBtn.setAttribute('title', isCollapsed ? 'Expandir menú' : 'Colapsar a solo iconos');
        }
    }

    function toggleAdminSidebar() {
        if (appLayout) {
            appLayout.classList.toggle('sidebar-collapsed');
            const isCollapsed = appLayout.classList.contains('sidebar-collapsed');
            updateToggleText(isCollapsed);
            try {
                localStorage.setItem('admin_sidebar_collapsed', isCollapsed ? '1' : '0');
            } catch (e) {}
        }
    }

    if (appLayout) {
        try {
            if (localStorage.getItem('admin_sidebar_collapsed') === '1') {
                appLayout.classList.add('sidebar-collapsed');
                updateToggleText(true);
            }
        } catch (e) {}
    }

    if (toggleBtn) {
        toggleBtn.addEventListener('click', toggleAdminSidebar);
    }
    if (collapseBtn) {
        collapseBtn.addEventListener('click', toggleAdminSidebar);
    }
});
