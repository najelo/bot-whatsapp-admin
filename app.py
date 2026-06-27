import streamlit as st
import pandas as pd
import plotly.express as px  # <--- IMPORTANTE: Agregar esta línea arriba
from datetime import datetime, time as datetime_time, timedelta
import io

# Importaciones locales personalizadas
from auth_utils import verificar_login, get_supabase
from db_utils import obtener_configuraciones, guardar_configuracion, subir_archivo_al_storage, listar_archivos_storage, eliminar_regla
from pagos_utils import obtener_configuracion_pagos, guardar_contacto, activar_contacto

# Nuevos módulos divididos
from log_utils import obtener_metricas_del_dia, obtener_todos_los_logs
from pdf_utils import exportar_logs_a_pdf

st.set_page_config(page_title="Admin Bot", layout="wide")
supabase = get_supabase()

# ... (Todo tu código de login, diálogos y tabs hasta llegar al tab3) ...

    # --- TAB 3: LOGS / HISTORIAL ---
    with tab3:
        st.subheader("📋 Historial Completo de Verificaciones")
        st.caption("Lecturas de comprobantes procesadas por el bot.")
        
        lista_logs = obtener_todos_los_logs(supabase)
        if lista_logs:
            df = pd.DataFrame(lista_logs)
            
            # --- 🥧 GRÁFICO DE SALUD DEL SISTEMA (Moverlo aquí adentro) ---
            st.markdown("#### 🥧 Salud de las Transacciones")
            conteo_estados = df['estado'].value_counts()
            fig = px.pie(
                values=conteo_estados.values, 
                names=conteo_estados.index, 
                color=conteo_estados.index,
                color_discrete_map={'aprobado': '#2ec4b6', 'alerta': '#ff9f1c', 'error': '#e71d36'}
            )
            fig.update_layout(margin=dict(t=0, b=0, l=0, r=0), height=250)
            st.plotly_chart(fig, use_container_width=True)
            # -------------------------------------------------------------

            # 1. Ajuste matemático de zona horaria
            df["created_at"] = pd.to_datetime(df["created_at"]).dt.tz_localize(None) - timedelta(hours=4)
            fecha_defecto = df["created_at"].dt.date.max() if not df.empty else datetime.now().date()

            # Filtros interactivos
            col_f1, col_f2, col_f3 = st.columns(3)
            with col_f1: 
                f_inicio = st.date_input("Desde", fecha_defecto, key="log_f_ini")
            with col_f2: 
                f_fin = st.date_input("Hasta", fecha_defecto, key="log_f_fin")
            with col_f3: 
                f_estado = st.selectbox("Filtrar por Estado", ["Todos", "Aprobado", "Alerta", "Error"], key="log_f_est")

            ini_dt = datetime.combine(f_inicio, datetime_time.min)
            fn_dt = datetime.combine(f_fin, datetime_time.max)
            df_filtrado = df[(df["created_at"] >= ini_dt) & (df["created_at"] <= fn_dt)]

            if f_estado != "Todos":
                df_filtrado = df_filtrado[df_filtrado["estado"].astype(str).str.strip().str.lower() == f_estado.lower()]

            # Gráfico de Tendencia por Hora
            st.markdown("#### 📊 Tendencia de Pagos por Hora (Rango Filtrado)")
            # ... (Resto de tu lógica de gráficos y tablas) ...
