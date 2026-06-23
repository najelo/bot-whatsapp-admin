import streamlit as st
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
        with st.form("nueva_config", clear_on_submit=True):
            c = st.text_input("Palabras clave (separadas por coma)")
            r = st.text_area("Respuesta automática")
            if st.form_submit_button("Guardar"):
                exito, msg = guardar_configuracion(c, r)
                if exito: st.success(msg); st.rerun()
                else: st.error(msg)

        st.divider()
        st.subheader("Reglas Actuales")
        configuraciones = obtener_configuraciones()
        todas_respuestas = obtener_todas_las_respuestas()
        
        # --- LÓGICA DE AGRUPACIÓN CORREGIDA ---
        agrupadas = {}
        for conf in configuraciones:
            # Agrupamos por respuesta_id para que una respuesta tenga varias palabras
            rid = conf['respuesta_id']
            if rid not in agrupadas:
                agrupadas[rid] = {
                    "contenido": conf['respuestas']['contenido'], 
                    "palabras": [], 
                    "ids": []
                }
            agrupadas[rid]["palabras"].append(conf['palabra_clave'])
            agrupadas[rid]["ids"].append(conf['id'])

        for rid, datos in agrupadas.items():
            with st.expander(f"Palabras: {', '.join(datos['palabras'])}"):
                st.write(f"**Respuesta:** {datos['contenido']}")
                
                # Selector de respuestas mejorado: muestra solo el contenido
                opciones = {r['contenido']: r['id'] for r in todas_respuestas}
                extra_sel = st.selectbox("Agregar otra palabra a esta respuesta:", [""] + list(opciones.keys()), key=f"sel_{rid}")
                
                if st.button("➕ Vincular palabra", key=f"btn_link_{rid}") and extra_sel:
                    guardar_palabra_individual(extra_sel, rid)
                    st.rerun()

                if st.button("🗑️ Eliminar esta regla", key=f"del_{rid}"):
                    for id_borrar in datos["ids"]: eliminar_configuracion(id_borrar)
                    st.rerun()
    
    with tab2:
        st.subheader("Registrar nuevos datos de pago")
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
                if c.get('activo'): col2.success("✅ Activo")
                else:
                    if col2.button("Activar", key=f"btn_activar_{c['id']}_{i}"):
                        activar_contacto(c['id'])
                        st.rerun()

    if st.sidebar.button("Cerrar sesión"):
        st.session_state["logueado"] = False
        st.rerun()
