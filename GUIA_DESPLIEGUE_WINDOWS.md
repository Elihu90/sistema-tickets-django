# Guía de Despliegue en Windows Server 2019 (AWS Lightsail)

Esta guía detalla los pasos para desplegar el "Sistema de Gestión de Tickets y Reparaciones" en una instancia de Windows Server 2019 en AWS Lightsail.

## Prerrequisitos

1.  **Cuenta de AWS** activa.
2.  **Instancia Lightsail** con Windows Server 2019 creada y corriendo.
3.  **Acceso RDP** (Escritorio Remoto) a la instancia.

## Paso 1: Preparar el Servidor

Conéctate a tu instancia mediante RDP y realiza las siguientes instalaciones:

### 1. Instalar Python
1.  Descarga el instalador de Python (versión 3.10 o superior) desde [python.org](https://www.python.org/downloads/windows/).
2.  Ejecuta el instalador.
3.  **IMPORTANTE:** Marca la casilla **"Add Python to PATH"** antes de dar clic en "Install Now".

### 2. Instalar PostgreSQL (Opcional)
*Si decides usar **SQLite** (base de datos en archivo, más simple pero menos potente), puedes saltar este paso.*

1.  Descarga el instalador de PostgreSQL desde [postgresql.org](https://www.postgresql.org/download/windows/).
2.  Ejecuta el instalador y sigue los pasos.
3.  Establece una contraseña segura para el usuario `postgres` y **guárdala**, la necesitarás más adelante.
4.  Al finalizar, abre **pgAdmin 4** (se instala junto con PostgreSQL) o usa SQL Shell (psql).
5.  Crea una nueva base de datos llamada `stgr_db`.

### 3. Instalar Git (Opcional pero recomendado)
1.  Descarga e instala Git desde [git-scm.com](https://git-scm.com/download/win).
2.  Esto facilitará descargar el código del proyecto.

## Paso 2: Descargar el Proyecto

1.  Abre PowerShell o CMD.
2.  Navega a la carpeta donde quieras alojar el proyecto (ej. `C:\Proyectos`).
3.  Clona el repositorio:
    ```powershell
    git clone <URL_DEL_REPOSITORIO> sgtr_proyecto
    ```
    *Si no usas Git, copia la carpeta del proyecto manualmente al servidor.*

## Paso 3: Configuración

1.  Entra a la carpeta del proyecto:
    ```powershell
    cd C:\Proyectos\sgtr_proyecto
    ```
2.  Copia el archivo de ejemplo de variables de entorno:
    ```powershell
    Copy-Item .env.example .env
    ```
3.  Abre el archivo `.env` con el Bloc de notas y edita lo siguiente:
    *   `SECRET_KEY`: Genera una clave aleatoria y segura.
    *   `DEBUG`: Asegúrate de que esté en `False`.
    *   `ALLOWED_HOSTS`: Agrega la IP pública de tu instancia Lightsail.
    *   **Si usas PostgreSQL:** Configura `DATABASE_URL` y `POSTGRES_PASSWORD`.
    *   **Si usas SQLite:** Comenta o borra la línea de `DATABASE_URL`.

## Paso 4: Instalación Automática

Ejecuta el script de instalación que hemos preparado. Abre PowerShell como Administrador y corre:

```powershell
.\setup_native.ps1
```

El script te preguntará si deseas usar **PostgreSQL** o **SQLite**.
*   Si eliges **SQLite**, configurará todo automáticamente sin pedir credenciales de base de datos.
*   Si eliges **PostgreSQL**, asegúrate de haber configurado el `.env` correctamente.

Este script:
*   Creará un entorno virtual de Python.
*   Instalará todas las librerías necesarias.
*   Configurará la base de datos.
*   Recolectará los archivos estáticos.

## Paso 5: Iniciar la Aplicación

Para probar que todo funciona, ejecuta:

```powershell
.\.venv\Scripts\python.exe run_waitress.py
```

Si ves un mensaje indicando que el servidor inició en el puerto 8000, abre el navegador en el servidor y ve a `http://localhost:8000`.

## Paso 6: Abrir el Puerto en el Firewall (Lightsail)

Para acceder desde fuera (Internet):

1.  Ve a la consola de **AWS Lightsail**.
2.  Selecciona tu instancia -> **Networking**.
3.  En la sección **IPv4 Firewall**, agrega una regla:
    *   Application: **Custom**
    *   Protocol: **TCP**
    *   Port or range: **8000**
4.  Guarda los cambios.

Ahora deberías poder acceder usando la IP pública de tu instancia: `http://<TU_IP_PUBLICA>:8000`.

> **Nota:** Para mantener la aplicación corriendo siempre (incluso si cierras sesión), se recomienda configurar un Servicio de Windows usando herramientas como **NSSM**.
