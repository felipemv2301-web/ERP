from django.contrib.auth import authenticate, login
from django.contrib.auth.views import LoginView
from django.contrib import messages
from django.shortcuts import render, redirect
from .forms import RegistroUsuarioForm
from .models import SolicitudAcceso

def registrar_usuario(request):
    if request.method == 'POST':
        form = RegistroUsuarioForm(request.POST)
        if form.is_valid():
            usuario = form.save(commit=False)
            usuario.is_active = False
            usuario.save()
            
            # Crear solicitud asociada
            SolicitudAcceso.objects.create(
                nombre=usuario.first_name + ' ' + usuario.last_name,
                email=usuario.email,
                empresa='Por definir',  # O agrega campo en el form si quieres
                telefono='Por definir', # Lo mismo
                motivo='Registro desde formulario',
                usuario_creado=usuario,
                estado='P',
            )
            
            messages.success(request, "Tu cuenta ha sido registrada y está pendiente de aprobación.")
            return redirect('login')
    else:
        form = RegistroUsuarioForm()
    return render(request, 'registration/registrar_usuario.html', {'form': form})

class CustomLoginView(LoginView):
    def form_valid(self, form):
        user = form.get_user()
        if not user.is_active:
            messages.error(self.request, "Tu cuenta aún no ha sido aprobada por un administrador.")
            return self.form_invalid(form)
        return super().form_valid(form)