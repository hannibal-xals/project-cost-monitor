# 04 - Riesgos y decisiones

## Decisiones técnicas
- Priorizar robustez operativa: fallback mock y health explícito por proveedor.
- Persistencia local en volumen Docker (`./state:/data`).
- Anti-spam Slack con estado `last_threshold_exceeded` en fichero.

## Riesgos
1. **Oracle API no trivial (firma OCI):**
   - Mitigación: placeholder live + mock funcional + mensaje claro en `source_health.oracle`.
2. **Cloudflare monedas mixtas:**
   - Mitigación MVP: sumar solo EUR; ignorar no-EUR y documentar.
3. **Sin credenciales en entorno:**
   - Mitigación: modo demo activado por defecto (`USE_MOCK_DATA=true`).
4. **Reinicio contenedor pierde estado de alertas si no hay volumen:**
   - Mitigación: volumen persistente `./state`.
