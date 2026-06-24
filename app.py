import streamlit as st
from db_utils import obtener_configuraciones, guardar_configuracion, subir_archivo_al_storage
from pagos_utils import obtener_configuracion_pagos, guardar_contacto, activar_contacto
from auth_utils import get_supabase

st.set_page_config(page_title="Admin Bot", layout="wide")

# Diálogos de edición (se mantienen igual)
@st.dialog("Editar Regla")
def abrir_editor(conf):
    resp_data = conf.get('respuestas') or {}
    contenido_actual = resp_data.get('contenido', '')
    nueva_palabra = st.text_input("Palabra clave", value=conf.get('palabra_clave', ''))
    
    # Vista previa
    if isinstance(contenido_actual, str) and contenido_actual.startswith("http"):
        st.write("Vista previa multimedia activa")
    
    nuevo_contenido = st.text_area("Contenido", value=contenido_actual)
    if st.button("Guardar Cambios"):
        get_supabase().table("clientes").update({"palabra_clave": nueva_palabra}).eq("id", conf['id']).execute()
        get_supabase().table("respuestas").update({"contenido": nuevo_contenido}).eq("id", resp_data['id']).execute()
        st.rerun()

st.title("🤖 Panel de Control")
tab1, tab2 = st.tabs(["⚙️ Reglas", "💳 Pagos"])

with tab1:
    # Depuración: Ver si hay datos
    datos = obtener_configuraciones()
    if not datos:
        st.warning("⚠️ No se encontraron reglas. Verifica que la tabla 'clientes' tenga datos vinculados a 'respuestas'.")
    
    for conf in datos:
        with st.container(border=True):
            col1, col2 = st.columns([4, 1])
            col1.write(f"🔑 **{conf.get('palabra_clave')}**")
            if col2.button("✏️ Editar", key=f"edit_{conf['id']}"): abrir_editor(conf)

with tab2:
    for c in obtener_configuracion_pagos():
        with st.container(border=True):
            st.write(f"Cédula: {c.get('cedula_esperada')}")
            # ... resto del código de pagos
