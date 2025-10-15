from django.db import models
from Pedidos.models import Pedido
from datetime import date
from Productos.models import Producto
from Clientes.models import DireccionCliente

class GuiaDespacho(models.Model):
    #Asociación fuerte. Guía es parte del pedido.
    pedido = models.ForeignKey(Pedido, on_delete=models.PROTECT)
    cod_guia_despacho = models.CharField(max_length=20, unique=True)
    fecha_despacho = models.DateField(default=date.today)

    #Revisar como acceder a la dirección del cliente específico
    direccion_entrega = models.ForeignKey(DireccionCliente, on_delete=models.SET_NULL, null=True, blank=True)
    observacion_despacho = models.TextField(blank=True, null=True)

    def save(self, *args, **kwargs):
        if not self.cod_guia_despacho:
            last_guia = GuiaDespacho.objects.all().order_by('-id').first()
            if last_guia and last_guia.cod_guia_despacho.startswith("GD-"):
                try:
                    last_number = int(last_guia.cod_guia_despacho.split('-')[1])
                    new_number = last_number + 1
                except:
                    new_number = 1001
            else:
                new_number = 1001
            self.cod_guia_despacho = f"GD-{new_number:04d}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Guía {self.cod_guia_despacho} - Pedido {self.pedido.cod_pedido}"

#Relación de composición fuerte con guia_despacho. Detalle no tiene sentido sin la guía
class DetalleDespacho(models.Model):
    guia_despacho = models.ForeignKey(GuiaDespacho, on_delete=models.CASCADE)
    producto = models.ForeignKey(Producto, on_delete=models.PROTECT, default=0)
    cantidad_despachada = models.PositiveIntegerField()
    nombre_repartidor = models.CharField(max_length=100)

    @property
    def total_pedido(self):
        """Retorna el total basado en la cantidad del pedido, no en lo despachado."""
        return (self.producto.cantidad_producto or 0) * (self.producto.precio_unitario_producto or 0)

    def __str__(self):
        return f"{self.producto.nombre_producto} - Cantidad: {self.cantidad_despachada}"
