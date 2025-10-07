from datetime import date
from django.db import models
from Facturas.models import Factura
from django.core.exceptions import ValidationError
from decimal import Decimal
from django.db.models import Sum

class Abono(models.Model):
    #Composición, debido a que el abono no tiene sentido sin una factura que lo respalde
    factura = models.ForeignKey(Factura, on_delete=models.CASCADE, related_name='abonos')
    fecha_abono = models.DateField(default=date.today)
    total_abono = models.DecimalField(max_digits=20, decimal_places=2)

    # Calcula el saldo pendiente antes de guardar
    def _calcular_saldo_disponible(self):
        """
        Calcula el saldo disponible de la factura EXCLUYENDO el abono actual.
        Este cálculo se usa para la validación y es un buen método interno.
        """
        factura = self.factura
        
        # Total de otros abonos (eficiente con ORM)
        total_otros_abonos = factura.abonos.exclude(pk=self.pk).aggregate(
            Sum('total_abono')
        )['total_abono__sum'] or Decimal('0.00')

        return factura.total_factura - total_otros_abonos
    

    def save(self, *args, **kwargs):
        
        # 1. Validación de Saldo (solo si es necesario)
        if self.total_abono: # Solo valida si hay un valor en total_abono
            saldo_disponible = self._calcular_saldo_disponible()
            
            if self.total_abono > saldo_disponible:
                raise ValidationError(
                    f"El abono no puede superar el saldo pendiente de ${saldo_disponible:.2f}."
                )
        
        # 2. Guardar y actualizar
        super().save(*args, **kwargs)
        self.factura.actualizar_estado()
