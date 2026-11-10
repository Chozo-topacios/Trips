import Anthropic from "@anthropic-ai/sdk";
import { z } from "zod";
import { planEnergia } from "./vehicle.js";
import { calcularRuta, buscarLugares } from "./google.js";

const client = new Anthropic();
const MODEL = process.env.CLAUDE_MODEL ?? "claude-opus-5-5";
const EFFORT = process.env.CLAUDE_EFFORT ?? "medium";
const MAX_ITERACIONES = 20;

// El prompt de sistema es estable (sin fechas ni datos variables) para que el caché de prompts funcione.
export const SYSTEM_PROMPT = `Eres "Ruta", un agente experto en planificación de viajes. Respondes siempre en español, con tono cercano y práctico.

FLUJO
1. Si aún no lo sabes, pregunta primero si el viaje es en CARRO o en AVIÓN.
2. CARRO: necesitas origen, destino, fecha, número de viajeros y presupuesto aproximado. Luego:
   • Ruta: usa calcular_ruta (Google Maps) para obtener rutas recomendadas y alternativas; si no está disponible, usa web_search. Entrega siempre el enlace de Google Maps.
   • Peajes y estado vial: lista cada peaje en la ruta con su tarifa vigente para categoría de automóvil (en Colombia, categoría I). Verifica con web_search en fuentes oficiales (ANI, INVÍAS, concesionarias) y cita la fuente y año. Consulta cierres o restricciones viales recientes.
   • Gestión de energía (iCAR 03T): el vehículo es 100 % ELÉCTRICO. Si el usuario pregunta por gasolina, aclárale amablemente que no aplica. Busca electrolineras / cargadores rápidos DC en la ruta (buscar_lugares o web_search) con su km aproximado y potencia, estima el desnivel de la ruta y llama a plan_energia. Indica con qué % salir, dónde parar, hasta qué % cargar, cuánto tiempo y un plan B para cada carga.
   • Sitios turísticos EN la ruta: paradas que valgan la pena (miradores, pueblos, gastronomía), idealmente coincidiendo con las paradas de carga.
   • Hospedajes estratégicos: preferiblemente con cargador para vehículo eléctrico o parqueadero con toma; incluye rango de precio.
   • Presupuesto: peajes + energía (kWh × tarifa) + hospedaje + comidas.
3. AVIÓN: necesitas destino, número de días, fechas, intereses y presupuesto. Luego:
   • Top sitios imperdibles y un itinerario día a día.
   • Zonas clave para hospedarse (por qué y rango de precio).
   • Movilidad local (transporte desde el aeropuerto, apps, tarjetas de transporte, seguridad).
   • Estimado de presupuesto (vuelos de referencia, hospedaje, comidas, actividades).

REGLAS
• Si falta un dato imprescindible, pregúntalo de forma breve (máximo 3 preguntas a la vez); si no es crítico, asume un valor razonable y dilo.
• Precios, tarifas y horarios cambian: verifícalos con web_search y aclara que son aproximados.
• No inventes nombres de lugares, hoteles ni cargadores: si no lo verificaste, dilo.
• Formato: Markdown con encabezados (##), tablas para peajes, paradas de carga y presupuesto, y listas cortas. Termina con un "Resumen rápido" de 3–5 viñetas.`;

const PlanEnergiaInput = z.object({
  distancia_km: z.number().positive(),
  subida_total_m: z.number().nonnegative().optional(),
  bajada_total_m: z.number().nonnegative().optional(),
  velocidad_promedio_kmh: z.number().positive().optional(),
  aire_acondicionado: z.boolean().optional(),
  pasajeros_extra_kg: z.number().nonnegative().optional(),
  soc_inicial_pct: z.number().min(1).max(100).optional(),
  soc_reserva_llegada_pct: z.number().min(0).max(50).optional(),
  cargadores_en_ruta: z
    .array(z.object({ nombre: z.string(), km: z.number().nonnegative(), potencia_kw: z.number().positive().optional() }))
    .optional(),
});
const RutaInput = z.object({
  origen: z.string().min(1),
  destino: z.string().min(1),
  paradas_intermedias: z.array(z.string()).optional(),
  evitar_peajes: z.boolean().optional(),
});
const LugaresInput = z.object({ consulta: z.string().min(1), maximo: z.number().int().min(1).max(10).optional() });

