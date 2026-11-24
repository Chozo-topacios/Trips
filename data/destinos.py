# Genera los viajes sugeridos de Leonardo (avión) y los incrusta en la página.
# Cifras aproximadas en COP para 3 viajeros (2 adultos y una niña de 9 años).
import json, re, unicodedata

def slug(s):
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode().lower()
    return re.sub(r"[^a-z0-9]+", "-", s).strip("-")

def act(hora, titulo, detalle, lugar, tipo, duracion="", costo=""):
    return {"hora": hora, "titulo": titulo, "detalle": detalle, "lugar": lugar, "tipo": tipo, "duracion": duracion, "costo": costo}

def dia(titulo, acts, dormir=None):
    return {"titulo": titulo, "tramo": None, "perfil": [], "actividades": acts,
            "dormir": {"donde": dormir[0], "por_que": dormir[1], "rango_noche": dormir[2]} if dormir else None}

D = []

# ------------------------------------------------------------------ Chile: ski en familia
D.append({
  "nombre": "Chile: ski en familia", "destino": "Santiago y Valle Nevado, Chile", "dias": 7, "viajeros": 3,
  "descripcion": "2 adultos y una niña de 9 años; primera vez en la nieve, con clases de ski para la niña.",
  "fechas": {"meses": ["evitar","evitar","evitar","evitar","evitar","buena","alta","mejor","mejor","evitar","evitar","evitar"],
             "recomendadas": "Del 22 al 28 de agosto", "inicio": "2027-08-22",
             "por_que": "En agosto la nieve está en su mejor momento y ya pasaron las vacaciones de invierno chilenas (mediados de julio), así que hay menos gente y los precios bajan. Septiembre también sirve y es más barato, con nieve de primavera.",
             "evitar": "Mediados de julio: vacaciones escolares en Chile, pistas llenas y todo más caro. Antes de mediados de junio puede no haber nieve suficiente."},
  "plan": {
    "titulo": "Chile: nieve, ski y cordillera en familia",
    "resumen": "Una semana con dos días de ski en Valle Nevado (con escuela para la niña), juego en la nieve en Farellones, Santiago a escala de niños y un día en Valparaíso.",
    "moneda": "COP",
    "clima": {"resumen": "Invierno: en Santiago 3–15 °C y seco; en la montaña (2.800–3.600 m) bajo cero y con viento.", "temperatura": "-8 a 15 °C",
              "que_llevar": ["Primera capa térmica (camiseta y licra)", "Chaqueta y pantalón impermeables (o arrendarlos)", "Guantes impermeables y de repuesto",
                             "Gorro, cuello y gafas de sol o antiparras", "Bloqueador alto y protector labial", "Medias gruesas de lana (2 pares por día)",
                             "Botas impermeables para la nieve", "Pasaportes o documentos de los tres", "Permiso de salida de la niña si viaja con un solo padre", "Snacks y termo"]},
    "dias": [
      dia("Bogotá → Santiago", [
        act("08:00", "Vuelo Bogotá → Santiago", "Vuelo directo de unas 6 h. Lleva abrigo a mano: aterrizas en pleno invierno.", "Aeropuerto El Dorado, Bogotá", "traslado", "6 h"),
        act("15:30", "Llegada y traslado a Las Condes", "Quedarse en Las Condes acorta mucho el camino a la montaña cada mañana.", "Las Condes, Santiago", "traslado", "45 min"),
        act("17:30", "Arriendo de ropa de nieve", "Prueba chaquetas, pantalones y botas para los tres; muchas tiendas de Las Condes arriendan por día y entregan todo listo.", "Las Condes, Santiago", "compras", "1 h 30 min", "$40.000 por persona/día"),
        act("19:30", "Cena temprana", "Pastel de choclo o empanadas de pino; mañana se madruga.", "Las Condes, Santiago", "comida", "1 h")],
        ("Las Condes", "cerca de la vía a Farellones", "$350.000–$500.000")),
      dia("Primer día en la nieve: Valle Nevado", [
        act("07:00", "Traslado a la montaña", "Camino de curvas (las «40 curvas») hasta 3.000 m. Mejor en transfer o tour: si arriendas carro, exigen cadenas y 4x4 según el día.", "Farellones, Chile", "traslado", "1 h 30 min", "$90.000 por persona ida y vuelta"),
        act("09:00", "Arriendo de equipo y escuela de ski", "Esquís, botas y casco para los tres. La niña entra a la escuela de ski infantil (grupos por edad) mientras ustedes toman su clase.", "Valle Nevado, Chile", "aventura", "3 h", "Clase niños aprox. $250.000"),
        act("12:30", "Almuerzo en la montaña", "Comida caliente en el centro de ski; hidrátense mucho por la altura.", "Valle Nevado, Chile", "comida", "1 h"),
        act("14:00", "Pistas verdes en familia", "Practiquen juntos lo aprendido en las pistas para principiantes.", "Valle Nevado, Chile", "aventura", "2 h"),
        act("16:30", "Regreso a Santiago", "Baja antes de las 17:00: el tránsito de bajada se controla por horarios.", "Las Condes, Santiago", "traslado", "1 h 30 min"),
        act("19:30", "Descanso", "Día largo y con altura: cena liviana y a dormir temprano.", "Las Condes, Santiago", "descanso")],
        ("Las Condes", "", "$350.000–$500.000")),
      dia("Ski y juego en la nieve: Farellones", [
        act("07:30", "Traslado a Farellones", "", "Farellones, Chile", "traslado", "1 h 15 min"),
        act("09:00", "Segundo día de ski en El Colorado", "Con un día de práctica ya se disfruta más. La niña puede repetir clase en la mañana.", "El Colorado, Farellones, Chile", "aventura", "3 h"),
        act("12:30", "Almuerzo", "", "Farellones, Chile", "comida", "1 h"),
        act("13:30", "Parque de nieve: trineos y tubing", "Zona de juegos en la nieve, ideal para la niña: bajar en neumático, trineos y hacer muñecos.", "Farellones, Chile", "naturaleza", "2 h", "aprox. $60.000 por persona"),
        act("16:30", "Regreso a Santiago", "", "Las Condes, Santiago", "traslado", "1 h 15 min")],
        ("Las Condes", "", "$350.000–$500.000")),
      dia("Santiago para niños", [
        act("10:00", "Teleférico y funicular del Cerro San Cristóbal", "Vista de toda la ciudad con la cordillera nevada detrás.", "Parque Metropolitano, Santiago", "mirador", "2 h", "aprox. $15.000 por persona"),
        act("12:30", "Almuerzo en Bellavista", "", "Barrio Bellavista, Santiago", "comida", "1 h"),
        act("14:00", "Museo Interactivo Mirador (MIM)", "Museo de ciencia para tocar y experimentar: perfecto para una niña de 9 años.", "Museo Interactivo Mirador, La Granja, Santiago", "cultura", "2 h 30 min", "aprox. $20.000 por persona"),
        act("18:00", "Atardecer en el Sky Costanera", "Mirador en el piso 62 del edificio más alto de Sudamérica.", "Sky Costanera, Providencia, Santiago", "sitio turístico", "1 h", "aprox. $70.000 por persona")],
        ("Las Condes", "", "$350.000–$500.000")),
      dia("Cajón del Maipo", [
        act("08:30", "Tour al Cajón del Maipo", "Valle de montaña con ríos y pueblos; en invierno, nieve en las partes altas. Mejor en tour: el acceso al Embalse El Yeso se cierra con mucha nieve.", "San José de Maipo, Chile", "naturaleza", "1 h 30 min", "Tour aprox. $250.000 por persona"),
        act("10:30", "Embalse El Yeso o zona de nieve", "Lago turquesa rodeado de montañas, si el camino está abierto.", "Embalse El Yeso, Chile", "naturaleza", "2 h"),
        act("13:30", "Almuerzo campestre con sopaipillas", "", "San José de Maipo, Chile", "comida", "1 h 30 min"),
        act("16:00", "Regreso y tarde libre", "", "Las Condes, Santiago", "descanso")],
        ("Las Condes", "", "$350.000–$500.000")),
      dia("Valparaíso y Viña del Mar", [
        act("08:30", "Bus o tour a Valparaíso", "Unas 1 h 30 min por carretera.", "Valparaíso, Chile", "traslado", "1 h 30 min"),
        act("10:30", "Cerros de colores y ascensores", "Suban en los ascensores (funiculares) y caminen por los cerros Alegre y Concepción, llenos de murales.", "Cerro Alegre, Valparaíso, Chile", "pueblo", "2 h 30 min"),
        act("13:30", "Almuerzo de mariscos o empanadas", "", "Valparaíso, Chile", "comida", "1 h"),
        act("15:00", "Viña del Mar: reloj de flores y playa", "Paseo corto frente al Pacífico.", "Reloj de Flores, Viña del Mar, Chile", "sitio turístico", "1 h 30 min"),
        act("19:00", "Regreso a Santiago", "", "Santiago, Chile", "traslado", "1 h 30 min")],
        ("Las Condes", "", "$350.000–$500.000")),
      dia("Regreso a Bogotá", [
        act("09:00", "Devolver ropa arrendada y últimas compras", "Chocolates, artesanía en lapislázuli o alfajores.", "Las Condes, Santiago", "compras", "1 h 30 min"),
        act("12:00", "Traslado al aeropuerto", "", "Aeropuerto de Santiago, Chile", "traslado", "45 min"),
        act("15:00", "Vuelo Santiago → Bogotá", "", "Aeropuerto de Santiago, Chile", "traslado", "6 h")])
    ],
    "mas_ideas": [
      {"titulo": "Portillo y la Laguna del Inca", "detalle": "Centro de ski clásico junto a una laguna congelada, a 2 h 30 min.", "lugar": "Portillo, Los Andes, Chile", "tipo": "naturaleza", "duracion": "día completo"},
      {"titulo": "Termas de Colina", "detalle": "Piscinas termales naturales en el Cajón del Maipo.", "lugar": "Baños Colina, Cajón del Maipo, Chile", "tipo": "naturaleza", "duracion": "día completo"},
      {"titulo": "Barrio Lastarria y Cerro Santa Lucía", "detalle": "Centro histórico caminable con helado y miradores.", "lugar": "Cerro Santa Lucía, Santiago", "tipo": "pueblo", "duracion": "medio día"},
      {"titulo": "Viña Concha y Toro", "detalle": "Viñedo con tour familiar (jugo de uva para la niña).", "lugar": "Pirque, Chile", "tipo": "cultura", "duracion": "medio día"}],
    "gastronomia": [{"plato": "Pastel de choclo", "detalle": "", "donde": "Restaurantes de comida chilena"},
                    {"plato": "Empanadas de pino", "detalle": "", "donde": "En todas partes"},
                    {"plato": "Sopaipillas", "detalle": "", "donde": "Cajón del Maipo y puestos callejeros"},
                    {"plato": "Mote con huesillo", "detalle": "", "donde": "Cerro San Cristóbal"}],
    "presupuesto": [
      {"concepto": "Vuelos Bogotá–Santiago (3)", "detalle": "ida y vuelta, temporada media", "total": 6000000},
      {"concepto": "Hospedaje 6 noches", "detalle": "Las Condes, habitación familiar", "total": 2600000},
      {"concepto": "Tickets de ski 2 días", "detalle": "2 adultos y niña", "total": 1700000},
      {"concepto": "Equipo y ropa de nieve", "detalle": "arriendo 2 días, 3 personas", "total": 1300000},
      {"concepto": "Escuela de ski de la niña", "detalle": "2 clases", "total": 500000},
      {"concepto": "Traslados a la montaña y tours", "detalle": "Farellones, Cajón del Maipo, Valparaíso", "total": 1500000},
      {"concepto": "Comidas", "detalle": "7 días, 3 personas", "total": 2100000},
      {"concepto": "Seguro de viaje e imprevistos", "detalle": "", "total": 600000}],
    "consejos": ["Los colombianos entran a Chile como turistas sin visa; lleven pasaporte o cédula vigente y el registro civil de la niña.",
                 "Si la niña viaja con uno solo de los padres, necesita permiso de salida del país firmado por el otro y autenticado en notaría.",
                 "Compren los tickets de ski y la escuela infantil en línea con anticipación: suelen salir más baratos.",
                 "La altura (3.000 m) cansa: mucha agua, bloqueador alto y gafas oscuras aunque esté nublado.",
                 "Revisen el estado del camino a Farellones el día antes: con nevadas fuertes lo cierran o exigen cadenas."],
    "energia": []
  }})

