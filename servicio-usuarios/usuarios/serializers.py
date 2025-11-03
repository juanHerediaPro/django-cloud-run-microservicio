from rest_framework import serializers
from .models import Usuario


class UsuarioSerializer(serializers.ModelSerializer):
    """
    Serializer para el modelo Usuario.
    """
    nombre_completo = serializers.ReadOnlyField()

    class Meta:
        model = Usuario
        fields = [
            'id',
            'nombre',
            'apellido',
            'nombre_completo',
            'email',
            'telefono',
            'tipo_usuario',
            'activo',
            'direccion',
            'fecha_registro',
            'fecha_actualizacion',
        ]
        read_only_fields = ['id', 'fecha_registro', 'fecha_actualizacion']

    def validate_email(self, value):
        """Validar que el email sea único"""
        if self.instance:
            # Si estamos actualizando, excluir el usuario actual de la validación
            if Usuario.objects.exclude(pk=self.instance.pk).filter(email=value).exists():
                raise serializers.ValidationError("Ya existe un usuario con este email")
        else:
            # Si estamos creando, verificar que no exista
            if Usuario.objects.filter(email=value).exists():
                raise serializers.ValidationError("Ya existe un usuario con este email")
        return value
