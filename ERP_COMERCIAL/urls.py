from django.contrib import admin
from django.urls import path, include
from ERP_COMERCIAL import views

urlpatterns = [
    path("admin/", admin.site.urls),
    path("clientes/", include("Clientes.urls")),
    path("pedidos/", include("Pedidos.urls")),
    path("facturas/", include("Facturas.urls")),
    path('despachos/', include('Despachos.urls')),
    path("inicio/", views.inicio)
]