import streamlit as st
from streamlit_folium import st_folium
import folium
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import datetime

st.set_page_config(page_title="Encuesta Comercio", layout="centered")
st.title("Encuesta de percepción ciudadana en zonas comerciales")

st.markdown("Completa la información a continuación. Todos los datos son confidenciales y se utilizarán únicamente con fines preventivos.")

# P1 - P3: Cantón, Distrito, Mapa
canton = st.text_input("1. Cantón")
distrito = st.selectbox("2. Distrito", ["Tamarindo", "Cartagena", "Cabo Velas (Flamingo)"])
st.markdown("3. Marque en el mapa la ubicación del local comercial:")
if "lat" in st.session_state and "lng" in st.session_state:
    m = folium.Map(location=[st.session_state.lat, st.session_state.lng], zoom_start=13)
    folium.Marker([st.session_state.lat, st.session_state.lng], popup="Ubicación seleccionada").add_to(m)
else:
    m = folium.Map(location=[10.52, -85.25], zoom_start=10)
map_data = st_folium(m, height=400, width=700)
if map_data["last_clicked"] is not None:
    st.session_state.lat = map_data["last_clicked"]["lat"]
    st.session_state.lng = map_data["last_clicked"]["lng"]

# P4 - P7: Edad, Sexo, Escolaridad, Tipo de local
edad = st.number_input("4. Edad", min_value=10, max_value=100, step=1)
sexo = st.radio("5. Sexo", ["Hombre", "Mujer", "LGBTQ+", "Otro / Prefiero no decirlo"])
escolaridad = st.selectbox("6. Escolaridad", ["Ninguna", "Primaria", "Primaria incompleta", "Secundaria completa", "Secundaria incompleta", "Universitaria", "Universitaria incompleta", "Técnico"])
tipo_local = st.selectbox("7. Tipo de local comercial", ["Supermercado", "Pulpería / Licorera", "Restaurante / Soda", "Bar", "Tienda de artículos", "Gasolineras", "Servicios estético", "Puesto de lotería", "Otro"])

# P8 - P8.1: Seguridad
seguridad = st.radio("8. ¿Qué tan seguro(a) se siente en esta zona comercial?", ["Muy seguro(a)", "Seguro(a)", "Ni seguro(a) Ni inseguro(a)", "Inseguro(a)", "Muy inseguro(a)"])
factores_inseguridad = []
if seguridad in ["Inseguro(a)", "Muy inseguro(a)"]:
    factores_inseguridad = st.multiselect("8.1 Factores que influyen en la percepción de inseguridad:", [
        "Presencia de personas desconocidas o con comportamientos inusuales",
        "Poca iluminación en la zona", "Escasa presencia policial", "Robos frecuentes",
        "Consumo de sustancias en la vía pública", "Horarios considerados peligrosos (6pm-5am)",
        "Disturbios o riñas cercanas", "Otro"
    ])

