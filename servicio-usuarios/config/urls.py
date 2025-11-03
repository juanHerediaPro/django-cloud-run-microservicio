"""
URL configuration for servicio-usuarios project.
"""
from django.contrib import admin
from django.urls import path, include
from django.http import JsonResponse

def healthz(request):
    """Health check endpoint para Cloud Run"""
    return JsonResponse({'status': 'OK'}, status=200)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('healthz', healthz, name='healthz'),
    path('api/', include('usuarios.urls')),
]
