$(document).ready(function() {

    // Abrir modal de edición de dirección vía AJAX
    $('.editar-direccion').click(function() {
        const direccionId = $(this).data('id');
        $.get(`/clientes/direccion/editar/${direccionId}/`, function(data) {
            $('#modal-container').html(data);
            const modal = new bootstrap.Modal(document.getElementById('editarDireccionModal'));
            modal.show();

            // Manejar submit vía AJAX
            $('#form-editar-direccion').submit(function(e) {
                e.preventDefault();
                const formData = $(this).serialize();
                $.post(`/clientes/direccion/editar/${direccionId}/`, formData, function(resp) {
                    if(resp.success) {
                        // Actualizar tabla
                        const row = $(`#direccion-${direccionId}`);
                        row.find('td:nth-child(1)').text(resp.direccion.calle);
                        row.find('td:nth-child(2)').text(resp.direccion.numero);
                        row.find('td:nth-child(3)').text(resp.direccion.comuna);
                        row.find('td:nth-child(4)').text(resp.direccion.ciudad);
                        modal.hide();
                    } else {
                        // Mostrar errores en el modal
                        $('#editarDireccionModal .modal-body').html(resp.html);
                    }
                });
            });
        });
    });

    // Eliminar dirección
    $('.eliminar-direccion').click(function() {
        const direccionId = $(this).data('id');
        if(confirm('¿Eliminar esta dirección?')) {
            $.post(`/clientes/direccion/eliminar/${direccionId}/`, {'csrfmiddlewaretoken': getCookie('csrftoken')}, function(resp) {
                if(resp.success) $(`#direccion-${direccionId}`).remove();
            });
        }
    });

});

// Función para obtener CSRF token
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let cookie of cookies) {
            cookie = cookie.trim();
            if (cookie.startsWith(name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}