const TOOLS = [
  {
    name: "calcular_ruta",
    description:
      "Calcula rutas en carro con Google Maps (Routes API): distancia, duración con tráfico, rutas alternativas, peajes estimados por Google y enlace a Google Maps. Úsala al inicio de cualquier viaje en carro.",
    eager_input_streaming: true,
    input_schema: {
      type: "object",
      properties: {
        origen: { type: "string", description: "Ciudad o dirección de origen" },
        destino: { type: "string", description: "Ciudad o dirección de destino" },
        paradas_intermedias: { type: "array", items: { type: "string" }, description: "Paradas opcionales en orden" },
        evitar_peajes: { type: "boolean" },
      },
      required: ["origen", "destino"],
      additionalProperties: false,
    },
  },
  {
    name: "buscar_lugares",
    description:
      "Busca lugares en Google Maps (Places API): hoteles, restaurantes, atracciones o cargadores para vehículo eléctrico (ej. 'cargador rápido vehículo eléctrico Honda Tolima'). Devuelve calificación, dirección, enlace y conectores de carga.",
    eager_input_streaming: true,
    input_schema: {
      type: "object",
      properties: {
        consulta: { type: "string", description: "Texto de búsqueda con el lugar, ej. 'hoteles con cargador eléctrico en Villa de Leyva'" },
        maximo: { type: "integer", description: "Número máximo de resultados (1-10)" },
      },
      required: ["consulta"],
      additionalProperties: false,
    },
  },
  {
    name: "plan_energia",
    description:
      "Calcula el consumo de batería de la iCAR 03T para un trayecto (incluye efecto de subidas, bajadas con regeneración y velocidad) y propone con qué % salir y en qué cargadores parar y hasta qué %. Pasa los cargadores con su km aproximado desde el origen.",
    eager_input_streaming: true,
    input_schema: {
      type: "object",
      properties: {
        distancia_km: { type: "number" },
        subida_total_m: { type: "number", description: "Desnivel positivo acumulado estimado de la ruta" },
        bajada_total_m: { type: "number", description: "Desnivel negativo acumulado estimado de la ruta" },
        velocidad_promedio_kmh: { type: "number" },
        aire_acondicionado: { type: "boolean" },
        pasajeros_extra_kg: { type: "number", description: "Peso extra de equipaje/pasajeros por encima de 1 adulto + equipaje ligero" },
        soc_inicial_pct: { type: "number", description: "% de batería al salir (por defecto 100)" },
        soc_reserva_llegada_pct: { type: "number", description: "% mínimo deseado al llegar a cada punto (por defecto 15)" },
        cargadores_en_ruta: {
          type: "array",
          items: {
            type: "object",
            properties: {
              nombre: { type: "string" },
              km: { type: "number", description: "Km desde el origen" },
              potencia_kw: { type: "number" },
            },
            required: ["nombre", "km"],
            additionalProperties: false,
          },
        },
      },
      required: ["distancia_km"],
      additionalProperties: false,
    },
  },
  { type: "web_search_20260209", name: "web_search", max_uses: 15, user_location: { type: "approximate", country: "CO" } },
  { type: "web_fetch_20260209", name: "web_fetch", max_uses: 6 },
];

