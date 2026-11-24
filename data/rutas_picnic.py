# Genera data/rutas-picnic.json: planes listos (carro iCAR 03T, rango extendido) para cada lugar
# de la lista de Google Maps "Rutas picnic" de Leonardo. Cifras aproximadas.
import json, re, unicodedata

# Chery iCAR 03T REEV (Colombia). Ficha: batería LFP 34,31 kWh; 160 km eléctricos (NEDC);
# 801 km combinados (WLTC) con tanque de 12 galones; generador 1.5 turbo; carga DC 90 kW.
# Consumos estimados a partir de la ficha (no hay cifra oficial de consumo):
#   eléctrico ≈ 24 kWh/100 km reales (34,31 kWh / 160 km NEDC, ajustado a uso real) → ~140 km con batería llena
#   gasolina (generador) ≈ 52 km/galón ((801 − ~150 km eléctricos) / 12 galones ≈ 54; coincide con los 7,15 L/100 km WLTC del iCAR V25, mismo 1.5T)
ICAR = {"ev_km": 140, "kwh_100": 24, "km_gal": 52, "precio_kwh": 800, "precio_gal": 16000}

def estimar(km):
    ev = min(km, ICAR["ev_km"]); gas = max(0, km - ev)
    kwh = ev * ICAR["kwh_100"] / 100; gal = gas / ICAR["km_gal"]
    return {"ev": ev, "gas": gas, "kwh": kwh, "gal": gal, "costo": int(round(kwh * ICAR["precio_kwh"] + gal * ICAR["precio_gal"], -3))}

def dec(x):
    return f"{x:.1f}".replace(".", ",")

def slug(s):
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode().lower()
    return re.sub(r"[^a-z0-9]+", "-", s).strip("-")

def act(hora, titulo, detalle, lugar, tipo, duracion="", costo=""):
    return {"hora": hora, "titulo": titulo, "detalle": detalle, "lugar": lugar, "tipo": tipo, "duracion": duracion, "costo": costo}

PICNIC = ["Mantel o cobija impermeable", "Comida y agua (no hay tiendas cerca)", "Bolsas para traer la basura de vuelta", "Chaqueta abrigada e impermeable", "Bloqueador y gorra", "Zapatos de caminata", "Efectivo para entradas y peajes", "Repelente"]
FRIO = ["Guantes y gorro (hace frío)", "Termo con bebida caliente"]
CALOR = ["Ropa ligera y vestido de baño", "Toalla", "Sandalias para el agua"]

def energia(extra, km_total):
    e = estimar(km_total)
    if e["gas"] <= 0:
        cuenta = f"Ida y vuelta son ~{km_total} km: con la batería al 100 % (34,3 kWh, ~140 km reales) lo haces todo en eléctrico, sin gastar gasolina."
    else:
        tanque = "de los 12 del tanque" if e["gal"] <= 12 else "(más que los 12 del tanque: tanquea en el camino y carga la batería en los hoteles)"
        cuenta = (f"Ida y vuelta son ~{km_total} km: ~{e['ev']} km en eléctrico con la batería llena y ~{e['gas']} km con el generador, "
                  f"unos {dec(e['gal'])} galones {tanque}.")
    base = ["Carga la batería al 100 % la noche anterior en casa (34,3 kWh LFP; en LFP cargar al 100 % está bien).",
            cuenta,
            "Si en el destino hay cargador rápido (hasta 90 kW), del 30 % al 80 % tarda unos 20 minutos.",
            "En la ciudad y en los tramos planos usa el modo eléctrico; en carretera, el modo híbrido mantiene la batería sin parar a cargar."]
    return base + extra

R = []
def add(**k): R.append(k)

# ---------------------------------------------------------------- 1
add(nombre="Parque Embalse El Hato", municipio="Carmen de Carupa, Cundinamarca", lat=5.2925512, lng=-73.9063211,
    km=130, horas="3 h", via="Autopista Norte → Zipaquirá → Ubaté → Carmen de Carupa", dias=1, tipo="Embalse de páramo", frio=True,
    peajes=30000, entrada="Entrada al parque aprox. $10.000 por persona",
    resumen="Embalse rodeado de páramo y bosque de pinos, con zonas de picnic, pesca de trucha y caminatas cortas. Un día completo de naturaleza fría y tranquila.",
    perfil=[("Bogotá",0,2600),("Zipaquirá",45,2650),("Sutatausa",85,2550),("Ubaté",100,2556),("Carmen de Carupa",120,2950),("Embalse El Hato",130,2900)],
    acts=[act("06:00","Salida de Bogotá","Sal temprano para evitar el tráfico de la Autopista Norte.","Bogotá","traslado"),
          act("08:30","Desayuno en Ubaté","Ubaté es la capital lechera: almojábanas, queso fresco y kumis.","Ubaté, Cundinamarca","pueblo","45 min","$20.000"),
          act("10:00","Llegada al Embalse El Hato","Recorre la orilla y elige un sitio de picnic con vista al agua y al páramo.","Parque Embalse El Hato, Carmen de Carupa, Cundinamarca","naturaleza","1 h"),
          act("11:00","Caminata por el bosque y el páramo","Sendero suave alrededor del embalse, con frailejones en la parte alta.","Parque Embalse El Hato, Carmen de Carupa, Cundinamarca","naturaleza","1 h 30 min"),
          act("12:30","Picnic junto al embalse","Almuerzo campestre; si te gusta pescar, pregunta en la entrada por la pesca de trucha.","Parque Embalse El Hato, Carmen de Carupa, Cundinamarca","comida","1 h 30 min"),
          act("15:00","Regreso por Ubaté","Parada opcional en la Basílica del Santo Cristo de Ubaté.","Basílica del Santo Cristo, Ubaté, Cundinamarca","sitio turístico","30 min"),
          act("18:00","Llegada a Bogotá","","Bogotá","traslado")],
    energia_extra=["La subida a Carmen de Carupa es larga: activa el modo de conservar batería antes de Ubaté.","En la bajada de regreso usa regeneración alta."],
    ideas=[("Laguna de Fúquene","Laguna enorme a 20 min de Ubaté, ideal para ver aves.","Fúquene, Cundinamarca","naturaleza"),("Farallones de Sutatausa","Formaciones rocosas con senderos y pictografías.","Sutatausa, Cundinamarca","naturaleza")],
    comida=[("Trucha al ajillo","Restaurantes de Carmen de Carupa"),("Almojábanas y kumis","Panaderías de Ubaté")])

