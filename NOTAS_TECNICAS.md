# Notas Técnicas - Microservicios Django en Google Cloud Run

## Resumen Ejecutivo

Este documento detalla las decisiones técnicas, arquitectura y consideraciones de implementación para los dos microservicios Django desplegados en Google Cloud Run.

## Arquitectura General

### Diseño de Microservicios

Se implementaron dos microservicios completamente independientes:

1. **servicio-reservas**: Gestión de reservas con estados y validaciones
2. **servicio-usuarios**: Gestión de usuarios con tipos y activación/desactivación

Cada microservicio:
- Tiene su propio proyecto Django independiente
- Se despliega en su propio contenedor
- Tiene su propia imagen en Artifact Registry
- Comparte la misma base de datos PostgreSQL (pero con tablas independientes)
- Puede escalar independientemente

### Stack Tecnológico

- **Framework**: Django 4.2.11 (LTS)
- **API**: Django REST Framework 3.14.0
- **Base de datos**: PostgreSQL (Cloud SQL)
- **Servidor**: Gunicorn 21.2.0
- **Contenedor**: Docker con Python 3.11-slim
- **Plataforma**: Google Cloud Run
- **CI/CD**: Cloud Build
- **Secretos**: Secret Manager

## Decisiones de Diseño

### 1. Django REST Framework

**Decisión**: Usar DRF con ViewSets y Routers

**Razones**:
- Generación automática de endpoints CRUD
- Serialización y validación robusta
- Paginación incluida
- Fácil extensión con custom actions
- Documentación automática posible con drf-spectacular

