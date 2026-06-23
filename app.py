import streamlit as st
import uuid
from auth_utils import verificar_login, get_supabase
from db_utils import obtener_configuraciones, guardar_configuracion
from pagos_utils import obtener_configuracion_pagos, guardar_contacto, activar_contacto

st.set_page_config(page_title="Admin Bot", page_icon="🤖", layout="wide")

# --- DIÁLOGO DE EDICIÓN ---
@st.dialog("Editar Regla")
def abrir_editor(conf):
    # Acceso seguro a los datos
    # Asumimos que conf es una fila de 'clientes' con un join a 'respuestas'
    respuesta_data = conf.get('respuestas', {})
    
    st.write(f"Editando palabra: **{conf.get('palabra_clave', 'N/A')}**")
    
    nueva_palabra = st.text_input("Palabra clave", value=conf.get('palabra_clave', ''))
    nuevo_contenido = st.text_area("Contenido", value=respuesta_data.get('contenido', ''))
    
    if st.button("Guardar Cambios"):
        try:
            # Validamos que existan los IDs necesarios
            cliente_id = conf.get('id')
            respuesta_id = respuesta_data.get('id')
            
            if not cliente_id or not respuesta_id:
                st.error(f"Error: No se pudo obtener el ID (Cliente: {cliente_id}, Respuesta: {respuesta_id})")
                return

            # Actualizar tabla 'clientes'
            get_supabase().table("clientes").update({
                "palabra_clave": nueva_palabra
            }).eq("id", cliente_id).execute()
            
            # Actualizar tabla 'respuestas'
            get_supabase().table("respuestas").update({
                "contenido": nuevo_contenido
            }).eq("id", respuesta_id).execute()
            
            st.success("¡Guardado correctamente!")
            st.rerun()
        except Exception as e:
            st.error(f"Error técnico: {e}")

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
        else:
            st.error(msg)
else:
    st.title("🤖 Panel de Control del Bot")
    tab1, tab2 = st.tabs(["Configurar Bot", "Configurar Pagos"])
    
    with tab1:
        st.subheader("Nueva Regla")
        with st.form("nueva_config", clear_on_submit=True):
            palabra = st.text_input("Palabras clave")
            res = st.text_area("Respuesta o URL")
            if st.form_submit_button("Guardar"):
                guardar_configuracion(palabra, res)
                st.rerun()

        st.divider()
        st.subheader("Reglas Activas")
        for conf in obtener_configuraciones():
            with st.container(border=True):
                c1, c2 = st.columns([4, 1])
                c1.write(f"🔑 **{conf.get('palabra_clave', 'N/A')}**")
                if c2.button("✏️ Editar", key=f"edit_{conf.get('id')}"):
                    abrir_editor(conf)
    
    with tab2:
        st.subheader("Configuración de Pagos")
        # Aquí va tu lógica de pagos existente
        pass

    if st.sidebar.button("Cerrar sesión"):
        st.session_state["logueado"] = False
        st.rerun()