# ---------------------------------------------------------------- 2
add(nombre="Laguna Siecha", municipio="Guasca, Cundinamarca", lat=4.7644444, lng=-73.8527778,
    km=60, horas="2 h", via="La Calera → Guasca → vía al sector Siecha (PNN Chingaza)", dias=1, tipo="Laguna de páramo", frio=True,
    peajes=0, entrada="Ingreso al PNN Chingaza (sector Siecha) con reserva previa; aprox. $20.000–$40.000 por persona",
    resumen="Tres lagunas glaciares en el páramo de Chingaza, rodeadas de frailejones. Caminata de páramo con picnic en un paisaje único. Requiere reserva con Parques Nacionales.",
    perfil=[("Bogotá",0,2600),("Alto de Patios",12,3000),("La Calera",20,2718),("Guasca",45,2710),("Laguna Siecha",60,3650)],
    acts=[act("05:30","Salida de Bogotá","Sal muy temprano: el ingreso al parque es en la mañana y los cupos son limitados.","Bogotá","traslado"),
          act("06:15","Café en el Alto de Patios","Mirador sobre Bogotá con café y arepas.","Alto de Patios, La Calera, Cundinamarca","mirador","20 min","$12.000"),
          act("07:30","Ingreso al sector Siecha","Registro en la cabaña de Parques Nacionales y charla de seguridad. El último tramo es destapado: maneja despacio.","Laguna Siecha, Guasca, Cundinamarca","naturaleza","30 min"),
          act("08:00","Caminata a las lagunas de Siecha","Sendero de páramo entre frailejones hasta las lagunas. Es exigente por la altura: ve a tu ritmo.","Laguna Siecha, Guasca, Cundinamarca","naturaleza","3 h 30 min"),
          act("12:00","Picnic en la zona autorizada","Come en el área indicada por los guardaparques y lleva toda la basura de vuelta.","Laguna Siecha, Guasca, Cundinamarca","comida","1 h"),
          act("14:30","Guasca y la Capilla de Siecha","Pueblo con plaza tranquila; la capilla doctrinera es de las más antiguas de la región.","Guasca, Cundinamarca","pueblo","1 h"),
          act("17:00","Llegada a Bogotá","","Bogotá","traslado")],
    energia_extra=["Subida fuerte al Alto de Patios y al páramo: activa el modo de conservar batería antes de salir de Bogotá.","El tramo destapado final pide velocidad baja; el modo eléctrico es suave y silencioso ahí."],
    ideas=[("Laguna Brava","Laguna en La Calera, más cerca y de fácil acceso.","La Calera, Cundinamarca","naturaleza"),("Termales de Guasca","Piscinas termales para cerrar el día.","Guasca, Cundinamarca","descanso")],
    comida=[("Trucha","Restaurantes de la vía Guasca"),("Envueltos y amasijos","Plaza de Guasca")])

# ---------------------------------------------------------------- 3
add(nombre="Restaurante Fundo Llanero Campestre", municipio="Sabana Centro, Cundinamarca", lat=4.9021197, lng=-74.0323482,
    km=35, horas="1 h", via="Autopista Norte o Calle 80 → Chía → Cajicá", dias=1, tipo="Almuerzo campestre", frio=False,
    peajes=13000, entrada="Almuerzo llanero aprox. $45.000–$70.000 por persona",
    resumen="Plan corto de medio día: almuerzo de comida llanera en un restaurante campestre de la Sabana, con paseo por los pueblos cercanos.",
    perfil=[("Bogotá",0,2600),("Chía",25,2564),("Fundo Llanero",35,2580)],
    acts=[act("09:30","Salida de Bogotá","Plan tranquilo, sin madrugar.","Bogotá","traslado"),
          act("10:30","Paseo por Cajicá","Parque principal, tiendas de tejidos y café.","Cajicá, Cundinamarca","pueblo","1 h"),
          act("12:30","Almuerzo en Fundo Llanero Campestre","Carne a la llanera, mamona y ambiente campestre.","Restaurante Fundo Llanero Campestre, Cajicá, Cundinamarca","comida","2 h","$45.000–$70.000"),
          act("15:00","Puente del Común y Chía","Puente colonial de piedra sobre el río Bogotá, a la entrada de Chía.","Puente del Común, Chía, Cundinamarca","sitio turístico","45 min"),
          act("16:30","Regreso a Bogotá","","Bogotá","traslado")],
    energia_extra=["Recorrido corto y plano: puedes hacerlo casi todo en modo eléctrico."],
    ideas=[("Laguna de Pantano Redondo","Laguna de páramo sobre Zipaquirá.","Zipaquirá, Cundinamarca","naturaleza"),("Tabio y sus termales","Pueblo cercano con piscinas termales.","Tabio, Cundinamarca","pueblo")],
    comida=[("Carne a la llanera","Fundo Llanero Campestre"),("Postres de Chía","Panaderías del parque de Chía")])

# ---------------------------------------------------------------- 4
add(nombre="Cascada La Bota", municipio="Macanal, Boyacá", lat=4.9118102, lng=-73.3254871,
    km=165, horas="4 h", via="Sesquilé → Machetá → Guateque → Macanal (Valle de Tenza)", dias=2, tipo="Cascada", frio=False,
    peajes=25000, entrada="Ingreso por finca privada aprox. $10.000 por persona",
    resumen="Cascada en el Valle de Tenza, cerca del embalse La Esmeralda. Fin de semana de pueblos boyacenses, clima templado y agua.",
    perfil=[("Bogotá",0,2600),("Sesquilé",50,2595),("Machetá",90,2100),("Guateque",120,1815),("Macanal",160,1350)],
    acts=[act("07:00","Salida de Bogotá","Ruta de montaña por el Valle de Tenza.","Bogotá","traslado"),
          act("09:30","Desayuno en Machetá","Pueblo con aguas termales y almojábanas.","Machetá, Cundinamarca","pueblo","45 min","$20.000"),
          act("11:00","Guateque","Plaza principal y el templo de piedra, uno de los más llamativos de Boyacá.","Guateque, Boyacá","pueblo","1 h"),
          act("13:30","Llegada a Macanal y almuerzo","Almuerzo típico en el pueblo.","Macanal, Boyacá","comida","1 h","$25.000"),
          act("15:00","Cascada La Bota","Caminata corta hasta la cascada y picnic en las piedras.","Cascada la bota, Macanal, Boyacá","naturaleza","2 h"),
          act("18:00","Noche en Macanal o Santa María","Hospedajes campestres sencillos.","Macanal, Boyacá","descanso")],
    dia2=[act("08:00","Embalse La Esmeralda","Mirador sobre el embalse de Chivor, a 30 min.","La Esmeralda Dam, Santa María, Boyacá","mirador","1 h"),
          act("10:00","Regreso por el Valle de Tenza","Parada en Tenza para ver cestería en chin.","Tenza, Boyacá","pueblo","45 min"),
          act("13:00","Almuerzo en Sesquilé","","Sesquilé, Cundinamarca","comida","1 h"),
          act("15:30","Llegada a Bogotá","","Bogotá","traslado")],
    dormir=("Macanal o Santa María (hospedaje campestre)", "$120.000–$200.000"),
    energia_extra=["La ruta baja mucho hacia Macanal: la regeneración recupera batería; úsala en el regreso de subida.","Activa el modo de conservar batería antes de las subidas del regreso."],
    ideas=[("Embalse La Esmeralda","Represa de Chivor, ideal para fotos.","Santa María, Boyacá","mirador"),("Termales de Machetá","Para descansar en el camino.","Machetá, Cundinamarca","descanso")],
    comida=[("Mute boyacense","Restaurantes de Macanal"),("Almojábanas","Machetá")])

