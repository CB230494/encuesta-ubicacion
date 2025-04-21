import streamlit as st
from streamlit_folium import st_folium
import folium
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import datetime

st.set_page_config(page_title="Encuesta de percepción ciudadana", layout="centered")

st.title("Encuesta de percepción ciudadana (Prueba)")
st.markdown("Por favor, completa la siguiente información y marca la ubicación en el mapa.")

edad = st.number_input("Edad", min_value=10, max_value=100, step=1)
ocupacion = st.text_input("Ocupación")

st.markdown("Haz clic en el mapa para marcar tu ubicación:")

m = folium.Map(location=[10.52, -85.25], zoom_start=10)
marker = folium.Marker(location=[10.52, -85.25], draggable=True)
marker.add_to(m)
map_data = st_folium(m, height=400, width=700)

if st.button("Enviar respuesta"):
    if not ocupacion:
        st.warning("Por favor, completa todos los campos.")
    elif map_data["last_clicked"] is None:
        st.warning("Debes hacer clic en el mapa para seleccionar tu ubicación.")
    else:
        lat = map_data["last_clicked"]["lat"]
        lng = map_data["last_clicked"]["lng"]
        enlace = f"https://www.google.com/maps?q={lat},{lng}"
        fecha = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
        creds = ServiceAccountCredentials.from_json_keyfile_name('client_secret.json', scope)
        client = gspread.authorize(creds)
        sheet = client.open("Encuesta_Geolocalizada").sheet1
        sheet.append_row([edad, ocupacion, fecha, enlace])

        st.success("✅ ¡Gracias! Tu respuesta ha sido registrada.")
