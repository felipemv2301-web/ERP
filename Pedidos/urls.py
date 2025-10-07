from django.urls import path
from . import views
from Pedidos.services.generador_pdf import pdf_un_pedido, pdf_pedidos
app_name = "pedidos"

"""
-------------------------------------------------
Conexión de URLs para vistas de Pedidos (HTML)
-------------------------------------------------
"""

urlpatterns = [
    path('ingresar/', views.ingresar_pedido, name='ingresar_pedido'),
    path('listar/', views.listar_pedidos, name='listar_pedidos'),
    path('editar/<int:pedido_id>/', views.editar_pedido, name='editar_pedido'),

    #Crear y procesar archivos para el ingreso del formulario
    #ENDPOINT es: http://127.0.0.1:8000/pedidos/api/procesar-documento/
    path('api/procesar-documento/', views.procesar_documento_api, name='procesar_documento_api'),

    #Crear Archivos PDF
    path('pdf/pedido/<int:pedido_id>/', pdf_un_pedido, name='pdf_un_pedido'),
    path('pdf/pedidos/', pdf_pedidos, name='pdf_pedidos'),
]
