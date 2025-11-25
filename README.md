# Sistema de Gestión de Tickets y Reparaciones (SGTR)

Sistema Django para la gestión de tickets de reparación de herramientas con soporte para inventario, usuarios y auditoría.

## 🚀 Características

- ✅ **Gestión de Tickets**: Creación, seguimiento y resolución de tickets de reparación
- ✅ **Inventario de Herramientas**: Control completo del inventario
- ✅ **Sistema de Usuarios**: Autenticación y permisos
- ✅ **Auditoría**: Registro completo de cambios
- ✅ **Seguridad ISO 27001**: Implementación de controles de seguridad
- ✅ **Base de Datos Dual**: SQLite para desarrollo, PostgreSQL para producción
- ✅ **Docker**: Despliegue containerizado con Docker Compose

## 📋 Requisitos Previos

### Para Desarrollo Local (SQLite)
- Python 3.13 o superior
- pip (gestor de paquetes de Python)

### Para Producción con Docker (PostgreSQL)
- Docker Desktop instalado y corriendo
- Docker Compose

## 🛠️ Instalación y Configuración

### Opción 1: Desarrollo Local con SQLite

#### Windows

1. **Clonar el repositorio** (si aplica)
   ```bash
   git clone <url-del-repositorio>
   cd sgtr_proyecto
   ```

2. **Crear y activar entorno virtual**
   ```bash
   python -m venv .venv
   .venv\Scripts\activate
   ```

3. **Instalar dependencias**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configurar variables de entorno** (opcional para desarrollo)
   ```bash
   set DEBUG=True
   set SECRET_KEY=dev-secret-key-change-in-production
   ```

5. **Aplicar migraciones**
   ```bash
   python manage.py migrate
   ```

6. **Crear superusuario**
   ```bash
   python manage.py createsuperuser
   ```

7. **Iniciar servidor**
   
   **Opción A - Servidor simple (solo localhost):**
   ```bash
   python manage.py runserver
   ```
   
   **Opción B - Servidor en red local (accesible desde otros equipos):**
   ```bash
   start_server.bat
   ```
   
   Esto iniciará el servidor en `0.0.0.0:8000` y mostrará la IP local para acceso desde otros equipos.

#### Linux/Mac

1. **Clonar el repositorio** (si aplica)
   ```bash
   git clone <url-del-repositorio>
   cd sgtr_proyecto
   ```

2. **Crear y activar entorno virtual**
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```

3. **Instalar dependencias**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configurar variables de entorno** (opcional para desarrollo)
   ```bash
   export DEBUG=True
   export SECRET_KEY=dev-secret-key-change-in-production
   ```

5. **Aplicar migraciones**
   ```bash
   python manage.py migrate
   ```

6. **Crear superusuario**
   ```bash
   python manage.py createsuperuser
   ```

7. **Iniciar servidor**
   
   **Opción A - Servidor simple:**
   ```bash
   python manage.py runserver
   ```
   
   **Opción B - Servidor en red local:**
   ```bash
   chmod +x start_server.sh
   ./start_server.sh
   ```

### Opción 2: Producción con Docker y PostgreSQL

#### Requisitos
- Docker Desktop debe estar **instalado y corriendo**
- Verificar con: `docker --version` y `docker-compose --version`

#### Pasos

1. **Configurar variables de entorno**
   
   Copiar el archivo de ejemplo y editarlo:
   ```bash
   copy .env.example .env     # Windows
   cp .env.example .env       # Linux/Mac
   ```
   
   Editar `.env` y cambiar los valores:
   ```env
   # Database
   POSTGRES_PASSWORD=tu_password_seguro_aqui
   
   # Django
   SECRET_KEY=genera_una_clave_secreta_unica
   DEBUG=False
   ALLOWED_HOSTS=localhost,127.0.0.1,tu-dominio.com
   ```
   
   **Generar SECRET_KEY seguro:**
   ```bash
   python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
   ```

2. **Construir las imágenes Docker**
   ```bash
   docker-compose build
   ```

3. **Iniciar los servicios**
   ```bash
   docker-compose up -d
   ```
   
   Esto iniciará:
   - PostgreSQL (base de datos)
   - Django/Gunicorn (aplicación web)

4. **Verificar que los servicios están corriendo**
   ```bash
   docker-compose ps
   ```

5. **Ver logs (opcional)**
   ```bash
   docker-compose logs -f web
   ```

6. **Crear superusuario (solo la primera vez)**
   ```bash
   docker-compose exec web python manage.py createsuperuser
   ```

7. **Acceder a la aplicación**
   - Abrir navegador en: `http://localhost:8000`

#### Comandos útiles de Docker

```bash
# Detener servicios
docker-compose stop

# Detener y eliminar contenedores
docker-compose down

# Detener y eliminar contenedores + volúmenes (¡CUIDADO! Borra la base de datos)
docker-compose down -v

# Ver logs en tiempo real
docker-compose logs -f

# Ejecutar comandos dentro del contenedor
docker-compose exec web python manage.py <comando>

# Reiniciar servicios
docker-compose restart

# Reconstruir y reiniciar
docker-compose up -d --build
```

