# Servicio de Reservas - Microservicio Django

Microservicio para la gestión completa de reservas desarrollado con Django + Django REST Framework, listo para desplegar en Google Cloud Run.

## Características

- ✅ CRUD completo de reservas
- ✅ Endpoints REST con Django REST Framework
- ✅ Conexión a PostgreSQL en Cloud SQL
- ✅ Configuración con Secret Manager
- ✅ Dockerfile optimizado para producción
- ✅ Cloud Build configurado para CI/CD
- ✅ Health check endpoint (`/healthz`)
- ✅ Gunicorn para producción

## Endpoints Disponibles

### Health Check
- `GET /healthz` - Verificar estado del servicio

### API de Reservas
- `GET /api/reservas/` - Listar todas las reservas
- `POST /api/reservas/` - Crear una nueva reserva
- `GET /api/reservas/{id}/` - Obtener una reserva específica
- `PUT /api/reservas/{id}/` - Actualizar una reserva completa
- `PATCH /api/reservas/{id}/` - Actualizar parcialmente una reserva
- `DELETE /api/reservas/{id}/` - Eliminar una reserva
- `POST /api/reservas/{id}/confirmar/` - Confirmar una reserva
- `POST /api/reservas/{id}/cancelar/` - Cancelar una reserva

### Filtros
- `GET /api/reservas/?estado=pendiente` - Filtrar por estado

## Modelo de Datos

\`\`\`python
Reserva:
  - id (auto)
  - nombre_cliente (string)
  - email_cliente (email)
  - telefono_cliente (string, opcional)
  - fecha_reserva (datetime)
  - numero_personas (integer)
  - estado (pendiente|confirmada|cancelada|completada)
  - notas (text, opcional)
  - fecha_creacion (datetime, auto)
  - fecha_actualizacion (datetime, auto)
\`\`\`

## Desarrollo Local

### Requisitos
- Python 3.11+
- PostgreSQL
- pip

### Configuración

1. Crear entorno virtual:
\`\`\`bash
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
\`\`\`

2. Instalar dependencias:
\`\`\`bash
pip install -r requirements.txt
\`\`\`

3. Configurar variables de entorno:
\`\`\`bash
export DATABASE_NAME=reservas
export DATABASE_USER=postgres
export DATABASE_PASSWORD=tu_password
export DATABASE_HOST=localhost
export DATABASE_PORT=5432
export DEBUG=True
\`\`\`

4. Ejecutar migraciones:
\`\`\`bash
python manage.py makemigrations
python manage.py migrate
\`\`\`

5. Crear superusuario (opcional):
\`\`\`bash
python manage.py createsuperuser
\`\`\`

6. Ejecutar servidor de desarrollo:
\`\`\`bash
python manage.py runserver
\`\`\`

El servicio estará disponible en `http://localhost:8000`

## Despliegue en Google Cloud Run

### Requisitos Previos
- Tener configurado `gcloud` CLI
- Permisos en el proyecto GCP
- Artifact Registry `django-despliegue` creado
- Instancia Cloud SQL configurada
- Secretos `USER` y `PASSWORD` en Secret Manager

### Despliegue Automático con Cloud Build

