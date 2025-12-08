# Despliegue Automático a Lightsail

## Uso Rápido

Para desplegar tus cambios al servidor con un solo comando:

```powershell
.\deploy_to_lightsail.ps1
```

O con un mensaje de commit personalizado:

```powershell
.\deploy_to_lightsail.ps1 "Agregar nueva funcionalidad X"
```

## ¿Qué hace el script?

1. **Commit local**: Agrega todos los cambios y hace commit
2. **Push a GitHub**: Sube los cambios a la rama `antigravity`
3. **Actualiza Lightsail**: Vía SSH ejecuta:
   - `git pull` para traer los cambios
   - Instala dependencias nuevas
   - Aplica migraciones de base de datos
   - Recolecta archivos estáticos
4. **Notifica**: Te indica que debes reiniciar Waitress manualmente

## Requisitos Previos

### 1. Configurar SSH sin contraseña

Para que el script funcione sin pedir contraseña cada vez, necesitas configurar autenticación por llave SSH.

**En tu máquina local, ejecuta:**

```powershell
# Generar llave SSH (si no tienes una)
ssh-keygen -t rsa -b 4096

# Copiar la llave pública al servidor
type $env:USERPROFILE\.ssh\id_rsa.pub | ssh Administrator@3.20.119.202 "cat >> .ssh/authorized_keys"
```

Después de esto, podrás conectarte sin contraseña.

### 2. Verificar conexión SSH

Prueba que puedes conectarte sin contraseña:

```powershell
ssh Administrator@3.20.119.202 "echo 'Conexión exitosa'"
```

Si pide contraseña, revisa el paso anterior.

## Reiniciar Waitress Automáticamente (Opcional)

Si quieres que el script también reinicie Waitress automáticamente, necesitarías:

1. Configurar Waitress como servicio de Windows, o
2. Usar una herramienta como `nssm` (Non-Sucking Service Manager)

Por ahora, el script te notifica que debes reiniciar manualmente.

## Troubleshooting

**Error: "ssh: connect to host 3.20.119.202 port 22: Connection refused"**
- Verifica que el servidor esté encendido
- Verifica que el puerto 22 (SSH) esté abierto en el firewall de Lightsail

**Error: "Permission denied (publickey)"**
- Revisa la configuración de SSH (paso 1)
- Verifica que la llave pública esté en `~/.ssh/authorized_keys` del servidor

**Los cambios no se reflejan**
- Asegúrate de reiniciar el servidor Waitress después del despliegue
- Limpia la caché del navegador (Ctrl+F5)
