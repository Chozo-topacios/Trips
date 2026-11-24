# 🧭 Planificador de viaje

Guías de viaje completas, día por día, en **carro** (Chery iCAR 03T de rango extendido) o en **avión**: siempre con naturaleza, pueblos y sitios turísticos, más enlaces a mapas, fotos e información, gráfica del perfil de altura de la ruta y del presupuesto. Todo se puede editar, mover, borrar o complementar con Claude.

Hay dos formas de usarla:

| | Artifact en Claude | Sitio abierto (este repositorio) |
|---|---|---|
| ¿Necesita cuenta de Claude quien la abre? | Sí | **No** |
| ¿Quién paga el uso de Claude? | Cada visitante, con su cuenta | **El dueño**, con su API key |
| ¿Dónde se guardan los viajes? | En la cuenta de Claude (se sincronizan) | En el navegador de cada visitante |

La página es la misma en ambos casos: `artifact/planificador.html`. El servidor la envuelve y le da un reemplazo del runtime de Claude (`public/claude-shim.js`) que manda las peticiones a `/api/json`.

## Funciones

- **Viajes de Leonardo** (avión): Chile, ski en familia (7 días) y México, Día de Muertos (8 días), para 2 adultos y una niña de 9 años, con fechas sugeridas día por día. Se generan con `data/destinos.py`.
- **Mejores fechas**: barra de 12 meses (mejor / buena / llena y cara / evitar), fechas recomendadas y por qué, en cada viaje (también en las rutas picnic y en las guías nuevas de Claude).

- **Guía gráfica por pestañas** (Itinerario · Dinero · Preparar · Ideas · Bitácora), **un día a la vez**, con línea de tiempo de íconos, barra horaria del día por tipo de actividad y detalles que se abren al tocar.
- **Bitácora con fotos** (hasta 4 por viaje) y **verificación de la ruta** al visitarla (entrada, reserva, estado de la vía).
- **Aviso del fin de semana** (versión abierta): la ruta por conocer con menos lluvia el sábado o domingo.

- **Guías con Claude**: plan general y luego actividades de a dos días; todo editable (mover, quitar, agregar, complementar con Claude).
- **Rutas picnic · Leonardo**: 19 planes listos (lista de Google Maps) para la iCAR 03T, sin generar nada.
- **Modo Hoy**: actividades del día con casillas, siguiente parada y botones para navegar con Google Maps o Waze.
- **Antes de salir**: lista para marcar según cada viaje (batería, gasolina que necesita, llantas, efectivo para peajes, reservas, tramos destapados, mapa sin señal, avisar a alguien).
- **Cargar y tanquear**: enlaces a cargadores y estaciones cerca del destino; en la versión abierta, cargadores públicos sobre la ruta (OpenStreetMap).
- **Gastos reales**: anotar en dos toques lo que se gasta (gasolina, peaje, comida…) y compararlo con el presupuesto.
- **Bitácora**: calificar con estrellas y anotar cómo estuvo; las rutas picnic muestran cuáles ya visitaste.
- **Mi carro y precios**: precio del galón y del kWh (y consumos) ajustables; todos los cálculos se actualizan.
- **Compartir**: el plan como texto para WhatsApp.
- **Pasar mis viajes a otro dispositivo**: código para copiar y pegar.
- Solo en la versión abierta (GitHub Pages): **funciona sin señal** (se instala como app), **pronóstico del clima** de 7 días, **¿A dónde vamos este fin de semana?** (rutas con menos lluvia) y **mapa** de las rutas. En Claude la página no puede consultar servicios externos.

## Cómo funciona

