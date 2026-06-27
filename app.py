import streamlit as st
import pandas as pd
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
                if st.form_submit_button("Entrar", use_container_width=True, type="primary"):
                    valido, msg = verificar_login(user, pwd)
                    if valido: 
                        st.session_state["logueado"] = True
                        st.rerun()
                    else: 
                        st.error(msg)
    st.stop()

# --- DIÁLOGOS GLOBALES DE EDICIÓN ---
@st.dialog("Editar Regla de Bot", width="large")
def abrir_editor(conf):
    resp_data = conf.get('respuestas') or {}
    contenido_actual = resp_data.get('contenido', '')
    st.markdown(f"### ✏️ Editando: `{conf.get('palabra_clave')}`")
    nueva_palabra = st.text_input("Palabra clave para el bot", value=conf.get('palabra_clave', ''))
    st.markdown("---")
    st.write("#### 📂 Archivo actual")
    st.markdown(f"[{contenido_actual}]({contenido_actual})")
    st.markdown("---")
    col_select, col_upload = st.columns(2)
    with col_select:
        archivos = listar_archivos_storage()
        seleccion = st.selectbox("Cambiar por:", ["-- Mantener actual --"] + archivos)
    with col_upload:
        nuevo_archivo = st.file_uploader("Subir archivo NUEVO", type=["pdf", "png", "jpg", "jpeg", "webp", "mp4", "mp3", "wav", "m4a", "ogg", "opus", "OPUS", "OGG"])
    
    col_save, col_del = st.columns([3, 1])
    with col_save:
        if st.button("💾 Guardar Cambios", use_container_width=True, type="primary"):
            try:
                final_content = subir_archivo_al_storage(nuevo_archivo.getvalue(), nuevo_archivo.name) if nuevo_archivo else (supabase.storage.from_("recetarios-helado").get_public_url(seleccion) if seleccion != "-- Mantener actual --" else contenido_actual)
                supabase.table("clientes").update({"palabra_clave": nueva_palabra}).eq("id", conf['id']).execute()
                supabase.table("respuestas").update({"contenido": final_content}).eq("id", resp_data['id']).execute()
                st.toast("Guardado", icon="✅")
                st.rerun()
            except Exception as e: 
                st.error(f"Error: {e}")
    with col_del:
        if st.button("🗑️ Borrar", use_container_width=True):
            if eliminar_regla(conf['id'], resp_data['id']): 
                st.rerun()

@st.dialog("Editar Cuenta de Pago", width="medium")
def abrir_editor_pago(cuenta):
    st.markdown(f"### ✏️ Editando Receptor ID: `{cuenta.get('id')}`")
    nueva_cedula = st.text_input("Nueva Cédula", value=cuenta.get('cedula_esperada', ''))
    nuevo_telefono = st.text_input("Nuevo Teléfono", value=cuenta.get('telefono_esperado', ''))
    st.markdown("---")
    if st.button("💾 Guardar Cambios Cuenta", use_container_width=True, type="primary"):
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
        st.button("Cerrar sesión", on_click=lambda: st.session_state.update(logueado=False), type="secondary", use_container_width=True)
    
    # 📊 DASHBOARD DE MÉTRICAS
    col_titulo_met, col_btn_refresh = st.columns([3, 1])
    with col_titulo_met:
        st.write("#### 📊 Actividad de Hoy")
    with col_btn_refresh:
        if st.button("🔄 Actualizar Métricas", use_container_width=True, type="secondary"):
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
    tab1, tab2, tab3 = st.tabs(["⚙️ Reglas del Bot", "💳 Gestión de Pagos", "📋 Historial de Logs"])

    # --- TAB 1: REGLAS ---
    with tab1:
        with st.expander("➕ Nueva Regla"):
            with st.form("nueva_regla_form", border=False):
                palabras = st.text_input("Palabra clave")
                archivo = st.file_uploader("Subir archivo", type=["pdf", "png", "jpg", "jpeg", "webp", "mp4", "mp3", "wav", "m4a", "ogg", "opus", "OPUS", "OGG"])
                res_texto = st.text_area("Respuesta texto")
                if st.form_submit_button("Guardar Regla", type="primary"):
                    cont = subir_archivo_al_storage(archivo.getvalue(), file_name=archivo.name) if archivo else res_texto
                    if cont: 
                        guardar_configuracion(palabras, cont)
                        st.toast("¡Regla guardada exitosamente!", icon="✅")
                        st.rerun()
        
        st.write("#### 🔑 Reglas del sistema")
        for conf in obtener_configuraciones():
            with st.container(border=True):
                c1, c2 = st.columns([5, 1])
                c1.write(f"🔑 **{conf.get('palabra_clave')}**")
                if c2.button("✏️ Editar", key=f"edit_{conf['id']}", use_container_width=True): 
                    abrir_editor(conf)

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
                    if st.form_submit_button("Registrar Pago Móvil", use_container_width=True):
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
                        if st.button("🚀 Activar", key=f"act_{c['id']}", use_container_width=True): 
                            activar_contacto(c['id'])
                            st.rerun()
                    else: 
                        st.button("✨ Principal", key=f"act_dis_{c['id']}", disabled=True, use_container_width=True)
                with col_edit:
                    if st.button("✏️ Editar", key=f"edit_pago_{c['id']}", use_container_width=True): 
                        abrir_editor_pago(c)
                with col_del:
                    if st.button("🗑️ Eliminar", key=f"del_pago_{c['id']}", use_container_width=True, type="secondary"):
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
                    guardar_montos = st.form_submit_button("💾 Guardar Montos", use_container_width=True)
                if guardar_montos:
                    for em, monto_nuevo in nuevos_valores.items(): 
                        supabase.table("montos_emojis").upsert({"emoji": em, "monto": monto_nuevo}).execute()
                    st.success("✅ ¡Montos actualizados!")
                    st.rerun()
        except Exception as e: 
            st.error(f"Error al conectar con la configuración de emojis: {e}")
with tab3:
        st.subheader("📋 Historial de Transacciones")
        lista_logs = obtener_todos_los_logs(supabase)
        
        if lista_logs:
            df = pd.DataFrame(lista_logs)
            # Asegurar formato de fecha
            df["created_at"] = pd.to_datetime(df["created_at"]).dt.tz_localize(None) - timedelta(hours=4)
            
            # Filtros de fecha
            col_f1, col_f2 = st.columns(2)
            fecha_inicio = col_f1.date_input("Fecha Inicio", value=datetime.now() - timedelta(days=7))
            fecha_fin = col_f2.date_input("Fecha Fin", value=datetime.now())
            
            # Aplicar filtro
            mask = (df["created_at"].dt.date >= fecha_inicio) & (df["created_at"].dt.date <= fecha_fin)
            df_filtrado = df.loc[mask]
            
            # Mostrar tabla filtrada
            st.dataframe(
                df_filtrado, 
                column_config={"monto": st.column_config.NumberColumn("Monto", format="Bs. %.2f")},
                use_container_width=True, 
                hide_index=True
            )
        else:
            st.info("No hay registros en el historial.")
