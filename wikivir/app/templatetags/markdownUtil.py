# this code from https://www.imzjy.com/blog/2018-05-20-render-the-markdown-in-django
from django import template
from django.template.defaultfilters import stringfilter
import markdown as md

register = template.Library()

@register.filter()
@stringfilter
def markdown(val):
    return md.markdown(val, extensions=['markdown.extensions.fenced_code'])