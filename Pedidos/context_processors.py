from Pedidos.models import Pedido
from django.db.models import Sum, Q, F

def notificaciones_context(request):
    pedidos_pendientes = (
        Pedido.objects
        .annotate(
            total_facturado=Sum(
                'factura__total_factura',
                filter=~Q(factura__estado_factura='Anulada')
            )
        )
        .filter(
            Q(total_facturado__lt=F('total_pedido')) |
            Q(total_facturado__isnull=True)
        )
        .distinct()
    )

    return {
        'total_notificaciones': pedidos_pendientes.count(),
    }
