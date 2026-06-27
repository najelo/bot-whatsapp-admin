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
    nueva_palabra = st.text_input("Palabra clave para el bot", value=conf.get('palabra_clave', ''))
    st.markdown("---")
    st.write("#### 📂 Archivo actual")
    st.markdown(f"[{contenido_actual}]({contenido_actual})")
    col_select, col_upload = st.columns(2)
    with col_select:
        archivos = listar_archivos_storage()
        seleccion = st.selectbox("Cambiar por:", ["-- Mantener actual --"] + archivos)
    with col_upload:
        nuevo_archivo = st.file_uploader("Subir archivo NUEVO", type=["pdf", "png", "jpg", "mp4", "mp3"])
    
    col_save, col_del = st.columns([3, 1])
    with col_save:
        if st.button("💾 Guardar Cambios", use_container_width=True, type="primary"):
            final_content = subir_archivo_al_storage(nuevo_archivo.getvalue(), nuevo_archivo.name) if nuevo_archivo else (supabase.storage.from_("recetarios-helado").get_public_url(seleccion) if seleccion != "-- Mantener actual --" else contenido_actual)
            supabase.table("clientes").update({"palabra_clave": nueva_palabra}).eq("id", conf['id']).execute()
            supabase.table("respuestas").update({"contenido": final_content}).eq("id", resp_data['id']).execute()
            st.rerun()
    with col_del:
        if st.button("🗑️ Borrar", use_container_width=True):
            if eliminar_regla(conf['id'], resp_data['id']): st.rerun()

@st.dialog("Editar Cuenta de Pago", width="medium")
def abrir_editor_pago(cuenta):
    nueva_cedula = st.text_input("Nueva Cédula", value=cuenta.get('cedula_esperada', ''))
    nuevo_telefono = st.text_input("Nuevo Teléfono", value=cuenta.get('telefono_esperado', ''))
    if st.button("💾 Guardar Cambios Cuenta", use_container_width=True, type="primary"):
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
                    if verificar_login(user, pwd)[0]: st.session_state["logueado"] = True; st.rerun()
    st.stop()

# --- ESTRUCTURA PRINCIPAL ---
col_izq, col_centro, col_der = st.columns([1, 4, 1])
with col_centro:
    h1, h2 = st.columns([4, 1])
    h1.title("🤖 Panel de Control")
    if h2.button("Cerrar sesión"): st.session_state.update(logueado=False); st.rerun()

    tab1, tab2, tab3 = st.tabs(["⚙️ Reglas", "💳 Pagos", "📋 Logs"])

    with tab1:
        for conf in obtener_configuraciones():
            with st.container(border=True):
                c1, c2 = st.columns([5, 1])
                c1.write(f"🔑 **{conf.get('palabra_clave')}**")
                if c2.button("✏️ Editar", key=f"e{conf['id']}"): abrir_editor(conf)

    with tab2:
        with st.expander("➕ Registrar Nuevo Receptor"):
            with st.form("nuevo_pago_form", clear_on_submit=True):
                c1, c2 = st.columns(2)
                ced, tel = c1.text_input("Cédula"), c2.text_input("Teléfono")
                if st.form_submit_button("Registrar"): guardar_contacto(ced, tel); st.rerun()
        
        for c in obtener_configuracion_pagos():
            with st.container(border=True):
                col1, col2 = st.columns([3, 1])
                col1.write(f"💳 **{c.get('cedula_esperada')}** | **{c.get('telefono_esperado')}**")
                col2.markdown(f"**{'🟢 Activo' if c.get('activo') else '🔴 Inactivo'}**")
                
                c_act, c_edit, c_del = st.columns(3)
                if not c.get('activo'):
                    if c_act.button("🚀 Activar", key=f"act_{c['id']}"): activar_contacto(c['id']); st.rerun()
                else: c_act.button("✨ Activo", disabled=True)
                
                if c_edit.button("✏️ Editar", key=f"edit_{c['id']}"): abrir_editor_pago(c)
                if c_del.button("🗑️ Eliminar", key=f"del_{c['id']}"): 
                    supabase.table("configuracion_pago").delete().eq("id", c['id']).execute(); st.rerun()

    with tab3:
        lista_logs = obtener_todos_logs = obtener_todos_logs = obtener_todos_los_logs(supabase)
        if lista_logs:
            df = pd.DataFrame(lista_logs)
            st.dataframe(df, use_container_width=True)
