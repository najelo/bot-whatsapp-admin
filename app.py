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
        st.subheader("Reglas Guardadas")
        configuraciones = obtener_configuraciones()
        todas_respuestas = obtener_todas_las_respuestas()
        
        # --- LÓGICA DE AGRUPACIÓN POR RESPUESTA ---
        agrupadas = {}
        for conf in configuraciones:
            r_id = conf['respuesta_id']
            if r_id not in agrupadas:
                agrupadas[r_id] = {
                    "palabras": [], 
                    "contenido": conf['respuestas']['contenido'],
                    "ids": []
                }
            agrupadas[r_id]["palabras"].append(conf['palabra_clave'])
            agrupadas[r_id]["ids"].append(conf['id'])

        for r_id, datos in agrupadas.items():
            with st.expander(f"Reglas: {', '.join(datos['palabras'])}"):
                st.info(f"**Respuesta asociada:** {datos['contenido']}")
                
                # Editar palabras del grupo
                nueva_lista = st.text_input("Editar palabras clave:", 
                                            value=", ".join(datos['palabras']), 
                                            key=f"input_{r_id}")
                
                col1, col2 = st.columns(2)
                if col1.button("Actualizar palabras", key=f"upd_{r_id}"):
                    for id_borrar in datos['ids']: eliminar_configuracion(id_borrar)
                    for p in nueva_lista.split(','): guardar_palabra_individual(p.strip(), r_id)
                    st.rerun()
                
                if col2.button("🗑️ Eliminar grupo", key=f"del_{r_id}"):
                    for id_borrar in datos['ids']: eliminar_configuracion(id_borrar)
                    st.rerun()

                st.divider()
                # Vincular respuesta extra
                opciones = {r['contenido']: r['id'] for r in todas_respuestas}
                extra_sel = st.selectbox("Vincular otra respuesta existente:", list(opciones.keys()), key=f"sel_{r_id}")
                if st.button("➕ Vincular a este grupo", key=f"link_{r_id}"):
                    guardar_palabra_individual(datos['palabras'][0], opciones[extra_sel])
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
                if c['activo']: col2.success("✅ Activo")
                else:
                    if col2.button("Activar", key=f"btn_activar_{c['id']}_{i}"):
                        activar_contacto(c['id'])
                        st.rerun()

    if st.sidebar.button("Cerrar sesión"):
        st.session_state["logueado"] = False
        st.rerun()