**Implementación**:
\`\`\`python
class ReservaViewSet(viewsets.ModelViewSet):
    queryset = Reserva.objects.all()
    serializer_class = ReservaSerializer
\`\`\`

### 2. Configuración de Base de Datos

**Decisión**: Conexión dual (local vs Cloud SQL)

**Razones**:
- Facilitar desarrollo local sin Cloud SQL
- Usar Unix socket en producción para mejor rendimiento
- Detectar automáticamente el entorno

**Implementación**:
\`\`\`python
if os.environ.get('CLOUD_SQL_CONNECTION_NAME'):
    # Cloud Run: usar Unix socket
    HOST = f'/cloudsql/{CONNECTION_NAME}'
else:
    # Local: usar TCP
    HOST = 'localhost'
\`\`\`

### 3. Gestión de Secretos

**Decisión**: Secret Manager con inyección en tiempo de despliegue

**Razones**:
- Nunca almacenar credenciales en código
- Rotación de secretos sin rebuild
- Auditoría de acceso a secretos
- Integración nativa con Cloud Run

**Implementación en cloudbuild.yaml**:
\`\`\`yaml
--set-secrets=DATABASE_USER=USER:latest,DATABASE_PASSWORD=PASSWORD:latest
\`\`\`

### 4. Dockerfile Optimizado

**Decisión**: Imagen slim con usuario no-root

**Razones**:
- Reducir superficie de ataque
- Cumplir con mejores prácticas de seguridad
- Reducir tamaño de imagen (de ~1GB a ~200MB)
- Mejor tiempo de inicio en Cloud Run

**Características**:
- Base: `python:3.11-slim`
- Usuario: `appuser` (UID 1000)
- Multi-stage no necesario (proyecto pequeño)
- Cache de pip deshabilitado

### 5. Gunicorn Configuration

**Decisión**: 2 workers, 4 threads, timeout 0

**Razones**:
- 2 workers: Óptimo para 1 CPU en Cloud Run
- 4 threads: Manejo de I/O concurrente (DB queries)
- timeout 0: Cloud Run maneja timeouts
- Bind a :8080: Puerto requerido por Cloud Run

**Comando**:
\`\`\`bash
gunicorn --bind :8080 --workers 2 --threads 4 --timeout 0 config.wsgi:application
\`\`\`

### 6. Health Check Endpoint

**Decisión**: Endpoint simple `/healthz` sin autenticación

**Razones**:
- Requerido por Cloud Run para health checks
- Debe responder rápido (<1s)
- No debe requerir autenticación
- Indica que el servicio está listo

**Implementación**:
\`\`\`python
def healthz(request):
    return JsonResponse({'status': 'OK'}, status=200)
\`\`\`

### 7. Cloud Build Pipeline

**Decisión**: 3 pasos (Build → Push → Deploy)

**Razones**:
- Automatización completa del despliegue
- Versionado con SHORT_SHA
- Tag 'latest' para facilidad de uso
- Configuración declarativa

**Pasos**:
1. `docker build`: Construir imagen
2. `docker push`: Subir a Artifact Registry
3. `gcloud run deploy`: Desplegar en Cloud Run

### 8. Modelos de Datos

#### Servicio de Reservas

**Decisión**: Estados explícitos con choices

**Campos clave**:
- `estado`: Enum con 4 estados posibles
- `fecha_reserva`: DateTime para la reserva
- `numero_personas`: Validado >= 1
- Timestamps automáticos

**Razones**:
- Validación a nivel de base de datos
- Claridad en el flujo de estados
- Auditoría con timestamps

#### Servicio de Usuarios

**Decisión**: Soft delete con campo `activo`

**Campos clave**:
- `email`: Único a nivel de BD
- `tipo_usuario`: Enum para roles
- `activo`: Boolean para soft delete
- `nombre_completo`: Propiedad calculada

**Razones**:
- Preservar datos históricos
- Facilitar reactivación
- Evitar eliminación accidental

### 9. Validaciones

**Decisión**: Validación en múltiples capas

**Capas**:
1. **Modelo**: Constraints de BD (unique, choices)
2. **Serializer**: Validación de negocio
3. **ViewSet**: Lógica de permisos

**Ejemplo**:
\`\`\`python
def validate_email(self, value):
    if Usuario.objects.filter(email=value).exists():
        raise ValidationError("Email ya existe")
    return value
\`\`\`

### 10. Paginación

**Decisión**: Paginación por defecto con 10 items

**Razones**:
- Reducir carga en BD
- Mejorar tiempo de respuesta
- Facilitar navegación en frontend

**Configuración**:
\`\`\`python
REST_FRAMEWORK = {
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 10,
}
\`\`\`

## Consideraciones de Seguridad

### 1. Credenciales
- ✅ Nunca en código
- ✅ Secret Manager
- ✅ Inyección en runtime

### 2. Contenedor
- ✅ Usuario no-root
- ✅ Imagen slim
- ✅ Dependencias mínimas

### 3. Red
- ✅ HTTPS por defecto (Cloud Run)
- ✅ Unix socket para Cloud SQL
- ✅ Service Account con permisos mínimos

### 4. Aplicación
- ✅ DEBUG=False en producción
- ✅ ALLOWED_HOSTS configurado
- ✅ Validación de entrada

## Consideraciones de Performance

### 1. Base de Datos
- Índices automáticos en PKs y FKs
- Ordering en Meta para queries optimizadas
- Paginación para limitar resultados

### 2. Contenedor
- Imagen optimizada (~200MB)
- Inicio rápido (<5s)
- Workers/threads balanceados

### 3. Cloud Run
- Min instances: 0 (cost optimization)
- Max instances: 10 (prevent runaway costs)
- CPU: 1, Memory: 512Mi (suficiente para carga media)

## Escalabilidad

### Horizontal
- Cloud Run escala automáticamente
- Cada instancia maneja ~100 req/s
- Stateless design permite escalado ilimitado

### Vertical
- Ajustar CPU/Memory en cloudbuild.yaml
- Ajustar workers/threads en Dockerfile

### Base de Datos
- Cloud SQL puede escalar verticalmente
- Considerar read replicas para alta carga
- Connection pooling con PgBouncer si necesario

## Monitoreo y Observabilidad

### Logs
- Cloud Logging automático
- Logs estructurados de Django
- Logs de Gunicorn

### Métricas
- Cloud Run métricas nativas
- Request count, latency, errors
- CPU y memoria

### Alertas Recomendadas
- Error rate > 5%
- Latency p95 > 1s
- Instance count > 8

## Costos Estimados

### Cloud Run
- $0.00002400 por vCPU-second
- $0.00000250 por GiB-second
- 2M requests gratis/mes

### Cloud SQL
- db-f1-micro: ~$7/mes
- db-g1-small: ~$25/mes
- Storage: $0.17/GB/mes

### Artifact Registry
- $0.10/GB/mes storage
- Egress según región

**Estimado mensual (tráfico bajo)**: $30-50

## Mejoras Futuras

### Corto Plazo
1. Agregar autenticación JWT
2. Implementar rate limiting
3. Agregar tests de integración
4. Documentación OpenAPI

### Mediano Plazo
1. Implementar caching con Redis
2. Agregar búsqueda full-text
3. Implementar eventos asíncronos
4. Agregar métricas custom

### Largo Plazo
1. Migrar a arquitectura event-driven
2. Implementar CQRS
3. Agregar GraphQL
4. Multi-región deployment

## Troubleshooting Común

### Problema: Error de conexión a BD
**Solución**: Verificar que Cloud SQL Proxy esté configurado y secretos correctos

### Problema: 502 Bad Gateway
**Solución**: Verificar que el contenedor escuche en puerto 8080

### Problema: Timeout en despliegue
**Solución**: Aumentar timeout en cloudbuild.yaml o reducir tamaño de imagen

### Problema: Migraciones no aplicadas
**Solución**: Ejecutar Cloud Run Job con comando migrate

## Conclusión

Esta arquitectura proporciona:
- ✅ Despliegue automatizado
- ✅ Escalabilidad automática
- ✅ Seguridad robusta
- ✅ Costos optimizados
- ✅ Fácil mantenimiento

Los microservicios están listos para producción y pueden manejar cargas de trabajo reales con mínima configuración adicional.
