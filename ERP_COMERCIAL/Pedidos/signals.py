from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from Productos.models import Producto
from Pedidos.models import Pedido

# ⚡ Cada vez que se crea o actualiza un producto
@receiver(post_save, sender=Producto)
def actualizar_totales_pedido(sender, instance, **kwargs):
    instance.pedido.calcular_totales()

# ⚡ Cada vez que se elimina un producto
@receiver(post_delete, sender=Producto)
def actualizar_totales_pedido_delete(sender, instance, **kwargs):
    instance.pedido.calcular_totales()