import streamlit as st
import uuid
from auth_utils import verificar_login, get_supabase
from db_utils import (
    obtener_configuraciones, guardar_configuracion, 
    eliminar_configuracion, guardar_palabra_individual,
    obtener_todas_las_respuestas
)
from pagos_utils import obtener_configuracion_pagos, guardar_contacto, activar_contacto

st.set_page_config(page_title="Admin Bot", page_icon="🤖")

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
    st.title("🤖 Panel de Control del Bot")
    tab1, tab2 = st.tabs(["Configurar Bot", "Configurar Pagos"])
    
    with tab1:
        st.subheader("Nueva Regla de Respuesta")
        tipo = st.radio("Tipo de respuesta:", ["Texto", "PDF"])
        
        with st.form("nueva_regla", clear_on_submit=True):
            p = st.text_input("Palabras clave (separadas por coma)")
            if tipo == "Texto":
                res = st.text_area("Respuesta")
            else:
                res = st.text_input("Link del PDF (o URL de Supabase)")
            
            if st.form_submit_button("Guardar Regla"):
                guardar_configuracion(p, res)
                st.rerun()

        st.subheader("Reglas Guardadas")
        configuraciones = obtener_configuraciones()
        for conf in configuraciones:
            st.write(f"**{conf['palabra_clave']}**: {conf['respuestas']['contenido']}")

    with tab2:
        st.subheader("Registrar nuevos datos de pago")
        with st.form("form_contacto", clear_on_submit=True):
            col_a, col_b = st.columns(2)
            ced = col_a.text_input("Cédula Esperada")
            tel = col_b.text_input("Teléfono Esperado")
            if st.form_submit_button("➕ Registrar Datos"):
                guardar_contacto(ced, tel); st.rerun()

        st.divider()
        st.subheader("Seleccionar Registro Activo")
        contactos = obtener_configuracion_pagos()
        for i, c in enumerate(contactos):
            with st.container(border=True):
                col1, col2 = st.columns([4, 1])
                col1.markdown(f"**Cédula:** `{c['cedula_esperada']}`")
                
                if c['activo']: 
                    col2.success("✅ Activo")
                else:
                    if col2.button("Activar", key=f"btn_{c['id']}"):
                        activar_contacto(c['id']); st.rerun()

    if st.sidebar.button("Cerrar sesión"):
        st.session_state["logueado"] = False; st.rerun()
