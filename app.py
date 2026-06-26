import streamlit as st
from auth_utils import verificar_login, get_supabase
from db_utils import obtener_configuraciones, guardar_configuracion, subir_archivo_al_storage, listar_archivos_storage, eliminar_regla
from pagos_utils import obtener_configuracion_pagos, guardar_contacto, activar_contacto

st.set_page_config(page_title="Admin Bot", layout="wide")

# --- LOGIN ---
if "logueado" not in st.session_state: st.session_state["logueado"] = False
if not st.session_state["logueado"]:
    st.title("🔐 Iniciar Sesión")
    user, pwd = st.text_input("Usuario"), st.text_input("Contraseña", type="password")
    if st.button("Entrar"):
        valido, msg = verificar_login(user, pwd)
        if valido: st.session_state["logueado"] = True; st.rerun()
        else: st.error(msg)
    st.stop()

# --- DIÁLOGO EDICIÓN ---
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
        # SE MODIFICÓ AQUÍ: Permitir cambiar el archivo viejo por audios nativos .opus/.ogg
        nuevo_archivo = st.file_uploader("Subir archivo NUEVO", type=["pdf", "png", "jpg", "jpeg", "webp", "mp4", "mp3", "wav", "m4a", "ogg", "opus", "OPUS", "OGG"])
    
    col_save, col_del = st.columns([3, 1])
    with col_save:
        if st.button("💾 Guardar Cambios", use_container_width=True, type="primary"):
            try:
                final_content = subir_archivo_al_storage(nuevo_archivo.getvalue(), nuevo_archivo.name) if nuevo_archivo else (get_supabase().storage.from_("recetarios-helado").get_public_url(seleccion) if seleccion != "-- Mantener actual --" else contenido_actual)
                get_supabase().table("clientes").update({"palabra_clave": nueva_palabra}).eq("id", conf['id']).execute()
                get_supabase().table("respuestas").update({"contenido": final_content}).eq("id", resp_data['id']).execute()
                st.toast("Guardado", icon="✅"); st.rerun()
            except Exception as e: st.error(f"Error: {e}")
    with col_del:
        if st.button("🗑️ Borrar", use_container_width=True):
            if eliminar_regla(conf['id'], resp_data['id']): st.rerun()

# --- PANTALLA ---
st.title("🤖 Panel de Control"); st.button("Cerrar sesión", on_click=lambda: st.session_state.update(logueado=False))
tab1, tab2 = st.tabs(["⚙️ Reglas", "💳 Pagos"])

with tab1:
    with st.expander("➕ Nueva Regla"):
        palabras = st.text_input("Palabra clave")
        # SE MODIFICÓ AQUÍ: Permitir formatos multimedia y audios en la creación primaria
        archivo = st.file_uploader("Subir archivo", type=["pdf", "png", "jpg", "jpeg", "webp", "mp4", "mp3", "wav", "m4a", "ogg", "opus", "OPUS", "OGG"])
        res_texto = st.text_area("Respuesta texto")
        if st.button("Guardar"):
            cont = subir_archivo_al_storage(archivo.getvalue(), archivo.name) if archivo else res_texto
            if cont: guardar_configuracion(palabras, cont); st.rerun()
    
    for conf in obtener_configuraciones():
        with st.container(border=True):
            c1, c2 = st.columns([4, 1])
            c1.write(f"🔑 **{conf.get('palabra_clave')}**")
            if c2.button("✏️ Editar", key=f"edit_{conf['id']}"): abrir_editor(conf)

with tab2:
    with st.form("nuevo_pago_form"):
        ced, tel = st.text_input("Cédula"), st.text_input("Teléfono")
        if st.form_submit_button("Registrar Pago"): guardar_contacto(ced, tel); st.rerun()
    for c in obtener_configuracion_pagos():
        with st.container(border=True):
            st.write(f"Cédula: {c.get('cedula_esperada')} | Tel: {c.get('telefono_esperado')}")
            if c.get('activo'): st.success("✅ Activo")
            elif st.button("Activar", key=f"act_{c['id']}"): activar_contacto(c['id']); st.rerun()
st.subheader("🖼️ Configuración de Montos por Emoji")
st.write("Modifica el monto asignado a cada emoji con el cual la IA verificará los captures.")

try:
  st.write("---")

st.subheader("🖼️ Configuración de Montos por Emoji")
st.write("Modifica el monto asignado a cada emoji con el cual la IA verificará los captures.")

try:
    # Ahora 'supabase' ya estará definido gracias al import superior
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
            
        guardar_montos = st.form_submit_button("Guardar Montos de Emojis")
        
        if guardar_montos:
            for em, monto_nuevo in nuevos_valores.items():
                supabase.table("montos_emojis").upsert({"emoji": em, "monto": monto_nuevo}).execute()
            st.success("✅ ¡Montos de emojis actualizados exitosamente!")
            st.rerun()

except Exception as e:
    st.error(f"Error al conectar con la configuración de emojis: {e}")
