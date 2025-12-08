<#
.SYNOPSIS
    Script de Despliegue Universal para SGTR (Windows Server 2019+)
    
.DESCRIPTION
    Este script automatiza la instalación y despliegue de la aplicación.
    Soporta dos modos:
    1. DOCKER (Recomendado): Usa contenedores para aislar la aplicación.
    2. NATIVO (Portable): Instala Python (si falta), crea entorno virtual y configura todo localmente.

.NOTES
    Versión: 2.0
    Autor: Antigravity
#>

$ErrorActionPreference = "Stop"
$ScriptPath = $PSScriptRoot

function Write-Color {
    param($Text, $Color = "White")
    Write-Host $Text -ForegroundColor $Color
}

function Check-Admin {
    $currentPrincipal = New-Object Security.Principal.WindowsPrincipal([Security.Principal.WindowsIdentity]::GetCurrent())
    if (-not $currentPrincipal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)) {
        Write-Color "Este script requiere permisos de Administrador para configurar el sistema." "Red"
        Write-Color "Por favor, ejecútalo como Administrador." "Yellow"
        exit 1
    }
}

function Setup-Native {
    Write-Color "`n=== Configuración Nativa (Portable) ===" "Cyan"
    
    # 1. Verificar Python
    try {
        $pyVersion = python --version 2>&1
        Write-Color "Python detectado: $pyVersion" "Green"
    }
    catch {
        Write-Color "Python no encontrado." "Red"
        Write-Color "Intentando descargar e instalar Python (esto puede tardar)..." "Yellow"
        # Aquí podríamos automatizar la descarga, pero por seguridad pedimos instalación manual o usamos winget si existe.
        if (Get-Command winget -ErrorAction SilentlyContinue) {
            Write-Color "Usando Winget para instalar Python..." "Cyan"
            winget install -e --id Python.Python.3.11
            Write-Color "Python instalado. Por favor reinicia el script." "Green"
            exit 0
        }
        else {
            Write-Error "No se pudo instalar Python automáticamente. Por favor instala Python 3.10+ manualmente desde python.org y agrégalo al PATH."
        }
    }

    # 2. Entorno Virtual
    if (-not (Test-Path "$ScriptPath\.venv")) {
        Write-Color "Creando entorno virtual..." "Yellow"
        python -m venv "$ScriptPath\.venv"
    }
    else {
        Write-Color "Entorno virtual existente detectado." "Green"
    }

    # 3. Dependencias
    Write-Color "Instalando/Actualizando dependencias..." "Yellow"
    & "$ScriptPath\.venv\Scripts\python.exe" -m pip install --upgrade pip
    & "$ScriptPath\.venv\Scripts\python.exe" -m pip install -r "$ScriptPath\requirements.txt"
    & "$ScriptPath\.venv\Scripts\python.exe" -m pip install waitress

    # 4. Configuración .env
    if (-not (Test-Path "$ScriptPath\.env")) {
        Write-Color "Creando archivo de configuración (.env)..." "Yellow"
        Copy-Item "$ScriptPath\.env.example" "$ScriptPath\.env"
        
        # Generar Secret Key aleatoria
        $secret = -join ((65..90) + (97..122) + (48..57) | Get-Random -Count 50 | % { [char]$_ })
        (Get-Content "$ScriptPath\.env") -replace 'django-insecure-.*', $secret | Set-Content "$ScriptPath\.env"
        
        # Configurar para SQLite por defecto (Portable)
        (Get-Content "$ScriptPath\.env") -replace '^DATABASE_URL=', '# DATABASE_URL=' | Set-Content "$ScriptPath\.env"
        Write-Color "Configuración base creada (Modo SQLite)." "Green"
    }

    # 5. Base de Datos y Estáticos
    Write-Color "Preparando base de datos..." "Yellow"
    & "$ScriptPath\.venv\Scripts\python.exe" "$ScriptPath\manage.py" migrate
    
    Write-Color "Recolectando archivos estáticos..." "Yellow"
    & "$ScriptPath\.venv\Scripts\python.exe" "$ScriptPath\manage.py" collectstatic --noinput

    # 6. Firewall
    Write-Color "Configurando Firewall de Windows (Puerto 8000)..." "Yellow"
    New-NetFirewallRule -DisplayName "SGTR Web App" -Direction Inbound -LocalPort 8000 -Protocol TCP -Action Allow -ErrorAction SilentlyContinue | Out-Null

    # 7. Ejecutar
    Write-Color "`n=== Instalación Completada ===" "Green"
    $ip = (Get-NetIPAddress -AddressFamily IPv4 | Where-Object { $_.InterfaceAlias -notlike "*Loopback*" }).IPAddress | Select-Object -First 1
    Write-Color "La aplicación se iniciará ahora." "Cyan"
    Write-Color "Accede vía web en: http://localhost:8000 o http://$($ip):8000" "Cyan"
    Write-Color "Presiona Ctrl+C para detener el servidor." "Yellow"
    
    & "$ScriptPath\.venv\Scripts\python.exe" "$ScriptPath\run_waitress.py"
}

function Setup-Docker {
    Write-Color "`n=== Configuración Docker ===" "Cyan"
    
    if (-not (Get-Command docker -ErrorAction SilentlyContinue)) {
        Write-Error "Docker no está instalado o no está en el PATH."
    }

    if (-not (Test-Path "$ScriptPath\.env")) {
        Copy-Item "$ScriptPath\.env.example" "$ScriptPath\.env"
        Write-Color "Archivo .env creado. Por favor edítalo si necesitas cambiar contraseñas." "Yellow"
    }

    Write-Color "Iniciando contenedores..." "Yellow"
    docker-compose up -d --build

    Write-Color "Esperando a que la base de datos inicie..." "Yellow"
    Start-Sleep -Seconds 10

    Write-Color "Ejecutando migraciones..." "Yellow"
    docker-compose exec web python manage.py migrate
    docker-compose exec web python manage.py collectstatic --noinput

    Write-Color "`n=== Despliegue Docker Completado ===" "Green"
    Write-Color "Accede en http://localhost:8000" "Cyan"
}

# --- Main ---
Clear-Host
Check-Admin
Write-Color "=== SGTR: Sistema de Gestión de Tickets y Reparaciones ===" "Cyan"
Write-Color "Selecciona el modo de despliegue:" "White"
Write-Color "1. NATIVO / PORTABLE (Recomendado para Server 2019 sin Docker)" "Green"
Write-Color "2. DOCKER (Requiere Docker Desktop instalado)" "Blue"
Write-Color "3. Salir" "Gray"

$opcion = Read-Host "Opción [1-3]"

switch ($opcion) {
    '1' { Setup-Native }
    '2' { Setup-Docker }
    '3' { exit }
    Default { Write-Color "Opción no válida." "Red" }
}
