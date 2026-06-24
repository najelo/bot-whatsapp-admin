import streamlit as st
from db_utils import obtener_configuraciones, guardar_configuracion, subir_archivo_al_storage
from pagos_utils import obtener_configuracion_pagos, guardar_contacto, activar_contacto

st.set_page_config(page_title="Admin Bot", layout="wide")
st.title("🤖 Panel de Control del Bot")

tab1, tab2 = st.tabs(["⚙️ Bot (Reglas)", "💳 Pagos"])

with tab1:
    st.subheader("Nueva Regla Multimedia")
    tipo = st.radio("¿Qué deseas subir?", ["Texto", "Imagen", "Audio", "PDF"])
    
    with st.form("form_regla", clear_on_submit=True):
        palabra = st.text_input("Palabra clave")
        
        if tipo == "Texto":
            res = st.text_area("Respuesta")
            if st.form_submit_button("Guardar Texto"):
                guardar_configuracion(palabra, res); st.rerun()
        else:
            archivo = st.file_uploader("Sube el archivo", type=["jpg", "png", "mp3", "ogg", "pdf"])
            if st.form_submit_button("Guardar Multimedia"):
                if archivo:
                    url = subir_archivo_al_storage(archivo.getvalue(), archivo.name)
                    if url:
                        guardar_configuracion(palabra, url)
                        st.success("Archivo subido con éxito")
                        st.rerun()

    st.divider()
    st.subheader("Reglas Activas")
    for conf in obtener_configuraciones():
        with st.container(border=True):
            contenido = conf.get('respuestas', {}).get('contenido', 'Sin contenido')
            st.write(f"🔑 **{conf.get('palabra_clave')}**")
            st.caption(f"Contenido: {contenido}")

with tab2:
    st.subheader("Gestión de Pagos")
    with st.form("form_pago"):
        ced = st.text_input("Cédula")
        tel = st.text_input("Teléfono")
        if st.form_submit_button("Registrar"):
            guardar_contacto(ced, tel); st.rerun()
            
    for c in obtener_configuracion_pagos():
        with st.container(border=True):
            st.write(f"Cédula: {c.get('cedula_esperada')}")
            if c.get('activo'):
                st.success("✅ Activo")
            elif st.button("Activar", key=f"act_{c['id']}"):
                activar_contacto(c['id']); st.rerun()
