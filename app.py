import streamlit as st
import uuid
from auth_utils import verificar_login, get_supabase
from db_utils import (
    obtener_configuraciones, guardar_configuracion
)
from pagos_utils import obtener_configuracion_pagos, guardar_contacto, activar_contacto

st.set_page_config(page_title="Admin Bot", page_icon="🤖", layout="wide")

# --- DIÁLOGO DE EDICIÓN ---
@st.dialog("Editar Regla")
def abrir_editor(conf):
    st.write(f"Editando palabra: **{conf['palabra_clave']}**")
    
    # Campos de edición
    nueva_palabra = st.text_input("Palabra clave", value=conf['palabra_clave'])
    nuevo_contenido = st.text_area("Editar contenido", value=conf['respuestas']['contenido'])
    
    if st.button("Guardar Cambios"):
        try:
            # Actualizamos la tabla 'respuestas' que es la que existe en tu panel
            # Asegúrate de que esta tabla tenga ambas columnas (o ajusta si están separadas)
            get_supabase().table("respuestas").update({
                "palabra_clave": nueva_palabra, 
                "contenido": nuevo_contenido
            }).eq("id", conf['id']).execute()
            
            st.success("¡Guardado!")
            st.rerun()
        except Exception as e:
            st.error(f"Error: {e}")

# --- LÓGICA PRINCIPAL ---
if "logueado" not in st.session_state: st.session_state["logueado"] = False

if not st.session_state["logueado"]:
    st.title("🔐 Acceso al Sistema")
    user = st.text_input("Usuario")
    pwd = st.text_input("Contraseña", type="password")
    if st.button("Ingresar"):
        exito, msg = verificar_login(user, pwd)
        if exito:
            st.session_state["logueado"] = True
            st.rerun()
        else: st.error(msg)
else:
    st.title("🤖 Panel de Control")
    tab1, tab2 = st.tabs(["Configurar Bot", "Configurar Pagos"])
    
    with tab1:
        st.subheader("Nueva Regla")
        with st.form("nueva_config", clear_on_submit=True):
            c = st.text_input("Palabras clave")
            r = st.text_area("Respuesta o URL de PDF")
            if st.form_submit_button("Guardar"):
                guardar_configuracion(c, r)
                st.rerun()

        st.divider()
        st.subheader("Reglas Activas")
        for conf in obtener_configuraciones():
            with st.container(border=True):
                c1, c2, c3 = st.columns([3, 1, 1])
                c1.write(f"🔑 **{conf['palabra_clave']}**")
                c2.write("📄 PDF" if "http" in conf['respuestas']['contenido'] else "💬 Texto")
                if c3.button("✏️ Editar", key=f"edit_{conf['id']}"):
                    abrir_editor(conf)
    
    with tab2:
        st.subheader("Gestión de Pagos")
        with st.form("form_pago", clear_on_submit=True):
            ced = st.text_input("Cédula")
            tel = st.text_input("Teléfono")
            if st.form_submit_button("Registrar"):
                guardar_contacto(ced, tel)
                st.rerun()
        
        for c in obtener_configuracion_pagos():
            with st.container(border=True):
                col1, col2 = st.columns([4, 1])
                col1.markdown(f"**Cédula:** `{c['cedula_esperada']}`")
                if c['activo']: col2.success("✅ Activo")
                elif col2.button("Activar", key=f"act_{c['id']}"):
                    activar_contacto(c['id']); st.rerun()

    if st.sidebar.button("Cerrar sesión"):
        st.session_state["logueado"] = False
        st.rerun()