# ---------------------------------------------------------------- 5
add(nombre="Embalse La Esmeralda", municipio="Santa María, Boyacá", lat=4.900833, lng=-73.296944,
    km=180, horas="4 h 30 min", via="Sesquilé → Guateque → Macanal → Santa María", dias=2, tipo="Embalse y cascadas", frio=False,
    peajes=25000, entrada="Miradores gratis; cascadas de Santa María aprox. $10.000–$15.000",
    resumen="Embalse de Chivor rodeado de montañas verdes y Santa María, pueblo de cascadas y clima cálido. Ideal para un fin de semana de agua y naturaleza.",
    perfil=[("Bogotá",0,2600),("Sesquilé",50,2595),("Guateque",120,1815),("Macanal",160,1350),("La Esmeralda",170,1280),("Santa María",185,830)],
    acts=[act("07:00","Salida de Bogotá","","Bogotá","traslado"),
          act("10:30","Guateque y Tenza","Templo de piedra y artesanías de chin.","Guateque, Boyacá","pueblo","1 h"),
          act("13:00","Mirador del Embalse La Esmeralda","Vista amplia del embalse; buen sitio para picnic.","La Esmeralda Dam, Santa María, Boyacá","mirador","1 h 30 min"),
          act("15:30","Llegada a Santa María","Pueblo cálido, puerta al piedemonte llanero.","Santa María, Boyacá","pueblo"),
          act("19:00","Cena en el pueblo","","Santa María, Boyacá","comida","1 h","$30.000")],
    dia2=[act("08:00","Ruta de cascadas de Santa María","Cascadas como Las Lajas o La Vieja; caminata con baño en pozos.","Santa María, Boyacá","naturaleza","3 h","$15.000"),
          act("11:30","Picnic junto al río","","Santa María, Boyacá","comida","1 h"),
          act("13:00","Regreso a Bogotá","Parada en Macanal para la Cascada La Bota si hay tiempo.","Macanal, Boyacá","traslado")],
    dormir=("Santa María (hoteles y fincas)", "$120.000–$220.000"),
    energia_extra=["Ida mayormente en bajada: llegarás con más batería de la que crees.","El regreso es de subida: sal con el tanque lleno y modo de conservar batería."],
    ideas=[("Cascada La Bota","Cascada en Macanal, en el camino.","Macanal, Boyacá","naturaleza")],
    comida=[("Pescado de embalse","Restaurantes de Santa María"),("Carne a la llanera","Santa María")])

# ---------------------------------------------------------------- 6
add(nombre="Cascadas Santuario San Miguel", municipio="Acacías, Meta", lat=3.9990372, lng=-73.8141782,
    km=140, horas="3 h 30 min", via="Vía al Llano: Chipaque → Guayabetal → Villavicencio → Acacías", dias=2, tipo="Cascadas (ecoturismo)", frio=False,
    peajes=60000, entrada="Recorrido guiado Meraki Ecoturismo aprox. $40.000–$60.000 por persona (reserva previa)",
    resumen="Recorrido ecológico por cascadas y pozos de agua cristalina en el piedemonte llanero, con un fin de semana de clima cálido en el Meta.",
    perfil=[("Bogotá",0,2600),("Chipaque",30,2400),("Guayabetal",75,1000),("Villavicencio",115,467),("Acacías",140,525)],
    acts=[act("06:30","Salida de Bogotá","Revisa el estado de la vía al Llano antes de salir (cierres frecuentes).","Bogotá","traslado"),
          act("09:30","Desayuno llanero en Villavicencio","","Villavicencio, Meta","comida","45 min","$25.000"),
          act("11:00","Llegada a Acacías","Parque principal y check-in.","Acacías, Meta","pueblo"),
          act("13:00","Almuerzo","Mamona o pescado de río.","Acacías, Meta","comida","1 h","$35.000"),
          act("15:00","Parque Las Malocas o piscina","Tarde de descanso con calor.","Villavicencio, Meta","descanso","2 h")],
    dia2=[act("07:00","Cascadas Santuario San Miguel","Caminata guiada entre cascadas y pozos; lleva vestido de baño.","Cascadas santuario San Miguel - Meraki Ecoturismo, Acacías, Meta","naturaleza","4 h"),
          act("11:30","Picnic junto al agua","","Cascadas santuario San Miguel - Meraki Ecoturismo, Acacías, Meta","comida","1 h"),
          act("13:30","Regreso a Bogotá","Evita salir después de las 3 p.m. el domingo por el tráfico.","Bogotá","traslado")],
    dormir=("Acacías o Villavicencio", "$150.000–$280.000"),
    energia_extra=["La vía al Llano baja ~2.000 m: la regeneración recarga la batería en la ida.","El regreso sube todo el tiempo: tanque lleno y modo híbrido desde Villavicencio.","Los túneles largos son buenos tramos para el modo eléctrico."],
    ideas=[("Caño Cristales (temporada)","Lejos, pero vale la pena planearlo aparte.","La Macarena, Meta","naturaleza"),("Bioparque Los Ocarros","Fauna llanera en Villavicencio.","Villavicencio, Meta","naturaleza")],
    comida=[("Mamona (ternera a la llanera)","Asaderos de Villavicencio"),("Cachama asada","Restaurantes de Acacías")])

