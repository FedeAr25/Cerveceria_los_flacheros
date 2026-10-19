# T01 — Instalar uv y Docker Desktop

**Fase:** 0
**Fecha:** 19/10/2026
**Estado:** Completada

## Qué se hizo
Instalamos las dos herramientas de entorno que pide el docente: `uv` (gestor de entornos virtuales y dependencias de Python) y Docker Desktop (la app local que corre contenedores). Ambas se instalaron con `winget`, que es el gestor de paquetes que trae Windows 11, y verificamos que respondan con su número de versión. En el camino descubrimos dos cosas de Windows que no teníamos previstas: que una terminal abierta no ve lo que winget acaba de instalar (por el PATH), y que el motor de Docker no arranca porque le falta WSL2, que hay que instalar con permisos de administrador. Ese último punto queda como pendiente del usuario: hasta que no corra `wsl --install` como admin y reinicie, `docker ps` va a seguir fallando.

No tocamos ningún archivo del proyecto en esta tarea: fue 100% instalación y verificación de herramientas en la máquina. Lo único que se anotó en el repositorio fue confirmar contra `tasks/plan.md` §5 que las versiones reales que instaló winget coinciden con las del plan (uv es 0.13.1, no 0.13.2 como decía el plan original).

## Conceptos que aparecen acá
- **Gestor de entornos virtuales (uv)** — herramienta que crea un entorno Python aislado por proyecto e instala ahí las dependencias, sin mezclar versiones con el Python del sistema. El docente lo exige porque así el proyecto se instala igual en cualquier máquina con un comando (`uv sync`) y las versiones quedan fijas en `uv.lock`.
- **winget** — el gestor de paquetes de Windows (como `apt` en Linux o `brew` en macOS). Sirve para instalar herramientas con un solo comando y de forma repetible: `winget install --id=astral-sh.uv -e`.
- **PATH de Windows** — la lista de carpetas donde Windows busca los ejecutables cuando escribís un comando. winget agrega la carpeta de `uv` al PATH del **usuario**, pero cada terminal guarda su propia copia del PATH al abrirse: una terminal que ya estaba abierta no se entera del cambio.
- **WSL2 (Windows Subsystems for Linux)** — la capa que hace correr un kernel de Linux real dentro de Windows. Docker Desktop en Windows necesita WSL2 para correr los contenedores, porque los contenedores son procesos Linux. Sin él, el motor de Docker no levanta.

## Archivos
- No se crearon ni modificaron archivos del proyecto. La tarea fue instalar `uv` y Docker Desktop con winget y verificarlos.
- `tasks/plan.md` §5 — se contrastó la tabla de stack con las versiones realmente instaladas (uv 0.13.1).

## Lo que hay que mirar en el código
- `tasks/plan.md`::§5 (tabla "Stack y versiones") — es la lista de versiones contra la que verificamos lo instalado; ahí queda registrado que uv es 0.13.1.
- `tasks/plan.md`::§10 (sección Docker) — el `Dockerfile` del plan copia los binarios de uv desde la imagen oficial de uv; es la parte del proyecto que depende de Docker y la que hoy está trabada por WSL2.
- No hay código de aplicación todavía: esta tarea no escribió ni un `.py`.

## Para la defensa
> **Pregunta:** 为什么使用 uv 而不是 pip — ¿por qué usan uv y no pip?
> **Respuesta:** uv resuelve e instala mucho más rápido que pip, administra el entorno virtual y las dependencias en un solo lugar, y genera un `uv.lock` que fija las versiones exactas: así el proyecto se instala igual en mi máquina, en la de mi compañero y en Docker, sin sorpresas de versiones.

> **Pregunta:** ¿Y Docker? Si el motor no levanta en esta máquina, ¿no es un problema?
> **Respuesta:** El proyecto se entrega con `Dockerfile` y `compose.yaml`, que es un requisito del docente; Docker Desktop es solo la herramienta local para probarlos. Si el motor no levanta en esta máquina el entregable no cambia, porque lo dockerizado está en los archivos del repo, no en la máquina.

## Errores que nos pasaron y cómo los resolvimos
- **Error:** `uv : El término 'uv' no se reconoce como elemento cmdlet...`
  **Causa:** winget instaló uv y modificó el PATH del usuario, pero la terminal que ya estaba abierta guardaba una copia vieja del PATH y no lo refresca solo.
  **Solución:** abrir una terminal nueva, o anteponer a los comandos el refresco del PATH: `$env:Path = [System.Environment]::GetEnvironmentVariable("Path","User") + ";" + [System.Environment]::GetEnvironmentVariable("Path","Machine")`.
- **Error:** `docker ps` falla y `wsl --status` responde "El subsistema de Windows para Linux no está instalado".
  **Causa:** Docker Desktop en Windows necesita WSL2 como motor y WSL2 no está instalado; instalarlo requiere permisos de administrador y reiniciar la máquina, y esta sesión no tiene admin.
  **Solución:** **Pendiente del usuario:** ejecutar `wsl --install` como administrador y reiniciar. Hasta entonces seguimos desarrollando en local con SQLite, que no necesita Docker.

## Verificación
- [ ] `uv --version` → `uv 0.13.1`
- [ ] `docker --version` → `Docker version 29.8.2`
- [ ] `docker compose version` → `Docker Compose version v5.6.0`
- [ ] `docker ps` → falla hasta instalar WSL2 (pendiente del usuario)
