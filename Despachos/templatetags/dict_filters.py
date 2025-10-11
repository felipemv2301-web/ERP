from django import template

register = template.Library()

@register.filter
def get_item(dictionary, key):
    """Devuelve el valor de un diccionario usando la clave dada."""
    if isinstance(dictionary, dict):
        return dictionary.get(key)
    return None