# ---------------------------------------------------------------- 7
add(nombre="Salto de las Monjas", municipio="Cachipay, Cundinamarca", lat=4.6902124, lng=-74.4404344,
    km=75, horas="2 h", via="Calle 13 → Mosquera → La Mesa → Cachipay", dias=1, tipo="Cascada", frio=False,
    peajes=13000, entrada="Ingreso aprox. $5.000–$10.000",
    resumen="Cascada en zona cafetera y de flores de Cachipay, clima templado. Día de naturaleza y pueblo con picnic.",
    perfil=[("Bogotá",0,2600),("Mosquera",20,2516),("Mondoñedo",35,2650),("La Mesa",60,1200),("Cachipay",75,1600)],
    acts=[act("07:00","Salida de Bogotá","","Bogotá","traslado"),
          act("08:45","Desayuno en La Mesa","Pueblo cálido con buena panadería y fruta.","La Mesa, Cundinamarca","pueblo","45 min","$20.000"),
          act("10:00","Salto de las Monjas","Sendero entre cafetales hasta la caída de agua.","Salto de las Monjas, Cachipay, Cundinamarca","naturaleza","2 h"),
          act("12:30","Picnic","","Salto de las Monjas, Cachipay, Cundinamarca","comida","1 h"),
          act("14:00","Cachipay, tierra de orquídeas","Parque principal y viveros de flores.","Cachipay, Cundinamarca","pueblo","1 h"),
          act("17:30","Llegada a Bogotá","","Bogotá","traslado")],
    energia_extra=["Bajada fuerte hacia La Mesa: regeneración alta.","El regreso sube a la sabana: modo híbrido desde La Mesa."],
    ideas=[("Cascada del Velo","Cascada en Bojacá, cerca de la ruta.","Bojacá, Cundinamarca","naturaleza")],
    comida=[("Sancocho","Restaurantes de La Mesa"),("Fruta tropical","Plaza de La Mesa")])

# ---------------------------------------------------------------- 8
add(nombre="Laguna de Iguaque", municipio="Villa de Leyva, Boyacá", lat=5.642778, lng=-73.564722,
    km=185, horas="4 h", via="Autopista Norte → Tunja → Villa de Leyva", dias=2, tipo="Laguna sagrada (SFF Iguaque)", frio=True,
    peajes=40000, entrada="Santuario de Flora y Fauna Iguaque con reserva previa; aprox. $30.000–$50.000 por persona",
    resumen="Laguna sagrada muisca a 3.600 m en el Santuario de Iguaque, con noche en Villa de Leyva. La caminata es exigente (4–5 h ida y vuelta).",
    perfil=[("Bogotá",0,2600),("Tocancipá",40,2605),("Chocontá",75,2655),("Tunja",145,2780),("Villa de Leyva",185,2150)],
    acts=[act("07:00","Salida de Bogotá","","Bogotá","traslado"),
          act("09:00","Desayuno en Chocontá","","Chocontá, Cundinamarca","comida","45 min","$20.000"),
          act("11:30","Puente de Boyacá","Sitio histórico de la independencia.","Puente de Boyacá, Ventaquemada, Boyacá","sitio turístico","45 min"),
          act("13:30","Llegada a Villa de Leyva","Almuerzo en la plaza empedrada.","Villa de Leyva, Boyacá","pueblo","1 h 30 min","$40.000"),
          act("16:00","Pozos Azules o el Fósil","Planes cortos cerca del pueblo.","Pozos Azules, Villa de Leyva, Boyacá","naturaleza","1 h 30 min","$10.000"),
          act("19:00","Cena y descanso temprano","Mañana se madruga.","Villa de Leyva, Boyacá","comida")],
    dia2=[act("06:30","Caminata a la Laguna de Iguaque","Desde la cabaña del santuario; subida por bosque de niebla y páramo.","Lake Iguaque, Villa de Leyva, Boyacá","naturaleza","5 h"),
          act("10:00","Picnic en la laguna","Come en silencio: es un lugar sagrado para los muiscas.","Lake Iguaque, Villa de Leyva, Boyacá","comida","45 min"),
          act("13:00","Almuerzo y regreso","Sal antes de las 2 p.m. para llegar de día.","Villa de Leyva, Boyacá","traslado")],
    dormir=("Villa de Leyva (centro histórico)", "$180.000–$350.000"),
    energia_extra=["Autopista Norte y Tunja: modo híbrido a velocidad constante (90–100 km/h).","En Villa de Leyva el pueblo es pequeño: muévete en modo eléctrico."],
    ideas=[("Ráquira","Pueblo de artesanías en barro, a 30 min.","Ráquira, Boyacá","pueblo"),("Desierto de La Candelaria","Paisaje árido y monasterio.","Ráquira, Boyacá","naturaleza")],
    comida=[("Cuchuco de trigo","Restaurantes de Villa de Leyva"),("Postres de Villa","Plaza mayor")])

# ---------------------------------------------------------------- 9
add(nombre="Laguna de Fúquene", municipio="Fúquene, Cundinamarca", lat=5.4567661, lng=-73.7419017,
    km=115, horas="2 h 30 min", via="Autopista Norte → Zipaquirá → Ubaté → Fúquene", dias=1, tipo="Laguna y aves", frio=True,
    peajes=30000, entrada="Paseos en lancha aprox. $15.000–$25.000 por persona",
    resumen="Laguna grande del altiplano con totorales, aves y paseos en lancha. Picnic en la orilla y pueblos lecheros.",
    perfil=[("Bogotá",0,2600),("Zipaquirá",45,2650),("Ubaté",100,2556),("Fúquene",115,2550)],
    acts=[act("07:00","Salida de Bogotá","","Bogotá","traslado"),
          act("09:00","Desayuno en Ubaté","Queso, almojábana y kumis.","Ubaté, Cundinamarca","pueblo","45 min","$20.000"),
          act("10:00","Laguna de Fúquene","Paseo en lancha entre totorales y observación de aves.","Lake Fúquene, Fúquene, Cundinamarca","naturaleza","1 h 30 min","$20.000"),
          act("12:30","Picnic en la orilla","","Lake Fúquene, Fúquene, Cundinamarca","comida","1 h 30 min"),
          act("14:30","Susa y la Laguna de Cucunubá","Pueblos cercanos con miradores.","Cucunubá, Cundinamarca","pueblo","1 h"),
          act("18:00","Llegada a Bogotá","","Bogotá","traslado")],
    energia_extra=["Ruta mayormente plana: el modo híbrido gasta poco y mantiene la batería."],
    ideas=[("Embalse El Hato","Páramo y embalse en Carmen de Carupa.","Carmen de Carupa, Cundinamarca","naturaleza")],
    comida=[("Queso de Ubaté","Ubaté"),("Pescado capitán","Restaurantes de Fúquene")])

