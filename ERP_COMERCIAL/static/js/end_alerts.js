function autoCloseAlerts(timeout = 5000) {
    document.addEventListener('DOMContentLoaded', function() {
        const alerts = document.querySelectorAll('.alert');
        alerts.forEach(function(alert) {
            // Espera el tiempo indicado y luego cierra la alerta usando Bootstrap
            setTimeout(function() {
                const bsAlert = bootstrap.Alert.getOrCreateInstance(alert);
                bsAlert.close();
            }, timeout);
        });
    });
}

// Llamada automática al cargar el script con timeout por defecto 5 segundos
autoCloseAlerts();