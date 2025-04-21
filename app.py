import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import json

st.set_page_config(page_title="Verificación Google Sheets", layout="centered")
st.title("🧪 Verificación de conexión con Google Sheets")

try:
    # Definir el alcance de acceso
    scope = ['https://spreadsheets.google.com/feeds','https://www.googleapis.com/auth/drive']

    # Cargar las credenciales desde los secretos de Streamlit
    service_account_info = json.loads(st.secrets["GCP_SERVICE_ACCOUNT"])
    creds = ServiceAccountCredentials.from_json_keyfile_dict(service_account_info, scope)

    # Autenticar y conectar con gspread
    client = gspread.authorize(creds)

    # Listar todos los documentos accesibles
    documentos = client.openall()
    nombres = [doc.title for doc in documentos]

    st.success("✅ Conexión exitosa con Google Sheets.")
    st.markdown("### 🗂️ Documentos accesibles:")
    for nombre in nombres:
        st.write(f"- {nombre}")

except Exception as e:
    st.error("❌ Error al conectar con Google Sheets:")
    st.exception(e)
