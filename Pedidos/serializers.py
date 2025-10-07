from rest_framework import serializers
from Pedidos.models import Pedido

class PedidoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Pedido
        fields = ('id', 'cod_orden_compra', 'cliente', 'fecha_pedido')


