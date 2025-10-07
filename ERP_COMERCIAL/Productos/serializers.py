from Productos.models import Producto
from rest_framework import serializers

class ProductoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Producto
        fields = ('nombre_producto', 'tipo_producto', 'tamano_producto', 'observacion_producto', 'precio_unitario_producto', 'cantidad_producto')