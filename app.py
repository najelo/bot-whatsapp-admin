import sys
import os
# --- CORRECCIÓN DE RUTA PARA QUE ENCUENTRE LOS ARCHIVOS ---
sys.path.append(os.path.join(os.path.dirname(__file__), "bot-whatsapp-admin-main"))

import streamlit as st
import uuid
from auth_utils import verificar_login, get_supabase
from db_utils import (
    obtener_configuraciones, guardar_configuracion, 
    eliminar_configuracion, guardar_palabra_individual,
    obtener_todas_las_respuestas
)
from pagos_utils import obtener_configuracion_pagos, guardar_contacto, activar_contacto

st.set_page_config(page_title="Admin Bot", page_icon="🤖")

if "logueado" not in st.session_state: st.session_state["logueado"] = False

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
    st.title("🤖 Panel de Control del Bot")
    tab1, tab2 = st.tabs(["Configurar Bot", "Configurar Pagos"])
    
    with tab1:
        st.subheader("Nueva Regla de Respuesta")
        tipo = st.radio("Tipo de respuesta:", ["Texto", "PDF"])
        
        with st.form("nueva_config", clear_on_submit=True):
            c = st.text_input("Palabras clave (separadas por coma)")
            
            if tipo == "Texto":
                r = st.text_area("Respuesta automática")
                if st.form_submit_button("Guardar Texto"):
                    exito, msg = guardar_configuracion(c, r)
                    if exito: st.success(msg); st.rerun()
                    else: st.error(msg)
            else:
                archivo = st.file_uploader("Sube el PDF", type="pdf")
                if st.form_submit_button("Subir PDF"):
                    if archivo:
                        try:
                            supabase = get_supabase()
                            # --- LÓGICA DE NOMBRE ÚNICO (UUID) ---
                            nombre_base = c.split(',')[0].strip().replace(' ', '_')
                            nombre_unico = f"{nombre_base}_{str(uuid.uuid4())[:8]}.pdf"
                            
                            supabase.storage.from_("recetarios-helado").upload(
                                path=nombre_unico,
                                file=archivo.getvalue()
                            )
                            url = supabase.storage.from_("recetarios-helado").get_public_url(nombre_unico)
                            
                            exito, msg = guardar_configuracion(c, url)
                            if exito: st.success("PDF subido correctamente"); st.rerun()
                            else: st.error(msg)
                        except Exception as e:
                            st.error(f"Error técnico: {e}")

        # ... (Mantén aquí el resto de tu lógica de visualización de reglas)
        # ...
