import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import io

# Importaciones locales
from auth_utils import verificar_login, get_supabase
from db_utils import obtener_configuraciones, guardar_configuracion, subir_archivo_al_storage, listar_archivos_storage, eliminar_regla
from pagos_utils import obtener_configuracion_pagos, guardar_contacto, activar_contacto
from log_utils import obtener_metricas_del_dia, obtener_todos_los_logs
from pdf_utils import exportar_logs_a_pdf

st.set_page_config(page_title="Admin Bot", layout="wide")
supabase = get_supabase()

# --- 1. DIÁLOGOS DE EDICIÓN ---
@st.dialog("Editar Regla de Bot", width="large")
def abrir_editor(conf):
    resp_data = conf.get('respuestas') or {}
    contenido_actual = resp_data.get('contenido', '')
    st.markdown(f"### ✏️ Editando: `{conf.get('palabra_clave')}`")
    nueva_palabra = st.text_input("Palabra clave", value=conf.get('palabra_clave', ''))
    st.write(f"📂 Archivo actual: [Link]({contenido_actual})")
    
    col_select, col_upload = st.columns(2)
    with col_select:
        archivos = listar_archivos_storage()
        seleccion = st.selectbox("Cambiar por:", ["-- Mantener actual --"] + archivos)
    with col_upload:
        nuevo_archivo = st.file_uploader("Subir archivo NUEVO", type=["pdf", "png", "jpg", "mp4", "mp3"])
    
    if st.button("💾 Guardar Cambios", type="primary"):
        final_content = subir_archivo_al_storage(nuevo_archivo.getvalue(), nuevo_archivo.name) if nuevo_archivo else (supabase.storage.from_("recetarios-helado").get_public_url(seleccion) if seleccion != "-- Mantener actual --" else contenido_actual)
        supabase.table("clientes").update({"palabra_clave": nueva_palabra}).eq("id", conf['id']).execute()
        supabase.table("respuestas").update({"contenido": final_content}).eq("id", resp_data['id']).execute()
        st.rerun()

@st.dialog("Editar Cuenta de Pago", width="medium")
def abrir_editor_pago(cuenta):
    nueva_cedula = st.text_input("Nueva Cédula", value=cuenta.get('cedula_esperada', ''))
    nuevo_telefono = st.text_input("Nuevo Teléfono", value=cuenta.get('telefono_esperado', ''))
    if st.button("💾 Guardar Cambios"):
        supabase.table("configuracion_pago").update({"cedula_esperada": nueva_cedula, "telefono_esperado": nuevo_telefono}).eq("id", cuenta['id']).execute()
        st.rerun()

# --- 2. LOGIN ---
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
                    if verificar_login(user, pwd)[0]: st.session_state["logueado"] = True; st.rerun()
    st.stop()

# --- 3. ESTRUCTURA PRINCIPAL ---
col_izq, col_centro, col_der = st.columns([1, 4, 1])
with col_centro:
    h1, h2 = st.columns([4, 1])
    h1.title("🤖 Panel de Control")
    if h2.button("Cerrar sesión"): st.session_state.update(logueado=False); st.rerun()

    tab1, tab2, tab3 = st.tabs(["⚙️ Reglas", "💳 Pagos", "📋 Historial"])
with tab1:
        # FORMULARIO DE CREACIÓN (REGLAS)
        with st.expander("➕ Crear Nueva Regla"):
            with st.form("form_regla", clear_on_submit=True):
                palabra = st.text_input("Palabra clave")
                archivo = st.file_uploader("Archivo")
                if st.form_submit_button("Crear Regla"):
                    guardar_configuracion(palabra, archivo)
                    st.rerun()
        # Lista existente
        for conf in obtener_configuraciones():
            if st.button(f"✏️ Editar {conf['palabra_clave']}", key=f"e_{conf['id']}"): abrir_editor(conf)

    with tab2:
        # FORMULARIO DE CREACIÓN (PAGOS)
        with st.expander("➕ Registrar Nuevo Receptor"):
            with st.form("form_pago", clear_on_submit=True):
                c, t = st.text_input("Cédula"), st.text_input("Teléfono")
                if st.form_submit_button("Registrar"):
                    guardar_contacto(c, t)
                    st.rerun()
        # Lista existente
        for c in obtener_configuracion_pagos():
            with st.container(border=True):
                st.write(f"💳 {c['cedula_esperada']}")
                if st.button(f"✏️ Editar", key=f"p_{c['id']}"): abrir_editor_pago(c)
    with tab3:
        st.subheader("📋 Historial")
        lista_logs = obtener_todos_los_logs(supabase)
        if lista_logs:
            df = pd.DataFrame(lista_logs)
            df["created_at"] = pd.to_datetime(df["created_at"]).dt.tz_localize(None) - timedelta(hours=4)
            
            # Filtro fechas
            c_f1, c_f2 = st.columns(2)
            f_ini = c_f1.date_input("Inicio", datetime.now() - timedelta(days=7))
            f_fin = c_f2.date_input("Fin", datetime.now())
            
            df_filt = df[(df["created_at"].dt.date >= f_ini) & (df["created_at"].dt.date <= f_fin)]
            
            st.dataframe(df_filt, use_container_width=True, hide_index=True)
            st.download_button("📊 Descargar Excel", data=io.BytesIO(), file_name="logs.xlsx")