# ---------------------------------------------------------------- 10
add(nombre="Laguna Verde", municipio="Tausa, Cundinamarca", lat=5.2152778, lng=-73.9991667,
    km=85, horas="2 h", via="Autopista Norte → Zipaquirá → Cogua → Tausa", dias=1, tipo="Laguna de páramo", frio=True,
    peajes=13000, entrada="Ingreso aprox. $5.000–$10.000 (predio rural)",
    resumen="Laguna de color esmeralda en el páramo de Tausa, poco concurrida. Caminata corta y picnic frío entre frailejones.",
    perfil=[("Bogotá",0,2600),("Zipaquirá",45,2650),("Cogua",55,2600),("Tausa",75,2931),("Laguna Verde",85,3200)],
    acts=[act("07:00","Salida de Bogotá","","Bogotá","traslado"),
          act("08:30","Desayuno en Zipaquirá","Plaza de los Comuneros.","Zipaquirá, Cundinamarca","pueblo","45 min","$20.000"),
          act("10:00","Laguna Verde","Caminata por el páramo hasta la laguna; el último tramo es destapado.","Laguna Verde, Tausa, Cundinamarca","naturaleza","2 h"),
          act("12:30","Picnic en el páramo","Abrígate: el viento es frío.","Laguna Verde, Tausa, Cundinamarca","comida","1 h"),
          act("14:30","Embalse del Neusa","Bosque de pinos y orilla del embalse en el regreso.","Embalse del Neusa, Cogua, Cundinamarca","naturaleza","1 h 30 min","$10.000"),
          act("17:30","Llegada a Bogotá","","Bogotá","traslado")],
    energia_extra=["Subida al páramo: activa el modo de conservar batería después de Zipaquirá."],
    ideas=[("Embalse del Neusa","Parque con zonas de picnic y pesca.","Cogua, Cundinamarca","naturaleza"),("Farallones de Sutatausa","Muy cerca de Tausa.","Sutatausa, Cundinamarca","naturaleza")],
    comida=[("Trucha","Restaurantes del Neusa"),("Fritanga","Zipaquirá")])

# ---------------------------------------------------------------- 11
add(nombre="Laguna Brava", municipio="La Calera, Cundinamarca", lat=4.6822222, lng=-73.8502778,
    km=35, horas="1 h 15 min", via="Vía La Calera (Alto de Patios) → La Calera", dias=1, tipo="Laguna de páramo", frio=True,
    peajes=0, entrada="Ingreso aprox. $10.000 (predio privado)",
    resumen="Laguna de páramo muy cerca de Bogotá. Plan corto de naturaleza con picnic y miradores de La Calera.",
    perfil=[("Bogotá",0,2600),("Alto de Patios",12,3000),("La Calera",20,2718),("Laguna Brava",35,3100)],
    acts=[act("07:30","Salida de Bogotá","","Bogotá","traslado"),
          act("08:00","Café en el Alto de Patios","","Alto de Patios, La Calera, Cundinamarca","mirador","20 min","$12.000"),
          act("09:00","Laguna Brava","Caminata corta alrededor de la laguna.","Laguna Brava, La Calera, Cundinamarca","naturaleza","2 h"),
          act("11:30","Picnic","","Laguna Brava, La Calera, Cundinamarca","comida","1 h"),
          act("13:30","Miradores de La Calera","Vista sobre Bogotá y el embalse de San Rafael.","Embalse de San Rafael, La Calera, Cundinamarca","mirador","1 h"),
          act("15:30","Regreso a Bogotá","","Bogotá","traslado")],
    energia_extra=["Ruta corta pero empinada: con la batería al 100 % puedes hacerla casi toda en eléctrico."],
    ideas=[("Laguna Siecha","Lagunas de Chingaza, a 1 h más.","Guasca, Cundinamarca","naturaleza")],
    comida=[("Arepas y café","Alto de Patios")])

# ---------------------------------------------------------------- 12
add(nombre="Laguna de Guatavita", municipio="Sesquilé, Cundinamarca", lat=4.9775, lng=-73.7755556,
    km=65, horas="1 h 30 min", via="Autopista Norte → Sopó → Sesquilé", dias=1, tipo="Laguna sagrada muisca", frio=True,
    peajes=13000, entrada="Reserva previa; aprox. $25.000 por persona (recorrido guiado)",
    resumen="La laguna de la leyenda de El Dorado, con recorrido guiado por senderos de bosque andino. Picnic y el pueblo de Guatavita junto al embalse de Tominé.",
    perfil=[("Bogotá",0,2600),("Sopó",35,2650),("Sesquilé",55,2595),("Laguna de Guatavita",65,3000)],
    acts=[act("07:00","Salida de Bogotá","","Bogotá","traslado"),
          act("08:30","Recorrido guiado a la Laguna de Guatavita","Sendero de 1,5 h con historia muisca y miradores.","Laguna Guatavita, Sesquilé, Cundinamarca","naturaleza","2 h","$25.000"),
          act("11:30","Picnic en la zona de visitantes","","Laguna Guatavita, Sesquilé, Cundinamarca","comida","1 h"),
          act("13:30","Pueblo de Guatavita","Pueblo blanco junto al embalse de Tominé.","Guatavita, Cundinamarca","pueblo","1 h 30 min"),
          act("15:30","Postre en Sopó","Alpina y el parque principal.","Sopó, Cundinamarca","pueblo","45 min"),
          act("17:00","Llegada a Bogotá","","Bogotá","traslado")],
    energia_extra=["Ruta plana hasta Sesquilé: modo eléctrico o híbrido; la subida final es corta."],
    ideas=[("Embalse de Tominé","Deportes náuticos y miradores.","Guatavita, Cundinamarca","naturaleza")],
    comida=[("Postres y yogur","Sopó"),("Trucha","Guatavita")])

# ---------------------------------------------------------------- 13
add(nombre="Laguna de Pantano Redondo", municipio="Zipaquirá, Cundinamarca", lat=5.0449485, lng=-74.0344188,
    km=55, horas="1 h 30 min", via="Autopista Norte → Zipaquirá → vereda Pantano Redondo", dias=1, tipo="Laguna de páramo", frio=True,
    peajes=13000, entrada="Ingreso aprox. $10.000–$15.000 (reserva natural)",
    resumen="Laguna de páramo sobre Zipaquirá con senderos entre frailejones, combinable con la Catedral de Sal.",
    perfil=[("Bogotá",0,2600),("Chía",25,2564),("Zipaquirá",45,2650),("Pantano Redondo",55,3250)],
    acts=[act("07:00","Salida de Bogotá","","Bogotá","traslado"),
          act("08:30","Laguna de Pantano Redondo","Caminata por el páramo hasta la laguna.","Laguna De Pantano Redondo, Zipaquirá, Cundinamarca","naturaleza","2 h 30 min"),
          act("11:30","Picnic con vista","","Laguna De Pantano Redondo, Zipaquirá, Cundinamarca","comida","1 h"),
          act("13:30","Catedral de Sal","Recorrido subterráneo por la mina de sal.","Catedral de Sal, Zipaquirá, Cundinamarca","sitio turístico","2 h","$100.000"),
          act("16:00","Centro histórico de Zipaquirá","Plaza de los Comuneros y café.","Zipaquirá, Cundinamarca","pueblo","1 h"),
          act("18:00","Llegada a Bogotá","","Bogotá","traslado")],
    energia_extra=["La subida a la vereda es corta y empinada; el resto es plano: ideal para modo eléctrico."],
    ideas=[("Laguna Verde de Tausa","Más páramo, a 40 min.","Tausa, Cundinamarca","naturaleza")],
    comida=[("Fritanga","Zipaquirá"),("Mantecada","Panaderías de Zipaquirá")])