\`\`\`bash
gcloud builds submit --config=cloudbuild.yaml .
\`\`\`

Este comando ejecutará:
1. Construcción de la imagen Docker
2. Push al Artifact Registry
3. Despliegue automático en Cloud Run
4. Configuración de Cloud SQL
5. Inyección de secretos desde Secret Manager

### Verificar Despliegue

Una vez desplegado, obtén la URL del servicio:
\`\`\`bash
gcloud run services describe servicio-reservas --region=us-central1 --format='value(status.url)'
\`\`\`

Verifica el health check:
\`\`\`bash
curl https://[TU-URL]/healthz
\`\`\`

## Ejecutar Migraciones en Cloud Run

Después del primer despliegue, ejecuta las migraciones:

\`\`\`bash
gcloud run jobs create servicio-reservas-migrate \
  --image=us-central1-docker.pkg.dev/[PROJECT_ID]/django-despliegue/servicio-reservas:latest \
  --region=us-central1 \
  --service-account=57187527650-compute@developer.gserviceaccount.com \
  --add-cloudsql-instances=practica2-477009:us-central1:id-postgres-bd \
  --set-env-vars=DATABASE_NAME=reservas,CLOUD_SQL_CONNECTION_NAME=practica2-477009:us-central1:id-postgres-bd \
  --set-secrets=DATABASE_USER=USER:latest,DATABASE_PASSWORD=PASSWORD:latest \
  --command=python \
  --args=manage.py,migrate

gcloud run jobs execute servicio-reservas-migrate --region=us-central1
\`\`\`

## Pruebas

Ejecutar tests localmente:
\`\`\`bash
python manage.py test
\`\`\`

## Ejemplo de Uso de la API

### Crear una reserva
\`\`\`bash
curl -X POST https://[TU-URL]/api/reservas/ \
  -H "Content-Type: application/json" \
  -d '{
    "nombre_cliente": "Juan Pérez",
    "email_cliente": "juan@example.com",
    "telefono_cliente": "1234567890",
    "fecha_reserva": "2025-02-15T19:00:00Z",
    "numero_personas": 4,
    "estado": "pendiente",
    "notas": "Mesa cerca de la ventana"
  }'
\`\`\`

### Listar reservas
\`\`\`bash
curl https://[TU-URL]/api/reservas/
\`\`\`

### Confirmar una reserva
\`\`\`bash
curl -X POST https://[TU-URL]/api/reservas/1/confirmar/
\`\`\`

## Configuración de Cloud

### Artifact Registry
- Nombre: `django-despliegue`
- Región: `us-central1`
- Formato: Docker

### Cloud SQL
- Instancia: `practica2-477009:us-central1:id-postgres-bd`
- Base de datos: `reservas`
- Engine: PostgreSQL

### Secret Manager
- `USER`: Usuario de la base de datos
- `PASSWORD`: Contraseña de la base de datos

### Service Account
- Email: `57187527650-compute@developer.gserviceaccount.com`
- Permisos necesarios:
  - Cloud Run Admin
  - Cloud SQL Client
  - Secret Manager Secret Accessor
  - Artifact Registry Writer

## Notas Técnicas

### Decisiones de Arquitectura

1. **Django REST Framework**: Elegido por su robustez y facilidad para crear APIs RESTful con serialización automática y validación.

2. **Gunicorn**: Servidor WSGI de producción con configuración de 2 workers y 4 threads, optimizado para Cloud Run.

3. **Conexión a Cloud SQL**: Utiliza Unix socket (`/cloudsql/[CONNECTION_NAME]`) para conexión segura y de baja latencia.

4. **Secret Manager**: Las credenciales se inyectan como variables de entorno en tiempo de ejecución, nunca se almacenan en el código.

5. **Health Check**: Endpoint `/healthz` requerido por Cloud Run para verificar el estado del servicio.

6. **Usuario no-root**: El contenedor ejecuta la aplicación con un usuario sin privilegios para mayor seguridad.

### Optimizaciones

- Imagen base `python:3.11-slim` para reducir tamaño
- Multi-stage no necesario dado el tamaño reducido
- Cache de pip deshabilitado para reducir tamaño de imagen
- Static files configurados para servirse desde Cloud Storage o CDN en producción

### Seguridad

- `ALLOWED_HOSTS` configurado para aceptar todas las peticiones (Cloud Run maneja el routing)
- `DEBUG=False` en producción
- Credenciales desde Secret Manager
- Usuario no-root en contenedor
- Service Account con permisos mínimos necesarios

## Troubleshooting

### Error de conexión a la base de datos
Verifica que:
- La instancia Cloud SQL esté activa
- Los secretos USER y PASSWORD estén correctamente configurados
- El Service Account tenga permisos de Cloud SQL Client

### Error 500 en producción
Revisa los logs:
\`\`\`bash
gcloud run services logs read servicio-reservas --region=us-central1
\`\`\`

### Migraciones no aplicadas
Ejecuta el job de migraciones como se indica en la sección correspondiente.

## Soporte

Para problemas o preguntas, revisa:
- Logs de Cloud Run
- Logs de Cloud Build
- Estado de Cloud SQL
- Configuración de Secret Manager
