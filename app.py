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

# --- DIÁLOGOS ---
@st.dialog("Editar Regla")
def abrir_editor(conf):
    resp_data = conf.get('respuestas') or {}
    contenido = resp_data.get('contenido', '')
    
    st.write(f"Editando: **{conf.get('palabra_clave')}**")
    
    # Vista previa visual
    if "http" in contenido:
        if any(ext in contenido for ext in [".jpg", ".png", ".jpeg"]): st.image(contenido, width=200)
        elif any(ext in contenido for ext in [".mp3", ".ogg"]): st.audio(contenido)
    
    # Selector de archivos existentes
    archivos = listar_archivos_storage()
    cambiar = st.selectbox("Cambiar archivo existente:", ["Mantener actual"] + archivos)
    
    nuevo_contenido = st.text_area("Contenido texto/URL", value=contenido)
    
    if st.button("Guardar Cambios"):
        final_val = get_supabase().storage.from_("media-bot").get_public_url(cambiar) if cambiar != "Mantener actual" else nuevo_contenido
        get_supabase().table("respuestas").update({"contenido": final_val}).eq("id", resp_data['id']).execute()
        st.rerun()

@st.dialog("Editar Pago")
def editar_pago(c):
    nueva_ced = st.text_input("Cédula", value=c.get('cedula_esperada', ''))
    nuevo_tel = st.text_input("Teléfono", value=c.get('telefono_esperado', ''))
    if st.button("Guardar"):
        get_supabase().table("configuracion_pago").update({"cedula_esperada": nueva_ced, "telefono_esperado": nuevo_tel}).eq("id", c['id']).execute()
        st.rerun()

# --- INTERFAZ ---
st.title("🤖 Panel de Control"); st.button("Cerrar sesión", on_click=lambda: st.session_state.update(logueado=False))
tab1, tab2 = st.tabs(["⚙️ Reglas", "💳 Pagos"])

with tab1:
    with st.expander("➕ Nueva Regla"):
        palabras = st.text_input("Palabra clave")
        archivo = st.file_uploader("Subir nuevo archivo")
        res_texto = st.text_area("Respuesta")
        if st.button("Guardar"):
            cont = subir_archivo_al_storage(archivo.getvalue(), archivo.name) if archivo else res_texto
            if cont: guardar_configuracion(palabras, cont); st.rerun()
    
    for conf in obtener_configuraciones():
        with st.container(border=True):
            c1, c2 = st.columns([4, 1])
            c1.write(f"🔑 **{conf.get('palabra_clave')}**")
            if c2.button("✏️ Editar", key=f"e_{conf['id']}"): abrir_editor(conf)

with tab2:
    for c in obtener_configuracion_pagos():
        with st.container(border=True):
            col1, col2, col3 = st.columns([3, 1, 1])
            col1.write(f"Cédula: {c.get('cedula_esperada')} | Tel: {c.get('telefono_esperado')}")
            if c.get('activo'): col2.success("✅ Activo")
            elif col2.button("Activar", key=f"act_{c['id']}"): activar_contacto(c['id']); st.rerun()
            col3.button("✏️", key=f"ep_{c['id']}", on_click=editar_pago, args=(c,))
