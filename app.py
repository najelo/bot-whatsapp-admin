import sys
import os

# --- CORRECCIÓN CRÍTICA: Añadir la subcarpeta al sistema de archivos ---
# Esto permite que app.py encuentre db_utils, auth_utils y pagos_utils
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
                            # Genera un nombre como: palabra_a1b2c3d4.pdf
                            nombre_base = c.split(',')[0].strip().replace(' ', '_')
                            nombre_unico = f"{nombre_base}_{str(uuid.uuid4())[:8]}.pdf"
                            
                            supabase.storage.from_("recetarios-helado").upload(
                                path=nombre_unico,
                                file=archivo.getvalue(),
                                file_options={"content-type": "application/pdf"}
                            )
                            url = supabase.storage.from_("recetarios-helado").get_public_url(nombre_unico)
                            
                            exito, msg = guardar_configuracion(c, url)
                            if exito: st.success("PDF subido correctamente"); st.rerun()
                            else: st.error(msg)
                        except Exception as e:
                            st.error(f"Error técnico: {e}")

        # ... (Tu lógica de visualización de reglas sigue aquí)
        st.divider()
        st.subheader("Reglas Guardadas")
        configuraciones = obtener_configuraciones()
        todas_respuestas = obtener_todas_las_respuestas()
        
        agrupadas = {}
        for conf in configuraciones:
            palabra = conf['palabra_clave'].strip()
            if palabra not in agrupadas: agrupadas[palabra] = {"respuestas": [], "ids": []}
            agrupadas[palabra]["respuestas"].append(conf['respuestas']['contenido'])
            agrupadas[palabra]["ids"].append(conf['id'])

        for palabra, datos in agrupadas.items():
            with st.expander(f"Regla: {palabra}"):
                for res in datos["respuestas"]: st.info(f"• {res}")
                
                opciones = {r['contenido']: r['id'] for r in todas_respuestas}
                extra_sel = st.selectbox("Agregar otra respuesta:", list(opciones.keys()), key=f"sel_{palabra}")
                if st.button("➕ Vincular respuesta", key=f"btn_link_{palabra}"):
                    guardar_palabra_individual(palabra, opciones[extra_sel])
                    st.rerun()
                if st.button("🗑️ Eliminar todas", key=f"del_{palabra}"):
                    for id_borrar in datos["ids"]: eliminar_configuracion(id_borrar)
                    st.rerun()
    
    with tab2:
        st.subheader("Registrar nuevos datos de pago")
        with st.form("form_contacto", clear_on_submit=True):
            col_a, col_b = st.columns(2)
            ced = col_a.text_input("Cédula Esperada")
            tel = col_b.text_input("Teléfono Esperado")
            if st.form_submit_button("➕ Registrar Datos"):
                guardar_contacto(ced, tel); st.rerun()

        st.divider()
        st.subheader("Seleccionar Registro Activo")
        contactos = obtener_configuracion_pagos()
        for i, c in enumerate(contactos):
            with st.container(border=True):
                col1, col2 = st.columns([4, 1])
                col1.markdown(f"**Cédula:** `{c['cedula_esperada']}`")
                if c['activo']: col2.success("✅ Activo")
                elif col2.button("Activar", key=f"btn_act_{c['id']}"):
                    activar_contacto(c['id']); st.rerun()

    if st.sidebar.button("Cerrar sesión"):
        st.session_state["logueado"] = False
        st.rerun()