## 🌐 Acceso a la Aplicación

### Desarrollo Local
- **URL**: `http://localhost:8000`
- **Admin**: `http://localhost:8000/admin`

### Red Local (usando start_server.bat/sh)
- **URL Local**: `http://localhost:8000`
- **URL Red**: `http://<tu-ip-local>:8000` (se muestra al iniciar el script)

### Docker
- **URL**: `http://localhost:8000`
- **Admin**: `http://localhost:8000/admin`

## 📁 Estructura del Proyecto

```
sgtr_proyecto/
├── sgtr/                   # Configuración principal de Django
│   ├── settings.py        # Configuración (con mejoras de seguridad)
│   ├── urls.py            # URLs principales
│   └── wsgi.py            # WSGI para producción
├── tickets/               # App de gestión de tickets
├── inventario/            # App de inventario de herramientas
├── usuarios/              # App de gestión de usuarios
├── templates/             # Plantillas HTML
├── static/                # Archivos estáticos (CSS, JS, imágenes)
├── dockerfile             # Configuración Docker
├── docker-compose.yml     # Orquestación de servicios
├── entrypoint.sh          # Script de inicio para Docker
├── start_server.bat       # Script de inicio para Windows
├── start_server.sh        # Script de inicio para Linux/Mac
├── requirements.txt       # Dependencias de Python
├── .env.example           # Plantilla de variables de entorno
└── README.md              # Este archivo
```

## 🔒 Seguridad

El proyecto implementa controles de seguridad según ISO 27001:

- ✅ **A.9.4.3**: Gestión de contraseñas (SECRET_KEY en variables de entorno)
- ✅ **A.12.4.1**: Registro de eventos (logging configurado)
- ✅ **A.13.1.3**: Segregación de redes (ALLOWED_HOSTS, CSRF_TRUSTED_ORIGINS)
- ✅ **A.14.1.2**: Seguridad de servicios (middleware de seguridad)
- ✅ **A.9.4.2**: Procedimientos de inicio de sesión seguros (expiración de sesión)

### Configuración de Seguridad en Producción

Cuando `DEBUG=False`, se activan automáticamente:
- HTTPS forzado (`SECURE_SSL_REDIRECT`)
- Cookies seguras (`SESSION_COOKIE_SECURE`, `CSRF_COOKIE_SECURE`)
- HSTS (HTTP Strict Transport Security)
- Protección XSS
- Protección contra clickjacking

## 🗄️ Base de Datos

El sistema soporta dos configuraciones:

### SQLite (Desarrollo)
- Automático cuando no hay `DATABASE_URL`
- Archivo: `db.sqlite3`
- Portable y fácil de respaldar

### PostgreSQL (Producción/Docker)
- Automático cuando hay `DATABASE_URL`
- Mejor rendimiento
- Conexiones persistentes
- Configurado en `docker-compose.yml`

## 📊 Migraciones

```bash
# Crear nuevas migraciones
python manage.py makemigrations

# Aplicar migraciones
python manage.py migrate

# Ver plan de migración
python manage.py migrate --plan

# Revertir migración
python manage.py migrate <app_name> <migration_number>
```

## 🧪 Verificación del Sistema

```bash
# Verificar configuración de Django
python manage.py check

# Verificar configuración de producción
python manage.py check --deploy

# Recolectar archivos estáticos
python manage.py collectstatic
```

## 🐛 Troubleshooting

### Error: "Docker daemon is not running"
**Solución**: Iniciar Docker Desktop

### Error: "Port 8000 is already in use"
**Solución**: 
```bash
# Windows
netstat -ano | findstr :8000
taskkill /PID <PID> /F

# Linux/Mac
lsof -ti:8000 | xargs kill -9
```

### Error: "No module named 'django'"
**Solución**: Activar el entorno virtual y reinstalar dependencias
```bash
.venv\Scripts\activate     # Windows
source .venv/bin/activate  # Linux/Mac
pip install -r requirements.txt
```

### Error de migraciones
**Solución**: Eliminar base de datos y volver a migrar
```bash
# SQLite
del db.sqlite3
python manage.py migrate

# Docker
docker-compose down -v
docker-compose up -d
```

## 📝 Logs

### Desarrollo Local
- Consola: Nivel INFO
- Archivo: `logs/django.log` (nivel WARNING)

### Docker
```bash
# Ver logs de la aplicación
docker-compose logs -f web

# Ver logs de la base de datos
docker-compose logs -f db
```

## 🤝 Contribución

1. Crear una rama para tu feature: `git checkout -b feature/nueva-funcionalidad`
2. Hacer commit de tus cambios: `git commit -am 'Agregar nueva funcionalidad'`
3. Push a la rama: `git push origin feature/nueva-funcionalidad`
4. Crear un Pull Request

## 📄 Licencia

[Especificar licencia]

## 👥 Autores

[Especificar autores]

## 📞 Soporte

Para reportar problemas o solicitar ayuda:
- Crear un issue en el repositorio
- Contactar al equipo de desarrollo

---

**Nota**: Este README asume que ya tienes el proyecto configurado. Si estás empezando desde cero, asegúrate de seguir todos los pasos en orden.
