# Script para actualizar el servidor Lightsail con los últimos cambios
# Ejecuta este script EN EL SERVIDOR LIGHTSAIL via RDP

$ErrorActionPreference = "Stop"

Write-Host "=== Actualizando SGTR en Lightsail ===" -ForegroundColor Cyan

# 1. Ir al directorio del proyecto
$ProjectPath = "C:\sgtr_proyecto"
if (-not (Test-Path $ProjectPath)) {
    $ProjectPath = "C:\Users\Administrator\Documents\GitHub\sistema-tickets-django"
}

if (-not (Test-Path $ProjectPath)) {
    Write-Host "ERROR: No se encontró el directorio del proyecto" -ForegroundColor Red
    Write-Host "Por favor, actualiza la variable `$ProjectPath en este script" -ForegroundColor Yellow
    exit 1
}

Set-Location $ProjectPath
Write-Host "Directorio del proyecto: $ProjectPath" -ForegroundColor Green

# 2. Hacer pull de los últimos cambios
Write-Host "`nObteniendo últimos cambios de GitHub..." -ForegroundColor Yellow
git fetch origin
git pull origin antigravity

# 3. Recolectar archivos estáticos (para las nuevas imágenes)
Write-Host "`nRecolectando archivos estáticos..." -ForegroundColor Yellow
& "$ProjectPath\.venv\Scripts\python.exe" "$ProjectPath\manage.py" collectstatic --noinput

# 4. Reiniciar el servidor
Write-Host "`nLos cambios se han aplicado." -ForegroundColor Green
Write-Host "IMPORTANTE: Debes reiniciar el servidor Waitress para ver los cambios." -ForegroundColor Yellow
Write-Host "`nOpciones para reiniciar:" -ForegroundColor Cyan
Write-Host "1. Si el servidor está corriendo en una ventana, presiona Ctrl+C y vuelve a ejecutar:" -ForegroundColor White
Write-Host "   .\.venv\Scripts\python.exe run_waitress.py" -ForegroundColor Gray
Write-Host "`n2. Si está corriendo como servicio, reinicia el servicio desde Services.msc" -ForegroundColor White
Write-Host "`n3. O simplemente reinicia la instancia de Lightsail desde la consola AWS" -ForegroundColor White

Write-Host "`n=== Actualización completada ===" -ForegroundColor Green
