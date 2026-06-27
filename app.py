import streamlit as st
import pandas as pd
from datetime import datetime, time as datetime_time, timedelta
import io

# Importaciones locales
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
    col_select, col_upload = st.columns(2)
    with col_select:
        archivos = listar_archivos_storage()
        seleccion = st.selectbox("Cambiar por:", ["-- Mantener actual --"] + archivos)
    with col_upload:
        nuevo_archivo = st.file_uploader("Subir archivo NUEVO", type=["pdf", "png", "jpg", "mp4", "mp3"])
    if st.button("💾 Guardar Cambios"):
        final_content = subir_archivo_al_storage(nuevo_archivo.getvalue(), nuevo_archivo.name) if nuevo_archivo else (supabase.storage.from_("recetarios-helado").get_public_url(seleccion) if seleccion != "-- Mantener actual --" else contenido_actual)
        supabase.table("clientes").update({"palabra_clave": nueva_palabra}).eq("id", conf['id']).execute()
        supabase.table("respuestas").update({"contenido": final_content}).eq("id", resp_data['id']).execute()
        st.rerun()

@st.dialog("Editar Cuenta", width="medium")
def abrir_editor_pago(cuenta):
    nueva_cedula = st.text_input("Nueva Cédula", value=cuenta.get('cedula_esperada', ''))
    nuevo_telefono = st.text_input("Nuevo Teléfono", value=cuenta.get('telefono_esperado', ''))
    if st.button("💾 Guardar"):
        supabase.table("configuracion_pago").update({"cedula_esperada": nueva_cedula, "telefono_esperado": nuevo_telefono}).eq("id", cuenta['id']).execute()
        st.rerun()

# --- LOGIN ---
if "logueado" not in st.session_state: st.session_state["logueado"] = False
if not st.session_state["logueado"]:
    _, col_login, _ = st.columns([1, 1.2, 1])
    with col_login:
        with st.container(border=True):
            st.title("🔐 Iniciar Sesión")
            with st.form("login_form"):
                user = st.text_input("Usuario")
                pwd = st.text_input("Contraseña", type="password")
                if st.form_submit_button("Entrar", type="primary"):
                    valido, msg = verificar_login(user, pwd)
                    if valido: st.session_state["logueado"] = True; st.rerun()
                    else: st.error(msg)
    st.stop()

# --- ESTRUCTURA ---
col_izq, col_centro, col_der = st.columns([1, 4, 1])
with col_centro:
    h1, h2 = st.columns([4, 1])
    h1.title("🤖 Panel de Control")
    if h2.button("Cerrar sesión"): st.session_state.update(logueado=False); st.rerun()

    metricas = obtener_metricas_del_dia(supabase)
    with st.container(border=True):
        m1, m2, m3 = st.columns(3)
        m1.metric("💰 Verificado Hoy", metricas["monto"])
        m2.metric("🖼️ Capturas Leídas", metricas["procesados"])
        m3.metric("🚨 Alertas", metricas["alertas"])

    tab1, tab2, tab3 = st.tabs(["⚙️ Reglas", "💳 Pagos", "📋 Logs"])

    with tab1:
        # Aquí va tu formulario de reglas...
        for conf in obtener_configuraciones():
            with st.container(border=True):
                c1, c2 = st.columns([5, 1])
                c1.write(f"🔑 **{conf.get('palabra_clave')}**")
                if c2.button("✏️", key=f"e{conf['id']}"): abrir_editor(conf)

    with tab2:
        # Aquí va tu formulario de pagos...
        for c in obtener_configuracion_pagos():
            with st.container(border=True):
                c1, c2 = st.columns([5, 1])
                c1.write(f"💳 {c.get('cedula_esperada')} | {c.get('telefono_esperado')}")
                if c2.button("✏️", key=f"p{c['id']}"): abrir_editor_pago(c)

    with tab3:
        st.subheader("📋 Historial")
        busqueda = st.text_input("🔍 Buscar por teléfono")
        lista_logs = obtener_todos_los_logs(supabase)
        if lista_logs:
            df = pd.DataFrame(lista_logs)
            if busqueda: df = df[df["phone"].astype(str).str.contains(busqueda, na=False)]
            st.dataframe(df, use_container_width=True)
            
            c1, c2 = st.columns(2)
            c1.download_button("📥 PDF", exportar_logs_a_pdf(lista_logs), "logs.pdf")
            buffer = io.BytesIO()
            with pd.ExcelWriter(buffer) as writer: df.to_excel(writer, index=False)
            c2.download_button("📊 Excel", buffer.getvalue(), "logs.xlsx")
