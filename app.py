import streamlit as st
import pandas as pd
from datetime import datetime, time as datetime_time, timedelta
import io

# Importaciones locales personalizadas
from auth_utils import verificar_login, get_supabase
from pagos_utils import obtener_configuracion_pagos, guardar_contacto, activar_contacto

# Módulos del Motor de Flujos
from db_flow import obtener_todos_los_flujos, crear_nuevo_flujo, obtener_datos_lienzo

# Nuevos módulos divididos
from log_utils import obtener_metricas_del_dia, obtener_todos_los_logs
from pdf_utils import exportar_logs_a_pdf

st.set_page_config(page_title="Admin Bot", layout="wide")
supabase = get_supabase()

# --- LOGIN ---
if "logueado" not in st.session_state: 
    st.session_state["logueado"] = False

if not st.session_state["logueado"]:
    _, col_login, _ = st.columns([1, 1.2, 1])
    with col_login:
        st.markdown("<br><br>", unsafe_allow_html=True)
        with st.container(border=True):
            st.title("🔐 Iniciar Sesión")
            with st.form("login_form", border=False):
                user = st.text_input("Usuario")
                pwd = st.text_input("Contraseña", type="password")
                if st.form_submit_button("Entrar", width='stretch', type="primary"):
                    valido, msg = verificar_login(user, pwd)
                    if valido: 
                        st.session_state["logueado"] = True
                        st.rerun()
                    else: 
                        st.error(msg)
    st.stop()

# --- DIÁLOGOS GLOBALES ---
@st.dialog("Editar Cuenta de Pago", width="medium")
def abrir_editor_pago(cuenta):
    st.markdown(f"### ✏️ Editando Receptor ID: `{cuenta.get('id')}`")
    nueva_cedula = st.text_input("Nueva Cédula", value=cuenta.get('cedula_esperada', ''))
    nuevo_telefono = st.text_input("Nuevo Teléfono", value=cuenta.get('telefono_esperado', ''))
    st.markdown("---")
    if st.button("💾 Guardar Cambios Cuenta", width='stretch', type="primary"):
        try:
            supabase.table("configuracion_pago").update({"cedula_esperada": nueva_cedula, "telefono_esperado": nuevo_telefono}).eq("id", cuenta['id']).execute()
            st.toast("Cuenta actualizada con éxito", icon="✅")
            st.rerun()
        except Exception as e: 
            st.error(f"Error al actualizar: {e}")

# --- ESTRUCTURA PRINCIPAL DE LA PANTALLA ---
col_izq, col_centro, col_der = st.columns([1, 4, 1])

