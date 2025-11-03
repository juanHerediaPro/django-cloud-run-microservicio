from rest_framework import serializers
from .models import Reserva


class ReservaSerializer(serializers.ModelSerializer):
    """
    Serializer para el modelo Reserva.
    """
    class Meta:
        model = Reserva
        fields = [
            'id',
            'nombre_cliente',
            'email_cliente',
            'telefono_cliente',
            'fecha_reserva',
            'numero_personas',
            'estado',
            'notas',
            'fecha_creacion',
            'fecha_actualizacion',
        ]
        read_only_fields = ['id', 'fecha_creacion', 'fecha_actualizacion']

    def validate_numero_personas(self, value):
        """Validar que el número de personas sea positivo"""
        if value < 1:
            raise serializers.ValidationError("El número de personas debe ser al menos 1")
        return value
