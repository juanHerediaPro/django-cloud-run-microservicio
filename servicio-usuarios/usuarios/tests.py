from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from .models import Usuario


class UsuarioModelTest(TestCase):
    def setUp(self):
        self.usuario = Usuario.objects.create(
            nombre="María",
            apellido="García",
            email="maria@example.com",
            telefono="9876543210",
            tipo_usuario='cliente',
            activo=True
        )

    def test_usuario_creation(self):
        """Test que un usuario se crea correctamente"""
        self.assertEqual(self.usuario.nombre, "María")
        self.assertEqual(self.usuario.email, "maria@example.com")
        self.assertTrue(self.usuario.activo)

    def test_nombre_completo(self):
        """Test de la propiedad nombre_completo"""
        self.assertEqual(self.usuario.nombre_completo, "María García")


class UsuarioAPITest(APITestCase):
    def setUp(self):
        self.usuario_data = {
            'nombre': 'Juan',
            'apellido': 'Pérez',
            'email': 'juan@example.com',
            'telefono': '1234567890',
            'tipo_usuario': 'cliente',
            'activo': True
        }

    def test_create_usuario(self):
        """Test crear un usuario vía API"""
        url = reverse('usuario-list')
        response = self.client.post(url, self.usuario_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Usuario.objects.count(), 1)
        self.assertEqual(Usuario.objects.get().email, 'juan@example.com')

    def test_get_usuarios(self):
        """Test obtener lista de usuarios"""
        Usuario.objects.create(**self.usuario_data)
        url = reverse('usuario-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_email_unico(self):
        """Test que el email debe ser único"""
        Usuario.objects.create(**self.usuario_data)
        url = reverse('usuario-list')
        response = self.client.post(url, self.usuario_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
