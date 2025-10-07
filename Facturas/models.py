from django.db import models
from django.db.models import Sum
from Pedidos.models import Pedido
from Clientes.models import Cliente
from datetime import date
from decimal import Decimal

class Factura(models.Model):
    ESTADO_CHOICES = [
        ('Pendiente', 'Pendiente'), 
        ('Pagada', 'Pagada'), 
        ('Anulada', 'Anulada')
    ]

    #Asociación. Un pedido puede tener varias facturas, pero una factura solo pertenece a un pedido.
    pedido = models.ForeignKey(Pedido, on_delete=models.PROTECT)
    cod_factura = models.CharField(max_length=20, unique=True)
    fecha_emision_factura = models.DateField(default=date.today)
    total_factura = models.DecimalField(max_digits=20, decimal_places=2)
    estado_factura = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='Pendiente')

    def actualizar_estado(self):
        if self.saldo_pendiente == Decimal('0.00'):
            self.estado_factura = 'Pagada'
        else:
            self.estado_factura = 'Pendiente'
        self.save(update_fields=['estado_factura'])

    @property
    def total_abonado(self):
        """Suma de todos los abonos asociados a esta factura de forma eficiente (usando ORM)."""
        # 💡 La Base de Datos hace la suma (más rápido y seguro)
        total = self.abonos.aggregate(Sum('total_abono'))['total_abono__sum']
        
        # Aseguramos que siempre devuelva un Decimal, no None.
        return total or Decimal('0.00')

    @property
    def saldo_pendiente(self):
        """Saldo pendiente por pagar de esta factura."""
        saldo = self.total_factura - self.total_abonado
        return max(Decimal('0.00'), saldo)  # nunca retorna negativo

    @property
    def cliente(self):
        """Devuelve el cliente asociado al pedido."""
        return self.pedido.cliente