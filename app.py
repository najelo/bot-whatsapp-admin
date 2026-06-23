import streamlit as st
import uuid
from auth_utils import verificar_login, get_supabase
from db_utils import (
    obtener_configuraciones, guardar_configuracion, eliminar_configuracion
)
from pagos_utils import obtener_configuracion_pagos, guardar_contacto, activar_contacto

st.set_page_config(layout="wide", page_title="Admin Bot")

if "logueado" not in st.session_state: st.session_state["logueado"] = False

# --- DIÁLOGO DE EDICIÓN (LA SOLUCIÓN A TU DUDA) ---
@st.dialog("Editar Regla de Bot")
def abrir_editor(conf):
    st.write(f"Editando palabra: **{conf['palabra_clave']}**")
    
    # 1. Editar Palabra Clave
    nueva_palabra = st.text_input("Palabra clave", value=conf['palabra_clave'])
    
    # 2. Identificar si es PDF o Texto
    contenido = conf['respuestas']['contenido']
    es_pdf = "http" in contenido # Asumimos que es PDF si es una URL
    
    st.info(f"Tipo actual: {'📄 PDF' if es_pdf else '💬 Texto'}")
    
    if es_pdf:
        st.write(f"Archivo actual: [Ver PDF]({contenido})")
        if st.checkbox("¿Reemplazar archivo PDF?"):
            nuevo_archivo = st.file_uploader("Subir nuevo PDF", type=["pdf"])
            if nuevo_archivo: nuevo_contenido = nuevo_archivo # Placeholder lógica subida
        else:
            nuevo_contenido = contenido
    else:
        nuevo_contenido = st.text_area("Contenido de respuesta", value=contenido)
        
    if st.button("Guardar Cambios"):
        # Lógica de actualización (usar tus funciones de db_utils)
        get_supabase().table("configuracion").update({"palabra_clave": nueva_palabra}).eq("id", conf['id']).execute()
        get_supabase().table("respuestas").update({"contenido": nuevo_contenido if not isinstance(nuevo_contenido, bytes) else "URL_NUEVA"}).eq("id", conf['respuestas']['id']).execute()
        st.rerun()

# --- LÓGICA PRINCIPAL ---
if not st.session_state["logueado"]:
    # ... (Login igual que antes) ...
    st.title("🔐 Acceso al Sistema")
    user = st.text_input("Usuario")
    pwd = st.text_input("Contraseña", type="password")
    if st.button("Ingresar"):
        exito, msg = verificar_login(user, pwd)
        if exito:
            st.session_state["logueado"] = True
            st.rerun()
else:
    # Sidebar
    menu = st.sidebar.radio("Navegación", ["🤖 Gestión de Respuestas", "💳 Gestión de Pagos"])
    
    if menu == "🤖 Gestión de Respuestas":
        col_form, col_lista = st.columns([1, 2])
        
        with col_form:
            st.subheader("Nueva Regla")
            tipo = st.radio("Tipo de respuesta:", ["Texto", "PDF"])
            with st.form("form_nueva", clear_on_submit=True):
                palabras = st.text_input("Palabras clave")
                respuesta = st.text_area("Contenido") if tipo == "Texto" else st.file_uploader("Subir PDF", type=["pdf"])
                if st.form_submit_button("Guardar Regla"):
                    guardar_configuracion(palabras, respuesta)
                    st.rerun()
        
        with col_lista:
            st.subheader("Reglas Activas")
            for conf in obtener_configuraciones():
                with st.container(border=True):
                    c1, c2, c3 = st.columns([3, 2, 1])
                    c1.write(f"**{conf['palabra_clave']}**")
                    # Visualización clara del tipo
                    tipo_icono = "📄 PDF" if "http" in conf['respuestas']['contenido'] else "💬 Texto"
                    c2.write(f"{tipo_icono}")
                    if c3.button("✏️ Editar", key=f"edit_{conf['id']}"):
                        abrir_editor(conf)
