// Perfil del vehículo y planificador de energía para la Chery iCAR 03T (100 % eléctrica).
// Los valores por defecto son de referencia: verifíquelos en la ficha técnica de su versión
// y ajústelos desde la interfaz ("Mi vehículo").

export const ICAR_03T_DEFAULTS = {
  nombre: "iCAR 03T (eléctrica, doble motor AWD)",
  bateria_kwh: 65.7, // capacidad útil aproximada (LFP)
  consumo_kwh_100km: 17.5, // consumo mixto real aproximado a ~90 km/h
  carga_dc_max_kw: 80, // potencia pico DC de referencia
  carga_ac_kw: 7, // cargador a bordo AC
  masa_kg: 1900, // vehículo + ocupantes promedio
};

const G = 9.81;
const EFICIENCIA_TREN = 0.88; // batería -> rueda
const REGENERACION = 0.6; // fracción recuperada en bajadas

/**
 * Estima la energía del trayecto y propone una estrategia de carga.
 * Todos los resultados son estimaciones; el agente debe presentarlos como tales.
 */
export function planEnergia(input, vehiculoUsuario = {}) {
  const v = { ...ICAR_03T_DEFAULTS, ...vehiculoUsuario };
  const {
    distancia_km,
    subida_total_m = 0,
    bajada_total_m = 0,
    velocidad_promedio_kmh = 80,
    aire_acondicionado = true,
    pasajeros_extra_kg = 0,
    soc_inicial_pct = 100,
    soc_reserva_llegada_pct = 15,
    cargadores_en_ruta = [], // [{ nombre, km, potencia_kw }]
  } = input;

  // Factor por velocidad (resistencia aerodinámica crece con v²)
  let factorVel = 1;
  if (velocidad_promedio_kmh > 100) factorVel = 1.3;
  else if (velocidad_promedio_kmh > 90) factorVel = 1.15;
  else if (velocidad_promedio_kmh < 60) factorVel = 0.92;
  const factorAC = aire_acondicionado ? 1.05 : 1;

  const masa = v.masa_kg + pasajeros_extra_kg;
  const kwhPlano = (distancia_km / 100) * v.consumo_kwh_100km * factorVel * factorAC;
  const kwhSubida = (masa * G * subida_total_m) / 3.6e6 / EFICIENCIA_TREN;
  const kwhRegen = ((masa * G * bajada_total_m) / 3.6e6) * REGENERACION * EFICIENCIA_TREN;
  const kwhTotal = Math.max(kwhPlano + kwhSubida - kwhRegen, kwhPlano * 0.5);
  const consumoEfectivo = (kwhTotal / distancia_km) * 100;

  const kwhDisponibles = (v.bateria_kwh * (soc_inicial_pct - soc_reserva_llegada_pct)) / 100;
  const autonomiaKm = (kwhDisponibles / kwhTotal) * distancia_km;
  const socLlegadaSinCargar = soc_inicial_pct - (kwhTotal / v.bateria_kwh) * 100;

  // Plan de paradas: cargar 10/20 % -> 80 % (zona rápida de la curva de carga).
  const paradas = [];
  const kmPorPct = distancia_km / ((kwhTotal / v.bateria_kwh) * 100);
  let soc = soc_inicial_pct;
  let km = 0;
  const ordenados = [...cargadores_en_ruta].sort((a, b) => a.km - b.km);
  let ultimoCargador = null;
  for (const c of ordenados) {
    const socAlLlegar = soc - (c.km - km) / kmPorPct;
    // ¿Alcanzo el siguiente cargador (o el destino) con reserva?
    const idx = ordenados.indexOf(c);
    const siguienteKm = idx + 1 < ordenados.length ? ordenados[idx + 1].km : distancia_km;
    const socEnSiguiente = socAlLlegar - (siguienteKm - c.km) / kmPorPct;
    if (socEnSiguiente < soc_reserva_llegada_pct) {
      const objetivo = Math.min(
        80,
        Math.max(socAlLlegar, soc_reserva_llegada_pct + (siguienteKm - c.km) / kmPorPct + 5),
      );
      const objetivoFinal = Math.max(objetivo, Math.min(80, socAlLlegar + 10));
      const kwh = ((objetivoFinal - socAlLlegar) / 100) * v.bateria_kwh;
      const potencia = Math.min(c.potencia_kw ?? v.carga_dc_max_kw, v.carga_dc_max_kw);
      const potenciaMedia = potencia > v.carga_ac_kw + 1 ? potencia * 0.7 : potencia;
      paradas.push({
        cargador: c.nombre,
        km: c.km,
        soc_llegada_pct: Math.round(socAlLlegar),
        cargar_hasta_pct: Math.round(objetivoFinal),
        kwh: +kwh.toFixed(1),
        minutos_estimados: Math.round((kwh / potenciaMedia) * 60),
        alcanza_sin_problema: socAlLlegar >= 5,
      });
      soc = objetivoFinal;
    } else {
      soc = socAlLlegar;
    }
    km = c.km;
    ultimoCargador = c;
  }
  const socFinal = soc - (distancia_km - km) / kmPorPct;

  let recomendacion;
  if (socLlegadaSinCargar >= soc_reserva_llegada_pct + 5) {
    recomendacion =
      "Sale al 100 % y llega sin necesidad de cargar. Cargue al 100 % la noche anterior (en LFP es seguro y ayuda a calibrar el BMS) y salga poco después de terminar.";
  } else if (cargadores_en_ruta.length === 0) {
    recomendacion =
      "El trayecto supera la autonomía con reserva: salga al 100 % y planee al menos una parada de carga rápida DC. Busque cargadores en ruta y vuelva a calcular con ellos.";
  } else {
    recomendacion =
      "Salga al 100 % y haga las paradas indicadas cargando solo hasta ~80 % (por encima la carga DC se vuelve lenta). Tenga un cargador alternativo para cada parada.";
  }

  return {
    vehiculo: v,
    nota_combustible:
      "La iCAR 03T es 100 % eléctrica: no usa gasolina. La gestión es solo de batería (SOC) y paradas de carga.",
    energia_estimada_kwh: +kwhTotal.toFixed(1),
    consumo_efectivo_kwh_100km: +consumoEfectivo.toFixed(1),
    desglose_kwh: {
      rodadura_y_aire: +kwhPlano.toFixed(1),
      subidas: +kwhSubida.toFixed(1),
      regeneracion_bajadas: -+kwhRegen.toFixed(1),
    },
    autonomia_estimada_km_con_reserva: Math.round(autonomiaKm),
    soc_llegada_sin_cargar_pct: Math.round(socLlegadaSinCargar),
    paradas_de_carga: paradas,
    soc_llegada_con_plan_pct: Math.round(socFinal),
    ultimo_cargador_considerado: ultimoCargador?.nombre ?? null,
    recomendacion,
    consejos: [
      "Mantener 90–100 km/h en autopista reduce el consumo notablemente frente a 110–120 km/h.",
      "En descensos largos use el nivel alto de regeneración / modo de un pedal.",
      "Preacondicione la cabina conectado al cargador antes de salir.",
      "Lleve el cargador portátil (Modo 2) y adaptadores para enchufes de hoteles.",
      "Revise presión de llantas: ±10 % de consumo con llantas bajas.",
    ],
    advertencia:
      "Estimación aproximada: el consumo real depende de clima, tráfico, carga y estilo de manejo.",
  };
}
