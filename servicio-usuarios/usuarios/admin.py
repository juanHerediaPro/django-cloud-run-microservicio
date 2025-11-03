from django.contrib import admin
from .models import Usuario


@admin.register(Usuario)
class UsuarioAdmin(admin.ModelAdmin):
    list_display = ['id', 'nombre_completo', 'email', 'tipo_usuario', 'activo', 'fecha_registro']
    list_filter = ['tipo_usuario', 'activo', 'fecha_registro']
    search_fields = ['nombre', 'apellido', 'email']
    ordering = ['-fecha_registro']
