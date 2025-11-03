from django.contrib import admin
from .models import Reserva


@admin.register(Reserva)
class ReservaAdmin(admin.ModelAdmin):
    list_display = ['id', 'nombre_cliente', 'fecha_reserva', 'numero_personas', 'estado', 'fecha_creacion']
    list_filter = ['estado', 'fecha_reserva']
    search_fields = ['nombre_cliente', 'email_cliente']
    ordering = ['-fecha_reserva']
