from django.urls import path
from . import views
from Usuarios.views import CustomLoginView  
from django.contrib.auth.views import ( LogoutView)

urlpatterns = [
    # Login personalizado que valida is_active
    path('login/', CustomLoginView.as_view(template_name='Registros/usuarios.html'), name='login'),

    # Logout
    path('logout/', LogoutView.as_view(next_page='login'), name='logout'),

   
    # Registro
    path('registrar_usuario/', views.registrar_usuario, name='registrar_usuario'),
]