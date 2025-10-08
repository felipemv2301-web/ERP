from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView

urlpatterns = [
    path("admin/", admin.site.urls),
    path("clientes/", include("Clientes.urls")),
    path("pedidos/", include("Pedidos.urls")),
    path("facturas/", include("Facturas.urls")),
    path('', include('Usuarios.urls')),  
    path('', RedirectView.as_view(url='/login/', permanent=False)),
]
