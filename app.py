import streamlit as st
import uuid # Necesario para los nombres únicos
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
        # Selector de tipo
        tipo = st.radio("Tipo de respuesta:", ["Texto", "PDF"])
        
        with st.form("nueva_config", clear_on_submit=True):
            c = st.text_input("Palabra clave")
            
            if tipo == "Texto":
                r = st.text_area("Respuesta automática")
                submit = st.form_submit_button("Guardar Texto")
                if submit:
                    exito, msg = guardar_configuracion(c, r)
                    if exito: st.success(msg); st.rerun()
                    else: st.error(msg)
            else:
                archivo = st.file_uploader("Sube el PDF", type="pdf")
                submit = st.form_submit_button("Subir PDF")
                if submit and archivo:
                    try:
                        # Lógica de nombre único con UUID
                        supabase = get_supabase()
                        nombre_unico = f"{c.replace(' ', '_')}_{str(uuid.uuid4())[:8]}.pdf"
                        
                        # Subida a Supabase Storage
                        supabase.storage.from_("recetarios-helado").upload(
                            path=nombre_unico,
                            file=archivo.getvalue()
                        )
                        # Obtener URL pública
                        url = supabase.storage.from_("recetarios-helado").get_public_url(nombre_unico)
                        
                        # Guardar en base de datos usando la función existente
                        exito, msg = guardar_configuracion(c, url)
                        if exito: st.success("PDF subido y registrado"); st.rerun()
                        else: st.error(msg)
                    except Exception as e:
                        st.error(f"Error subiendo archivo: {e}")

        st.divider()
        st.subheader("Reglas Guardadas")
        # (El resto de tu código original se mantiene igual)
        configuraciones = obtener_configuraciones()
        todas_respuestas = obtener_todas_las_respuestas()
        
        agrupadas = {}
        for conf in configuraciones:
            palabra = conf['palabra_clave'].strip()
            if palabra not in agrupadas:
                agrupadas[palabra] = {"respuestas": [], "ids": []}
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

                if st.button("🗑️ Eliminar todas las respuestas", key=f"del_{palabra}"):
                    for id_borrar in datos["ids"]: eliminar_configuracion(id_borrar)
                    st.rerun()
    
    with tab2:
        st.subheader("Registrar nuevos datos de pago")
        # (Tu código original de pagos se mantiene igual aquí)
        with st.form("form_contacto", clear_on_submit=True):
            col_a, col_b = st.columns(2)
            ced = col_a.text_input("Cédula Esperada")
            tel = col_b.text_input("Teléfono Esperado")
            if st.form_submit_button("➕ Registrar Datos"):
                guardar_contacto(ced, tel)
                st.rerun()

        st.divider()
        st.subheader("Seleccionar Registro Activo")
        contactos = obtener_configuracion_pagos()
        for i, c in enumerate(contactos):
            with st.container(border=True):
                col1, col2 = st.columns([4, 1], vertical_alignment="center")
                col1.markdown(f"**Cédula:** `{c['cedula_esperada']}`  |  **Tel:** `{c['telefono_esperado']}`")
                if c['activo']: col2.success("✅ Activo")
                else:
                    if col2.button("Activar", key=f"btn_activar_{c['id']}_{i}"):
                        activar_contacto(c['id'])
                        st.rerun()

    if st.sidebar.button("Cerrar sesión"):
        st.session_state["logueado"] = False
        st.rerun()
