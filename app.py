import streamlit as st
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
        st.subheader("Subir Recetario (PDF)")
        archivo_pdf = st.file_uploader("Selecciona el PDF", type="pdf")
        palabra_clave_pdf = st.text_input("Palabra clave para el recetario")

        if st.button("Subir al Storage y Guardar"):
            if archivo_pdf and palabra_clave_pdf:
                supabase = get_supabase()
                nombre_archivo = f"{palabra_clave_pdf.lower().replace(' ', '_')}.pdf"
                # Subir a Supabase Storage
                supabase.storage.from_("recetarios-helado").upload(nombre_archivo, archivo_pdf.getvalue(), {"content-type": "application/pdf"})
                url_publica = supabase.storage.from_("recetarios-helado").get_public_url(nombre_archivo)
                # Guardar link en tabla 'respuestas'
                guardar_configuracion(palabra_clave_pdf, url_publica)
                st.success("¡Recetario guardado!")

        st.divider()
        # ... (aquí va el resto de tu lógica original de tab1)