# P9 - P20.1: Factores sociales, delitos y control territorial
riesgos_sociales = st.multiselect("9. ¿Cuáles de los siguientes factores afectan la seguridad en su zona comercial?", [
    "Falta de oportunidades laborales", "Problemas vecinales", "Asentamientos ilegales (precarios)", "Personas en situación de calle",
    "Zona de prostitución", "Consumo de alcohol en vía pública", "Personas con exceso de tiempo de ocio", "Cuarterías",
    "Lotes baldíos", "Ventas informales", "Pérdida de espacios públicos", "Otro"
])
inversion_social = st.multiselect("10. ¿Qué falta en su zona comercial?", [
    "Falta de oferta educativa", "Falta de oferta deportiva", "Falta de oferta recreativa", "Falta de actividades culturales"
])
consumo_drogas = st.multiselect("11. ¿Dónde se da el consumo de drogas?", ["Área privada", "Área pública"])
bunker = st.multiselect("12. ¿Dónde ha identificado posibles búnkeres?", ["Casa de habitación", "Edificación abandonada", "Lote baldío", "Otro"])
delitos_generales = st.multiselect("13. ¿Qué delitos considera que ocurren cerca de su comercio?", [
    "Disturbios en vía pública (riñas, agresiones)", "Daños a la propiedad", "Intimidación o amenazas con fines de lucro", "Hurto",
    "Receptación", "Contrabando (licor, cigarrillos, ropa, etc.)", "Otro"
])
venta_drogas = st.multiselect("14. ¿Dónde se da la venta de drogas?", ["Búnker (espacio cerrado)", "Vía pública", "Exprés"])
delitos_vida = st.multiselect("15. Delitos contra la vida", ["Homicidios", "Heridos"])
delitos_sexuales = st.multiselect("16. Delitos sexuales", ["Abuso sexual", "Acoso sexual", "Violación"])
asaltos = st.multiselect("17. ¿Qué tipo de asalto ocurre en la zona?", ["Asalto a personas", "Asalto a comercio", "Asalto a vivienda", "Asalto a transporte público"])
estafas = st.multiselect("18. ¿Qué tipo de estafa ocurre en la zona?", ["Billetes falsos", "Documentos falsos", "Estafa (Oro)", "Lotería falsos", "Estafas informáticas", "Estafa telefónica", "Estafa con tarjetas"])
robo = st.multiselect("19. Robo (Sustracción con fuerza)", ["Tacha a comercio", "Tacha a edificaciones", "Tacha a vivienda", "Tacha de vehículos", "Robo de vehículos"])
presencia_control = st.radio("20. ¿Ha notado personas o grupos que ejercen control sobre la zona comercial?", ["Sí, he observado comportamientos similares", "He escuchado comentarios de otros comercios", "No", "Prefiero no responder"])
comportamientos_observados = []
if presencia_control == "Sí, he observado comportamientos similares":
    comportamientos_observados = st.multiselect("20.1 ¿Qué tipo de comportamientos ha observado?", [
        "Cobros o 'cuotas' por dejar operar un local", "Personas que vigilan entradas/salidas de negocios",
        "Amenazas veladas o directas a comerciantes", "Restricciones impuestas sobre horarios o actividades",
        "Intermediarios que 'negocian seguridad'", "Personas ajenas con control visible", "Interferencia en la operación del local",
        "Grupos que autorizan el funcionamiento de locales", "Otro"
    ])

# Envío de formulario
if st.button("Enviar formulario"):
    if "lat" not in st.session_state or "lng" not in st.session_state:
        st.warning("⚠️ Debe marcar la ubicación en el mapa.")
    else:
        enlace = f"https://www.google.com/maps?q={st.session_state.lat},{st.session_state.lng}"
        fecha = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        scope = ['https://spreadsheets.google.com/feeds','https://www.googleapis.com/auth/drive']
        creds = ServiceAccountCredentials.from_json_keyfile_name('client_secret.json', scope)
        client = gspread.authorize(creds)
        sheet = client.open("Encuesta_Geolocalizada").sheet1

        fila = [
            canton, distrito, enlace, edad, sexo, escolaridad, tipo_local,
            seguridad, ", ".join(factores_inseguridad),
            ", ".join(riesgos_sociales), ", ".join(inversion_social), ", ".join(consumo_drogas),
            ", ".join(bunker), ", ".join(delitos_generales), ", ".join(venta_drogas),
            ", ".join(delitos_vida), ", ".join(delitos_sexuales), ", ".join(asaltos),
            ", ".join(estafas), ", ".join(robo), presencia_control, ", ".join(comportamientos_observados),
            fecha
        ]

        sheet.append_row(fila)
        st.success("✅ ¡Formulario enviado correctamente!")
        st.markdown(f"📍 [Ver ubicación seleccionada en Google Maps]({enlace})")
        del st.session_state["lat"]
        del st.session_state["lng"]

# P21 - Victimización
victimizacion = st.radio("21. ¿Usted o su local comercial han sido víctima de algún delito en los últimos 12 meses?", [
    "Sí, y presenté la denuncia",
    "Sí, pero no presenté la denuncia",
    "No",
    "Prefiero no responder"
])

