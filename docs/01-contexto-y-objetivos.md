# 01 - Contexto y objetivos

## Objetivo MVP
Monitorizar coste mensual Oracle + Cloudflare en EUR, publicar JSON agregado para Hub y alertar en Slack si total > 5€.

## Decisiones cerradas
- Proveedores: Oracle + Cloudflare
- Moneda: EUR
- Frecuencia: cada 6h
- Umbral alerta: 5€
- Repo: `hannibal-xals/project-cost-monitor`

## Alcance
- Scheduler periódico
- Adaptadores por proveedor con health explícito
- Persistencia JSON local
- Endpoint HTTP simple
- Alertas Slack anti-spam (transición + recuperación)

## Fuera de alcance (MVP)
- Conversión automática divisa (USD->EUR)
- Persistencia histórica/series temporales
- Dashboard UI propio
