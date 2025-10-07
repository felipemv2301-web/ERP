from django.urls import path
from Clientes import views

app_name = "clientes"

urlpatterns = [
    #Cliente
    path("ingresar/", views.ingresar_cliente, name="ingresar_cliente"),
    path("listar/", views.listar_clientes, name="listar_clientes"),
    path("detalle/<int:cliente_id>/", views.detalle_cliente, name="detalle_cliente"),

    #Dirección
    path("direccion/nuevo/<int:cliente_id>/", views.ingresar_direccion, name="ingresar_direccion"),
    #path("direccion/editar/<int:direccion_id>/", views.editar_direccion, name="editar_direccion"),
    path("direccion/eliminar/<int:direccion_id>/", views.eliminar_direccion, name="eliminar_direccion"),

    #Contacto
    path("contacto/nuevo/<int:cliente_id>/", views.ingresar_contacto, name="ingresar_contacto"),
    path("contacto/eliminar/<int:contacto_id>/", views.eliminar_contacto, name="eliminar_contacto"),
]