# ------------------------------------------------------------------ México: Día de Muertos
D.append({
  "nombre": "México: Día de Muertos", "destino": "Ciudad de México y Oaxaca, México", "dias": 8, "viajeros": 3,
  "descripcion": "2 adultos y una niña de 9 años; vivir el Día de Muertos en Ciudad de México y Oaxaca.",
  "fechas": {"meses": ["evitar","evitar","evitar","evitar","evitar","evitar","evitar","evitar","evitar","mejor","mejor","evitar"],
             "recomendadas": "Del 27 de octubre al 3 de noviembre", "inicio": "2027-10-27",
             "por_que": "Las ofrendas, las comparsas y las noches en los panteones son del 31 de octubre al 2 de noviembre. Llegar unos días antes deja ver la Megaofrenda y el desfile en Ciudad de México y estar en Oaxaca en las noches más importantes.",
             "evitar": "Reservar tarde: Oaxaca se llena en esas fechas. Reserven hotel y vuelos con 4 a 6 meses de anticipación."},
  "plan": {
    "titulo": "México: Día de Muertos en familia",
    "resumen": "Cuatro días en Ciudad de México (ofrendas, desfile, pirámides y trajineras) y cuatro en Oaxaca, la celebración más tradicional, con comparsas, ofrendas y panteones iluminados.",
    "moneda": "COP",
    "clima": {"resumen": "Otoño seco y agradable: días soleados y noches frescas, sobre todo en Oaxaca y en los panteones.", "temperatura": "10–25 °C",
              "que_llevar": ["Chaqueta liviana para la noche", "Zapatos cómodos para caminar", "Bloqueador y gorra", "Pasaportes de los tres",
                             "Permiso de salida de la niña si viaja con un solo padre", "Reserva de hotel y tiquete de regreso impresos", "Linterna pequeña para los panteones",
                             "Algo blanco o negro para la comparsa (opcional)", "Pesos mexicanos en efectivo para mercados", "Antiácido: la comida es picante"]},
    "dias": [
      dia("Llegada a Ciudad de México", [
        act("08:00", "Vuelo Bogotá → Ciudad de México", "Vuelo directo de unas 4 h 30 min.", "Aeropuerto El Dorado, Bogotá", "traslado", "4 h 30 min"),
        act("14:00", "Hotel en el Centro o la Roma", "Zonas caminables y cerca de todo.", "Colonia Roma, Ciudad de México", "traslado", "1 h"),
        act("17:00", "Zócalo y Megaofrenda", "La plaza principal se llena de ofrendas y figuras gigantes de calaveras en esas fechas.", "Zócalo, Ciudad de México", "sitio turístico", "2 h"),
        act("19:30", "Tacos al pastor y pan de muerto", "El pan de muerto solo se hace en esta temporada: pruébenlo con chocolate caliente.", "Centro Histórico, Ciudad de México", "comida", "1 h")],
        ("Colonia Roma o Centro Histórico", "caminable y céntrico", "$300.000–$450.000")),
      dia("Coyoacán y Frida Kahlo", [
        act("10:00", "Museo Frida Kahlo (Casa Azul)", "Compren la entrada en línea con días de anticipación: se agota.", "Museo Frida Kahlo, Coyoacán, Ciudad de México", "cultura", "1 h 30 min", "aprox. $60.000 por persona"),
        act("12:00", "Ofrendas y mercado de Coyoacán", "Plazas llenas de ofrendas, catrinas y alebrijes; churros y esquites para la niña.", "Coyoacán, Ciudad de México", "pueblo", "2 h"),
        act("14:30", "Almuerzo en el mercado", "", "Mercado de Coyoacán, Ciudad de México", "comida", "1 h"),
        act("17:00", "Maquillaje de catrina", "En Coyoacán pintan la cara de calavera a niños y adultos: a la niña le va a encantar.", "Coyoacán, Ciudad de México", "cultura", "45 min", "aprox. $20.000")],
        ("Colonia Roma o Centro Histórico", "", "$300.000–$450.000")),
      dia("Pirámides de Teotihuacán", [
        act("07:00", "Tour a Teotihuacán", "Salgan temprano para subir con menos sol y menos gente.", "Teotihuacán, Estado de México", "traslado", "1 h", "Tour aprox. $150.000 por persona"),
        act("08:30", "Pirámides del Sol y de la Luna", "Ciudad prehispánica enorme; la Calzada de los Muertos tiene más sentido en estas fechas.", "Teotihuacán, Estado de México", "sitio turístico", "3 h"),
        act("12:30", "Almuerzo en una cueva", "Restaurantes cerca de las pirámides funcionan dentro de cuevas naturales.", "Teotihuacán, Estado de México", "comida", "1 h 30 min"),
        act("17:00", "Desfile de Día de Muertos (si coincide)", "El gran desfile suele ser el fin de semana previo al 2 de noviembre: confirmen la fecha exacta del año.", "Paseo de la Reforma, Ciudad de México", "cultura", "2 h")],
        ("Colonia Roma o Centro Histórico", "", "$300.000–$450.000")),
      dia("Xochimilco y vuelo a Oaxaca", [
        act("09:00", "Trajineras en Xochimilco", "Paseo en lanchas de colores por los canales, con música y comida que pasa en otras barcas.", "Embarcadero Nuevo Nativitas, Xochimilco, Ciudad de México", "naturaleza", "2 h", "aprox. $200.000 la trajinera"),
        act("15:00", "Vuelo Ciudad de México → Oaxaca", "Vuelo de 1 h.", "Aeropuerto de Ciudad de México", "traslado", "1 h"),
        act("18:00", "Llegada al centro de Oaxaca", "Hospedaje en el centro para ir a pie a todo.", "Centro Histórico, Oaxaca", "traslado", "30 min"),
        act("19:30", "Primera comparsa", "Grupos disfrazados recorren las calles con banda de música: síganla un rato.", "Andador Macedonio Alcalá, Oaxaca", "cultura", "1 h 30 min")],
        ("Centro de Oaxaca", "a pie de las comparsas", "$400.000–$600.000")),
      dia("31 de octubre: ofrendas y mercados", [
        act("10:00", "Templo de Santo Domingo", "La joya de Oaxaca, con el jardín etnobotánico al lado.", "Templo de Santo Domingo, Oaxaca", "sitio turístico", "1 h 30 min"),
        act("12:00", "Mercado 20 de Noviembre", "Pasillo de humo para elegir carne asada; prueben tlayuda y chocolate oaxaqueño.", "Mercado 20 de Noviembre, Oaxaca", "comida", "1 h 30 min"),
        act("15:00", "Taller de pan de muerto o alebrijes", "Muchos talleres reciben niños: pinten su propio alebrije.", "Oaxaca", "cultura", "2 h", "aprox. $100.000 por persona"),
        act("19:00", "Tapetes de arena y ofrendas del centro", "Las calles se llenan de altares y tapetes de arena de colores.", "Centro Histórico, Oaxaca", "pueblo", "2 h")],
        ("Centro de Oaxaca", "", "$400.000–$600.000")),
      dia("1 de noviembre: Monte Albán y panteón de noche", [
        act("09:00", "Zona arqueológica de Monte Albán", "Ciudad zapoteca en la cima de una montaña, con vista de todo el valle.", "Monte Albán, Oaxaca", "sitio turístico", "3 h", "aprox. $25.000 por persona"),
        act("13:00", "Almuerzo: mole negro", "", "Centro Histórico, Oaxaca", "comida", "1 h 30 min"),
        act("16:00", "Descanso en el hotel", "Esta noche se trasnocha un poco.", "Centro de Oaxaca", "descanso", "2 h"),
        act("20:00", "Panteón de Xoxocotlán iluminado", "Las familias acompañan a sus muertos con velas, flores y música. Es un momento respetuoso: pidan permiso antes de tomar fotos.", "Panteón de Santa Cruz Xoxocotlán, Oaxaca", "cultura", "2 h")],
        ("Centro de Oaxaca", "", "$400.000–$600.000")),
      dia("2 de noviembre: naturaleza y artesanías", [
        act("08:00", "Hierve el Agua", "Cascadas petrificadas y pozas en lo alto de la montaña.", "Hierve el Agua, San Lorenzo Albarradas, Oaxaca", "naturaleza", "3 h", "aprox. $15.000 por persona"),
        act("12:30", "Árbol del Tule", "Uno de los árboles más anchos del mundo.", "Santa María del Tule, Oaxaca", "naturaleza", "45 min"),
        act("14:00", "Teotitlán del Valle", "Pueblo de tapetes de lana teñidos con colores naturales: ven cómo los tejen.", "Teotitlán del Valle, Oaxaca", "pueblo", "1 h 30 min"),
        act("19:00", "Cena de despedida", "", "Centro Histórico, Oaxaca", "comida", "1 h 30 min")],
        ("Centro de Oaxaca", "", "$400.000–$600.000")),
      dia("Regreso a Bogotá", [
        act("08:00", "Vuelo Oaxaca → Ciudad de México", "", "Aeropuerto de Oaxaca", "traslado", "1 h"),
        act("12:00", "Vuelo Ciudad de México → Bogotá", "", "Aeropuerto de Ciudad de México", "traslado", "4 h 30 min")])
    ],
    "mas_ideas": [
      {"titulo": "Pátzcuaro y la isla de Janitzio", "detalle": "La Noche de Muertos más famosa de Michoacán, con velas sobre el lago.", "lugar": "Pátzcuaro, Michoacán", "tipo": "pueblo", "duracion": "2 días"},
      {"titulo": "Bosque y Castillo de Chapultepec", "detalle": "Parque enorme con castillo y museos.", "lugar": "Castillo de Chapultepec, Ciudad de México", "tipo": "naturaleza", "duracion": "medio día"},
      {"titulo": "Museo Nacional de Antropología", "detalle": "El mejor museo para entender las culturas de México.", "lugar": "Museo Nacional de Antropología, Ciudad de México", "tipo": "cultura", "duracion": "medio día"},
      {"titulo": "San Martín Tilcajete", "detalle": "Pueblo de los alebrijes de madera.", "lugar": "San Martín Tilcajete, Oaxaca", "tipo": "pueblo", "duracion": "medio día"}],
    "gastronomia": [{"plato": "Pan de muerto", "detalle": "", "donde": "Panaderías, solo en temporada"},
                    {"plato": "Tlayuda", "detalle": "", "donde": "Mercados de Oaxaca"},
                    {"plato": "Mole negro", "detalle": "", "donde": "Oaxaca"},
                    {"plato": "Tacos al pastor", "detalle": "", "donde": "Ciudad de México"},
                    {"plato": "Chocolate oaxaqueño", "detalle": "", "donde": "Mercado 20 de Noviembre"}],
    "presupuesto": [
      {"concepto": "Vuelos Bogotá–Ciudad de México (3)", "detalle": "ida y vuelta, reservar con anticipación", "total": 4800000},
      {"concepto": "Vuelos Ciudad de México–Oaxaca (3)", "detalle": "ida y vuelta", "total": 1200000},
      {"concepto": "Hospedaje Ciudad de México 3 noches", "detalle": "", "total": 1100000},
      {"concepto": "Hospedaje Oaxaca 4 noches", "detalle": "temporada alta", "total": 2000000},
      {"concepto": "Tours y entradas", "detalle": "Teotihuacán, Xochimilco, Monte Albán, Hierve el Agua", "total": 1300000},
      {"concepto": "Comidas", "detalle": "8 días, 3 personas", "total": 2000000},
      {"concepto": "Transporte local y seguro de viaje", "detalle": "", "total": 800000}],
    "consejos": ["Los colombianos no necesitan visa para México como turistas, pero en migración piden reserva de hotel, tiquete de regreso y a veces solvencia: llévenlos impresos.",
                 "Si la niña viaja con uno solo de los padres, necesita permiso de salida del país autenticado en notaría.",
                 "Reserven Oaxaca con 4 a 6 meses de anticipación: en estas fechas se llena.",
                 "En los panteones es una celebración familiar y respetuosa: silencio, sin pisar las tumbas y pidan permiso para fotos.",
                 "Pidan la comida «sin picante» para la niña: casi todo lleva chile."],
    "energia": []
  }})

