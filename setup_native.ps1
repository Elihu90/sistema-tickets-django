# Script de Instalación para SGTR en Windows Server
# Requiere Python 3.10+ y PostgreSQL instalados previamente

$ErrorActionPreference = "Stop"

Write-Host "=== Iniciando Instalación de SGTR ===" -ForegroundColor Cyan

# 1. Verificar Python
try {
    $pythonVersion = python --version
    Write-Host "Python detectado: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Error "Python no encontrado. Por favor instala Python 3.10+ y agrégalo al PATH."
    exit 1
}

# 2. Crear Entorno Virtual
if (-not (Test-Path ".venv")) {
    Write-Host "Creando entorno virtual..." -ForegroundColor Yellow
    python -m venv .venv
} else {
    Write-Host "Entorno virtual ya existe." -ForegroundColor Green
}

# 3. Activar Entorno e Instalar Dependencias
Write-Host "Instalando dependencias..." -ForegroundColor Yellow
& .\.venv\Scripts\python.exe -m pip install --upgrade pip
& .\.venv\Scripts\python.exe -m pip install -r requirements.txt

# 4. Configurar Base de Datos
$dbChoice = Read-Host "¿Deseas usar PostgreSQL (P) o SQLite (S)? (P/S)"
if ($dbChoice -eq 'S') {
    Write-Host "Configurando para SQLite..." -ForegroundColor Green
    if (Test-Path ".env") {
        # Comentar DATABASE_URL si existe para forzar SQLite
        (Get-Content .env) -replace '^DATABASE_URL=', '# DATABASE_URL=' | Set-Content .env
    } else {
        Copy-Item .env.example .env
        # Asegurar que DATABASE_URL esté comentada en el nuevo .env
        (Get-Content .env) -replace '^DATABASE_URL=', '# DATABASE_URL=' | Set-Content .env
    }
    Write-Host "Usando SQLite. No se requiere configuración adicional de base de datos." -ForegroundColor Green
} else {
    Write-Host "Configurando para PostgreSQL..." -ForegroundColor Green
    if (Test-Path ".env") {
        Write-Host "Archivo .env detectado." -ForegroundColor Green
    } else {
        Write-Warning "Archivo .env no encontrado. Por favor crea uno basado en .env.example antes de continuar."
        Copy-Item .env.example .env
        Write-Host "Se ha creado un archivo .env de plantilla. Por favor edítalo con tus credenciales de PostgreSQL." -ForegroundColor Magenta
        exit 1
    }
}

Write-Host "Aplicando migraciones de base de datos..." -ForegroundColor Yellow
& .\.venv\Scripts\python.exe manage.py migrate

Write-Host "Recolectando archivos estáticos..." -ForegroundColor Yellow
& .\.venv\Scripts\python.exe manage.py collectstatic --noinput

# 5. Crear Superusuario (Opcional)
$crearAdmin = Read-Host "¿Deseas crear un superusuario administrador? (S/N)"
if ($crearAdmin -eq 'S') {
    & .\.venv\Scripts\python.exe manage.py createsuperuser
}

Write-Host "=== Instalación Completada con Éxito ===" -ForegroundColor Cyan
Write-Host "Para iniciar el servidor, ejecuta:"
Write-Host "    .\.venv\Scripts\python.exe run_waitress.py" -ForegroundColor Green
