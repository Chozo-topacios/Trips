const $ = (s) => document.querySelector(s);
const estado = { sessionId: null, modo: null, vehiculo: {}, ocupado: false };

const VEH_KEY = "ruta.vehiculo";
try { estado.vehiculo = JSON.parse(localStorage.getItem(VEH_KEY) || "{}"); } catch { estado.vehiculo = {}; }

let defaultsVehiculo = {};
fetch("/api/config").then((r) => r.json()).then((c) => { defaultsVehiculo = c.vehiculo; }).catch(() => {});

function mostrar(id) {
  for (const s of ["#paso-modo", "#paso-datos", "#chat"]) $(s).classList.toggle("hidden", s !== id);
}

// Paso 1: tipo de viaje
document.querySelectorAll(".modo").forEach((b) =>
  b.addEventListener("click", () => {
    estado.modo = b.dataset.modo;
    $("#form-carro").classList.toggle("hidden", estado.modo !== "carro");
    $("#form-avion").classList.toggle("hidden", estado.modo !== "avion");
    mostrar("#paso-datos");
    document.querySelector(`#form-${estado.modo} input`).focus();
  }),
);
document.querySelectorAll(".volver").forEach((b) => b.addEventListener("click", () => mostrar("#paso-modo")));

// Paso 2: datos -> primer mensaje
function enviarFormulario(form, construir) {
  form.addEventListener("submit", (e) => {
    e.preventDefault();
    const d = Object.fromEntries(new FormData(form));
    mostrar("#chat");
    enviar(construir(d));
  });
}
enviarFormulario($("#form-carro"), (d) =>
  [
    `Quiero planear un viaje en CARRO con mi iCAR 03T.`,
    `- Origen: ${d.origen}`,
    `- Destino: ${d.destino}`,
    d.fecha && `- Fecha de salida: ${d.fecha}`,
    `- Duración: ${d.dias} días (${d.idavuelta === "Sí" ? "ida y vuelta" : "solo ida"})`,
    `- Viajeros: ${d.viajeros}`,
    `- Batería al salir: ${d.soc}%`,
    d.presupuesto && `- Presupuesto: ${d.presupuesto}`,
    d.intereses && `- Intereses: ${d.intereses}`,
    ``,
    `Dame la ruta recomendada (y alternativas), peajes con tarifas, estado vial, plan de carga de la batería, sitios turísticos en la ruta, hospedajes estratégicos y presupuesto.`,
  ].filter(Boolean).join("\n"),
);
enviarFormulario($("#form-avion"), (d) =>
  [
    `Quiero planear un viaje en AVIÓN.`,
    d.origen && `- Salgo desde: ${d.origen}`,
    `- Destino: ${d.destino}`,
    d.fecha && `- Fecha de llegada: ${d.fecha}`,
    `- Días: ${d.dias}`,
    `- Viajeros: ${d.viajeros}`,
    d.presupuesto && `- Presupuesto: ${d.presupuesto}`,
    d.intereses && `- Intereses: ${d.intereses}`,
    ``,
    `Dame los sitios imperdibles con itinerario por día, zonas clave para hospedarme, consejos de movilidad local y un estimado de presupuesto.`,
  ].filter(Boolean).join("\n"),
);

// Paso 3: chat
const entrada = $("#entrada");
entrada.addEventListener("input", () => { entrada.style.height = "auto"; entrada.style.height = entrada.scrollHeight + "px"; });
entrada.addEventListener("keydown", (e) => {
  if (e.key === "Enter" && !e.shiftKey) { e.preventDefault(); $("#form-chat").requestSubmit(); }
});
$("#form-chat").addEventListener("submit", (e) => {
  e.preventDefault();
  const t = entrada.value.trim();
  if (!t || estado.ocupado) return;
  entrada.value = "";
  entrada.style.height = "auto";
  enviar(t);
});

function burbuja(clase, texto) {
  const div = document.createElement("div");
  div.className = `msg ${clase}`;
  if (texto) div.textContent = texto;
  $("#mensajes").appendChild(div);
  div.scrollIntoView({ block: "end", behavior: "smooth" });
  return div;
}

const render = (md) => DOMPurify.sanitize(marked.parse(md));

