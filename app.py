import streamlit as st
import pandas as pd
import plotly.express as px
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

# --- ESTRUCTURA PRINCIPAL ---
col_izq, col_centro, col_der = st.columns([1, 4, 1])
with col_centro:
    # Cabecera con botón de salir
    head1, head2 = st.columns([4, 1])
    with head1: st.title("🤖 Panel de Control")
    with head2:
        st.markdown("<br>", unsafe_allow_html=True)
        st.button("Cerrar sesión", on_click=lambda: st.session_state.update(logueado=False), type="secondary", use_container_width=True)
    
    metricas = obtener_metricas_del_dia(supabase)
    with st.container(border=True):
        m1, m2, m3 = st.columns(3)
        m1.metric("💰 Verificado Hoy", metricas["monto"])
        m2.metric("🖼️ Capturas Leídas", metricas["procesados"])
        m3.metric("🚨 Alertas", metricas["alertas"])

    tab1, tab2, tab3 = st.tabs(["⚙️ Reglas del Bot", "💳 Gestión de Pagos", "📋 Historial de Logs"])

    with tab1:
        # (Aquí va tu lógica de reglas...)
        st.write("Gestiona tus reglas aquí")

    with tab2:
        # (Aquí va tu lógica de pagos...)
        st.write("Gestiona tus pagos aquí")

    with tab3:
        st.subheader("📋 Historial Completo de Verificaciones")
        lista_logs = obtener_todos_los_logs(supabase)
        if lista_logs:
            df = pd.DataFrame(lista_logs)
            
            # Gráfico de Salud
            st.markdown("#### 🥧 Salud de las Transacciones")
            conteo = df['estado'].value_counts()
            fig = px.pie(values=conteo.values, names=conteo.index, 
                         color_discrete_map={'aprobado': '#2ec4b6', 'alerta': '#ff9f1c', 'error': '#e71d36'})
            fig.update_layout(margin=dict(t=0, b=0, l=0, r=0), height=250)
            st.plotly_chart(fig, use_container_width=True)

            # Filtros y Tabla
            df["created_at"] = pd.to_datetime(df["created_at"]).dt.tz_localize(None) - timedelta(hours=4)
            st.dataframe(df, use_container_width=True)

            # --- BOTONES DE DESCARGA (Recuperados) ---
            col_d1, col_d2 = st.columns(2)
            with col_d1:
                pdf_data = exportar_logs_a_pdf(lista_logs)
                st.download_button("📥 Descargar Todo en PDF", pdf_data, file_name="logs.pdf", mime="application/pdf", use_container_width=True)
            with col_d2:
                buffer = io.BytesIO()
                with pd.ExcelWriter(buffer) as writer: df.to_excel(writer, index=False)
                st.download_button("📊 Descargar en Excel", buffer.getvalue(), file_name="logs.xlsx", use_container_width=True)
        else:
            st.info("No hay registros.")
