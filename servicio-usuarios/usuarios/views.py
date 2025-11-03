from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Usuario
from .serializers import UsuarioSerializer


class UsuarioViewSet(viewsets.ModelViewSet):
    """
    ViewSet para operaciones CRUD de Usuarios.
    
    Endpoints disponibles:
    - GET /api/usuarios/ - Listar todos los usuarios
    - POST /api/usuarios/ - Crear un nuevo usuario
    - GET /api/usuarios/{id}/ - Obtener un usuario específico
    - PUT /api/usuarios/{id}/ - Actualizar un usuario completo
    - PATCH /api/usuarios/{id}/ - Actualizar parcialmente un usuario
    - DELETE /api/usuarios/{id}/ - Eliminar un usuario
    - GET /api/usuarios/activos/ - Listar solo usuarios activos
    - POST /api/usuarios/{id}/desactivar/ - Desactivar un usuario
    - POST /api/usuarios/{id}/activar/ - Activar un usuario
    """
    queryset = Usuario.objects.all()
    serializer_class = UsuarioSerializer

    def get_queryset(self):
        """Permitir filtrado por tipo de usuario y estado activo"""
        queryset = Usuario.objects.all()
        tipo = self.request.query_params.get('tipo', None)
        activo = self.request.query_params.get('activo', None)
        
        if tipo:
            queryset = queryset.filter(tipo_usuario=tipo)
        if activo is not None:
            queryset = queryset.filter(activo=activo.lower() == 'true')
        
        return queryset

    @action(detail=False, methods=['get'])
    def activos(self, request):
        """Endpoint para obtener solo usuarios activos"""
        usuarios = self.queryset.filter(activo=True)
        serializer = self.get_serializer(usuarios, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def desactivar(self, request, pk=None):
        """Endpoint personalizado para desactivar un usuario"""
        usuario = self.get_object()
        usuario.activo = False
        usuario.save()
        serializer = self.get_serializer(usuario)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def activar(self, request, pk=None):
        """Endpoint personalizado para activar un usuario"""
        usuario = self.get_object()
        usuario.activo = True
        usuario.save()
        serializer = self.get_serializer(usuario)
        return Response(serializer.data)
