# Script de Despliegue con Docker para SGTR en Windows Server
# Requiere Docker Desktop (o Docker Engine) y Docker Compose instalados

$ErrorActionPreference = "Stop"

Write-Host "=== Iniciando Despliegue con Docker ===" -ForegroundColor Cyan

# 1. Verificar Docker
try {
    $dockerVersion = docker --version
    Write-Host "Docker detectado: $dockerVersion" -ForegroundColor Green
} catch {
    Write-Error "Docker no encontrado. Por favor instala Docker Desktop y asegúrate de que esté corriendo."
    exit 1
}

# 2. Configurar Variables de Entorno
if (Test-Path ".env") {
    Write-Host "Archivo .env detectado." -ForegroundColor Green
} else {
    Write-Warning "Archivo .env no encontrado. Creando desde plantilla..."
    Copy-Item .env.example .env
    Write-Host "IMPORTANTE: Se ha creado el archivo .env." -ForegroundColor Magenta
    Write-Host "Por favor, edítalo para configurar contraseñas seguras antes de continuar." -ForegroundColor Magenta
    
    $continuar = Read-Host "¿Ya editaste el archivo .env? (S/N)"
    if ($continuar -ne 'S') {
        Write-Host "Edita el archivo y vuelve a ejecutar este script." -ForegroundColor Yellow
        exit 0
    }
}

# 3. Construir e Iniciar Contenedores
Write-Host "Construyendo e iniciando contenedores..." -ForegroundColor Yellow
docker-compose up -d --build

# 4. Verificar Estado
Write-Host "Verificando estado de los servicios..." -ForegroundColor Yellow
Start-Sleep -Seconds 10 # Esperar un poco a que inicien
docker-compose ps

# 5. Ejecutar Migraciones (dentro del contenedor)
Write-Host "Ejecutando migraciones de base de datos..." -ForegroundColor Yellow
docker-compose exec web python manage.py migrate

# 6. Recolectar Estáticos
Write-Host "Recolectando archivos estáticos..." -ForegroundColor Yellow
docker-compose exec web python manage.py collectstatic --noinput

# 7. Crear Superusuario (Opcional)
$crearAdmin = Read-Host "¿Deseas crear un superusuario administrador? (S/N)"
if ($crearAdmin -eq 'S') {
    docker-compose exec web python manage.py createsuperuser
}

Write-Host "=== Despliegue Completado ===" -ForegroundColor Cyan
Write-Host "La aplicación debería estar accesible en http://localhost:8000" -ForegroundColor Green
