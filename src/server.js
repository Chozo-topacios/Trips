// Planificador de viaje — versión abierta (sin cuenta de Claude para los visitantes).
// Sirve la misma página del artifact (artifact/planificador.html) y un endpoint /api/json
// que llama a Claude con la API key del dueño. Los viajes se guardan en el navegador de cada visitante.
import express from "express";
import fs from "node:fs";
import { buildPage, fragmentPath } from "./page.js";
import path from "node:path";
import { fileURLToPath } from "node:url";
import Anthropic from "@anthropic-ai/sdk";

const root = path.join(path.dirname(fileURLToPath(import.meta.url)), "..");

const MODEL = process.env.CLAUDE_MODEL ?? "claude-opus-5-5";
const EFFORT = process.env.CLAUDE_EFFORT ?? "medium";
const LIMIT_PER_HOUR = Number(process.env.RATE_LIMIT_PER_HOUR ?? 40); // peticiones por IP por hora
const MAX_PROMPT_CHARS = 60_000;

const client = new Anthropic();
const app = express();
app.set("trust proxy", 1); // detrás del proxy del hosting, para leer la IP real
app.use(express.json({ limit: "256kb" }));

// La página publicada en GitHub Pages llama a este servicio desde otro dominio.
const ALLOWED_ORIGINS = (process.env.ALLOWED_ORIGINS ?? "https://chozo-topacios.github.io").split(",").map((x) => x.trim()).filter(Boolean);
app.use("/api", (req, res, next) => {
  const origin = req.headers.origin;
  if (origin && ALLOWED_ORIGINS.includes(origin)) {
    res.set({ "Access-Control-Allow-Origin": origin, "Access-Control-Allow-Methods": "POST, OPTIONS", "Access-Control-Allow-Headers": "Content-Type", "Access-Control-Max-Age": "86400", Vary: "Origin" });
  }
  if (req.method === "OPTIONS") return res.sendStatus(204);
  next();
});

// ---------- Página: el mismo HTML del artifact, envuelto en un documento completo ----------
let page = buildPage();
if (process.env.NODE_ENV !== "production") {
  fs.watchFile(fragmentPath, { interval: 1000 }, () => { page = buildPage(); });
}
app.get("/", (_req, res) => res.type("html").send(page));
app.use(express.static(path.join(root, "public")));
app.get("/health", (_req, res) => res.json({ ok: true }));

// ---------- Límite simple por IP (en memoria) ----------
const hits = new Map();
function allowed(ip) {
  const now = Date.now();
  const list = (hits.get(ip) ?? []).filter((t) => now - t < 3_600_000);
  if (list.length >= LIMIT_PER_HOUR) { hits.set(ip, list); return false; }
  list.push(now); hits.set(ip, list);
  return true;
}
setInterval(() => { const now = Date.now(); for (const [ip, l] of hits) if (!l.some((t) => now - t < 3_600_000)) hits.delete(ip); }, 600_000).unref();

// ---------- Lectura tolerante de JSON (igual criterio que sample.json del artifact) ----------
function parseJSON(text) {
  const tryParse = (s) => { try { return JSON.parse(s); } catch { return undefined; } };
  let v = tryParse(text.trim());
  if (v !== undefined) return v;
  const fence = text.match(/```(?:json)?\s*([\s\S]*?)```/);
  if (fence && (v = tryParse(fence[1].trim())) !== undefined) return v;
  const start = text.search(/[[{]/), end = Math.max(text.lastIndexOf("}"), text.lastIndexOf("]"));
  if (start >= 0 && end > start && (v = tryParse(text.slice(start, end + 1))) !== undefined) return v;
  return undefined;
}

const SYSTEM = "Eres un planificador de viajes experto. Responde siempre en español. Tu respuesta será leída por un programa: escribe únicamente el objeto JSON pedido, sin texto antes ni después y sin bloques de código.";

app.post("/api/json", async (req, res) => {
  const prompt = req.body?.prompt;
  if (typeof prompt !== "string" || !prompt.trim() || prompt.length > MAX_PROMPT_CHARS) {
    return res.status(400).json({ code: "invalid_request", message: "Petición inválida." });
  }
  if (!allowed(req.ip)) {
    return res.status(429).json({ code: "rate_limited", message: "Demasiadas solicitudes. Intenta más tarde." });
  }

  const controller = new AbortController();
  res.on("close", () => { if (!res.writableEnded) controller.abort(); });

  try {
    const stream = client.beta.messages.stream(
      {
        model: MODEL,
        max_tokens: 32000,
        betas: ["server-side-fallback-2026-07-01"],
        fallbacks: "default",
        thinking: { type: "adaptive" },
        output_config: { effort: EFFORT },
        system: SYSTEM,
        messages: [{ role: "user", content: prompt }],
      },
      { signal: controller.signal },
    );
    const msg = await stream.finalMessage();

    if (msg.stop_reason === "refusal") return res.status(422).json({ code: "refused", message: "Claude no respondió esta solicitud." });
    const text = msg.content.filter((b) => b.type === "text").map((b) => b.text).join("");
    if (msg.stop_reason === "max_tokens") return res.status(502).json({ code: "invalid_json", message: "Respuesta incompleta." });
    const value = parseJSON(text);
    if (value === undefined) return res.status(502).json({ code: "invalid_json", message: "Respuesta sin JSON válido." });
    res.json({ value });
  } catch (err) {
    if (controller.signal.aborted) return; // el visitante canceló
    let code = "upstream_error";
    if (err instanceof Anthropic.RateLimitError) code = "rate_limited";
    else if (err instanceof Anthropic.AuthenticationError) code = "server_key";
    else if (err instanceof Anthropic.APIError && err.status === 529) code = "overloaded";
    console.error("[api/json]", err?.status ?? "", err?.message ?? err);
    if (!res.headersSent) res.status(502).json({ code, message: "No se pudo completar la solicitud." });
  }
});

const PORT = Number(process.env.PORT ?? 3000);
app.listen(PORT, () => {
  console.log(`Planificador de viaje en http://localhost:${PORT}`);
  if (!process.env.ANTHROPIC_API_KEY) console.log("Aviso: falta ANTHROPIC_API_KEY; las guías no se podrán armar.");
});
