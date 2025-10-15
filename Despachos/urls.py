from django.urls import path
from . import views

app_name = 'despachos'

urlpatterns = [
    # Registrar nueva guía de despacho para un pedido
    path('ingresar/<int:pedido_id>/', views.ingresar_guia_despacho, name='ingresar_guia'),
    path('pedido/<int:pedido_id>/guias/', views.listar_guias_despacho, name='listar_guia_despacho'),
    path('ver/<int:guia_id>/', views.ver_guia_despacho, name="ver_guia_despacho"),
    path('editar/<int:guia_id>/', views.editar_guia_despacho, name="editar_guia_despacho")
]