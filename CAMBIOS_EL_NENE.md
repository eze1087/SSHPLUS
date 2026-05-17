# Cambios aplicados - SSHPLUS BY El NeNe

## Reparaciones principales

- Se corrigieron `proxy.py`, `open.py`, `wsproxy.py` y se agregó `PDirect.py` en Python 3.
- Se cambió el arranque de redireccionamientos desde `python` a `python3` en el menú de conexión.
- Se integró el menú `redireccion_python` dentro de `MODO DE CONEXIÓN -> [05] PROXY/WEBSOCKET`, opción `[7] REDIRECCIONAMIENTO PYTHON EL NENE`.
- Se reparó BadVPN reemplazando el módulo viejo por un gestor con systemd: activar, detener, reiniciar, cambiar puerto y ver logs.
- Se agregó `badvpn-udpgw` a `Modulos/` para que el instalador lo copie a `/bin/badvpn-udpgw`.
- Se reparó `badpro1` para que use el mismo gestor BadVPN corregido.
- Se reparó el test de velocidad usando `speedtest-cli --simple --share`, con instalación automática si falta.
- Se corrigió el instalador para usar Python 3 y evitar forzar alternativas viejas de Python 3.6.
- Se cambió la zona horaria de instalación a `America/Argentina/Buenos_Aires`.
- Se corrigieron errores de sintaxis en `utili`, `gltunnel` y `v2raymanager`.
- Se pasaron menús principales y funciones modificadas a castellano argentino.

## Rutas importantes

- Menú principal: `/bin/menu`
- Redireccionamiento integrado: `/bin/redireccion_python`
- Proxys Python: `/etc/SSHPlus/proxy.py`, `/etc/SSHPlus/wsproxy.py`, `/etc/SSHPlus/open.py`, `/etc/SSHPlus/PDirect.py`
- BadVPN: `/bin/badvpn` o `/bin/badpro1`
- Servicio BadVPN: `badvpn-udpgw.service`

## Pruebas realizadas en sandbox

- `bash -n` sin errores en todos los scripts Bash detectados.
- `python3 -m py_compile` sin errores en los módulos Python corregidos.
- Prueba funcional local de `proxy.py`, `wsproxy.py` y `open.py` usando puertos altos y un backend local.

## Nota para GitHub

Los instaladores quedaron apuntando por defecto a:

```bash
eze1087/SSHPLUS/main
```

Si el repositorio va a tener otro usuario/nombre, editá `ssh-plus`, `script/install`, `script/64/Plus`, `script/arm64/Plus` e `Install/list`, o ejecutá el instalador con las variables `GITHUB_USER`, `GITHUB_REPO` y `GITHUB_BRANCH` cuando uses `ssh-plus`.


## Revisión de usuarios
- Reparada renovación/cambio de fecha de usuarios (`mudardata`): antes la validación buscaba `/$usuario:` en `/etc/passwd` y podía fallar siempre.
- Reparado cambio de contraseña (`alterarsenha`) con validación real por `getent` y guardado en `/etc/SSHPlus/senha`.
- Reparado cambio de límite (`alterarlimite`) con selección por número o nombre y actualización segura de `/root/usuarios.db`.
- Rehecha eliminación de usuarios (`remover`) evitando borrar rutas peligrosas y limpiando contraseña, límite, test y OVPN.
- Rehecha creación de usuarios y usuarios test con validaciones de nombre, días, contraseña y límite.
- Rehecho bloqueo/desbloqueo (`blockuser`) con lista de bloqueados sin duplicados y desconexión de sesiones al bloquear.
- Rehechos `expcleaner`, `uexpired`, `infousers`, `sshmonitor`, `limiter` y `droplimiter` para trabajar solo con usuarios UID >= 1000 y evitar tocar cuentas del sistema.
- Eliminadas condiciones peligrosas que podían borrar `/bin` si faltaba una marca/licencia.

## Integración VPS-AGN - Token/HWID, UDP y CheckUser 2052

Se integraron complementos útiles tomando como referencia `VPS-AGN-main.zip`:

- Nuevo módulo `/bin/usuarios_token_hwid`:
  - crear cuentas por TOKEN;
  - crear cuentas por HWID;
  - listar cuentas TOKEN/HWID;
  - renovar vencimiento;
  - eliminar;
  - bloquear/desbloquear;
  - guarda datos en `/etc/SSHPlus/User-TOKEN`, `/etc/SSHPlus/User-HWID`, `/etc/SSHPlus/senha` y mantiene límite en `/root/usuarios.db`.

- Nuevo módulo `/bin/udp_agn`:
  - método UDP con `badvpn-udpgw`;
  - puerto por defecto 7300;
  - puerto personalizado;
  - servicio systemd `sshplus-udp-agn.service`;
  - estado y logs.

- Nuevo módulo `/bin/checkuser2052`:
  - CheckUser HTTP para apps en puerto 2052;
  - valida usuarios SSH normales, TOKEN y HWID;
  - endpoints compatibles por GET/POST:
    - `/check?user=USUARIO&pass=CLAVE`
    - `/checkuser?username=USUARIO&password=CLAVE`
    - `/plain?user=USUARIO&pass=CLAVE`
  - servicio systemd `sshplus-checkuser2052.service`.

- Menú principal actualizado:
  - `[24] TOKEN / HWID`
  - `[25] MÉTODO UDP AGN`
  - `[26] CHECKUSER 2052`
