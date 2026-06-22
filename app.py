import streamlit as st
from pypdf import PdfReader
from auth_utils import verificar_login, get_supabase
from db_utils import (
    obtener_configuraciones, guardar_configuracion, 
    eliminar_configuracion, guardar_palabra_individual,
    obtener_todas_las_respuestas, guardar_respuesta_pdf
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
        with st.form("nueva_config", clear_on_submit=True):
            c = st.text_input("Palabras clave (separadas por coma)")
            r = st.text_area("Respuesta automática")
            if st.form_submit_button("Guardar"):
                exito, msg = guardar_configuracion(c, r)
                if exito: st.success(msg); st.rerun()
                else: st.error(msg)

        st.divider()
        st.subheader("Subir PDF como respuesta")
        archivo_pdf = st.file_uploader("Selecciona un PDF", type="pdf")
        if archivo_pdf:
            reader = PdfReader(archivo_pdf)
            texto_pdf = "\n".join([page.extract_text() for page in reader.pages])
            st.text_area("Vista previa:", value=texto_pdf[:500] + "...", disabled=True)
            palabras_pdf = st.text_input("Palabras clave para este PDF:")
            if st.button("Guardar PDF"):
                exito, r_id = guardar_respuesta_pdf(texto_pdf)
                if exito:
                    for p in palabras_pdf.split(','): guardar_palabra_individual(p.strip(), r_id)
                    st.success("PDF guardado correctamente"); st.rerun()

        st.divider()
        st.subheader("Reglas Guardadas")
        configuraciones = obtener_configuraciones()
        agrupadas = {}
        for conf in configuraciones:
            p = conf['palabra_clave']
            if p not in agrupadas: agrupadas[p] = {"respuestas": [], "ids": []}
            agrupadas[p]["respuestas"].append(conf['respuestas']['contenido'])
            agrupadas[p]["ids"].append(conf['id'])

        for palabra, datos in agrupadas.items():
            with st.expander(f"Regla: {palabra}"):
                for res in datos["respuestas"]: st.info(res)
                if st.button(f"🗑️ Eliminar: {palabra}", key=f"del_{palabra}"):
                    for id_b in datos["ids"]: eliminar_configuracion(id_b)
                    st.rerun()
    
    with tab2:
        # ... (Mantener lógica de pagos igual)
        pass