def build(d):
    p = d["plan"]
    for di, dd in enumerate(p["dias"]):
        dd["id"] = f"{slug(d['nombre'])[:20]}-d{di + 1}"
        for ai, a in enumerate(dd["actividades"]):
            a["id"] = f"{dd['id']}-a{ai + 1}"
    for i, x in enumerate(p["presupuesto"]): x["id"] = f"p{i}"
    for i, x in enumerate(p["mas_ideas"]): x["id"] = f"i{i}"
    p["fechas"] = d["fechas"]
    return {"id": "destino-" + slug(d["nombre"]), "nombre": d["nombre"], "destino": d["destino"], "dias": d["dias"], "viajeros": d["viajeros"],
            "descripcion": d["descripcion"], "plan": p}

out = [build(d) for d in D]
json.dump(out, open("data/destinos.json", "w", encoding="utf-8"), ensure_ascii=False, separators=(",", ":"))
html_path = "artifact/planificador.html"
html = open(html_path, encoding="utf-8").read()
blob = json.dumps(out, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")
start, end = '<script id="destinos" type="application/json">', "</script><!-- /destinos -->"
block = start + blob + end
if start in html:
    a = html.index(start); b = html.index(end, a) + len(end); html = html[:a] + block + html[b:]
else:
    html = html.replace('<div id="tip" hidden></div>', block + '\n<div id="tip" hidden></div>', 1)
open(html_path, "w", encoding="utf-8").write(html)
print(len(out), "destinos incrustados")
