# Reparación de `menu: command not found`

El problema era que el instalador estaba descargando archivos desde la rama `main` aunque se ejecutaba desde `SSHPLUS-BY-NeNePro`.

Archivos corregidos:

- `ssh-plus`
- `script/64/Plus`
- `script/arm64/Plus`
- `Install/list`

Después de subir este ZIP a GitHub en la rama `SSHPLUS-BY-NeNePro`, reinstalá en la VPS:

```bash
rm -f ssh-plus
wget -O ssh-plus https://raw.githubusercontent.com/eze1087/SSHPLUS/refs/heads/SSHPLUS-BY-NeNePro/ssh-plus
chmod 777 ssh-plus
GITHUB_BRANCH=SSHPLUS-BY-NeNePro bash ./ssh-plus
hash -r
menu
```

Verificación rápida:

```bash
ls -l /bin/menu /usr/local/bin/menu /usr/bin/menu 2>/dev/null
```
