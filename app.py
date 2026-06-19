import streamlit as st
from supabase import create_client

# 1. Configuración de conexión
try:
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    supabase = create_client(url, key)
except Exception as e:
    st.error("Error cargando credenciales: " + str(e))
    st.stop()

st.title("Admin de Bot")

with st.form("registro", clear_on_submit=True):
    pregunta = st.text_input("Pregunta:")
    respuesta = st.text_area("Respuesta:")
    archivo = st.file_uploader("Imagen (opcional):", type=['png', 'jpg'])
    
    if st.form_submit_button("Guardar"):
        url_imagen = None
        
        # Subida al Storage
        if archivo:
            nombre_archivo = f"respuestas/{archivo.name}"
            # Asegúrate que el bucket se llame 'imagenes-bot'
            supabase.storage.from_("imagenes-bot").upload(nombre_archivo, archivo.getvalue())
            url_imagen = supabase.storage.from_("imagenes-bot").get_public_url(nombre_archivo)
        
        # Guardado en la Tabla
        supabase.table("preguntas_respuestas").insert({
            "pregunta": pregunta,
            "respuesta": respuesta,
            "url_imagen": url_imagen # Debe coincidir con la columna en Supabase
        }).execute()
        
        st.success("Guardado con éxito")
