import streamlit as st
from supabase import create_client

# --- CONFIGURACIÓN DE SUPABASE ---
# Sustituye con tus credenciales reales
SUPABASE_URL = "https://oxsimejylqyjahlagvzy.supabase.co"
SUPABASE_KEY = "sb_publishable_O_oQDHdJWqxXaL3UzZHkzw_-F6O6-sA"
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

st.title("Admin de Respuestas - Bot WhatsApp")

# --- INTERFAZ ---
with st.form("nuevo_registro"):
    pregunta = st.text_input("Pregunta del cliente:")
    respuesta = st.text_area("Respuesta del bot:")
    
    submitted = st.form_submit_button("Guardar en Supabase")

    if submitted:
        if pregunta and respuesta:
            try:
                # Insertar en la tabla 'preguntas_respuestas'
                data = supabase.table("preguntas_respuestas").insert({
                    "pregunta": pregunta.lower(), 
                    "respuesta": respuesta
                }).execute()
                
                st.success("¡Guardado correctamente!")
            except Exception as e:
                st.error(f"Error al guardar: {e}")
        else:
            st.warning("Por favor, llena ambos campos.")

# --- VISUALIZAR LO QUE YA TIENES ---
st.subheader("Respuestas actuales")
if st.button("Actualizar lista"):
    response = supabase.table("preguntas_respuestas").select("*").execute()
    st.table(response.data)