from django.db import models
from Pedidos.models import Pedido
from django.apps import apps

class Producto(models.Model):
    TAMANO_CHOICES = [
        ('No definido', 'No definido'),
        ('S', 'S'),
        ('M', 'M'),
        ('L', 'L'),
        ('XL', 'XL'),
    ]

    #Composición debido a que el producto en este caso, no existe sin el pedido (debido a que es personalizado)
    pedido = models.ForeignKey(Pedido, on_delete=models.CASCADE)
    nombre_producto = models.CharField(max_length=100)
    tipo_producto = models.CharField(max_length=50, blank=True, null=True)
    tamano_producto = models.CharField(max_length=50, blank=True, null=True, choices=TAMANO_CHOICES)
    observacion_producto = models.TextField(blank=True, null=True)
    precio_unitario_producto = models.DecimalField(max_digits=20, decimal_places=2)
    cantidad_producto = models.PositiveIntegerField(default=1)

    def subtotal(self):
        return self.precio_unitario_producto * self.cantidad_producto

    def __str__(self):
        return self.nombre_producto
