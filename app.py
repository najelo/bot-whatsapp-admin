import streamlit as st
import uuid
from auth_utils import verificar_login, get_supabase
from db_utils import (
    obtener_configuraciones, guardar_configuracion, 
    eliminar_configuracion, guardar_palabra_individual,
    obtener_todas_las_respuestas
)
from pagos_utils import obtener_configuracion_pagos, guardar_contacto, activar_contacto

st.set_page_config(page_title="Admin Bot", page_icon="🤖", layout="wide")

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
    # --- NAVEGACIÓN LATERAL ---
    st.sidebar.title("Navegación")
    menu = st.sidebar.radio("", ["🤖 Gestión de Respuestas", "💳 Gestión de Pagos"])
    st.sidebar.markdown("---")
    if st.sidebar.button("Cerrar sesión"):
        st.session_state["logueado"] = False
        st.rerun()

    st.title("🤖 Panel de Control del Bot")

    # --- GESTIÓN DE RESPUESTAS (ESTILO DASHBOARD) ---
    if menu == "🤖 Gestión de Respuestas":
        col_form, col_lista = st.columns([1, 2])
        
        with col_form:
            st.subheader("Nueva Regla")
            tipo = st.radio("Tipo:", ["Texto", "PDF"])
            with st.form("form_nueva_regla", clear_on_submit=True):
                palabras = st.text_input("Palabras clave (separadas por coma)")
                if tipo == "Texto":
                    respuesta = st.text_area("Contenido de la respuesta")
                else:
                    respuesta = st.file_uploader("Subir PDF", type=["pdf"])
                
                if st.form_submit_button("Guardar"):
                    if tipo == "PDF" and respuesta:
                        # Lógica de subida que ya tenías
                        supabase = get_supabase()
                        nombre_archivo = f"{uuid.uuid4()}.pdf"
                        supabase.storage.from_("recetarios-helado").upload(nombre_archivo, respuesta.getvalue())
                        url = supabase.storage.from_("recetarios-helado").get_public_url(nombre_archivo)
                        exito, msg = guardar_configuracion(palabras, url)
                    else:
                        exito, msg = guardar_configuracion(palabras, respuesta)
                    
                    if exito: st.success(msg); st.rerun()
                    else: st.error(msg)
            
        with col_lista:
            st.subheader("Reglas Activas")
            for conf in obtener_configuraciones():
                with st.container(border=True):
                    st.write(f"**Palabra:** `{conf['palabra_clave']}`")
                    st.write(f"**Contenido:** {conf['respuestas']['contenido']}")
                    if st.button("🗑️ Eliminar", key=f"del_{conf['id']}"):
                        eliminar_configuracion(conf['id']); st.rerun()

    # --- GESTIÓN DE PAGOS ---
    elif menu == "💳 Gestión de Pagos":
        st.subheader("💳 Configurar Pagos")
        with st.container(border=True):
            col_a, col_b, col_c = st.columns([2, 2, 1])
            ced = col_a.text_input("Cédula")
            tel = col_b.text_input("Teléfono")
            if col_c.button("➕ Registrar"):
                guardar_contacto(ced, tel); st.rerun()

        st.divider()
        st.subheader("Registros Guardados")
        for c in obtener_configuracion_pagos():
            with st.container(border=True):
                col1, col2, col3 = st.columns([3, 1, 1])
                col1.markdown(f"**Cédula:** `{c['cedula_esperada']}` | **Tel:** `{c['telefono_esperado']}`")
                if c['activo']: col2.success("✅ Activo")
                else:
                    if col2.button("Activar", key=f"act_{c['id']}"): activar_contacto(c['id']); st.rerun()
                if col3.button("🗑️", key=f"del_{c['id']}"):
                    get_supabase().table("configuracion_pago").delete().eq("id", c['id']).execute(); st.rerun()
