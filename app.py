import streamlit as st
import uuid
from auth_utils import verificar_login, get_supabase
from db_utils import obtener_configuraciones, guardar_configuracion, subir_archivo_al_storage
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
@st.dialog("Editar Regla")
def abrir_editor(conf):
    resp_data = conf.get('respuestas') or {}
    contenido_actual = resp_data.get('contenido', '')
    
    st.write(f"Editando: **{conf.get('palabra_clave')}**")
    nueva_palabra = st.text_input("Palabra clave", value=conf.get('palabra_clave', ''))
    
    st.info(f"🔗 Archivo/Contenido actual: `{contenido_actual}`")
    
    # Opción para reemplazar
    nuevo_archivo = st.file_uploader("Subir nuevo archivo para reemplazar el anterior", type=["pdf", "jpg", "png"])
    nuevo_texto = st.text_area("O editar contenido (texto):", value=contenido_actual)
    
    if st.button("Guardar Cambios"):
        try:
            # Si se sube archivo, sobrescribe el contenido
            final_content = subir_archivo_al_storage(nuevo_archivo.getvalue(), nuevo_archivo.name) if nuevo_archivo else nuevo_texto
            
            get_supabase().table("clientes").update({"palabra_clave": nueva_palabra}).eq("id", conf['id']).execute()
            get_supabase().table("respuestas").update({"contenido": final_content}).eq("id", resp_data['id']).execute()
            st.success("¡Guardado!")
            st.rerun()
        except Exception as e:
            st.error(f"Error: {e}")

# --- PANTALLA PRINCIPAL ---
st.title("🤖 Panel de Control"); st.button("Cerrar sesión", on_click=lambda: st.session_state.update(logueado=False))
tab1, tab2 = st.tabs(["⚙️ Reglas", "💳 Pagos"])

with tab1:
    with st.expander("➕ Nueva Regla"):
        palabras = st.text_input("Palabra clave")
        archivo = st.file_uploader("Subir archivo")
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
    for c in obtener_configuracion_pagos():
        with st.container(border=True):
            st.write(f"Cédula: {c.get('cedula_esperada')} | Tel: {c.get('telefono_esperado')}")
            if c.get('activo'): st.success("✅ Activo")
            elif st.button("Activar", key=f"act_{c['id']}"): activar_contacto(c['id']); st.rerun()
