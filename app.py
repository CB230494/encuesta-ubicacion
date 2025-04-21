import streamlit as st
from streamlit_folium import st_folium
import folium
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import datetime

st.set_page_config(page_title="Encuesta con Mapa", layout="centered")
st.title("Encuesta de percepción ciudadana (Prueba)")

st.markdown("Por favor, completa la siguiente información y marca la ubicación en el mapa.")

# Formulario
edad = st.number_input("Edad", min_value=10, max_value=100, step=1)
ocupacion = st.text_input("Ocupación")

# Mapa base sin marcador
st.markdown("Haz clic en el mapa para seleccionar tu ubicación:")

# Mostrar mapa con marcador si ya hay clic
if "lat" in st.session_state and "lng" in st.session_state:
    m = folium.Map(location=[st.session_state.lat, st.session_state.lng], zoom_start=13)
    folium.Marker([st.session_state.lat, st.session_state.lng], popup="Tu ubicación seleccionada").add_to(m)
else:
    m = folium.Map(location=[10.52, -85.25], zoom_start=10)

# Mostrar mapa y capturar clic
map_data = st_folium(m, height=400, width=700)

# Guardar coordenadas al hacer clic
if map_data["last_clicked"] is not None:
    st.session_state.lat = map_data["last_clicked"]["lat"]
    st.session_state.lng = map_data["last_clicked"]["lng"]

# Botón para enviar
if st.button("Enviar respuesta"):
    if not ocupacion:
        st.warning("⚠️ Por favor, completa todos los campos.")
    elif "lat" not in st.session_state or "lng" not in st.session_state:
        st.warning("⚠️ Debes hacer clic en el mapa para seleccionar tu ubicación.")
    else:
        # Preparar datos
        lat = st.session_state.lat
        lng = st.session_state.lng
        fecha = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        enlace = f"https://www.google.com/maps?q={lat},{lng}"

        # Guardar en Google Sheets
        scope = ['https://spreadsheets.google.com/feeds','https://www.googleapis.com/auth/drive']
        creds = ServiceAccountCredentials.from_json_keyfile_name('client_secret.json', scope)
        client = gspread.authorize(creds)
        sheet = client.open("Encuesta_Geolocalizada").sheet1
        sheet.append_row([edad, ocupacion, fecha, enlace])

        # Confirmación visual
        st.success("✅ ¡Gracias! Tu respuesta ha sido registrada.")
        st.markdown(f"🔗 [Ver ubicación en Google Maps]({enlace})")

        # Mostrar mapa con pin
        m_confirm = folium.Map(location=[lat, lng], zoom_start=13)
        folium.Marker([lat, lng], popup="Ubicación registrada").add_to(m_confirm)
        st_folium(m_confirm, height=400, width=700)

        # Limpiar coordenadas para el siguiente uso
        del st.session_state["lat"]
        del st.session_state["lng"]
