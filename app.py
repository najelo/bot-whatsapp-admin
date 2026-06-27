import streamlit as st
import pandas as pd
from datetime import datetime, time as datetime_time
# Asegúrate de importar tus utilidades de Supabase y autenticación
from auth_utils import get_supabase  
import log_utils

# 1. CONFIGURACIÓN DE LA PÁGINA (Debe ser lo primero en el script)
st.set_page_config(
    page_title="Panel de Control - Bot WhatsApp",
    page_icon="📊",
    layout="wide"
)

# Inicializar cliente de Supabase
supabase = get_supabase()

# ==========================================
# BARRA LATERAL (SIDEBAR)
# ==========================================
st.sidebar.title("🤖 WhatsApp Admin")
st.sidebar.markdown("---")

# Filtro de Rango de Fechas
st.sidebar.subheader("📅 Rango de Fechas")
fecha_inicio = st.sidebar.date_input("Desde", datetime.now().date())
fecha_fin = st.sidebar.date_input("Hasta", datetime.now().date())

st.sidebar.markdown("---")

# Selector de Estado para la Tabla
st.sidebar.subheader("🔍 Filtrar Tabla por Estado")
estado_filtro = st.sidebar.selectbox(
    "Selecciona un estado:",
    ["Todos", "Aprobado", "Alerta", "Error"]
)

st.sidebar.markdown("---")

# Botón Rojo de Cerrar Sesión (Usa el tipo primary, configurado en config.toml)
if st.sidebar.button("🔒 Cerrar Sesión", type="primary", use_container_width=True):
    st.session_state.clear()
    st.rerun()

# ==========================================
# CUERPO PRINCIPAL DEL PANEL
# ==========================================
st.title("📈 Dashboard de Verificación de Pagos")
st.markdown(f"Monitoreo de transacciones desde **{fecha_inicio}** hasta **{fecha_fin}**")
st.markdown("---")

# Cargar todos los logs reales desde Supabase usando tu función corregida
logs_reales = log_utils.obtener_todos_los_logs(supabase)

if not logs_reales:
    st.info("No se encontraron registros en la base de datos para este rango.")
else:
    # Convertir a DataFrame de Pandas para manipular los datos fácilmente
    df = pd.DataFrame(logs_reales)
    
    # Convertir columna de fecha a objeto datetime de Python y normalizar zonas
    df["created_at"] = pd.to_datetime(df["created_at"]).dt.tz_localize(None)
    
    # Filtrar el DataFrame según el rango de fechas elegido en la barra lateral
    inicio_dt = datetime.combine(fecha_inicio, datetime_time.min)
    fin_dt = datetime.combine(fecha_fin, datetime_time.max)
    df_filtrado = df[(df["created_at"] >= inicio_dt) & (df["created_at"] <= fin_dt)]

    # ==========================================
    # SECCIÓN: TARJETAS DE MÉTRICAS
    # ==========================================
    # Cálculos dinámicos basados en los filtros
    aprobados = df_filtrado[df_filtrado["estado"] == "aprobado"]
    alertas = df_filtrado[df_filtrado["estado"] == "alerta"]
    errores = df_filtrado[df_filtrado["estado"] == "error"]
    
    monto_total = aprobados["monto"].sum()
    monto_retenido = alertas["monto"].sum()  # Nueva métrica recomendada
    total_procesados = len(df_filtrado)

    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(label="💰 Monto Procesado", value=f"Bs. {monto_total:,.2f}")
    with col2:
        st.metric(label="🛑 Monto Retenido / Alertas", value=f"Bs. {monto_retenido:,.2f}")
    with col3:
        st.metric(label="✅ Capturas Leídas", value=str(total_procesados))
    with col4:
        st.metric(label="🚨 Alertas Totales", value=str(len(alertas) + len(errores)))

    st.markdown("---")

    # ==========================================
    # SECCIÓN: GRÁFICO DE TENDENCIA POR HORA (EJE FIJO)
    # ==========================================
    st.subheader("📊 Tendencia de Pagos por Hora")
    if not aprobados.empty:
        # Agrupar los montos aprobados por hora del día
        aprobados["Hora"] = aprobados["created_at"].dt.hour
        grafico_data = aprobados.groupby("Hora")["monto"].sum().reset_index()
        
        # Crear estructura fija de 24 horas para evitar deformaciones visuales
        todas_las_horas = pd.DataFrame({"Hora": range(24)})
        grafico_completo = pd.merge(todas_las_horas, grafico_data, on="Hora", how="left").fillna(0)
        
        # Graficar usando la herramienta nativa de barras de Streamlit
        st.bar_chart(data=grafico_completo, x="Hora", y="monto", color="#25D366")
    else:
        st.caption("No hay suficientes datos aprobados en este rango para armar el gráfico.")

    st.markdown("---")

    # ==========================================
    # SECCIÓN: TABLA DE HISTORIAL FILTRADA & EXCEL
    # ==========================================
    st.subheader("📋 Historial de Transacciones Recientes")
    
    # Buscador por texto para el teléfono
    busqueda_telefono = st.text_input("🔍 Buscar por número de teléfono (Ej: 58412...):", "")
    
    # Aplicar el filtro de estado de la barra lateral al DataFrame de la tabla
    if estado_filtro != "Todos":
        df_tabla = df_filtrado[df_filtrado["estado"] == estado_filtro.lower()]
    else:
        df_tabla = df_filtrado

    # Aplicar el filtro del buscador por teléfono si tiene texto
    if busqueda_telefono.strip() != "":
        df_tabla = df_tabla[df_tabla["phone"].astype(str).str.contains(busqueda_telefono.strip())]

    # Formatear la visualización del DataFrame para el usuario
    df_visual = df_tabla.copy()
    if not df_visual.empty:
        df_visual["created_at"] = df_visual["created_at"].dt.strftime("%Y-%m-%d %H:%M:%S")
        df_visual["monto"] = df_visual["monto"].map("Bs. {:,.2f}".format)
        
        # Mostrar la tabla interactiva en el dashboard
        st.dataframe(df_visual[["id", "created_at", "phone", "monto", "estado"]], use_container_width=True)

        # Botón para descargar a Excel (CSV)
        col_izq, col_der = st.columns([1, 5])
        with col_izq:
            csv_data = df_tabla.to_csv(index=False).encode("utf-8")
            st.download_button(
                label="📥 Descargar Reporte (CSV)",
                data=csv_data,
                file_name=f"reporte_bot_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
                mime="text/csv",
                use_container_width=True
            )
    else:
        st.caption("No hay datos para mostrar con los filtros seleccionados.")
