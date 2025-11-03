# Microservicios Django para Google Cloud Run

Este proyecto contiene dos microservicios independientes desarrollados en Django + Django REST Framework, listos para desplegar en Google Cloud Run.

## Estructura del Proyecto

\`\`\`
.
├── servicio-reservas/       # Microservicio de gestión de reservas
│   ├── Dockerfile
│   ├── cloudbuild.yaml
│   ├── requirements.txt
│   ├── manage.py
│   ├── README.md
│   └── ...
└── servicio-usuarios/       # Microservicio de gestión de usuarios
    ├── Dockerfile
    ├── cloudbuild.yaml
    ├── requirements.txt
    ├── manage.py
    ├── README.md
    └── ...
\`\`\`

## Microservicios

### 1. servicio-reservas
Gestión completa de reservas con endpoints CRUD.

### 2. servicio-usuarios
Gestión completa de usuarios con endpoints CRUD.

## Despliegue Rápido

Para desplegar cada microservicio:

\`\`\`bash
# Navegar al directorio del microservicio
cd servicio-reservas  # o servicio-usuarios

# Ejecutar Cloud Build
gcloud builds submit --config=cloudbuild.yaml .
\`\`\`

## Configuración de Google Cloud

Ambos microservicios están configurados para:
- **Artifact Registry**: `django-despliegue`
- **Cloud SQL Instance**: `practica2-477009:us-central1:id-postgres-bd`
- **Base de datos**: `reservas`
- **Secret Manager**: Variables `USER` y `PASSWORD`
- **Service Account**: `57187527650-compute@developer.gserviceaccount.com`

## Requisitos Previos

1. Tener configurado `gcloud` CLI
2. Permisos en el proyecto GCP
3. Artifact Registry `django-despliegue` creado
4. Instancia Cloud SQL configurada
5. Secretos `USER` y `PASSWORD` en Secret Manager

## Documentación Detallada

Consulta el README.md dentro de cada microservicio para instrucciones específicas.
