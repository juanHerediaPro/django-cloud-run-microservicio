from django.db import models


class Usuario(models.Model):
    """
    Modelo para gestionar usuarios del sistema.
    """
    TIPO_CHOICES = [
        ('cliente', 'Cliente'),
        ('administrador', 'Administrador'),
        ('empleado', 'Empleado'),
    ]

    nombre = models.CharField(max_length=200)
    apellido = models.CharField(max_length=200)
    email = models.EmailField(unique=True)
    telefono = models.CharField(max_length=20, blank=True)
    tipo_usuario = models.CharField(max_length=20, choices=TIPO_CHOICES, default='cliente')
    activo = models.BooleanField(default=True)
    direccion = models.TextField(blank=True)
    fecha_registro = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-fecha_registro']
        verbose_name = 'Usuario'
        verbose_name_plural = 'Usuarios'

    def __str__(self):
        return f"{self.nombre} {self.apellido} ({self.email})"

    @property
    def nombre_completo(self):
        return f"{self.nombre} {self.apellido}"