function tarjetaEnergia(d) {
  const el = document.createElement("div");
  el.className = "energy";
  const items = [
    [`${d.energia_estimada_kwh} kWh`, "energía estimada"],
    [`${d.consumo_efectivo_kwh_100km}`, "kWh/100 km efectivos"],
    [`${d.autonomia_estimada_km_con_reserva} km`, "autonomía con reserva"],
    [`${d.paradas_de_carga.length}`, "paradas de carga"],
  ];
  for (const [b, s] of items) {
    const c = document.createElement("div");
    c.innerHTML = `<b></b><span></span>`;
    c.querySelector("b").textContent = b;
    c.querySelector("span").textContent = s;
    el.appendChild(c);
  }
  return el;
}

async function enviar(texto) {
  estado.ocupado = true;
  $("#enviar").disabled = true;
  burbuja("user", texto);
  const caja = burbuja("agent");
  const extras = document.createElement("div");
  const chips = document.createElement("div");
  chips.className = "chips";
  const status = document.createElement("div");
  status.className = "status";
  status.textContent = "Pensando…";
  const cuerpo = document.createElement("div");
  extras.append(chips);
  caja.append(status, extras, cuerpo);

  let md = "";
  let pendiente = false;
  const pintar = () => {
    if (pendiente) return;
    pendiente = true;
    requestAnimationFrame(() => { cuerpo.innerHTML = render(md); pendiente = false; });
  };

  try {
    const res = await fetch("/api/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ sessionId: estado.sessionId, message: texto, vehiculo: estado.vehiculo }),
    });
    if (!res.ok || !res.body) throw new Error((await res.json().catch(() => ({}))).error || `HTTP ${res.status}`);

    const reader = res.body.getReader();
    const dec = new TextDecoder();
    let buf = "";
    for (;;) {
      const { value, done } = await reader.read();
      if (done) break;
      buf += dec.decode(value, { stream: true });
      let i;
      while ((i = buf.indexOf("\n\n")) >= 0) {
        const linea = buf.slice(0, i);
        buf = buf.slice(i + 2);
        if (!linea.startsWith("data: ")) continue;
        const ev = JSON.parse(linea.slice(6));
        switch (ev.type) {
          case "session": estado.sessionId = ev.sessionId; break;
          case "status": status.textContent = ev.text; break;
          case "text": md += ev.delta; pintar(); break;
          case "route": {
            const a = document.createElement("a");
            a.className = "chip"; a.href = ev.url; a.target = "_blank"; a.rel = "noopener";
            a.textContent = `🗺️ Ver ruta ${ev.origen} → ${ev.destino} en Google Maps`;
            chips.appendChild(a);
            break;
          }
          case "energy": extras.appendChild(tarjetaEnergia(ev.data)); break;
          case "error": throw new Error(ev.text);
        }
      }
    }
  } catch (err) {
    burbuja("error", `⚠️ ${err.message}`);
  } finally {
    status.remove();
    if (!md) cuerpo.innerHTML = render(md || "_(sin respuesta)_");
    estado.ocupado = false;
    $("#enviar").disabled = false;
    entrada.focus();
  }
}

// Nuevo viaje
$("#btn-nuevo").addEventListener("click", async () => {
  if (estado.sessionId) fetch("/api/reset", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ sessionId: estado.sessionId }) });
  estado.sessionId = null;
  $("#mensajes").innerHTML = "";
  mostrar("#paso-modo");
});

// Ajustes del vehículo
const dlg = $("#dlg-vehiculo");
$("#btn-vehiculo").addEventListener("click", () => {
  const f = $("#form-vehiculo");
  for (const el of f.elements) if (el.name) el.value = estado.vehiculo[el.name] ?? defaultsVehiculo[el.name] ?? "";
  dlg.showModal();
});
dlg.addEventListener("close", () => {
  if (dlg.returnValue !== "ok") return;
  const v = {};
  for (const el of $("#form-vehiculo").elements) if (el.name && el.value !== "") v[el.name] = Number(el.value);
  estado.vehiculo = v;
  try { localStorage.setItem(VEH_KEY, JSON.stringify(v)); } catch {}
});
