import express from "express";
import { randomUUID } from "node:crypto";
import path from "node:path";
import { fileURLToPath } from "node:url";
import Anthropic from "@anthropic-ai/sdk";
import { ejecutarTurno } from "./agent.js";
import { ICAR_03T_DEFAULTS } from "./vehicle.js";
import { googleDisponible } from "./google.js";

const here = path.dirname(fileURLToPath(import.meta.url));
const app = express();
app.use(express.json({ limit: "1mb" }));
app.use(express.static(path.join(here, "..", "public")));
const nm = path.join(here, "..", "node_modules");
app.get("/vendor/marked.min.js", (_q, r) => r.sendFile(path.join(nm, "marked", "lib", "marked.umd.js")));
app.get("/vendor/purify.min.js", (_q, r) => r.sendFile(path.join(nm, "dompurify", "dist", "purify.min.js")));

// Sesiones en memoria (se pierden al reiniciar el servidor).
const sesiones = new Map();

app.get("/api/config", (_req, res) => {
  res.json({ vehiculo: ICAR_03T_DEFAULTS, google: googleDisponible() });
});

app.post("/api/chat", async (req, res) => {
  const { sessionId, message } = req.body ?? {};
  // Solo se aceptan campos numéricos conocidos del perfil del vehículo.
  const vehiculo = Object.fromEntries(
    Object.entries(req.body?.vehiculo ?? {}).filter(
      ([k, v]) => k in ICAR_03T_DEFAULTS && typeof v === "number" && Number.isFinite(v) && v > 0,
    ),
  );
  if (typeof message !== "string" || !message.trim()) return res.status(400).json({ error: "Mensaje vacío" });

  const id = sesiones.has(sessionId) ? sessionId : randomUUID();
  const sesion = sesiones.get(id) ?? { messages: [], ocupada: false };
  sesiones.set(id, sesion);
  if (sesion.ocupada) return res.status(409).json({ error: "El agente aún está respondiendo." });
  sesion.ocupada = true;

  res.writeHead(200, {
    "Content-Type": "text/event-stream; charset=utf-8",
    "Cache-Control": "no-cache",
    Connection: "keep-alive",
  });
  const emit = (ev) => res.write(`data: ${JSON.stringify(ev)}\n\n`);
  emit({ type: "session", sessionId: id });

  const controller = new AbortController();
  res.on("close", () => controller.abort());

  // Contexto variable (fecha, vehículo) va en el mensaje del usuario, no en el system prompt.
  const contexto = `[Contexto: fecha de hoy ${new Date().toISOString().slice(0, 10)}. Vehículo del usuario: ${JSON.stringify(
    { ...ICAR_03T_DEFAULTS, ...vehiculo },
  )}]`;
  const largoPrevio = sesion.messages.length;
  sesion.messages.push({ role: "user", content: `${contexto}\n\n${message.trim()}` });

  try {
    await ejecutarTurno(sesion.messages, { emit, vehiculo, signal: controller.signal });
    emit({ type: "done" });
  } catch (err) {
    // Deshacer el turno incompleto para que el historial siga siendo válido.
    sesion.messages.length = largoPrevio;
    let texto = "Ocurrió un error inesperado.";
    if (err instanceof Anthropic.AuthenticationError) texto = "API key de Anthropic inválida o ausente (ANTHROPIC_API_KEY).";
    else if (err instanceof Anthropic.RateLimitError) texto = "Límite de solicitudes alcanzado; intenta en un momento.";
    else if (err instanceof Anthropic.APIError) texto = `Error de la API (${err.status}): ${err.message}`;
    else if (err instanceof Error) texto = err.message;
    if (!controller.signal.aborted) emit({ type: "error", text: texto });
    console.error(err);
  } finally {
    sesion.ocupada = false;
    res.end();
  }
});

app.post("/api/reset", (req, res) => {
  sesiones.delete(req.body?.sessionId);
  res.json({ ok: true });
});

const PORT = Number(process.env.PORT ?? 3000);
app.listen(PORT, () => {
  console.log(`Agente de viajes en http://localhost:${PORT}`);
  if (!googleDisponible()) console.log("Aviso: sin GOOGLE_MAPS_API_KEY; el agente usará búsqueda web para rutas y lugares.");
});
