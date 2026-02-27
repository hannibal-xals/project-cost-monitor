# project-cost-monitor

MVP dockerizado para monitorizar coste mensual de **Oracle + Cloudflare** en **EUR**, exponer estado en JSON y alertar por Slack cuando el total mensual cruza el umbral.

## Qué hace

- Consulta coste por proveedor cada `UPDATE_INTERVAL_HOURS` (default: 6h)
- Genera `/data/cost-status.json` con formato:
  - `provider_costs.oracle_eur`
  - `provider_costs.cloudflare_eur`
  - `total_eur`
  - `threshold_eur`
  - `threshold_exceeded`
  - `last_updated_at`
  - `source_health` por proveedor
- Expone endpoint HTTP `GET /cost-status`
- Envía alertas Slack por transición:
  - `false -> true` (supera umbral)
  - `true -> false` (recuperación)

## Estado adaptadores MVP

- **Oracle:** adaptador placeholder con error explícito en modo live (falta firma OCI); funciona en mock.
- **Cloudflare:** implementación live básica contra `user/billing/history` (suma importes en EUR).

## Quick start

```bash
cp .env.example .env
# opcional: ajustar mock y webhook

docker compose up --build -d
curl -s http://localhost:8080/cost-status | jq .
```

## Modo demo / sin credenciales

Dejar `USE_MOCK_DATA=true` para validar end-to-end sin bloquearse por permisos.

## Validación local sin Docker

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python -m app.main
curl -s http://localhost:8080/cost-status
```

## Estructura

- `app/main.py`: API HTTP + scheduler
- `app/providers.py`: adaptadores Oracle/Cloudflare
- `app/notifier.py`: anti-spam de alertas por transición
- `docs/01..05`: contexto, especificación, plan, riesgos y checklist
