import streamlit as st
from auth_utils import verificar_login, get_supabase
from db_utils import obtener_configuraciones, guardar_configuracion, subir_archivo_al_storage, listar_archivos_storage
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

# --- DIÁLOGO EDICIÓN REGLAS ---
@st.dialog("Editar Regla")
def abrir_editor(conf):
    resp_data = conf.get('respuestas') or {}
    contenido = resp_data.get('contenido', '')
    st.write(f"Editando: **{conf.get('palabra_clave')}**")
    
    # Visor visual
    if contenido.startswith("http"):
        st.info("Archivo actual vinculado:")
        st.write(f"[Abrir archivo actual]({contenido})")
        if any(ext in contenido for ext in [".png", ".jpg", ".jpeg"]): st.image(contenido, width=200)

    st.divider()
    st.subheader("Archivos disponibles en Storage")
    archivos = listar_archivos_storage()
    st.write(archivos) # Lista los que puedes usar
    
    nuevo_contenido = st.text_area("URL o Texto", value=contenido)
    if st.button("Guardar"):
        get_supabase().table("respuestas").update({"contenido": nuevo_contenido}).eq("id", resp_data['id']).execute()
        st.rerun()

# --- INTERFAZ ---
st.title("🤖 Panel de Control"); st.button("Cerrar sesión", on_click=lambda: st.session_state.update(logueado=False))
tab1, tab2 = st.tabs(["⚙️ Reglas", "💳 Pagos"])

with tab1:
    for conf in obtener_configuraciones():
        with st.container(border=True):
            c1, c2 = st.columns([4, 1])
            c1.write(f"🔑 **{conf.get('palabra_clave')}**")
            if c2.button("✏️ Editar", key=f"e_{conf['id']}"): abrir_editor(conf)

with tab2:
    with st.form("form_pago"):
        ced, tel = st.text_input("Cédula"), st.text_input("Teléfono")
        if st.form_submit_button("Registrar"): guardar_contacto(ced, tel); st.rerun()
    for c in obtener_configuracion_pagos():
        with st.container(border=True):
            st.write(f"Cédula: {c.get('cedula_esperada')} | Tel: {c.get('telefono_esperado')}")
            if c.get('activo'): st.success("✅ Activo")
            elif st.button("Activar", key=f"act_{c['id']}"): activar_contacto(c['id']); st.rerun()
