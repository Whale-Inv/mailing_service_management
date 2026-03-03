from django import template

register = template.Library()

@register.filter
def get_attr(obj, attr):
    return getattr(obj, attr)

@register.filter
def multiply(value, arg):
    """Умножение"""
    try:
        return float(value) * float(arg)
    except (ValueError, TypeError):
        return 0

@register.filter
def divide(value, arg):
    """Деление"""
    try:
        if float(arg) == 0:
            return 0
        return float(value) / float(arg)
    except (ValueError, TypeError):
        return 0