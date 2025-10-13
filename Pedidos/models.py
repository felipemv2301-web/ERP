from decimal import Decimal
from django.db import models
from Clientes.models import Cliente
from datetime import date
from django.db.models import Sum
from django.shortcuts import render

class Pedido(models.Model):
    cod_pedido = models.CharField(max_length=20, unique=True, blank=True)
    cod_orden_compra = models.CharField(max_length=20, default=0, blank=True, null=True)

    #Asociación con cliente, debido a que un pedido tiene un cliente, pero un cliente tiene varios pedidos.composition
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE)
    fecha_pedido = models.DateField(default=date.today)
    total_neto_pedido = models.DecimalField(max_digits=20, decimal_places=2, default=Decimal('0.00'))
    iva_pedido = models.DecimalField(max_digits=4, decimal_places=2, default=Decimal('0.19'))
    total_pedido = models.DecimalField(max_digits=20, decimal_places=2, default=Decimal('0.00'))

    def calcular_totales(self):
        """Calcula neto y total con IVA de todos los productos asociados al pedido."""
        productos = self.producto_set.all()
        neto = sum([Decimal(p.subtotal()) for p in productos])
        total = neto + (neto * self.iva_pedido)
        self.total_neto_pedido = neto
        self.total_pedido = total
        self.save(update_fields=['total_neto_pedido', 'total_pedido'])

    def save(self, *args, **kwargs):
        """Genera un código único para el pedido, asegurando que comience en 1001."""

        if not self.cod_pedido:
        
            last_pedido = Pedido.objects.all().order_by("-id").first()
            
            if last_pedido and last_pedido.cod_pedido.startswith("PED-"):
                try:
                    # Intenta extraer la parte numérica (e.g., de "PED-0073" o "PED-1000")
                    # No importa si hay ceros iniciales, int() lo maneja.
                    last_number = int(last_pedido.cod_pedido.split("-")[1])
                    new_number = max(last_number + 1, 1001) 
                    
                except (IndexError, ValueError):
                    # Si el formato del último código es inválido (e.g., "PED-ABC"), iniciamos en 1001
                    new_number = 1001
            else:
                # Si no hay pedidos o el último no tiene el prefijo, iniciamos en 1001
                new_number = 1001

            # --- 2. Asignar el nuevo código ---
            # El ':04d' garantiza que se rellene con ceros hasta 4 dígitos (e.g., 1001)
            self.cod_pedido = f"PED-{new_number:04d}"
            
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.cod_pedido} - {self.cliente.razon_social_cliente}"

    @property
    def total_facturado(self):
        """Suma el total de todas las facturas asociadas a este pedido."""
        return sum(Decimal(f.total_factura) for f in self.factura_set.all())

    @property
    def saldo_por_facturar(self):
        """Devuelve cuánto falta por facturar del total del pedido."""
        saldo = self.total_pedido - self.total_facturado
        return max(Decimal('0.00'), saldo)  # nunca retorna negativo
    