async function ejecutarHerramienta(nombre, input, ctx) {
  switch (nombre) {
    case "calcular_ruta": {
      const p = RutaInput.safeParse(input);
      if (!p.success) return { invalid: true };
      const r = await calcularRuta(p.data);
      ctx.emit({ type: "route", url: r.google_maps_url, origen: p.data.origen, destino: p.data.destino });
      return r;
    }
    case "buscar_lugares": {
      const p = LugaresInput.safeParse(input);
      if (!p.success) return { invalid: true };
      return buscarLugares(p.data);
    }
    case "plan_energia": {
      const p = PlanEnergiaInput.safeParse(input);
      if (!p.success) return { invalid: true };
      const r = planEnergia(p.data, ctx.vehiculo);
      ctx.emit({ type: "energy", data: r });
      return r;
    }
    default:
      return { error: `Herramienta desconocida: ${nombre}` };
  }
}

const ETIQUETAS = {
  web_search: "Buscando en la web",
  web_fetch: "Leyendo página",
  calcular_ruta: "Calculando ruta en Google Maps",
  buscar_lugares: "Buscando lugares en Google Maps",
  plan_energia: "Calculando plan de energía iCAR 03T",
};

/**
 * Ejecuta un turno del agente. `messages` es el historial completo (se modifica in situ).
 * `emit` envía eventos al navegador (SSE).
 */
export async function ejecutarTurno(messages, { emit, vehiculo, signal }) {
  let reintentosJson = 0;
  for (let i = 0; i < MAX_ITERACIONES; i++) {
    const stream = client.beta.messages.stream(
      {
        model: MODEL,
        max_tokens: 64000,
        betas: ["server-side-fallback-2026-07-01"],
        fallbacks: "default",
        thinking: { type: "adaptive", display: "summarized" },
        output_config: { effort: EFFORT },
        cache_control: { type: "ephemeral" },
        system: SYSTEM_PROMPT,
        tools: TOOLS,
        messages,
      },
      { signal },
    );

    let message;
    try {
      for await (const event of stream) {
        if (event.type === "content_block_start") {
          const b = event.content_block;
          if (b.type === "thinking") emit({ type: "status", text: "Pensando…" });
          else if (b.type === "server_tool_use" || b.type === "tool_use")
            emit({ type: "status", text: ETIQUETAS[b.name] ?? b.name });
        } else if (event.type === "content_block_delta" && event.delta.type === "text_delta") {
          emit({ type: "text", delta: event.delta.text });
        }
      }
      message = await stream.finalMessage();
      reintentosJson = 0;
    } catch (err) {
      if (err instanceof Anthropic.APIError || signal?.aborted || reintentosJson++ >= 2) throw err;
      continue; // entrada de herramienta con JSON no parseable: reintentar el turno
    }

    if (message.stop_reason === "refusal") {
      emit({ type: "text", delta: "\n\n_No puedo ayudar con esa solicitud._" });
      return;
    }
    messages.push({ role: "assistant", content: message.content });

    if (message.stop_reason === "pause_turn") continue;
    const usos = message.content.filter((b) => b.type === "tool_use");
    if (usos.length === 0) return; // end_turn u otra parada final
    if (message.stop_reason === "max_tokens") throw new Error("Respuesta truncada por max_tokens.");

    const resultados = await Promise.all(
      usos.map(async (u) => {
        try {
          const r = await ejecutarHerramienta(u.name, u.input, { emit, vehiculo });
          if (r?.invalid)
            return { type: "tool_result", tool_use_id: u.id, is_error: true, content: JSON.stringify({ INVALID_JSON: JSON.stringify(u.input) }) };
          return { type: "tool_result", tool_use_id: u.id, content: JSON.stringify(r) };
        } catch (e) {
          return { type: "tool_result", tool_use_id: u.id, is_error: true, content: String(e?.message ?? e) };
        }
      }),
    );
    messages.push({ role: "user", content: resultados });
    emit({ type: "text", delta: "\n\n" });
  }
  emit({ type: "text", delta: "\n\n_Se alcanzó el límite de pasos para este turno._" });
}
