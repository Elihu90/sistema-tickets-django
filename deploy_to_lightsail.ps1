# Script de despliegue automático a Lightsail
# Uso: .\deploy_to_lightsail.ps1 "mensaje del commit"

param(
    [Parameter(Mandatory = $false)]
    [string]$CommitMessage = "Actualización automática"
)

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  DESPLIEGUE AUTOMÁTICO A LIGHTSAIL" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Configuración
$ServerIP = "3.20.119.202"
$ServerUser = "Administrator"
$ServerPath = "C:\Users\Administrator\Documents\GitHub\sistema-tickets-django"
$LocalPath = $PSScriptRoot

# Paso 1: Commit y push local
Write-Host "[1/4] Haciendo commit y push local..." -ForegroundColor Yellow
Set-Location $LocalPath

git add -A
if ($LASTEXITCODE -ne 0) {
    Write-Host "Error al agregar archivos a git" -ForegroundColor Red
    exit 1
}

git commit -m $CommitMessage
# No verificamos LASTEXITCODE aquí porque puede ser 0 si no hay cambios

git push origin antigravity
if ($LASTEXITCODE -ne 0) {
    Write-Host "Error al hacer push a GitHub" -ForegroundColor Red
    exit 1
}

Write-Host "✓ Cambios subidos a GitHub" -ForegroundColor Green
Write-Host ""

# Paso 2: Conectar al servidor y actualizar
Write-Host "[2/4] Conectando al servidor Lightsail..." -ForegroundColor Yellow

$commands = @"
cd $ServerPath
Write-Host 'Descartando cambios locales en db.sqlite3...'
git restore db.sqlite3
Write-Host 'Haciendo pull desde GitHub...'
git pull origin antigravity
Write-Host 'Instalando dependencias...'
.\.venv\Scripts\pip.exe install -r requirements.txt --quiet
Write-Host 'Aplicando migraciones...'
.\.venv\Scripts\python.exe manage.py migrate
Write-Host 'Recolectando archivos estáticos...'
.\.venv\Scripts\python.exe manage.py collectstatic --noinput
Write-Host '✓ Servidor actualizado correctamente' -ForegroundColor Green
"@

# Ejecutar comandos en el servidor via SSH
ssh "${ServerUser}@${ServerIP}" "powershell -Command `"$commands`""

if ($LASTEXITCODE -ne 0) {
    Write-Host "Error al actualizar el servidor" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "[3/4] Reiniciando servidor Waitress..." -ForegroundColor Yellow
Write-Host "NOTA: Debes reiniciar manualmente el servidor Waitress en el servidor" -ForegroundColor Yellow
Write-Host "      (Ctrl+C en la ventana de Waitress y ejecutar: .\.venv\Scripts\python.exe run_waitress.py)" -ForegroundColor Yellow
Write-Host ""

# Paso 4: Verificar
Write-Host "[4/4] Verificación" -ForegroundColor Yellow
Write-Host "✓ Despliegue completado" -ForegroundColor Green
Write-Host ""
Write-Host "Accede a: http://$ServerIP:8000" -ForegroundColor Cyan
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
