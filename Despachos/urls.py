from django.urls import path
from . import views

app_name = 'despachos'

urlpatterns = [
    # Registrar nueva guía de despacho para un pedido
    path('ingresar/<int:pedido_id>/', views.ingresar_guia_despacho, name='ingresar_guia'),
    path('pedido/<int:pedido_id>/guias/', views.listar_guias_despacho, name='listar_guia_despacho')
]