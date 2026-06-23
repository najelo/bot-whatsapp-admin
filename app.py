import streamlit as st
import uuid
from auth_utils import verificar_login, get_supabase
from db_utils import (
    obtener_configuraciones, guardar_configuracion
)
from pagos_utils import obtener_configuracion_pagos, guardar_contacto, activar_contacto

st.set_page_config(page_title="Admin Bot", page_icon="🤖", layout="wide")

# --- DIÁLOGO DE EDICIÓN ---
@st.dialog("Editar Regla")
def abrir_editor(conf):
    st.write(f"Editando: **{conf['palabra_clave']}**")
    
    # Edición de Palabra
    nueva_palabra = st.text_input("Palabra clave", value=conf['palabra_clave'])
    
    # Detección de PDF
    contenido_actual = conf['respuestas']['contenido']
    es_pdf = "http" in contenido_actual
    
    if es_pdf:
        st.write(f"📄 **Archivo PDF actual:** [Ver archivo]({contenido_actual})")
        nuevo_contenido = contenido_actual # Mantenemos la URL
    else:
        nuevo_contenido = st.text_area("Editar respuesta", value=contenido_actual)
    
    if st.button("Guardar Cambios"):
        try:
            # Asegúrate que 'respuestas' sea el nombre de tu tabla
            get_supabase().table("respuestas").update({
                "palabra_clave": nueva_palabra, 
                "contenido": nuevo_contenido
            }).eq("id", conf['id']).execute()
            st.success("¡Guardado!")
            st.rerun()
        except Exception as e:
            st.error(f"Error: {e}")

# --- LÓGICA PRINCIPAL ---
if "logueado" not in st.session_state: st.session_state["logueado"] = False

if not st.session_state["logueado"]:
    st.title("🔐 Acceso al Sistema")
    user = st.text_input("Usuario")
    pwd = st.text_input("Contraseña", type="password")
    if st.button("Ingresar"):
        if verificar_login(user, pwd)[0]:
            st.session_state["logueado"] = True
            st.rerun()
else:
    tab1, tab2 = st.tabs(["Configurar Bot", "Configurar Pagos"])
    
    with tab1:
        st.subheader("Nueva Regla (Texto o PDF)")
        tipo = st.radio("Selecciona tipo:", ["Texto", "PDF"])
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
                        # Usamos tu lógica de subida a Storage
                        nombre = f"{uuid.uuid4()}.pdf"
                        get_supabase().storage.from_("recetarios-helado").upload(nombre, archivo.getvalue())
                        url = get_supabase().storage.from_("recetarios-helado").get_public_url(nombre)
                        guardar_configuracion(palabra, url); st.rerun()

        st.divider()
        st.subheader("Reglas Activas")
        for conf in obtener_configuraciones():
            with st.container(border=True):
                c1, c2, c3 = st.columns([3, 1, 1])
                c1.write(f"🔑 **{conf['palabra_clave']}**")
                c2.write("📄 PDF" if "http" in conf['respuestas']['contenido'] else "💬 Texto")
                if c3.button("✏️ Editar", key=f"edit_{conf['id']}"):
                    abrir_editor(conf)
    
    with tab2:
        # Tu lógica de pagos aquí
        pass
