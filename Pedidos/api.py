# api.py o views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from decimal import Decimal

from Pedidos.serializers import PedidoSerializer
from Productos.serializers import ProductoSerializer
from services.pdf_parser import procesar_archivo_pdf, procesar_archivo_ocr  # importa tus funciones

class ProcesarDocumentoAPIView(APIView):
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request, *args, **kwargs):
        archivo = request.FILES.get("documento")
        if not archivo:
            return Response({"error": "No se envió ningún archivo"}, status=400)

        # Detectar tipo y procesar
        if archivo.name.endswith(".pdf"):
            pedido_data, productos = procesar_archivo_pdf(archivo)
        else:
            pedido_data, productos = procesar_archivo_ocr(archivo)

        # Opcional: Serializar productos si quieres devolverlos como objetos JSON
        productos_serializados = []
        for p in productos:
            productos_serializados.append({
                "nombre_producto": p.get("nombre_producto", ""),
                "tipo_producto": p.get("tipo_producto", ""),
                "tamano_producto": p.get("tamano_producto", ""),
                "observacion_producto": p.get("observacion_producto", ""),
                "cantidad_producto": p.get("cantidad_producto", 0),
                "precio_unitario_producto": str(p.get("precio_unitario_producto", Decimal("0.0")))
            })

        respuesta = {
            "pedido": pedido_data,
            "productos": productos_serializados
        }

        return Response(respuesta)
