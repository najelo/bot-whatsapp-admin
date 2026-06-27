import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import io

from auth_utils import verificar_login, get_supabase
from db_utils import obtener_configuraciones, guardar_configuracion, subir_archivo_al_storage, listar_archivos_storage, eliminar_regla
from pagos_utils import obtener_configuracion_pagos, guardar_contacto, activar_contacto
from log_utils import obtener_metricas_del_dia, obtener_todos_los_logs
from pdf_utils import exportar_logs_a_pdf

st.set_page_config(page_title="Admin Bot", layout="wide")
supabase = get_supabase()

# --- DIÁLOGOS DE EDICIÓN ---
@st.dialog("Editar Regla de Bot", width="large")
def abrir_editor(conf):
    resp_data = conf.get('respuestas') or {}
    contenido_actual = resp_data.get('contenido', '')
    st.markdown(f"### ✏️ Editando: `{conf.get('palabra_clave')}`")
    nueva_palabra = st.text_input("Palabra clave", value=conf.get('palabra_clave', ''))
    if st.button("💾 Guardar"):
        supabase.table("clientes").update({"palabra_clave": nueva_palabra}).eq("id", conf['id']).execute()
        st.rerun()

@st.dialog("Editar Pago", width="medium")
def abrir_editor_pago(cuenta):
    nueva_cedula = st.text_input("Nueva Cédula", value=cuenta.get('cedula_esperada', ''))
    if st.button("💾 Guardar"):
        supabase.table("configuracion_pago").update({"cedula_esperada": nueva_cedula}).eq("id", cuenta['id']).execute()
        st.rerun()

# --- LOGIN ---
if "logueado" not in st.session_state: st.session_state["logueado"] = False
if not st.session_state["logueado"]:
    st.title("🔐 Iniciar Sesión")
    if st.button("Simular Login"): st.session_state["logueado"] = True; st.rerun()
    st.stop()

# --- ESTRUCTURA PRINCIPAL ---
col_izq, col_centro, col_der = st.columns([1, 4, 1])
with col_centro:
    tab1, tab2, tab3 = st.tabs(["⚙️ Reglas", "💳 Pagos", "📋 Historial"])

    with tab1:
        st.subheader("⚙️ Reglas")
        with st.expander("➕ Agregar Regla"):
            if st.button("Crear"): st.rerun()
        for conf in obtener_configuraciones():
            if st.button(f"✏️ Editar {conf.get('palabra_clave')}", key=f"e{conf['id']}"): abrir_editor(conf)

    with tab2:
        st.subheader("💳 Pagos")
        with st.expander("➕ Registrar Pago"):
            if st.button("Registrar"): st.rerun()
        for c in obtener_configuracion_pagos():
            if st.button(f"✏️ Editar {c.get('cedula_esperada')}", key=f"p{c['id']}"): abrir_editor_pago(c)

    with tab3:
        st.subheader("📋 Historial")
        lista_logs = obtener_todos_los_logs(supabase)
        if lista_logs:
            st.dataframe(pd.DataFrame(lista_logs))
