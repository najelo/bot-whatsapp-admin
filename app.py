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
        
        # Subida al Storage mejorada
        if archivo:
            try:
                nombre_archivo = f"respuestas/{archivo.name}"
                # Usamos 'upsert=True' para sobrescribir si el archivo ya existe
                supabase.storage.from_("imagenes-bot").upload(
                    path=nombre_archivo, 
                    file=archivo.getvalue(),
                    file_options={"upsert": "true"}
                )
                url_imagen = supabase.storage.from_("imagenes-bot").get_public_url(nombre_archivo)
            except Exception as e:
                st.error(f"Error al subir la imagen: {e}")
                # Si falla la imagen, decidimos si detener o continuar sin ella
                st.stop()
        
        # Guardado en la Tabla
        try:
            supabase.table("preguntas_respuestas").insert({
                "pregunta": pregunta,
                "respuesta": respuesta,
                "url_imagen": url_imagen
            }).execute()
            st.success("Guardado con éxito")
        except Exception as e:
            st.error(f"Error al guardar en la base de datos: {e}")
