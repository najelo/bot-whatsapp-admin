import streamlit as st
import pandas as pd
from datetime import datetime, time as datetime_time, timedelta
import io

from auth_utils import verificar_login, get_supabase
from db_utils import obtener_configuraciones, guardar_configuracion, subir_archivo_al_storage, listar_archivos_storage, eliminar_regla
from pagos_utils import obtener_configuracion_pagos, guardar_contacto, activar_contacto
from log_utils import obtener_metricas_del_dia, obtener_todos_los_logs
from pdf_utils import exportar_logs_a_pdf

st.set_page_config(page_title="Admin Bot", layout="wide")
supabase = get_supabase()

# --- LOGIN (Mantenido igual) ---
if "logueado" not in st.session_state: st.session_state["logueado"] = False
if not st.session_state["logueado"]:
    # ... (Tu lógica de login original se mantiene)
    st.stop()

# --- ESTRUCTURA PRINCIPAL ---
col_izq, col_centro, col_der = st.columns([1, 4, 1])
with col_centro:
    tab1, tab2, tab3 = st.tabs(["⚙️ Reglas", "💳 Pagos", "📋 Historial"])

    with tab1:
        # Aquí va tu lógica de reglas original
        pass

    with tab2:
        # Aquí va tu lógica de pagos original
        pass

    # --- PESTAÑA LOGS (RESTAURADA EXACTAMENTE COMO EN TU ARCHIVO) ---
    with tab3:
        st.subheader("📋 Historial de Transacciones")
        lista_logs = obtener_todos_los_logs(supabase)
        
        if lista_logs:
            df = pd.DataFrame(lista_logs)
            df["created_at"] = pd.to_datetime(df["created_at"]).dt.tz_localize(None) - timedelta(hours=4)
            
            # Filtros que tenías en tu archivo original
            col_f1, col_f2 = st.columns(2)
            fecha_inicio = col_f1.date_input("Fecha Inicio", value=datetime.now() - timedelta(days=7))
            fecha_fin = col_f2.date_input("Fecha Fin", value=datetime.now())
            
            mask = (df["created_at"].dt.date >= fecha_inicio) & (df["created_at"].dt.date <= fecha_fin)
            df_filtrado = df.loc[mask]
            
            # Botón Excel que tenías en tu archivo
            buffer_excel = io.BytesIO()
            with pd.ExcelWriter(buffer_excel) as writer:
                df_filtrado.to_excel(writer, index=False, sheet_name='Historial')
            
            st.download_button(
                label="📊 Descargar Filtro en Excel",
                data=buffer_excel.getvalue(),
                file_name=f"historial_{datetime.now().strftime('%Y%m%d')}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True
            )
            
            # Tabla interactiva original
            df_visual = df_filtrado.copy()
            df_visual["created_at"] = df_visual["created_at"].dt.strftime("%Y-%m-%d %H:%M:%S")
            st.dataframe(
                df_visual, 
                column_config={"monto": st.column_config.NumberColumn("Monto", format="Bs. %.2f")},
                use_container_width=True, hide_index=True
            )
        else:
            st.info("No hay registros en el historial.")
