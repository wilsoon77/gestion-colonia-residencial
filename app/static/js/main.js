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
});