| Archivo | Qué hace |
|---|---|
| `artifact/planificador.html` | La aplicación completa (interfaz, guías, edición, gráficas, guardado) |
| `public/claude-shim.js` | Hace que la página use el servidor propio en vez de la cuenta de Claude del visitante |
| `src/server.js` | Sirve la página y el endpoint `/api/json`, que llama a Claude con tu API key; límite de peticiones por IP |
| `src/page.js`, `scripts/build-pages.mjs` | Arman el documento completo; la segunda genera `dist/` para GitHub Pages |
| `.github/workflows/pages.yml` | Publica la página en GitHub Pages |
| `public/sw.js`, `public/manifest.webmanifest`, íconos | Uso sin señal e instalación en el teléfono |
| `data/rutas_picnic.py` | Genera las 19 rutas picnic y las incrusta en la página |
| `render.yaml` | Configuración del servicio de guías en Render |

La guía se arma en pasos cortos (plan general y luego de a dos días) para que ninguna petición se pase del tiempo máximo.

## Publicación

**Página:** https://chozo-topacios.github.io/Trips/ — se publica sola con GitHub Pages (`.github/workflows/pages.yml`) en cada push. Cualquiera la abre sin cuenta.

**Servicio de guías:** la página necesita un servidor pequeño que guarde tu API key de Claude (en una página pública la clave quedaría expuesta). Una sola vez:

1. Crea una API key en https://console.anthropic.com, cárgale saldo y pon un límite de gasto mensual.
2. En https://render.com (entra con GitHub): **New + → Blueprint**, elige este repositorio y pega tu `ANTHROPIC_API_KEY` cuando la pida.
3. Copia la dirección que te da Render (por ejemplo `https://planificador-de-viaje.onrender.com`).
4. En GitHub: **Settings → Secrets and variables → Actions → Variables → New repository variable**, nombre `PLANIFICADOR_API`, valor esa dirección.
5. En **Actions → Publicar en GitHub Pages → Run workflow** para volver a publicar la página ya conectada.

Mientras no esté conectado, la página abre y muestra los viajes guardados, pero al armar una guía avisa que el servicio no está conectado.

En el plan gratis de Render el servicio se "duerme" tras un rato sin uso y la primera guía tarda cerca de un minuto más.

## Probar en tu computador

```bash
npm install
```

```bash
cp .env.example .env
```

Pon tu `ANTHROPIC_API_KEY` en `.env` y luego:

```bash
npm start
```

Abre http://localhost:3000.

## Variables

| Variable | Por defecto | Uso |
|---|---|---|
| `ANTHROPIC_API_KEY` | — | Obligatoria |
| `CLAUDE_MODEL` | `claude-opus-5-5` | Modelo |
| `CLAUDE_EFFORT` | `medium` | `low` es más rápido y barato; `high`, más detallado |
| `ALLOWED_ORIGINS` | `https://chozo-topacios.github.io` | Sitios que pueden usar el servicio |
| `RATE_LIMIT_PER_HOUR` | `40` | Peticiones por IP por hora (una guía de 4 días usa unas 3) |
| `PORT` | `3000` | Puerto |

## Datos de la iCAR 03T

Tomados de la ficha publicada en Colombia (Chery y prensa automotriz): batería LFP (CATL) de **34,31 kWh**, **160 km** eléctricos (NEDC), **801 km** combinados (WLTC) con tanque de **12 galones**, generador **1.5 turbo** que no mueve las ruedas, carga rápida DC de hasta **90 kW** (30→80 % en ~20 min).

No hay una cifra oficial de consumo, así que la app usa estimaciones a partir de esa ficha: **~24 kWh/100 km** en eléctrico (~140 km reales con la batería llena) y **~52 km/galón** con el generador ((801 − ~150 km eléctricos) / 12 galones ≈ 54 km/gal, en línea con los 7,15 L/100 km WLTC del iCAR V25, que usa el mismo generador). Precios de referencia: $800/kWh en casa y $16.000/galón. Se ajustan en `ICAR` (página) y en `data/rutas_picnic.py`.

## Costos y cuidados

- Cada guía y cada "Complementar" consumen tu saldo de la API. Pon un **límite de gasto mensual** en la consola de Anthropic.
- El límite por IP evita abusos básicos, pero cualquiera con el enlace puede usarla: comparte el enlace con cuidado.
- Las guías salen del conocimiento de Claude, sin consulta en vivo: precios, horarios y peajes son aproximados.
