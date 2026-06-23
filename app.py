import streamlit as st
import uuid
from auth_utils import verificar_login, get_supabase
from db_utils import (
    obtener_configuraciones, guardar_configuracion, eliminar_configuracion
)
from pagos_utils import obtener_configuracion_pagos, guardar_contacto, activar_contacto

st.set_page_config(page_title="Admin Bot", page_icon="🤖", layout="wide")

if "logueado" not in st.session_state: st.session_state["logueado"] = False

# --- DIÁLOGO DE EDICIÓN ---
@st.dialog("Editar Regla")
def abrir_editor(conf):
    st.write(f"Editando: **{conf['palabra_clave']}**")
    
    # Edición de Palabra
    nueva_palabra = st.text_input("Palabra clave", value=conf['palabra_clave'])
    
    # Identificar contenido
    contenido = conf['respuestas']['contenido']
    es_pdf = "http" in contenido
    
    if es_pdf:
        st.info("Este registro tiene un PDF vinculado.")
        if st.checkbox("¿Eliminar este PDF?"):
            nuevo_contenido = None # Lógica para borrar archivo
        else:
            nuevo_contenido = contenido
    else:
        nuevo_contenido = st.text_area("Contenido", value=contenido)
        
    if st.button("Guardar Cambios"):
        get_supabase().table("configuracion").update({"palabra_clave": nueva_palabra}).eq("id", conf['id']).execute()
        get_supabase().table("respuestas").update({"contenido": nuevo_contenido}).eq("id", conf['respuestas']['id']).execute()
        st.rerun()

# --- LÓGICA PRINCIPAL ---
if not st.session_state["logueado"]:
    st.title("🔐 Acceso al Sistema")
    user = st.text_input("Usuario")
    pwd = st.text_input("Contraseña", type="password")
    if st.button("Ingresar"):
        exito, msg = verificar_login(user, pwd)
        if exito:
            st.session_state["logueado"] = True
            st.rerun()
        else: st.error(msg)
else:
    # Sidebar
    st.sidebar.title("Navegación")
    menu = st.sidebar.radio("Opciones", ["🤖 Gestión de Respuestas", "💳 Gestión de Pagos"])
    
    if st.sidebar.button("Cerrar sesión"):
        st.session_state["logueado"] = False
        st.rerun()

    # --- SECCIÓN: RESPUESTAS ---
    if menu == "🤖 Gestión de Respuestas":
        col_form, col_lista = st.columns([1, 2])
        with col_form:
            st.subheader("Nueva Regla")
            tipo = st.radio("Tipo:", ["Texto", "PDF"])
            with st.form("form_nueva", clear_on_submit=True):
                palabras = st.text_input("Palabras clave")
                respuesta = st.text_area("Contenido") if tipo == "Texto" else st.file_uploader("Subir PDF", type=["pdf"])
                if st.form_submit_button("Guardar"):
                    guardar_configuracion(palabras, respuesta)
                    st.rerun()
        
        with col_lista:
            st.subheader("Reglas Activas")
            for conf in obtener_configuraciones():
                with st.container(border=True):
                    c1, c2, c3 = st.columns([3, 2, 1])
                    c1.write(f"🔑 **{conf['palabra_clave']}**")
                    c2.write("📄 PDF" if "http" in conf['respuestas']['contenido'] else "💬 Texto")
                    if c3.button("✏️ Editar", key=f"edit_{conf['id']}"):
                        abrir_editor(conf)

    # --- SECCIÓN: PAGOS (RECUPERADA) ---
    elif menu == "💳 Gestión de Pagos":
        st.subheader("💳 Configuración de Pagos")
        with st.container(border=True):
            st.write("### ➕ Registrar nuevos datos")
            col_a, col_b, col_c = st.columns([2, 2, 1])
            ced = col_a.text_input("Cédula Esperada")
            tel = col_b.text_input("Teléfono Esperado")
            if col_c.button("Registrar Datos"):
                guardar_contacto(ced, tel)
                st.rerun()

        st.divider()
        st.subheader("Seleccionar Registro Activo")
        contactos = obtener_configuracion_pagos()
        for c in contactos:
            with st.container(border=True):
                col1, col2, col3 = st.columns([3, 1, 1])
                col1.markdown(f"**Cédula:** `{c['cedula_esperada']}` | **Tel:** `{c['telefono_esperado']}`")
                if c.get('activo', False):
                    col2.success("✅ Activo")
                else:
                    if col2.button("Activar", key=f"act_{c['id']}"):
                        activar_contacto(c['id']); st.rerun()
                if col3.button("🗑️ Eliminar", key=f"del_{c['id']}"):
                    get_supabase().table("configuracion_pago").delete().eq("id", c['id']).execute()
                    st.rerun()
