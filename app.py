import streamlit as st
from streamlit_folium import st_folium
import folium
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import datetime

st.set_page_config(page_title="Encuesta con Mapa", layout="centered")
st.title("Encuesta de percepción ciudadana (Prueba)")

st.markdown("Por favor, completa la siguiente información y marca la ubicación en el mapa.")

# --- Formulario ---
edad = st.number_input("Edad", min_value=10, max_value=100, step=1)
ocupacion = st.text_input("Ocupación")

# --- Mapa base sin marcador ---
st.markdown("Haz clic en el mapa para seleccionar tu ubicación:")
m = folium.Map(location=[10.52, -85.25], zoom_start=10)
map_data = st_folium(m, height=400, width=700)

# --- Solo continuar si hay clic ---
if st.button("Enviar respuesta"):
    if not ocupacion:
        st.warning("⚠️ Por favor, completa todos los campos.")
    elif map_data["last_clicked"] is None:
        st.warning("⚠️ Debes hacer clic en el mapa para seleccionar tu ubicación.")
    else:
        # Extraer coordenadas
        lat = map_data["last_clicked"]["lat"]
        lng = map_data["last_clicked"]["lng"]
        fecha = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        enlace = f"https://www.google.com/maps?q={lat},{lng}"

        # --- Google Sheets ---
        scope = ['https://spreadsheets.google.com/feeds','https://www.googleapis.com/auth/drive']
        creds = ServiceAccountCredentials.from_json_keyfile_name('client_secret.json', scope)
        client = gspread.authorize(creds)
        sheet = client.open("Encuesta_Geolocalizada").sheet1
        sheet.append_row([edad, ocupacion, fecha, enlace])

        st.success("✅ ¡Gracias! Tu respuesta ha sido registrada.")

        # Mostrar mapa con marcador de confirmación
        m_confirm = folium.Map(location=[lat, lng], zoom_start=13)
        folium.Marker([lat, lng], popup="Ubicación registrada").add_to(m_confirm)
        st_folium(m_confirm, height=400, width=700)
