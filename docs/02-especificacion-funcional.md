# 02 - Especificación funcional

## Flujo
1. Cada 6h el scheduler consulta Oracle + Cloudflare.
2. Genera `cost-status.json` con estructura acordada.
3. Evalúa umbral total > 5€.
4. Si hay transición de estado, envía Slack.
5. Endpoint `/cost-status` sirve el JSON actual.

## Contrato JSON
```json
{
  "provider_costs": {"oracle_eur": 0, "cloudflare_eur": 0},
  "total_eur": 0,
  "threshold_eur": 5,
  "threshold_exceeded": false,
  "last_updated_at": "ISO-8601",
  "source_health": {
    "oracle": {"status": "ok|mock|error", "message": "...", "checked_at": "ISO-8601"},
    "cloudflare": {"status": "ok|mock|error", "message": "...", "checked_at": "ISO-8601"}
  }
}
```

## Alerting
- `false -> true`: alerta de exceso.
- `true -> false`: alerta de recuperación.
- Sin transición: no enviar (evitar spam).
