# 03 - Plan de implementación

## Stack
- Python 3.12
- Flask (endpoint HTTP)
- Requests (APIs + webhook Slack)
- Docker + docker-compose

## Tareas
1. Scaffold repo y docs estándar.
2. Implementar `Config` y variables de entorno.
3. Implementar adaptadores proveedores:
   - Oracle: mock + error explícito live no implementado.
   - Cloudflare: consulta live y suma EUR.
4. Implementar generador `cost-status.json`.
5. Implementar notificador Slack con estado persistido.
6. Exponer `/health` y `/cost-status`.
7. Añadir Dockerfile, compose, `.env.example`, README.
8. Validar con modo mock y documentar comandos.
