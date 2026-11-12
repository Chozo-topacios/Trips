# 🧭 Planificador de viaje

Guías de viaje completas, día por día, en **carro** (Chery iCAR 03T de rango extendido) o en **avión**: siempre con naturaleza, pueblos y sitios turísticos, más enlaces a mapas, fotos e información, gráfica del perfil de altura de la ruta y del presupuesto. Todo se puede editar, mover, borrar o complementar con Claude.

Hay dos formas de usarla:

| | Artifact en Claude | Sitio abierto (este repositorio) |
|---|---|---|
| ¿Necesita cuenta de Claude quien la abre? | Sí | **No** |
| ¿Quién paga el uso de Claude? | Cada visitante, con su cuenta | **El dueño**, con su API key |
| ¿Dónde se guardan los viajes? | En la cuenta de Claude (se sincronizan) | En el navegador de cada visitante |

La página es la misma en ambos casos: `artifact/planificador.html`. El servidor la envuelve y le da un reemplazo del runtime de Claude (`public/claude-shim.js`) que manda las peticiones a `/api/json`.

## Cómo funciona

| Archivo | Qué hace |
|---|---|
| `artifact/planificador.html` | La aplicación completa (interfaz, guías, edición, gráficas, guardado) |
| `public/claude-shim.js` | Hace que la página use el servidor propio en vez de la cuenta de Claude del visitante |
| `src/server.js` | Sirve la página y el endpoint `/api/json`, que llama a Claude con tu API key; límite de peticiones por IP |
| `src/page.js`, `scripts/build-pages.mjs` | Arman el documento completo; la segunda genera `dist/` para GitHub Pages |
| `.github/workflows/pages.yml` | Publica la página en GitHub Pages |
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

## Costos y cuidados

- Cada guía y cada "Complementar" consumen tu saldo de la API. Pon un **límite de gasto mensual** en la consola de Anthropic.
- El límite por IP evita abusos básicos, pero cualquiera con el enlace puede usarla: comparte el enlace con cuidado.
- Las guías salen del conocimiento de Claude, sin consulta en vivo: precios, horarios y peajes son aproximados.