# ---------------------------------------------------------------- 14
add(nombre="Cascada del Velo", municipio="Bojacá, Cundinamarca", lat=4.689835, lng=-74.358564,
    km=50, horas="1 h 30 min", via="Calle 13 → Mosquera → Madrid → Bojacá", dias=1, tipo="Cascada", frio=True,
    peajes=13000, entrada="Ingreso aprox. $5.000–$10.000",
    resumen="Cascada cercana en Bojacá, con caminata corta y picnic; se combina con el santuario del pueblo.",
    perfil=[("Bogotá",0,2600),("Mosquera",20,2516),("Madrid",30,2554),("Bojacá",45,2598),("Cascada del Velo",50,2700)],
    acts=[act("08:00","Salida de Bogotá","","Bogotá","traslado"),
          act("09:30","Cascada del Velo","Sendero corto hasta la caída de agua.","Cascada Del Velo, Bojacá, Cundinamarca","naturaleza","2 h"),
          act("12:00","Picnic","","Cascada Del Velo, Bojacá, Cundinamarca","comida","1 h"),
          act("13:30","Santuario del Señor de la Salud","Templo de peregrinación en el centro de Bojacá.","Bojacá, Cundinamarca","pueblo","45 min"),
          act("14:30","Mirador de Zipacón","Pueblo con vista al valle.","Zipacón, Cundinamarca","mirador","1 h"),
          act("16:30","Llegada a Bogotá","","Bogotá","traslado")],
    energia_extra=["Ruta plana y corta: puedes hacerla completa en modo eléctrico."],
    ideas=[("Salto de las Monjas","Cascada de clima templado más adelante.","Cachipay, Cundinamarca","naturaleza")],
    comida=[("Envueltos de mazorca","Plaza de Bojacá")])

# ---------------------------------------------------------------- 15
add(nombre="Cascada El Hoyo", municipio="Granada, Cundinamarca", lat=4.5384143, lng=-74.3575854,
    km=50, horas="1 h 30 min", via="Autopista Sur → Soacha → Sibaté → Granada", dias=1, tipo="Cascada", frio=True,
    peajes=0, entrada="Ingreso aprox. $5.000–$10.000",
    resumen="Cascada escondida en un cañón de Granada, con bosque andino. Plan de un día con picnic y paso por Sibaté.",
    perfil=[("Bogotá",0,2600),("Soacha",15,2565),("Sibaté",30,2700),("Granada",45,2500),("Cascada El Hoyo",50,2300)],
    acts=[act("07:30","Salida de Bogotá","Sal temprano para evitar la Autopista Sur.","Bogotá","traslado"),
          act("08:30","Desayuno en Sibaté","Embalse del Muña y el pueblo.","Sibaté, Cundinamarca","pueblo","45 min","$20.000"),
          act("10:00","Cascada El Hoyo","Bajada por sendero al cañón; usa calzado con buen agarre.","Cascada El Hoyo, Granada, Cundinamarca","naturaleza","2 h 30 min"),
          act("12:45","Picnic","","Cascada El Hoyo, Granada, Cundinamarca","comida","1 h"),
          act("14:30","Pueblo de Granada","Parque y miradores.","Granada, Cundinamarca","pueblo","45 min"),
          act("16:30","Llegada a Bogotá","","Bogotá","traslado")],
    energia_extra=["Ruta corta: con la batería llena alcanza en eléctrico casi toda."],
    ideas=[("Salto del Tequendama","Mirador y Casa Museo, cerca de la ruta.","Soacha, Cundinamarca","sitio turístico")],
    comida=[("Postres de leche","Sibaté")])

# ---------------------------------------------------------------- 16
add(nombre="Cascadas del Chupal", municipio="La Vega, Cundinamarca", lat=5.0467457, lng=-74.3101127,
    km=60, horas="1 h 45 min", via="Calle 80 → Siberia → El Rosal → La Vega", dias=1, tipo="Cascadas", frio=False,
    peajes=26000, entrada="Manai Cascadas del Chupal aprox. $15.000–$30.000 por persona",
    resumen="Recorrido por varias cascadas con pozos en clima templado. Día de agua, sol y picnic.",
    perfil=[("Bogotá",0,2600),("Siberia",15,2560),("El Rosal",25,2685),("La Vega",55,1230),("Cascadas del Chupal",60,1500)],
    acts=[act("07:00","Salida de Bogotá","","Bogotá","traslado"),
          act("08:30","Desayuno en La Vega","","La Vega, Cundinamarca","pueblo","45 min","$20.000"),
          act("09:30","Cascadas del Chupal","Caminata entre cascadas con baño en pozos; lleva vestido de baño.","Chupal Falls, La Vega, Cundinamarca","naturaleza","3 h","$20.000"),
          act("12:45","Picnic","","Chupal Falls, La Vega, Cundinamarca","comida","1 h"),
          act("14:30","Laguna El Tabacal","Reserva natural con laguna y bosque.","Laguna El Tabacal, La Vega, Cundinamarca","naturaleza","1 h 30 min","$10.000"),
          act("17:30","Regreso a Bogotá","Sal antes de las 5 p.m. el domingo por el tráfico de la Calle 80.","Bogotá","traslado")],
    energia_extra=["Bajada de 1.400 m hacia La Vega: regeneración alta en la ida.","El regreso es de subida: modo híbrido desde La Vega."],
    ideas=[("Laguna El Tabacal","Reserva natural muy cerca.","La Vega, Cundinamarca","naturaleza"),("Villeta","Pueblo cálido con piscinas.","Villeta, Cundinamarca","pueblo")],
    comida=[("Bocadillo y fruta","Puestos de la vía"),("Sancocho","La Vega")])

# ---------------------------------------------------------------- 17
add(nombre="Cascada de Sueva", municipio="Junín, Cundinamarca", lat=4.8107153, lng=-73.7333116,
    km=100, horas="2 h 30 min", via="La Calera → Guasca → Junín → Sueva", dias=1, tipo="Cascada de bosque", frio=True,
    peajes=0, entrada="Ingreso aprox. $10.000 por persona",
    resumen="Cascada en bosque húmedo andino, cerca del límite de Chingaza. Ruta de montaña con pueblos tranquilos.",
    perfil=[("Bogotá",0,2600),("Alto de Patios",12,3000),("La Calera",20,2718),("Guasca",45,2710),("Junín",90,2300),("Sueva",100,2000)],
    acts=[act("06:30","Salida de Bogotá","","Bogotá","traslado"),
          act("07:30","Desayuno en Guasca","","Guasca, Cundinamarca","pueblo","45 min","$20.000"),
          act("10:00","Cascada de Sueva","Sendero por bosque húmedo hasta la cascada.","Cascada de Sueva Nemosten, Junín, Cundinamarca","naturaleza","2 h 30 min"),
          act("12:45","Picnic","","Cascada de Sueva Nemosten, Junín, Cundinamarca","comida","1 h"),
          act("14:15","Pueblo de Junín","Plaza y artesanías.","Junín, Cundinamarca","pueblo","45 min"),
          act("18:00","Llegada a Bogotá","","Bogotá","traslado")],
    energia_extra=["Ruta de montaña con subidas y bajadas: modo híbrido y regeneración alta en las bajadas."],
    ideas=[("Laguna Siecha","Lagunas de Chingaza en el camino.","Guasca, Cundinamarca","naturaleza")],
    comida=[("Trucha","Restaurantes de Guasca")])

