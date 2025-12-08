$IntervalSeconds = 30
$PythonScript = "run_waitress.py"
$Branch = "antigravity"

# Detectar Entorno Virtual
if (Test-Path ".\.venv\Scripts\python.exe") {
    $PythonExe = ".\.venv\Scripts\python.exe"
    Write-Host "Usando Entorno Virtual: $PythonExe" -ForegroundColor Cyan
}
else {
    $PythonExe = "python"
    Write-Host "Usando Python del Sistema (Advertencia: .venv no detectado)" -ForegroundColor Yellow
}

Write-Host "INICIANDO PUENTE DE DESPLIEGUE" -ForegroundColor Cyan
git checkout $Branch

$AppProcess = Start-Process $PythonExe -ArgumentList $PythonScript -PassThru -NoNewWindow
Write-Host "Servidor iniciado (PID: $($AppProcess.Id))" -ForegroundColor Green

while ($true) {
    Start-Sleep -Seconds $IntervalSeconds
    
    try {
        git fetch origin $Branch
        
        $LocalHash = (git rev-parse HEAD).Trim()
        $RemoteHash = (git rev-parse "origin/$Branch").Trim()
        
        if ($LocalHash -ne $RemoteHash) {
            Write-Host "NUEVA VERSION DETECTADA" -ForegroundColor Magenta
            
            # Detener proceso
            if (-not $AppProcess.HasExited) {
                Stop-Process -Id $AppProcess.Id -Force -ErrorAction SilentlyContinue
            }
            Get-Process python -ErrorAction SilentlyContinue | Where-Object { $_.Path -like "*$PythonScript*" } | Stop-Process -Force
            
            # Actualizar
            git pull origin $Branch
            
            # Reiniciar
            $AppProcess = Start-Process $PythonExe -ArgumentList $PythonScript -PassThru -NoNewWindow
            Write-Host "APP REINICIADA" -ForegroundColor Green
        }
    }
    catch {
        Write-Host "Error en ciclo" -ForegroundColor Red
    }
}
