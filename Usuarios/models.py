from django.db import models

# Create your models here.
from django.db import models
from django.contrib.auth.models import User

class SolicitudAcceso(models.Model):
    ESTADOS = (
        ('P', 'Pendiente'),
        ('A', 'Aprobado'),
        ('R', 'Rechazado'),
    )
    
    nombre = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    empresa = models.CharField(max_length=100)
    telefono = models.CharField(max_length=20)
    motivo = models.TextField()
    estado = models.CharField(max_length=1, choices=ESTADOS, default='P')
    fecha_solicitud = models.DateTimeField(auto_now_add=True)
    usuario_creado = models.OneToOneField(
        User,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='solicitud_acceso'
    )

    def __str__(self):
        return f"Solicitud de {self.nombre} ({self.empresa}) - {self.get_estado_display()}"

