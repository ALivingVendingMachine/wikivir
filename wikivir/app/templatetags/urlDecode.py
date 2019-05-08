from django.template.defaultfilters import stringfilter
from django import template
from urllib.parse import unquote

register = template.Library()

@register.filter()
@stringfilter
def unquote_raw(value):
    return unquote(value)