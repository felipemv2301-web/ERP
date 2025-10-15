from django.db import models


class Cliente(models.Model):
    cod_cliente = models.CharField(max_length=20, unique=True)
    razon_social_cliente = models.CharField(max_length=100)
    nombre_fantasia_cliente = models.CharField(max_length=100)
    rut_cliente = models.CharField(max_length=12, unique=True)
    activo = models.BooleanField(default=True)

    def save(self, *args, **kwargs):
        # seguridad: si no hay código aún, lo generamos
        if not self.cod_cliente:
            last_cliente = Cliente.objects.all().order_by("-id").first()
            if last_cliente:
                last_number = int(last_cliente.cod_cliente.split("-")[1])
                new_number = last_number + 1
            else:
                new_number = 1

            self.cod_cliente = f"CLI-{new_number:04d}"

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.cod_cliente} - {self.razon_social_cliente}"


#Relación de composición. Sin cliente no hay dirección, pero al revés si  
class DireccionCliente(models.Model):
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE)
    calle = models.CharField(max_length=100)
    numero = models.CharField(max_length=10)
    ciudad = models.CharField(max_length=50)
    comuna = models.CharField(max_length=50)

#Relación de composición, sin cliente no hay contactos, pero al revés si
class ContactoCliente(models.Model):
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE)
    nombre_contacto = models.CharField(max_length=100)
    email_contacto = models.EmailField(unique=True)
    telefono_contacto = models.CharField(max_length=15, unique=True)
    cargo_contacto = models.CharField(max_length=50, blank=True, null=True)

