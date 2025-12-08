# Guía de Despliegue con Docker en Windows Server 2019

Esta guía explica cómo desplegar la aplicación usando Docker en una instancia de Windows Server 2019.

## Prerrequisitos

1.  **Instancia Lightsail** con Windows Server 2019.
2.  **Virtualización Habilitada**: Las instancias de Lightsail generalmente soportan virtualización anidada, necesaria para Docker Desktop/WSL2.
3.  **Docker Desktop** instalado y corriendo (configurado para *Linux Containers*).

## Paso 1: Instalar Docker Desktop

1.  En tu servidor, descarga Docker Desktop para Windows.
2.  Instálalo asegurándote de habilitar la integración con WSL2 si es posible (o usa Hyper-V backend).
3.  Reinicia el servidor si es necesario.
4.  Inicia Docker Desktop y espera a que el icono en la barra de tareas se quede fijo.

## Paso 2: Descargar el Proyecto

1.  Instala Git (opcional) o descarga el código.
2.  Clona el repositorio:
    ```powershell
    git clone <URL_DEL_REPOSITORIO> sgtr_proyecto
    ```

## Paso 3: Configuración

1.  Entra a la carpeta del proyecto:
    ```powershell
    cd C:\Proyectos\sgtr_proyecto
    ```
2.  Ejecuta el script de instalación automática:
    ```powershell
    .\setup_docker.ps1
    ```

## Qué hace el script `setup_docker.ps1`?

1.  Verifica que Docker esté instalado.
2.  Crea el archivo `.env` si no existe y te pide configurarlo.
3.  Ejecuta `docker-compose up -d --build` para levantar la base de datos y la aplicación.
4.  Ejecuta las migraciones y recolecta archivos estáticos automáticamente.
5.  Te da la opción de crear un superusuario.

## Paso 4: Acceso

Una vez finalizado el script, la aplicación estará corriendo en el puerto **8000**.

*   Accede localmente: `http://localhost:8000`
*   Accede remotamente: `http://<IP_PUBLICA>:8000` (Asegúrate de abrir el puerto 8000 en el firewall de Lightsail).

## Solución de Problemas

*   **Error de memoria**: Si Docker falla, intenta aumentar la memoria de tu instancia Lightsail o ajusta los límites en `docker-compose.yml`.
*   **Puertos ocupados**: Asegúrate de que ningún otro servicio use el puerto 8000.
