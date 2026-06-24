import streamlit as st
import uuid
from auth_utils import verificar_login, get_supabase
from db_utils import obtener_configuraciones, guardar_configuracion, subir_archivo_al_storage
from pagos_utils import obtener_configuracion_pagos, guardar_contacto, activar_contacto

st.set_page_config(page_title="Admin Bot", layout="wide")

# --- LOGIN (NUEVO) ---
if "logueado" not in st.session_state: st.session_state["logueado"] = False

if not st.session_state["logueado"]:
    st.title("🔐 Iniciar Sesión")
    user = st.text_input("Usuario")
    pwd = st.text_input("Contraseña", type="password")
    if st.button("Entrar"):
        valido, msg = verificar_login(user, pwd)
        if valido: st.session_state["logueado"] = True; st.rerun()
        else: st.error(msg)
    st.stop() # Detiene la ejecución aquí si no está logueado

# --- DIÁLOGO DE EDICIÓN CON VISTA PREVIA ---
@st.dialog("Editar Regla")
def abrir_editor(conf):
    resp_data = conf.get('respuestas') or {}
    contenido = resp_data.get('contenido', '')
    
    st.write(f"Editando: **{conf.get('palabra_clave')}**")
    
    # Vista previa inteligente
    if "http" in contenido:
        st.info("🔗 Contenido Multimedia detectado:")
        if any(ext in contenido for ext in [".jpg", ".png", ".jpeg"]): st.image(contenido, width=200)
        elif any(ext in contenido for ext in [".mp3", ".ogg"]): st.audio(contenido)
        else: st.write(f"Archivo: [Abrir en nueva pestaña]({contenido})")
    
    nuevo_contenido = st.text_area("Contenido", value=contenido)
    if st.button("Guardar"):
        get_supabase().table("respuestas").update({"contenido": nuevo_contenido}).eq("id", resp_data['id']).execute()
        st.rerun()

# --- PANTALLA PRINCIPAL ---
st.title("🤖 Panel de Control")
if st.button("Cerrar sesión"): st.session_state["logueado"] = False; st.rerun()

tab1, tab2 = st.tabs(["⚙️ Reglas", "💳 Pagos"])
with tab1:
    # ... (Tu lógica de subir archivos aquí, igual a la anterior) ...
    for conf in obtener_configuraciones():
        with st.container(border=True):
            col1, col2 = st.columns([4, 1])
            col1.write(f"🔑 **{conf.get('palabra_clave')}**")
            if col2.button("✏️ Editar", key=f"e_{conf['id']}"): abrir_editor(conf)
with tab2:
    # ... (Tu lógica de pagos aquí) ...
