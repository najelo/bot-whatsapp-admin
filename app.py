import streamlit as st
from auth_utils import get_supabase
from db_utils import obtener_configuraciones, guardar_configuracion, subir_archivo_al_storage
from pagos_utils import obtener_configuracion_pagos, guardar_contacto, activar_contacto

st.set_page_config(page_title="Admin Bot", layout="wide")

# --- DIÁLOGO EDICIÓN REGLAS ---
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

# --- DIÁLOGO EDICIÓN PAGOS ---
@st.dialog("Editar Pago")
def editar_pago(c):
    nueva_ced = st.text_input("Cédula", value=c.get('cedula_esperada', ''))
    nuevo_tel = st.text_input("Teléfono", value=c.get('telefono_esperado', ''))
    if st.button("Guardar Cambios"):
        get_supabase().table("configuracion_pago").update({"cedula_esperada": nueva_ced, "telefono_esperado": nuevo_tel}).eq("id", c['id']).execute()
        st.rerun()

st.title("🤖 Panel de Control")
tab1, tab2 = st.tabs(["⚙️ Reglas", "💳 Pagos"])

with tab1:
    with st.expander("➕ Nueva Regla"):
        palabras = st.text_input("Palabras clave (separadas por coma)")
        archivo = st.file_uploader("Subir multimedia (opcional)")
        res_texto = st.text_area("Respuesta texto")
        if st.button("Guardar"):
            contenido = subir_archivo_al_storage(archivo.getvalue(), archivo.name) if archivo else res_texto
            if contenido: guardar_configuracion(palabras, contenido); st.rerun()

    for conf in obtener_configuraciones():
        with st.container(border=True):
            c1, c2 = st.columns([4, 1])
            c1.write(f"🔑 **{conf.get('palabra_clave')}**")
            if c2.button("✏️", key=f"edit_{conf['id']}"): abrir_editor(conf)

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
            col3.button("✏️", key=f"ep_{c['id']}", on_click=editar_pago, args=(c,))
