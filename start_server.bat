@echo off
REM ========================================
REM Sistema de Tickets - Inicio en Red Local
REM ========================================
echo.
echo ========================================
echo Sistema de Tickets - Inicio
echo ========================================
echo.

cd /d "%~dp0"

REM Verificar si existe el entorno virtual
if not exist ".venv\Scripts\activate.bat" (
    echo ERROR: No se encontro el entorno virtual
    echo.
    echo Creando entorno virtual...
    python -m venv .venv
    if errorlevel 1 (
        echo ERROR: No se pudo crear el entorno virtual
        pause
        exit /b 1
    )
    echo Entorno virtual creado exitosamente
)

REM Activar entorno virtual
call .venv\Scripts\activate.bat

REM Verificar si requirements.txt existe e instalar dependencias
if exist "requirements.txt" (
    echo Verificando dependencias...
    pip install -q -r requirements.txt
)

REM Configurar variables de entorno para desarrollo local
set DEBUG=True
set ALLOWED_HOSTS=*

REM Obtener IP local
for /f "tokens=2 delims=:" %%a in ('ipconfig ^| findstr /c:"IPv4"') do set IP=%%a
set IP=%IP:~1%

REM Crear directorio de logs si no existe
if not exist "logs" mkdir logs

echo.
echo Aplicando migraciones...
python manage.py migrate --noinput

if errorlevel 1 (
    echo.
    echo ERROR: Hubo un problema al aplicar las migraciones
    echo Revisa los errores anteriores
    pause
    exit /b 1
)

echo.
echo Recolectando archivos estaticos...
python manage.py collectstatic --noinput --clear

echo.
echo ========================================
echo Servidor Iniciado Exitosamente
echo ========================================
echo.
echo Acceso local:  http://localhost:8000
echo Acceso en red: http://%IP%:8000
echo.
echo Presiona Ctrl+C para detener el servidor
echo ========================================
echo.

REM Iniciar servidor
python manage.py runserver 0.0.0.0:8000

pause
