// Integración opcional con Google Maps Platform (Routes API + Places API New).
// Si no hay GOOGLE_MAPS_API_KEY, las herramientas devuelven un error que le indica
// al agente usar la búsqueda web en su lugar.

const KEY = () => process.env.GOOGLE_MAPS_API_KEY;

export function googleDisponible() {
  return Boolean(KEY());
}

export function urlGoogleMaps(origen, destino, paradas = []) {
  const p = new URLSearchParams({ api: "1", origin: origen, destination: destino, travelmode: "driving" });
  if (paradas.length) p.set("waypoints", paradas.join("|"));
  return `https://www.google.com/maps/dir/?${p.toString()}`;
}

function formatoDuracion(s) {
  const seg = parseInt(String(s).replace("s", ""), 10) || 0;
  const h = Math.floor(seg / 3600);
  const m = Math.round((seg % 3600) / 60);
  return h ? `${h} h ${m} min` : `${m} min`;
}

function formatoDinero(m) {
  if (!m) return null;
  const valor = Number(m.units ?? 0) + (m.nanos ?? 0) / 1e9;
  return { moneda: m.currencyCode, valor };
}

export async function calcularRuta({ origen, destino, paradas_intermedias = [], evitar_peajes = false }) {
  const mapsUrl = urlGoogleMaps(origen, destino, paradas_intermedias);
  if (!KEY()) {
    return {
      error: "GOOGLE_MAPS_API_KEY no configurada. Usa web_search para rutas, distancias y peajes.",
      google_maps_url: mapsUrl,
    };
  }
  const body = {
    origin: { address: origen },
    destination: { address: destino },
    intermediates: paradas_intermedias.map((address) => ({ address })),
    travelMode: "DRIVE",
    routingPreference: "TRAFFIC_AWARE",
    computeAlternativeRoutes: paradas_intermedias.length === 0,
    extraComputations: ["TOLLS"],
    routeModifiers: { avoidTolls: evitar_peajes, vehicleInfo: { emissionType: "ELECTRIC" } },
    languageCode: "es",
    units: "METRIC",
  };
  const res = await fetch("https://routes.googleapis.com/directions/v2:computeRoutes", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "X-Goog-Api-Key": KEY(),
      "X-Goog-FieldMask": [
        "routes.description",
        "routes.distanceMeters",
        "routes.duration",
        "routes.warnings",
        "routes.travelAdvisory.tollInfo",
        "routes.legs.distanceMeters",
        "routes.legs.duration",
        "routes.legs.startLocation",
        "routes.legs.endLocation",
      ].join(","),
    },
    body: JSON.stringify(body),
  });
  const data = await res.json();
  if (!res.ok) return { error: data.error?.message ?? `HTTP ${res.status}`, google_maps_url: mapsUrl };

  return {
    google_maps_url: mapsUrl,
    rutas: (data.routes ?? []).map((r, i) => ({
      opcion: i + 1,
      via: r.description,
      distancia_km: +(r.distanceMeters / 1000).toFixed(1),
      duracion: formatoDuracion(r.duration),
      peajes_estimados_google: r.travelAdvisory?.tollInfo?.estimatedPrice?.map(formatoDinero) ?? null,
      advertencias: r.warnings ?? [],
      tramos: (r.legs ?? []).map((l) => ({
        distancia_km: +(l.distanceMeters / 1000).toFixed(1),
        duracion: formatoDuracion(l.duration),
        inicio: l.startLocation?.latLng,
        fin: l.endLocation?.latLng,
      })),
    })),
    nota:
      "Si peajes_estimados_google es null, Google no tiene tarifas para esa vía: consulta las tarifas oficiales con web_search.",
  };
}

export async function buscarLugares({ consulta, maximo = 6 }) {
  if (!KEY()) return { error: "GOOGLE_MAPS_API_KEY no configurada. Usa web_search." };
  const res = await fetch("https://places.googleapis.com/v1/places:searchText", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "X-Goog-Api-Key": KEY(),
      "X-Goog-FieldMask": [
        "places.displayName",
        "places.formattedAddress",
        "places.rating",
        "places.userRatingCount",
        "places.priceLevel",
        "places.googleMapsUri",
        "places.websiteUri",
        "places.evChargeOptions",
      ].join(","),
    },
    body: JSON.stringify({ textQuery: consulta, languageCode: "es", maxResultCount: Math.min(maximo, 10) }),
  });
  const data = await res.json();
  if (!res.ok) return { error: data.error?.message ?? `HTTP ${res.status}` };
  return {
    lugares: (data.places ?? []).map((p) => ({
      nombre: p.displayName?.text,
      direccion: p.formattedAddress,
      calificacion: p.rating,
      resenas: p.userRatingCount,
      precio: p.priceLevel,
      mapa: p.googleMapsUri,
      web: p.websiteUri,
      carga_ev: p.evChargeOptions
        ? {
            conectores: p.evChargeOptions.connectorCount,
            tipos: p.evChargeOptions.connectorAggregation?.map((c) => ({
              tipo: c.type,
              kw: c.maxChargeRateKw,
              cantidad: c.count,
            })),
          }
        : undefined,
    })),
  };
}
