from django.contrib import admin

# Register your models here.

from .models import Profile, Log

admin.site.register(Profile)
admin.site.register(Log)