# ---------------------------------------------------------------- 18
add(nombre="Cascada Caída del Dragón", municipio="Jardín, Antioquia", lat=5.62431, lng=-75.78788,
    km=500, horas="10 h", via="Honda → Manizales → Riosucio → Jardín", dias=5, tipo="Cascada y pueblo patrimonio", frio=False,
    peajes=180000, entrada="Recorrido a la Caída del Dragón aprox. $20.000–$40.000",
    resumen="Viaje largo a Jardín, uno de los pueblos más bonitos de Antioquia, con la cascada Caída del Dragón y paradas en Honda y Manizales.",
    perfil=[("Bogotá",0,2600),("Alto del Trigo",90,2400),("Honda",150,229),("Fresno",210,1478),("Manizales",300,2150),("Riosucio",390,1783),("Jardín",500,1750)],
    acts=[act("06:00","Salida de Bogotá","Día largo de carretera.","Bogotá","traslado"),
          act("09:30","Honda, ciudad de los puentes","Centro histórico y el río Magdalena.","Honda, Tolima","pueblo","1 h 30 min"),
          act("13:00","Almuerzo en Fresno","","Fresno, Tolima","comida","1 h","$30.000"),
          act("16:30","Llegada a Manizales","Atardecer en el Cable Aéreo o la Catedral.","Manizales, Caldas","sitio turístico","2 h")],
    dias_extra=[
        ("Manizales → Jardín", [act("08:00","Salida a Jardín","Vía por Riosucio y el occidente de Caldas.","Manizales, Caldas","traslado"),
          act("11:00","Riosucio","Pueblo del Carnaval del Diablo.","Riosucio, Caldas","pueblo","45 min"),
          act("14:00","Llegada a Jardín","Plaza con sillas de colores y la basílica.","Jardín, Antioquia","pueblo","2 h"),
          act("17:00","Garrucha al Cerro Cristo Rey","Mirador sobre el pueblo.","Jardín, Antioquia","mirador","1 h","$10.000")], ("Jardín (centro)","$150.000–$280.000")),
        ("Caída del Dragón", [act("08:00","Caída del Dragón","Caminata por la montaña hasta la cascada que cae dentro de una cueva.","Cascada Caida del Dragon, Jardín, Antioquia","naturaleza","4 h","$30.000"),
          act("12:30","Picnic con vista","","Cascada Caida del Dragon, Jardín, Antioquia","comida","1 h"),
          act("15:00","Charco Corazón","Pozo de agua natural cerca del pueblo.","Charco Corazón, Jardín, Antioquia","naturaleza","1 h 30 min")], ("Jardín (centro)","$150.000–$280.000")),
        ("Jardín → Manizales", [act("09:00","Regreso hacia Manizales","","Jardín, Antioquia","traslado"),
          act("14:00","Termales en Manizales","Descanso después del viaje.","Termales del Otoño, Manizales, Caldas","descanso","2 h","$60.000")], ("Manizales","$150.000–$250.000")),
        ("Manizales → Bogotá", [act("07:00","Regreso a Bogotá","Parada para almorzar en Honda.","Honda, Tolima","traslado"),
          act("16:00","Llegada a Bogotá","","Bogotá","traslado")], None)],
    dormir=("Manizales","$150.000–$250.000"),
    energia_extra=["Ruta con desniveles enormes (Bogotá 2.600 m → Honda 230 m → Manizales 2.150 m): regeneración alta en cada bajada.","Llena el tanque en Honda y en Manizales: hay tramos largos de montaña."],
    ideas=[("Cueva del Esplendor","Cascada dentro de una cueva, cerca de Jardín.","Jardín, Antioquia","naturaleza")],
    comida=[("Trucha","Restaurantes de Jardín"),("Bandeja paisa","Plaza de Jardín")])

# ---------------------------------------------------------------- 19
add(nombre="Farallones de Sutatausa", municipio="Sutatausa, Cundinamarca", lat=5.2144376, lng=-73.8495843,
    km=85, horas="2 h", via="Autopista Norte → Zipaquirá → vía a Ubaté → Sutatausa", dias=1, tipo="Formaciones rocosas", frio=True,
    peajes=26000, entrada="Ingreso aprox. $10.000–$15.000 (con guía local)",
    resumen="Paredes de roca con miradores, senderos y pictografías muiscas. Caminata con picnic y pueblo colonial.",
    perfil=[("Bogotá",0,2600),("Zipaquirá",45,2650),("Sutatausa",80,2550),("Farallones",85,2900)],
    acts=[act("07:00","Salida de Bogotá","","Bogotá","traslado"),
          act("09:00","Pueblo de Sutatausa","Templo doctrinero con pinturas murales coloniales.","Sutatausa, Cundinamarca","pueblo","45 min"),
          act("10:00","Caminata a los Farallones","Senderos con miradores y pictografías; mejor con guía local.","Farallones De Sutatausa, Sutatausa, Cundinamarca","naturaleza","2 h 30 min","$15.000"),
          act("12:45","Picnic en el mirador","","Farallones De Sutatausa, Sutatausa, Cundinamarca","comida","1 h"),
          act("14:30","Ubaté","Basílica y productos lácteos.","Ubaté, Cundinamarca","pueblo","1 h"),
          act("17:30","Llegada a Bogotá","","Bogotá","traslado")],
    energia_extra=["Ruta plana por la autopista; la subida a los farallones es corta."],
    ideas=[("Laguna Verde","Laguna de páramo en Tausa, muy cerca.","Tausa, Cundinamarca","naturaleza"),("Laguna de Fúquene","A 30 min de Ubaté.","Fúquene, Cundinamarca","naturaleza")],
    comida=[("Queso y kumis","Ubaté")])

FLAGS = {'Laguna Siecha': (True, True), 'Laguna de Guatavita': (True, False), 'Laguna de Iguaque': (True, False), 'Cascadas Santuario San Miguel': (True, False), 'Laguna Verde': (False, True), 'Cascada El Hoyo': (False, False), 'Laguna de Pantano Redondo': (False, True), 'Laguna Brava': (False, True)}

