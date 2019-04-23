from django.contrib import admin
from .models import MalwareSample, Topic

# Register your models here.
admin.site.register(MalwareSample)
admin.site.register(Topic)
