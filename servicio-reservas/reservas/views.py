from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Reserva
from .serializers import ReservaSerializer


class ReservaViewSet(viewsets.ModelViewSet):
    """
    ViewSet para operaciones CRUD de Reservas.
    
    Endpoints disponibles:
    - GET /api/reservas/ - Listar todas las reservas
    - POST /api/reservas/ - Crear una nueva reserva
    - GET /api/reservas/{id}/ - Obtener una reserva específica
    - PUT /api/reservas/{id}/ - Actualizar una reserva completa
    - PATCH /api/reservas/{id}/ - Actualizar parcialmente una reserva
    - DELETE /api/reservas/{id}/ - Eliminar una reserva
    - GET /api/reservas/por_estado/?estado=pendiente - Filtrar por estado
    """
    queryset = Reserva.objects.all()
    serializer_class = ReservaSerializer

    def get_queryset(self):
        """Permitir filtrado por estado"""
        queryset = Reserva.objects.all()
        estado = self.request.query_params.get('estado', None)
        if estado:
            queryset = queryset.filter(estado=estado)
        return queryset

    @action(detail=True, methods=['post'])
    def confirmar(self, request, pk=None):
        """Endpoint personalizado para confirmar una reserva"""
        reserva = self.get_object()
        reserva.estado = 'confirmada'
        reserva.save()
        serializer = self.get_serializer(reserva)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def cancelar(self, request, pk=None):
        """Endpoint personalizado para cancelar una reserva"""
        reserva = self.get_object()
        reserva.estado = 'cancelada'
        reserva.save()
        serializer = self.get_serializer(reserva)
        return Response(serializer.data)
