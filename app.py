import streamlit as st
from db_utils import obtener_configuraciones, guardar_configuracion, subir_archivo_al_storage
from pagos_utils import obtener_configuracion_pagos, guardar_contacto, activar_contacto
from auth_utils import get_supabase

st.set_page_config(page_title="Admin Bot", layout="wide")

# --- DIÁLOGO DE EDICIÓN REGLAS ---
@st.dialog("Editar Regla")
def abrir_editor(conf):
    resp_data = conf.get('respuestas') or {}
    contenido_actual = resp_data.get('contenido', '')
    nueva_palabra = st.text_input("Palabra clave", value=conf.get('palabra_clave', ''))
    nuevo_contenido = st.text_area("Contenido", value=contenido_actual)
    if st.button("Guardar Cambios"):
        get_supabase().table("clientes").update({"palabra_clave": nueva_palabra}).eq("id", conf['id']).execute()
        get_supabase().table("respuestas").update({"contenido": nuevo_contenido}).eq("id", resp_data['id']).execute()
        st.rerun()

# --- DIÁLOGO DE EDICIÓN PAGOS ---
@st.dialog("Editar Datos de Pago")
def editar_pago(c):
    nueva_ced = st.text_input("Cédula", value=c.get('cedula_esperada', ''))
    nuevo_tel = st.text_input("Teléfono", value=c.get('telefono_esperado', ''))
    if st.button("Guardar Cambios"):
        get_supabase().table("configuracion_pago").update({"cedula_esperada": nueva_ced, "telefono_esperado": nuevo_tel}).eq("id", c['id']).execute()
        st.rerun()

st.title("🤖 Panel de Control del Bot")
tab1, tab2 = st.tabs(["⚙️ Bot (Reglas)", "💳 Pagos"])

with tab1:
    tipo = st.radio("Tipo:", ["Texto", "Multimedia"])
    with st.form("form_regla", clear_on_submit=True):
        palabra = st.text_input("Palabra clave")
        if tipo == "Texto":
            res = st.text_area("Respuesta")
            if st.form_submit_button("Guardar"): guardar_configuracion(palabra, res); st.rerun()
        else:
            archivo = st.file_uploader("Archivo", type=["jpg", "png", "mp3", "ogg", "pdf"])
            if st.form_submit_button("Guardar"):
                url = subir_archivo_al_storage(archivo.getvalue(), archivo.name) if archivo else None
                if url: guardar_configuracion(palabra, url); st.rerun()
    for conf in obtener_configuraciones():
        with st.container(border=True):
            c1, c2 = st.columns([4, 1])
            c1.write(f"🔑 **{conf.get('palabra_clave')}**")
            if c2.button("✏️ Editar", key=f"edit_{conf['id']}"): abrir_editor(conf)

with tab2:
    with st.form("form_pago"):
        ced, tel = st.text_input("Cédula"), st.text_input("Teléfono")
        if st.form_submit_button("Registrar"): guardar_contacto(ced, tel); st.rerun()
    for c in obtener_configuracion_pagos():
        with st.container(border=True):
            col1, col2, col3 = st.columns([3, 1, 1])
            col1.write(f"Cédula: {c.get('cedula_esperada')} | Tel: {c.get('telefono_esperado')}")
            if c.get('activo'): col2.success("✅ Activo")
            elif col2.button("Activar", key=f"act_{c['id']}"): activar_contacto(c['id']); st.rerun()
            col3.button("✏️ Editar", key=f"edit_p_{c['id']}", on_click=editar_pago, args=(c,))
