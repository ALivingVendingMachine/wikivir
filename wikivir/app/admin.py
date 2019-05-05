from django.contrib import admin
from .models import MalwareSample, Topic
from django import template

register = template.Library()

# Register your models here.
admin.site.register(MalwareSample)
admin.site.register(Topic)