motivo_no_denuncia = []
if victimizacion == "Sí, pero no presenté la denuncia":
    motivo_no_denuncia = st.multiselect("22. ¿Por qué no denunció?", [
        "Distancia (falta de oficinas para denunciar)",
        "Miedo a represalias",
        "Falta de respuesta oportuna",
        "He realizado denuncias y no ha pasado nada",
        "Complejidad al colocar la denuncia",
        "Desconocimiento de dónde colocar la denuncia",
        "Un policía me dijo que no denunciara",
        "Falta de tiempo para denunciar"
    ])

delito_sufrido = []
if victimizacion == "Sí, y presenté la denuncia":
    delito_sufrido = st.multiselect("22.1 ¿Qué delito sufrió?", [
        "Hurto", "Asalto", "Cobro por protección", "Estafa", "Daños a la propiedad",
        "Venta o consumo de drogas", "Amenazas (verbales o físicas)", "Cobros periódicos o 'cuotas' por operar", "Otro"
    ])

horario_delito = st.selectbox("23. ¿En qué horario ocurrió el delito (si lo sabe)?", [
    "00:00 - 02:59 a. m.", "03:00 - 05:59 a. m.", "06:00 - 08:59 a. m.",
    "09:00 - 11:59 a. m.", "12:00 - 14:59 p. m.", "15:00 - 17:59 p. m.",
    "18:00 - 20:59 p. m.", "21:00 - 23:59 p. m.", "DESCONOCIDO"
])

modo_operar = st.multiselect("24. ¿Cuál fue el modo de operar del delito?", [
    "Arma blanca (cuchillo, machete, etc.)", "Arma de fuego", "Amenazas (verbales o físicas)",
    "Cobros o 'cuotas' por operar", "Arrebato", "Boquete", "Ganzúa (pata de chancho)",
    "Engaño", "No sé", "Otro"
])

exigencia = st.radio("25. ¿Ha recibido su local alguna exigencia económica o cuota obligatoria?", [
    "Sí", "No", "Prefiero no responder"
])

detalle_exigencia = ""
if exigencia == "Sí":
    detalle_exigencia = st.text_area("26. Detalle cómo ocurrió (frecuencia, forma de contacto, tipo de exigencia, etc.):")

# P27 - P33
servicio_policial = st.radio("27. ¿Cómo califica el servicio policial cerca de su local?", [
    "Excelente", "Bueno", "Regular", "Malo", "Muy malo"
])

cambio_servicio = st.radio("28. ¿Cómo ha cambiado el servicio policial en los últimos 12 meses?", [
    "Ha mejorado mucho", "Ha mejorado", "Igual", "Ha empeorado", "Ha empeorado mucho"
])

conoce_policias = st.radio("29. ¿Conoce a los policías de la Fuerza Pública o Policía Turística que patrullan su zona?", [
    "Sí", "No"
])

programa_seguridad = st.radio("30. ¿Conoce o participa en el Programa de Seguridad Comercial de la Fuerza Pública?", [
    "No lo conozco", "Lo conozco, pero no participo", "Lo conozco y participo activamente",
    "No lo conozco, pero me gustaría participar", "Prefiero no responder"
])

contacto_programa = ""
if programa_seguridad in ["No lo conozco", "Lo conozco, pero no participo", "No lo conozco, pero me gustaría participar"]:
    contacto_programa = st.text_area("30.1 Si desea ser contactado para participar, indique nombre del comercio, correo electrónico y número de teléfono:")

medidas_fp = st.text_area("31. ¿Qué medidas considera importantes que implemente la Fuerza Pública para mejorar la seguridad en su zona comercial?")
medidas_muni = st.text_area("32. ¿Qué medidas considera necesarias por parte de la municipalidad para mejorar la seguridad en su zona comercial?")
info_adicional = st.text_area("33. ¿Desea brindar alguna otra información adicional?")

# Agregar columnas a la fila antes de enviar
fila.extend([
    victimizacion,
    ", ".join(motivo_no_denuncia),
    ", ".join(delito_sufrido),
    horario_delito,
    ", ".join(modo_operar),
    exigencia,
    detalle_exigencia,
    servicio_policial,
    cambio_servicio,
    conoce_policias,
    programa_seguridad,
    contacto_programa,
    medidas_fp,
    medidas_muni,
    info_adicional
])