with col_centro:
    head1, head2 = st.columns([4, 1])
    with head1: 
        st.title("🤖 Panel de Control")
    with head2:
        st.markdown("<br>", unsafe_allow_html=True)
        st.button("Cerrar sesión", on_click=lambda: st.session_state.update(logueado=False), type="secondary", width='stretch')
    
    # 📊 DASHBOARD DE MÉTRICAS
    col_titulo_met, col_btn_refresh = st.columns([3, 1])
    with col_titulo_met:
        st.write("#### 📊 Actividad de Hoy")
    with col_btn_refresh:
        if st.button("🔄 Actualizar Métricas", width='stretch', type="secondary"):
            st.rerun()
            
    metricas = obtener_metricas_del_dia(supabase)
    
    with st.container(border=True):
        m1, m2, m3 = st.columns(3)
        with m1: 
            st.metric(label="💰 Verificado Hoy", value=metricas["monto"])
        with m2: 
            st.metric(label="🖼️ Capturas Leídas", value=metricas["procesados"])
        with m3:
            color_alerta = "inverse" if int(metricas["alertas"]) > 0 else "normal"
            st.metric(label="🚨 Alertas / Fallas", value=metricas["alertas"], delta=f"{metricas['alertas']} pendientes" if int(metricas["alertas"]) > 0 else None, delta_color=color_alerta)
            
    st.markdown("<br>", unsafe_allow_html=True)
    tab1, tab2, tab3 = st.tabs(["🛠️ Constructor de Flujos", "💳 Gestión de Pagos", "📋 Historial de Logs"])

    # --- TAB 1: CONSTRUCTOR DE FLUJOS ---
    with tab1:
        st.write("### 🔀 Flujos Automatizados de Conversación")
        
        with st.expander("➕ Crear Nuevo Flujo Visual"):
            with st.form("nuevo_flujo_form", border=False):
                nombre_flujo = st.text_input("Nombre identificativo de la campaña/flujo", placeholder="Ej: Campaña Helados de Fresa")
                keyword_flujo = st.text_input("Palabra clave disparadora (Trigger)", placeholder="Ej: hola")
                
                # CORREGIDO: cambiado a width='stretch'
                if st.form_submit_button("Inicializar Flujo en Red", width='stretch', type="primary"):
                    if nombre_flujo and keyword_flujo:
                        if crear_nuevo_flujo(nombre_flujo, keyword_flujo):
                            st.toast("¡Flujo inicializado con éxito! Nodo base 'Inicio' configurado.", icon="✅")
                            st.rerun()
                        else:
                            st.error("Error al inicializar. Revisa si esa palabra clave ya está ocupada por otro flujo.")
                    else:
                        st.warning("Por favor completa el nombre del flujo y su palabra clave.")

        st.write("#### 🔑 Lienzos y Disparadores Activos")
        flujos_actuales = obtener_todos_los_flujos()
        
        if not flujos_actuales:
            st.info("No posees ningún flujo en red configurado. Utiliza el formulario superior para crear el primero.")
        else:
            for fl in flujos_actuales:
                with st.container(border=True):
                    c1, c2 = st.columns([4, 1])
                    c1.write(f"🗺️ **{fl.get('nombre')}** — Disparador: `{fl.get('palabra_clave')}`")
                    
                    if c2.button("👁️ Inspeccionar Red", key=f"flow_{fl['id']}", width='stretch'):
                        nodos, conexiones = obtener_datos_lienzo(fl['id'])
                        
                        st.markdown("---")
                        st.write(f"**Estructura interna de: `{fl.get('nombre')}`**")
                        
                        col_n, col_c = st.columns(2)
                        with col_n:
                            st.caption("📦 Bloques (Nodos asignados)")
                            for n in nodos:
                                st.code(f"ID: {n['id'][:8]}...\nTipo: {n['tipo_nodo'].upper()}\nConfig: {n['configuracion']}", language="json")
                        with col_c:
                            st.caption("🔌 Conexiones (Cables instalados)")
                            if not conexiones:
                                i_info = st.info("Este flujo no tiene cables interconectando bloques todavía.")
                            for con in conexiones:
                                st.code(f"De: {con['nodo_origen_id'][:8]}... ➡️ A: {con['nodo_destino_id'][:8]}...", language="text")

    # --- TAB 2: PAGOS ---
    with tab2:
        with st.expander("➕ Registrar Nuevo Pago Móvil (Receptor)"):
            with st.form("nuevo_pago_form", border=False, clear_on_submit=True):
                c_ced, c_tel = st.columns(2)
                with c_ced: 
                    ced = st.text_input("Cédula Receptor")
                with c_tel: 
                    tel = st.text_input("Teléfono Receptor")
                _, c_btn = st.columns([2, 1])
                with c_btn:
                    # CORREGIDO: cambiado a width='stretch'
                    if st.form_submit_button("Registrar Pago Móvil", width='stretch'):
                        if ced and tel:
                            guardar_contacto(ced, tel)
                            st.toast("¡Pago Móvil registrado!", icon="✅")
                            st.rerun()
                        else: 
                            st.warning("Por favor, rellena ambos campos.") 

        st.write("#### 📋 Cuentas Registradas (Pago Móvil)")
        for c in obtener_configuracion_pagos():
            with st.container(border=True):
                inf1, inf2 = st.columns([3, 1])
                inf1.write(f"💳 **Cédula:** `{c.get('cedula_esperada')}` | **Tel:** `{c.get('telefono_esperado')}`")
                with inf2:
                    if c.get('activo'): 
                        st.markdown("<span style='color:#2ec4b6; font-weight:bold;'>● Activo</span>", unsafe_allow_html=True)
                    else: 
                        st.markdown("<span style='color:#e71d36; font-weight:bold;'>● Inactivo</span>", unsafe_allow_html=True)
                col_act, col_edit, col_del = st.columns([2, 1, 1])
                with col_act:
                    if not c.get('activo'):
                        if st.button("🚀 Activar", key=f"act_{c['id']}", width='stretch'): 
                            activar_contacto(c['id'])
                            st.rerun()
                    else: 
                        st.button("✨ Principal", key=f"act_dis_{c['id']}", disabled=True, width='stretch')
                with col_edit:
                    if st.button("✏️ Editar", key=f"edit_pago_{c['id']}", width='stretch'): 
                        abrir_editor_pago(c)
                with col_del:
                    if st.button("🗑️ Eliminar", key=f"del_pago_{c['id']}", width='stretch', type="secondary"):
                        try:
                            supabase.table("configuracion_pago").delete().eq("id", c['id']).execute()
                            st.toast("Cuenta eliminada", icon="🗑️")
                            st.rerun()
                        except Exception as e: 
                            st.error(f"No se pudo eliminar: {e}")

        st.write("---")
        st.subheader("🖼️ Montos de Verificación por Emoji")
        try:
            nuevos_valores = {}
            query_emojis = supabase.table("montos_emojis").select("*").execute()
            datos_emojis = {item['emoji']: float(item['monto']) for item in query_emojis.data} if query_emojis.data else {}
            with st.form("form_montos_emojis"):
                col1, col2, col3 = st.columns(3)
                with col1: 
                    nuevos_valores["💖"] = st.number_input("Monto para 💖", min_value=0.0, value=datos_emojis.get("💖", 3300.0), step=1.0)
                with col2: 
                    nuevos_valores["⭐"] = st.number_input("Monto para ⭐", min_value=0.0, value=datos_emojis.get("⭐", 20.0), step=1.0)
                with col3: 
                    nuevos_valores["💎"] = st.number_input("Monto para 💎", min_value=0.0, value=datos_emojis.get("💎", 10.0), step=1.0)
                _, c_btn_em = st.columns([2, 1])
                with c_btn_em: 
                    # CORREGIDO: cambiado a width='stretch'
                    guardar_montos = st.form_submit_button("💾 Guardar Montos", width='stretch')
                if guardar_montos:
                    for em, monto_nuevo in nuevos_valores.items(): 
                        supabase.table("montos_emojis").upsert({"emoji": em, "monto": monto_nuevo}).execute()
                    st.success("✅ ¡Montos actualizados!")
                    st.rerun()
        except Exception as e: 
            st.error(f"Error al conectar con la configuración de emojis: {e}")
            
    # --- TAB 3: LOGS ---
    with tab3:
        st.subheader("📋 Historial de Transacciones")
        lista_logs = obtener_todos_los_logs(supabase)
        
        if lista_logs and len(lista_logs) > 0:
            df = pd.DataFrame(lista_logs)
            df["created_at"] = pd.to_datetime(df["created_at"]).dt.tz_localize(None) - timedelta(hours=4)
            
            col_f1, col_f2, col_f3 = st.columns(3)
            f_inicio = col_f1.date_input("Inicio", value=datetime.now() - timedelta(days=30))
            f_fin = col_f2.date_input("Fin", value=datetime.now())
            busqueda_tel = col_f3.text_input("Buscar por Teléfono")
            
            mask = (df["created_at"].dt.date >= f_inicio) & (df["created_at"].dt.date <= f_fin)
            if busqueda_tel:
                mask = mask & df['phone'].astype(str).str.contains(busqueda_tel, na=False)
            
            df_filtrado = df.loc[mask]
            
            if not df_filtrado.empty:
                buffer = io.BytesIO()
                with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
                    df_filtrado.to_excel(writer, index=False, sheet_name='Historial')
                    writer.sheets['Historial'].column_dimensions['B'].width = 25
                
                st.download_button("📊 Descargar Excel", data=buffer.getvalue(), 
                                   file_name="historial.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
                
                st.dataframe(df_filtrado, width='stretch', hide_index=True)
            else:
                st.warning("No se encontraron registros con los filtros actuales. Prueba cambiando el rango de fechas.")
        else:
            st.info("No hay datos cargados en el historial o la base de datos está vacía.")
