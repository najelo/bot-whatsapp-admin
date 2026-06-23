import streamlit as st
import uuid
from auth_utils import verificar_login, get_supabase
from db_utils import (
    obtener_configuraciones, guardar_configuracion, 
    eliminar_configuracion
)
from pagos_utils import obtener_configuracion_pagos, guardar_contacto, activar_contacto

# Configuración inicial con layout wide
st.set_page_config(page_title="Admin Bot", page_icon="🤖", layout="wide")

if "logueado" not in st.session_state: 
    st.session_state["logueado"] = False

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
    # --- TODO ESTO ESTÁ DENTRO DEL ELSE (Solo visible si logueado) ---
    
    # Navegación Lateral (Ahora bien indentada)
    st.sidebar.title("Navegación")
    menu = st.sidebar.radio(
        "Selecciona una opción:", 
        ["🤖 Gestión de Respuestas", "💳 Gestión de Pagos"]
    )

    st.sidebar.markdown("---")
    if st.sidebar.button("Cerrar sesión"):
        st.session_state["logueado"] = False
        st.rerun()

    st.title("🤖 Panel de Control del Bot")

    # --- Lógica de Gestión de Respuestas ---
    if menu == "🤖 Gestión de Respuestas":
        col_form, col_lista = st.columns([1, 2])
        
        with col_form:
            st.subheader("Nueva Regla")
            with st.form("form_nueva_regla"):
                palabras = st.text_input("Palabras clave (separadas por coma)")
                respuesta = st.text_area("Contenido de la respuesta")
                if st.form_submit_button("Guardar Regla"):
                    exito, msg = guardar_configuracion(palabras, respuesta)
                    if exito: st.success(msg); st.rerun()
                    else: st.error(msg)
            
        with col_lista:
            st.subheader("Reglas Activas")
            configuraciones = obtener_configuraciones()
            for conf in configuraciones:
                with st.container(border=True):
                    st.write(f"**Palabra:** `{conf['palabra_clave']}`")
                    st.write(f"**Respuesta:** {conf['respuestas']['contenido']}")
                    if st.button("🗑️ Eliminar", key=f"del_{conf['id']}"):
                        eliminar_configuracion(conf['id']); st.rerun()

    # --- Lógica de Gestión de Pagos ---
    elif menu == "💳 Gestión de Pagos":
        st.subheader("💳 Gestión de Pagos")
        
        with st.container(border=True):
            st.markdown("### ➕ Agregar Nueva Identidad")
            c1, c2, c3, c4 = st.columns([2, 2, 2, 1])
            ced = c1.text_input("Cédula")
            tel = c2.text_input("Teléfono")
            monto = c3.number_input("Monto Mín.", min_value=0.0)
            if c4.button("Registrar"):
                try:
                    guardar_contacto(ced, tel)
                    st.rerun()
                except Exception as e: st.error(f"Error: {e}")

        st.divider()
        st.subheader("Registros Guardados")
        contactos = obtener_configuracion_pagos()
        
        for c in contactos:
            with st.container(border=True):
                col1, col2, col3 = st.columns([3, 1, 1])
                col1.markdown(f"**Cédula:** `{c.get('cedula_esperada', 'N/A')}` | **Tel:** `{c.get('telefono_esperado', 'N/A')}`")
                
                if c.get('activo', False): 
                    col2.success("✅ Activo")
                else:
                    if col2.button("Activar", key=f"btn_act_{c['id']}"):
                        activar_contacto(c['id']); st.rerun()
                
                if col3.button("🗑️", key=f"del_{c['id']}"):
                    get_supabase().table("configuracion_pago").delete().eq("id", c['id']).execute()
                    st.rerun()
