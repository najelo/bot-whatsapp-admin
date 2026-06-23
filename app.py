import streamlit as st
import uuid
from auth_utils import verificar_login, get_supabase
from db_utils import obtener_configuraciones, guardar_configuracion
from pagos_utils import obtener_configuracion_pagos, guardar_contacto, activar_contacto

st.set_page_config(page_title="Admin Bot", page_icon="🤖", layout="wide")

# --- DIÁLOGO DE EDICIÓN ---
@st.dialog("Editar Regla")
def abrir_editor(conf):
    # Obtenemos la data de respuestas de forma segura
    resp_data = conf.get('respuestas') or {}
    contenido_actual = resp_data.get('contenido', '')
    
    st.write(f"Editando: **{conf.get('palabra_clave')}**")
    nueva_palabra = st.text_input("Palabra clave", value=conf.get('palabra_clave', ''))
    
    # Lógica de PDF o Texto
    if "http" in contenido_actual:
        st.info("📄 Archivo PDF detectado.")
        nuevo_contenido = contenido_actual
    else:
        nuevo_contenido = st.text_area("Contenido", value=contenido_actual)
    
    if st.button("Guardar Cambios"):
        try:
            # 1. Actualizar tabla 'clientes'
            get_supabase().table("clientes").update({"palabra_clave": nueva_palabra}).eq("id", conf['id']).execute()
            
            # 2. Actualizar tabla 'respuestas'
            get_supabase().table("respuestas").update({"contenido": nuevo_contenido}).eq("id", resp_data['id']).execute()
            
            st.success("¡Guardado!")
            st.rerun()
        except Exception as e:
            st.error(f"Error: {e}")

# --- LÓGICA PRINCIPAL ---
if "logueado" not in st.session_state: st.session_state["logueado"] = False

if not st.session_state["logueado"]:
    st.title("🔐 Acceso")
    user = st.text_input("Usuario")
    pwd = st.text_input("Contraseña", type="password")
    if st.button("Ingresar"):
        if verificar_login(user, pwd)[0]:
            st.session_state["logueado"] = True
            st.rerun()
else:
    tab1, tab2 = st.tabs(["Configurar Bot", "Configurar Pagos"])
    
    with tab1:
        st.subheader("Nueva Regla")
        tipo = st.radio("Tipo:", ["Texto", "PDF"])
        with st.form("nueva_config", clear_on_submit=True):
            palabra = st.text_input("Palabras clave")
            if tipo == "Texto":
                res = st.text_area("Respuesta")
                if st.form_submit_button("Guardar"):
                    guardar_configuracion(palabra, res); st.rerun()
            else:
                archivo = st.file_uploader("Subir PDF", type="pdf")
                if st.form_submit_button("Guardar PDF"):
                    if archivo:
                        nombre = f"{uuid.uuid4()}.pdf"
                        get_supabase().storage.from_("recetarios-helado").upload(nombre, archivo.getvalue())
                        url = get_supabase().storage.from_("recetarios-helado").get_public_url(nombre)
                        guardar_configuracion(palabra, url); st.rerun()

        st.divider()
        for conf in obtener_configuraciones():
            with st.container(border=True):
                c1, c2 = st.columns([4, 1])
                c1.write(f"🔑 **{conf.get('palabra_clave')}**")
                if c2.button("✏️ Editar", key=f"edit_{conf['id']}"):
                    abrir_editor(conf)
    
    with tab2:
        st.subheader("Gestión de Pagos")
        with st.form("form_pago", clear_on_submit=True):
            ced = st.text_input("Cédula")
            tel = st.text_input("Teléfono")
            if st.form_submit_button("Registrar"):
                guardar_contacto(ced, tel); st.rerun()
        
        for c in obtener_configuracion_pagos():
            with st.container(border=True):
                col1, col2 = st.columns([4, 1])
                col1.markdown(f"**Cédula:** `{c.get('cedula_esperada')}`")
                if c.get('activo'): col2.success("✅ Activo")
                elif col2.button("Activar", key=f"act_{c['id']}"):
                    activar_contacto(c['id']); st.rerun()

    if st.sidebar.button("Cerrar sesión"):
        st.session_state["logueado"] = False
        st.rerun()
