from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from datetime import datetime, timedelta
from .models import Reserva


class ReservaModelTest(TestCase):
    def setUp(self):
        self.reserva = Reserva.objects.create(
            nombre_cliente="Juan Pérez",
            email_cliente="juan@example.com",
            telefono_cliente="1234567890",
            fecha_reserva=datetime.now() + timedelta(days=1),
            numero_personas=4,
            estado='pendiente'
        )

    def test_reserva_creation(self):
        """Test que una reserva se crea correctamente"""
        self.assertEqual(self.reserva.nombre_cliente, "Juan Pérez")
        self.assertEqual(self.reserva.estado, 'pendiente')
        self.assertEqual(self.reserva.numero_personas, 4)


class ReservaAPITest(APITestCase):
    def setUp(self):
        self.reserva_data = {
            'nombre_cliente': 'María García',
            'email_cliente': 'maria@example.com',
            'telefono_cliente': '9876543210',
            'fecha_reserva': (datetime.now() + timedelta(days=2)).isoformat(),
            'numero_personas': 2,
            'estado': 'pendiente'
        }

    def test_create_reserva(self):
        """Test crear una reserva vía API"""
        url = reverse('reserva-list')
        response = self.client.post(url, self.reserva_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Reserva.objects.count(), 1)
        self.assertEqual(Reserva.objects.get().nombre_cliente, 'María García')

    def test_get_reservas(self):
        """Test obtener lista de reservas"""
        Reserva.objects.create(**self.reserva_data)
        url = reverse('reserva-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
