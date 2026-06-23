import streamlit as st
import uuid
from auth_utils import verificar_login, get_supabase
# NOTA: Asegúrate que db_utils.py no contenga referencias a la tabla 'configuracion'
from db_utils import obtener_configuraciones, guardar_configuracion
from pagos_utils import obtener_configuracion_pagos, guardar_contacto, activar_contacto

st.set_page_config(page_title="Admin Bot", page_icon="🤖", layout="wide")

# --- DIÁLOGO DE EDICIÓN ---
@st.dialog("Editar Regla")
def abrir_editor(conf):
    # 'conf' contiene los datos de 'clientes' con un join a 'respuestas'
    resp_data = conf.get('respuestas', {})
    
    st.write(f"Editando: **{conf.get('palabra_clave')}**")
    
    nueva_palabra = st.text_input("Palabra clave", value=conf.get('palabra_clave', ''))
    nuevo_contenido = st.text_area("Contenido", value=resp_data.get('contenido', ''))
    
    if st.button("Guardar Cambios"):
        try:
            # Actualizar tabla 'clientes'
            get_supabase().table("clientes").update({"palabra_clave": nueva_palabra}).eq("id", conf['id']).execute()
            # Actualizar tabla 'respuestas'
            get_supabase().table("respuestas").update({"contenido": nuevo_contenido}).eq("id", resp_data['id']).execute()
            
            st.success("¡Guardado!")
            st.rerun()
        except Exception as e:
            st.error(f"Error: {e}")

# --- LÓGICA PRINCIPAL ---
if "logueado" not in st.session_state: st.session_state["logueado"] = False

if not st.session_state["logueado"]:
    st.title("🔐 Acceso")
    user = st.text_input("Usuario")
    pwd = st.text_input("Contraseña", type="password")
    if st.button("Ingresar"):
        if verificar_login(user, pwd)[0]:
            st.session_state["logueado"] = True
            st.rerun()
else:
    tab1, tab2 = st.tabs(["Bot", "Pagos"])
    
    with tab1:
        with st.form("nueva_config", clear_on_submit=True):
            palabra = st.text_input("Palabras clave")
            res = st.text_area("Respuesta")
            if st.form_submit_button("Guardar"):
                guardar_configuracion(palabra, res); st.rerun()

        for conf in obtener_configuraciones():
            with st.container(border=True):
                col1, col2 = st.columns([4, 1])
                col1.write(f"🔑 **{conf.get('palabra_clave')}**")
                if col2.button("✏️ Editar", key=f"edit_{conf['id']}"):
                    abrir_editor(conf)
    
    with tab2:
        for c in obtener_configuracion_pagos():
            with st.container(border=True):
                st.write(f"Cédula: {c.get('cedula_esperada')}")
                if not c.get('activo') and st.button("Activar", key=f"act_{c['id']}"):
                    activar_contacto(c['id']); st.rerun()

    if st.sidebar.button("Cerrar sesión"):
        st.session_state["logueado"] = False
        st.rerun()
