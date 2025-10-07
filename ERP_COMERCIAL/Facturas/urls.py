from django.urls import path
from . import views
from Abonos.views import ingresar_abono

app_name = 'facturas'

urlpatterns = [
    path('ingresar/<int:pedido_id>/', views.ingresar_factura, name='ingresar_factura'),
    path('detalle_factura/<int:factura_id>/', views.detalle_factura, name='detalle_factura'),
    path('editar_abono/<int:abono_id>/', views.editar_abono, name='editar_abono'),
    path('eliminar_abono/<int:abono_id>/', views.eliminar_abono, name='eliminar_abono'),
    path('listar_facturas_ajax/', views.listar_facturas_ajax, name='listar_facturas_ajax'),
]