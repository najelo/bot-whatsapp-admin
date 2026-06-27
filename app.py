import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, time as datetime_time, timedelta
import io

# Importaciones locales personalizadas
from auth_utils import verificar_login, get_supabase
from db_utils import obtener_configuraciones, guardar_configuracion, subir_archivo_al_storage, listar_archivos_storage, eliminar_regla
from pagos_utils import obtener_configuracion_pagos, guardar_contacto, activar_contacto
from log_utils import obtener_metricas_del_dia, obtener_todos_los_logs
from pdf_utils import exportar_logs_a_pdf

st.set_page_config(page_title="Admin Bot", layout="wide")
supabase = get_supabase()

# --- LOGIN ---
if "logueado" not in st.session_state: st.session_state["logueado"] = False
if not st.session_state["logueado"]:
    _, col_login, _ = st.columns([1, 1.2, 1])
    with col_login:
        st.markdown("<br><br>", unsafe_allow_html=True)
        with st.container(border=True):
            st.title("🔐 Iniciar Sesión")
            with st.form("login_form", border=False):
                user = st.text_input("Usuario")
                pwd = st.text_input("Contraseña", type="password")
                if st.form_submit_button("Entrar", type="primary"):
                    valido, msg = verificar_login(user, pwd)
                    if valido: st.session_state["logueado"] = True; st.rerun()
                    else: st.error(msg)
    st.stop()

# --- DIÁLOGOS Y ESTRUCTURA ---
@st.dialog("Editar Regla de Bot", width="large")
def abrir_editor(conf):
    resp_data = conf.get('respuestas') or {}
    contenido_actual = resp_data.get('contenido', '')
    nueva_palabra = st.text_input("Palabra clave", value=conf.get('palabra_clave', ''))
    col_select, col_upload = st.columns(2)
    with col_select:
        archivos = listar_archivos_storage()
        seleccion = st.selectbox("Cambiar por:", ["-- Mantener actual --"] + archivos)
    with col_upload:
        nuevo_archivo = st.file_uploader("Subir archivo NUEVO", type=["pdf", "png", "jpg", "webp", "mp4", "mp3"])
    if st.button("💾 Guardar Cambios"):
        final_content = subir_archivo_al_storage(nuevo_archivo.getvalue(), nuevo_archivo.name) if nuevo_archivo else (supabase.storage.from_("recetarios-helado").get_public_url(seleccion) if seleccion != "-- Mantener actual --" else contenido_actual)
        supabase.table("clientes").update({"palabra_clave": nueva_palabra}).eq("id", conf['id']).execute()
        supabase.table("respuestas").update({"contenido": final_content}).eq("id", resp_data['id']).execute()
        st.rerun()

col_izq, col_centro, col_der = st.columns([1, 4, 1])
with col_centro:
    st.title("🤖 Panel de Control")
    col_titulo_met, col_btn_refresh = st.columns([3, 1])
    with col_titulo_met: st.write("#### 📊 Actividad de Hoy")
    with col_btn_refresh:
        if st.button("🔄 Actualizar Métricas"): st.rerun()
            
    metricas = obtener_metricas_del_dia(supabase)
    with st.container(border=True):
        m1, m2, m3 = st.columns(3)
        m1.metric("💰 Verificado Hoy", metricas["monto"])
        m2.metric("🖼️ Capturas Leídas", metricas["procesados"])
        m3.metric("🚨 Alertas", metricas["alertas"])
            
    tab1, tab2, tab3 = st.tabs(["⚙️ Reglas del Bot", "💳 Gestión de Pagos", "📋 Historial de Logs"])

    with tab1:
        # Aquí va toda tu lógica original de Reglas...
        st.write("Gestiona tus reglas aquí...")

    with tab2:
        # Aquí va toda tu lógica original de Pagos...
        st.write("Gestiona tus pagos aquí...")

    with tab3:
        st.subheader("📋 Historial Completo de Verificaciones")
        lista_logs = obtener_todos_los_logs(supabase)
        if lista_logs:
            df = pd.DataFrame(lista_logs)
            
            # --- NUEVO GRÁFICO ---
            st.markdown("#### 🥧 Salud de las Transacciones")
            conteo = df['estado'].value_counts()
            fig = px.pie(values=conteo.values, names=conteo.index, 
                         color_discrete_map={'aprobado': '#2ec4b6', 'alerta': '#ff9f1c', 'error': '#e71d36'})
            fig.update_layout(margin=dict(t=0, b=0, l=0, r=0), height=250)
            st.plotly_chart(fig, use_container_width=True)
            
            # Tu lógica de filtros, botones y tablas que tenías antes...
            st.dataframe(df, use_container_width=True)