def build(r):
    q = lambda n, m: f"{n}, {m}"
    destino = r["municipio"].split(",")[0]
    tramo_ida = {"desde": "Bogotá", "hasta": destino, "km": r["km"], "horas": r["horas"]}
    perfil = [{"lugar": l, "km": k, "altitud_m": a} for l, k, a in r["perfil"]]
    perfil_vuelta = [{"lugar": l, "km": r["km"] - k, "altitud_m": a} for l, k, a in reversed(r["perfil"])]
    dias = []
    if r["dias"] == 1:
        dias.append({"titulo": f"Bogotá → {r['nombre']} → Bogotá", "tramo": tramo_ida, "perfil": perfil, "actividades": r["acts"], "dormir": None})
    else:
        dor = r.get("dormir")
        dias.append({"titulo": f"Bogotá → {destino}", "tramo": tramo_ida, "perfil": perfil, "actividades": r["acts"],
                     "dormir": {"donde": dor[0], "por_que": "Para no manejar de noche y aprovechar el día siguiente.", "rango_noche": dor[1]} if dor else None})
        if r.get("dias_extra"):
            for i, (tit, acts, dd) in enumerate(r["dias_extra"]):
                last = i == len(r["dias_extra"]) - 1
                d = {"titulo": tit, "tramo": None, "perfil": [], "actividades": acts, "dormir": {"donde": dd[0], "por_que": "", "rango_noche": dd[1]} if dd else None}
                if " → " in tit and not last:
                    a, b = tit.split(" → ")
                    d["tramo"] = {"desde": a, "hasta": b, "km": 200, "horas": "4 h 30 min"}
                if last:
                    d["tramo"] = {"desde": "Manizales", "hasta": "Bogotá", "km": 300, "horas": "7 h"}
                    d["perfil"] = [{"lugar": "Manizales", "km": 0, "altitud_m": 2150}, {"lugar": "Fresno", "km": 90, "altitud_m": 1478}, {"lugar": "Honda", "km": 150, "altitud_m": 229}, {"lugar": "Alto del Trigo", "km": 210, "altitud_m": 2400}, {"lugar": "Bogotá", "km": 300, "altitud_m": 2600}]
                dias.append(d)
        else:
            dias.append({"titulo": f"{r['nombre']} y regreso", "tramo": {"desde": destino, "hasta": "Bogotá", "km": r["km"], "horas": r["horas"]},
                         "perfil": perfil_vuelta, "actividades": r["dia2"], "dormir": None})
    for di, d in enumerate(dias):
        d["id"] = f"{slug(r['nombre'])[:24]}-d{di + 1}"
        for ai, a in enumerate(d["actividades"]):
            a["id"] = f"{d['id']}-a{ai + 1}"
    km_total = r["km"] * 2 if r["dias"] < 5 else 1200
    noches = r["dias"] - 1
    presupuesto = [
        {"concepto": "Energía y gasolina (ida y vuelta)", "detalle": (lambda e: f"~{km_total} km: {e['kwh']:.0f} kWh de la batería (~$800/kWh en casa)" + (f" + {dec(e['gal'])} gal (~$16.000/gal)" if e['gal'] > 0 else ""))(estimar(km_total)), "total": estimar(km_total)["costo"]},
        {"concepto": "Peajes (ida y vuelta)", "detalle": "Automóvil categoría I, aprox.", "total": r["peajes"] * 2},
        {"concepto": "Entradas y actividades", "detalle": r["entrada"], "total": 30000 * 2 if r["dias"] == 1 else 50000 * 2},
        {"concepto": "Comida del picnic", "detalle": "Mercado para 2 personas", "total": 60000 * r["dias"]},
        {"concepto": "Comidas en ruta", "detalle": "Desayunos y almuerzos, 2 personas", "total": 70000 * r["dias"]},
    ]
    if noches:
        lo = int(re.sub(r"\D", "", (r.get("dormir") or ("", "$150.000"))[1].split("–")[0]) or 150000)
        presupuesto.append({"concepto": f"Hospedaje {noches} {'noche' if noches == 1 else 'noches'}", "detalle": "Habitación doble, aprox.", "total": lo * noches})
    for i, x in enumerate(presupuesto): x["id"] = f"p{i}"
    plan = {
        "titulo": r["nombre"], "resumen": r["resumen"], "moneda": "COP",
        "clima": {"resumen": "Clima frío de montaña; puede llover en la tarde." if r["frio"] else "Clima templado o cálido; lleva ropa ligera y algo para la lluvia.",
                  "temperatura": "8–16 °C" if r["frio"] else "18–28 °C", "que_llevar": PICNIC + (FRIO if r["frio"] else CALOR)},
        "dias": dias,
        "mas_ideas": [{"id": f"i{i}", "titulo": t, "detalle": d, "lugar": l, "tipo": ty} for i, (t, d, l, ty) in enumerate(r["ideas"])],
        "gastronomia": [{"plato": p, "detalle": "", "donde": w} for p, w in r["comida"]],
        "presupuesto": presupuesto,
        "consejos": [f"Ruta: {r['via']}.", r["entrada"] + ". Confirma precios y horarios antes de ir.",
                     "Sal temprano los fines de semana y festivos para evitar los trancones de salida y regreso.",
                     "No dejes basura en los sitios naturales y respeta las zonas de picnic autorizadas."],
        "energia": energia(r["energia_extra"], km_total),
    }
    flags = FLAGS.get(r["nombre"], (False, False))
    return {"id": "picnic-" + slug(r["nombre"]), "nombre": r["nombre"], "reserva": flags[0], "destapado": flags[1], "entrada": r["entrada"], "municipio": r["municipio"], "lat": r["lat"], "lng": r["lng"],
            "km": r["km"], "horas": r["horas"], "dias": r["dias"], "tipo": r["tipo"], "plan": plan}

out = [build(r) for r in R]
json.dump(out, open("data/rutas-picnic.json", "w", encoding="utf-8"), ensure_ascii=False, separators=(",", ":"))
print(len(out), "rutas")

# Incrustar en la página (single-file) entre marcadores.
html_path = "artifact/planificador.html"
html = open(html_path, encoding="utf-8").read()
blob = json.dumps(out, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")
start, end = '<script id="rutas-picnic" type="application/json">', "</script><!-- /rutas-picnic -->"
block = start + blob + end
if start in html:
    a = html.index(start); b = html.index(end, a) + len(end)
    html = html[:a] + block + html[b:]
else:
    html = html.replace('<div id="tip" hidden></div>', block + '\n<div id="tip" hidden></div>', 1)
open(html_path, "w", encoding="utf-8").write(html)
print("incrustado en", html_path)
