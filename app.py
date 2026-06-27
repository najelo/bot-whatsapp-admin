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

# --- ESTRUCTURA ---
col_izq, col_centro, col_der = st.columns([1, 4, 1])
with col_centro:
    st.title("🤖 Panel de Control")
    metricas = obtener_metricas_del_dia(supabase)
    with st.container(border=True):
        m1, m2, m3 = st.columns(3)
        m1.metric("💰 Verificado Hoy", metricas["monto"])
        m2.metric("🖼️ Capturas Leídas", metricas["procesados"])
        m3.metric("🚨 Alertas", metricas["alertas"])

    tab1, tab2, tab3 = st.tabs(["⚙️ Reglas del Bot", "💳 Gestión de Pagos", "📋 Historial de Logs"])

    with tab1:
        # FORMULARIO NUEVA REGLA
        with st.expander("➕ Nueva Regla"):
            with st.form("nueva_regla_form", border=False):
                palabras = st.text_input("Palabra clave")
                archivo = st.file_uploader("Subir archivo (opcional)", type=["pdf", "png", "jpg", "mp4", "mp3"])
                res_texto = st.text_area("Respuesta texto")
                if st.form_submit_button("Guardar Regla", type="primary"):
                    cont = subir_archivo_al_storage(archivo.getvalue(), archivo.name) if archivo else res_texto
                    guardar_configuracion(palabras, cont)
                    st.rerun()
        
        st.write("#### 🔑 Reglas existentes")
        for conf in obtener_configuraciones():
            with st.container(border=True):
                st.write(f"🔑 **{conf.get('palabra_clave')}**")

    with tab2:
        # FORMULARIO NUEVO PAGO
        with st.expander("➕ Registrar Nuevo Receptor"):
            with st.form("nuevo_pago_form", clear_on_submit=True):
                c1, c2 = st.columns(2)
                ced = c1.text_input("Cédula")
                tel = c2.text_input("Teléfono")
                if st.form_submit_button("Registrar Pago Móvil"):
                    guardar_contacto(ced, tel)
                    st.rerun()
        
        st.write("#### 📋 Cuentas Registradas")
        for c in obtener_configuracion_pagos():
            with st.container(border=True):
                st.write(f"💳 **Cédula:** `{c.get('cedula_esperada')}` | **Tel:** `{c.get('telefono_esperado')}`")

    with tab3:
        st.subheader("📋 Historial Completo")
        lista_logs = obtener_todos_los_logs(supabase)
        if lista_logs:
            df = pd.DataFrame(lista_logs)
            
            # Gráfico de salud
            st.markdown("#### 🥧 Salud de las Transacciones")
            conteo = df['estado'].value_counts()
            fig = px.pie(values=conteo.values, names=conteo.index, 
                         color_discrete_map={'aprobado': '#2ec4b6', 'alerta': '#ff9f1c', 'error': '#e71d36'})
            fig.update_layout(margin=dict(t=0, b=0, l=0, r=0), height=250)
            st.plotly_chart(fig, use_container_width=True)
            
            # Tabla
            st.dataframe(df, use_container_width=True)
