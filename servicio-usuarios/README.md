# Servicio de Usuarios - Microservicio Django

Microservicio para la gestión completa de usuarios desarrollado con Django + Django REST Framework, listo para desplegar en Google Cloud Run.

## Características

- ✅ CRUD completo de usuarios
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

### API de Usuarios
- `GET /api/usuarios/` - Listar todos los usuarios
- `POST /api/usuarios/` - Crear un nuevo usuario
- `GET /api/usuarios/{id}/` - Obtener un usuario específico
- `PUT /api/usuarios/{id}/` - Actualizar un usuario completo
- `PATCH /api/usuarios/{id}/` - Actualizar parcialmente un usuario
- `DELETE /api/usuarios/{id}/` - Eliminar un usuario
- `GET /api/usuarios/activos/` - Listar solo usuarios activos
- `POST /api/usuarios/{id}/desactivar/` - Desactivar un usuario
- `POST /api/usuarios/{id}/activar/` - Activar un usuario

### Filtros
- `GET /api/usuarios/?tipo=cliente` - Filtrar por tipo de usuario
- `GET /api/usuarios/?activo=true` - Filtrar por estado activo

## Modelo de Datos

\`\`\`python
Usuario:
  - id (auto)
  - nombre (string)
  - apellido (string)
  - email (email, único)
  - telefono (string, opcional)
  - tipo_usuario (cliente|administrador|empleado)
  - activo (boolean)
  - direccion (text, opcional)
  - fecha_registro (datetime, auto)
  - fecha_actualizacion (datetime, auto)
  - nombre_completo (propiedad calculada)
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
gcloud run services describe servicio-usuarios --region=us-central1 --format='value(status.url)'
\`\`\`

Verifica el health check:
\`\`\`bash
curl https://[TU-URL]/healthz
\`\`\`

## Ejecutar Migraciones en Cloud Run

Después del primer despliegue, ejecuta las migraciones:

\`\`\`bash
gcloud run jobs create servicio-usuarios-migrate \
  --image=us-central1-docker.pkg.dev/[PROJECT_ID]/django-despliegue/servicio-usuarios:latest \
  --region=us-central1 \
  --service-account=57187527650-compute@developer.gserviceaccount.com \
  --add-cloudsql-instances=practica2-477009:us-central1:id-postgres-bd \
  --set-env-vars=DATABASE_NAME=reservas,CLOUD_SQL_CONNECTION_NAME=practica2-477009:us-central1:id-postgres-bd \
  --set-secrets=DATABASE_USER=USER:latest,DATABASE_PASSWORD=PASSWORD:latest \
  --command=python \
  --args=manage.py,migrate

gcloud run jobs execute servicio-usuarios-migrate --region=us-central1
\`\`\`

## Pruebas

Ejecutar tests localmente:
\`\`\`bash
python manage.py test
\`\`\`

## Ejemplo de Uso de la API

### Crear un usuario
\`\`\`bash
curl -X POST https://[TU-URL]/api/usuarios/ \
  -H "Content-Type: application/json" \
  -d '{
    "nombre": "Juan",
    "apellido": "Pérez",
    "email": "juan@example.com",
    "telefono": "1234567890",
    "tipo_usuario": "cliente",
    "activo": true,
    "direccion": "Calle Principal 123"
  }'
\`\`\`

### Listar usuarios
\`\`\`bash
curl https://[TU-URL]/api/usuarios/
\`\`\`

### Desactivar un usuario
\`\`\`bash
curl -X POST https://[TU-URL]/api/usuarios/1/desactivar/
\`\`\`

### Filtrar usuarios activos
\`\`\`bash
curl https://[TU-URL]/api/usuarios/?activo=true
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

7. **Email único**: El modelo Usuario implementa validación de email único tanto a nivel de base de datos como en el serializer.

### Optimizaciones

- Imagen base `python:3.11-slim` para reducir tamaño
- Multi-stage no necesario dado el tamaño reducido
- Cache de pip deshabilitado para reducir tamaño de imagen
- Static files configurados para servirse desde Cloud Storage o CDN en producción
- Propiedad calculada `nombre_completo` para facilitar el uso en frontend

### Seguridad

- `ALLOWED_HOSTS` configurado para aceptar todas las peticiones (Cloud Run maneja el routing)
- `DEBUG=False` en producción
- Credenciales desde Secret Manager
- Usuario no-root en contenedor
- Service Account con permisos mínimos necesarios
- Validación de email único para prevenir duplicados

## Troubleshooting

### Error de conexión a la base de datos
Verifica que:
- La instancia Cloud SQL esté activa
- Los secretos USER y PASSWORD estén correctamente configurados
- El Service Account tenga permisos de Cloud SQL Client

### Error 500 en producción
Revisa los logs:
\`\`\`bash
gcloud run services logs read servicio-usuarios --region=us-central1
\`\`\`

### Migraciones no aplicadas
Ejecuta el job de migraciones como se indica en la sección correspondiente.

### Error de email duplicado
El sistema valida que los emails sean únicos. Si intentas crear un usuario con un email existente, recibirás un error 400.

## Soporte

Para problemas o preguntas, revisa:
- Logs de Cloud Run
- Logs de Cloud Build
- Estado de Cloud SQL
- Configuración de Secret Manager
