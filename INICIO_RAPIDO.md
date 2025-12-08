# 🚀 Guía de Inicio Rápido - Desarrollo Local

## ✅ Estado del Sistema

El sistema está **completamente configurado y listo** para trabajar en modo local con SQLite.

### Lo que ya está hecho:
- ✅ Python 3.13.7 instalado
- ✅ Entorno virtual (.venv) creado
- ✅ Todas las dependencias instaladas
- ✅ Migraciones aplicadas a la base de datos SQLite
- ✅ 137 archivos estáticos recolectados
- ✅ Configuración verificada sin errores

---

## 🎯 Cómo Iniciar el Servidor

### Opción 1: Usando el Script Automático (Recomendado)

```bash
start_server.bat
```

Este script:
- Activa el entorno virtual automáticamente
- Configura las variables de entorno para desarrollo
- Muestra tu IP local para acceso desde otros equipos en la red
- Inicia el servidor en `0.0.0.0:8000`

### Opción 2: Manualmente (Paso a Paso)

```bash
# 1. Activar entorno virtual
.venv\Scripts\activate

# 2. Iniciar servidor
python manage.py runserver
```

Para acceso desde la red local:
```bash
python manage.py runserver 0.0.0.0:8000
```

---

## 🌐 Acceder a la Aplicación

Una vez iniciado el servidor:

- **Acceso local**: http://localhost:8000
- **Panel de administración**: http://localhost:8000/admin
- **Acceso desde red local**: http://TU_IP_LOCAL:8000

---

## 👤 Crear Superusuario (Si no existe)

```bash
# Activar entorno virtual
.venv\Scripts\activate

# Crear superusuario
python manage.py createsuperuser
```

Sigue las instrucciones para crear:
- Nombre de usuario
- Email (opcional)
- Contraseña

---

## 📝 Comandos Útiles

### Gestión de Base de Datos

```bash
# Ver estado de migraciones
python manage.py showmigrations

# Crear nuevas migraciones (después de cambiar modelos)
python manage.py makemigrations

# Aplicar migraciones
python manage.py migrate

# Abrir shell de Django
python manage.py shell
```

### Gestión de Archivos Estáticos

```bash
# Recolectar archivos estáticos
python manage.py collectstatic
```

### Verificación del Sistema

```bash
# Verificar configuración
python manage.py check

# Verificar configuración para producción
python manage.py check --deploy
```

---

## 🔧 Configuración Actual

### Base de Datos
- **Tipo**: SQLite
- **Archivo**: `db.sqlite3`
- **Ubicación**: Raíz del proyecto

### Modo de Desarrollo
- **DEBUG**: True (automático en desarrollo local)
- **ALLOWED_HOSTS**: Todos permitidos en desarrollo
- **SECRET_KEY**: Clave de desarrollo (cambiar en producción)

### Archivos Estáticos
- **Directorio fuente**: `static/`
- **Directorio recolectado**: `staticfiles/`

---

## 📂 Estructura de URLs

```
/                          → Página de inicio
/admin/                    → Panel de administración Django
/cuentas/login/            → Login de usuarios
/tickets/                  → Gestión de tickets
/inventario/               → Gestión de inventario
/usuarios/                 → Gestión de usuarios
```

---

## 🛑 Detener el Servidor

Presiona `Ctrl + C` en la terminal donde está corriendo el servidor.

---

## 💡 Tips

1. **Mantén el entorno virtual activado** mientras trabajas:
   ```bash
   .venv\Scripts\activate
   ```

2. **Usa el script automático** para no preocuparte por configuraciones:
   ```bash
   start_server.bat
   ```

3. **Acceso desde otros equipos**: Si usas `start_server.bat` o `runserver 0.0.0.0:8000`, otros equipos en tu red local pueden acceder usando tu IP

4. **Respaldo de base de datos**: Copia `db.sqlite3` regularmente para tener respaldos

---

## 🚀 ¡Listo para Trabajar!

El sistema está completamente funcional. Solo necesitas:

1. Ejecutar `start_server.bat`
2. Abrir http://localhost:8000 en tu navegador
3. ¡Empezar a trabajar!

Si necesitas crear un superusuario para acceder al admin, usa:
```bash
.venv\Scripts\activate
python manage.py createsuperuser
```
