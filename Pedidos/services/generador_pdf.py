from Pedidos.models import Pedido
from django.http import HttpResponse
from django.template.loader import get_template
from xhtml2pdf import pisa

'''
-------------------------------------------------
Funcion que genera archivos PDF en base a uno o
varios pedidos usando xhtml2pdf
-------------------------------------------------
'''

def pdf_un_pedido(request, pedido_id):
    pedido = Pedido.objects.prefetch_related('producto_set').get(id=pedido_id)
    template_path = 'Pedidos/pdf_un_pedido.html'
    context = {
        'pedido': pedido,
        'productos': pedido.producto_set.all(),
        'total_neto': f"{pedido.total_neto_pedido:,.2f}",
        'iva': f"{pedido.iva_pedido:.2%}",
        'total': f"{pedido.total_pedido:,.2f}",
    }

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'inline; filename="pedido_{pedido.cod_pedido}.pdf"'

    template = get_template(template_path)
    html = template.render(context)
    pisa_status = pisa.CreatePDF(html, dest=response)
    if pisa_status.err:
        return HttpResponse(f'Error al generar PDF: {pisa_status.err}')
    return response

def pdf_pedidos(request):
    pedidos = Pedido.objects.prefetch_related('producto_set').all()
    template_path = 'Pedidos/pdf_pedidos.html'
    context = {
        'pedidos': pedidos,
    }

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'inline; filename="pedidos.pdf"'

    template = get_template(template_path)
    html = template.render(context)
    pisa_status = pisa.CreatePDF(html, dest=response)
    if pisa_status.err:
        return HttpResponse(f'Error al generar PDF: {pisa_status.err}')
    return response