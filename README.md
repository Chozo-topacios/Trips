# 🧭 Ruta: agente web de planificación de viajes

Agente conversacional (Claude + herramientas) para planear viajes **en carro** con la **Chery iCAR 03T** o **en avión**.

```
[INICIO] → ¿Carro o avión?
   ├─ CARRO: origen/destino → ruta en Google Maps (y alternativas) → peajes y estado vial
   │         → gestión de energía iCAR 03T → sitios turísticos en ruta → hospedajes → presupuesto
   └─ AVIÓN: destino y días → imperdibles + itinerario → zonas para hospedarse
             → movilidad local → presupuesto
```

## Cómo funciona

| Pieza | Archivo | Qué hace |
|---|---|---|
| Interfaz web | `public/` | Asistente por pasos (carro/avión → formulario) y luego chat con respuestas en streaming |
| Servidor | `src/server.js` | Express + SSE; guarda la conversación por sesión en memoria |
| Agente | `src/agent.js` | Ciclo de herramientas con Claude (`claude-opus-5-5`), con búsqueda y lectura web |
| Google Maps | `src/google.js` | `calcular_ruta` (Routes API: rutas, alternativas, duración con tráfico y peajes) y `buscar_lugares` (Places API: hoteles, atracciones y cargadores EV) |
| Energía iCAR 03T | `src/vehicle.js` | `plan_energia`: consumo según distancia, desnivel, velocidad y A/C; con qué % salir y dónde y hasta qué % cargar |

**Sobre la iCAR 03T:** es 100 % eléctrica, así que no hay gasolina que gestionar. El plan te dice si basta con salir al 100 % o qué paradas de carga rápida hacer (cargando hasta ~80 %, que es donde la carga DC es eficiente). Los datos del vehículo (batería, consumo, potencia de carga) son valores de referencia. Ajústalos en **⚡ Mi vehículo** con la ficha técnica de tu versión.

Los peajes se toman de Google cuando los tiene. Si no, el agente busca las tarifas oficiales (ANI, INVÍAS, concesionarias) y cita la fuente.

## Puesta en marcha

Requisitos: Node.js 20.6 o superior.

```bash
npm install
```

```bash
cp .env.example .env
```

Edita `.env`:

- `ANTHROPIC_API_KEY`: obligatoria.
- `GOOGLE_MAPS_API_KEY`: opcional pero recomendada. Activa **Routes API** y **Places API (New)** en Google Cloud. Sin ella el agente usa la búsqueda web y te da el enlace de Google Maps igualmente.

```bash
npm start
```

Abre http://localhost:3000.

### Variables opcionales

| Variable | Por defecto | Uso |
|---|---|---|
| `CLAUDE_MODEL` | `claude-opus-5-5` | Modelo |
| `CLAUDE_EFFORT` | `medium` | `low` / `medium` / `high`: más esfuerzo da planes más completos pero más lentos y costosos |
| `PORT` | `3000` | Puerto |

## Notas

- Si el modelo principal rechaza una solicitud, la API la reintenta automáticamente con otro modelo (`fallbacks: "default"`).
- Las conversaciones viven en memoria: se pierden al reiniciar el servidor.
- Precios, peajes y horarios son estimaciones: verifícalos antes de viajar.
