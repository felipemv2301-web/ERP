from django.db import models
from Pedidos.models import Pedido

class GuiaDespacho(models.Model):
    #Asociación fuerte. Guía es parte del pedido.
    pedido = models.ForeignKey(Pedido, on_delete=models.PROTECT)
    cod_guia_despacho = models.CharField(max_length=20, unique=True)
    fecha_despacho = models.DateField(auto_now_add=True)

    #Revisar como acceder a la dirección del cliente específico
    direccion_entrega = models.CharField(max_length=200)
    observacion_despacho = models.TextField(blank=True, null=True)

#Relación de composición fuerte con guia_despacho. Detalle no tiene sentido sin la guía
class DetalleDespacho(models.Model):
    guia_despacho = models.ForeignKey(GuiaDespacho, on_delete=models.CASCADE)
    cantidad_despachada = models.PositiveIntegerField()
    nombre_repartidor = models.CharField(max_length=100)
