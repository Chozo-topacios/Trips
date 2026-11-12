// Reemplazo del runtime de Claude para la versión abierta del planificador.
// La página pide `claude.use("sample")` para armar guías; aquí esa llamada va al servidor propio (/api/json).
// No hay base de datos ni usuario: la página guarda los viajes en el navegador de cada visitante.
(() => {
  const base = String(window.PLANIFICADOR_API || "").replace(/\/+$/, "");
  // En GitHub Pages no hay servidor propio: sin dirección configurada, no hay cómo llamar a Claude.
  const staticHost = /\.github\.io$/.test(location.hostname);
  async function json(prompt, opts = {}) {
    if (!base && staticHost) throw { code: "no_backend", message: "Servicio de guías sin configurar." };
    let res;
    try {
      res = await fetch(base + "/api/json", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ prompt }),
        signal: opts.signal,
      });
    } catch (e) {
      throw { code: e && e.name === "AbortError" ? "cancelled" : "upstream_error", message: String(e) };
    }
    const data = await res.json().catch(() => null);
    if (!res.ok || !data || !("value" in data)) {
      throw { code: (data && data.code) || "upstream_error", message: (data && data.message) || `HTTP ${res.status}` };
    }
    return data.value;
  }
  async function sample() { throw { code: "capability_removed", message: "No disponible en esta versión." }; }
  sample.json = json;
  sample.limits = async () => ({ maxPromptBytes: 60000 });
  window.claude = { use: async (name) => (name === "sample" ? sample : null) };
})();
