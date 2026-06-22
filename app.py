import streamlit as st
from auth_utils import verificar_login
from db_utils import (
    obtener_configuraciones, guardar_configuracion, 
    eliminar_configuracion, guardar_palabra_individual
)
from pagos_utils import obtener_configuracion_pagos, guardar_contacto, activar_contacto

st.set_page_config(page_title="Admin Bot", page_icon="🤖")

if "logueado" not in st.session_state: st.session_state["logueado"] = False

if not st.session_state["logueado"]:
    st.title("🔐 Acceso")
    user, pwd = st.text_input("Usuario"), st.text_input("Contraseña", type="password")
    if st.button("Ingresar"):
        exito, msg = verificar_login(user, pwd)
        if exito: st.session_state["logueado"] = True; st.rerun()
        else: st.error(msg)
else:
    st.title("🤖 Panel de Control")
    tab1, tab2 = st.tabs(["Configurar Bot", "Configurar Pagos"])
    
    with tab1:
        st.subheader("Nueva Regla")
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
        
        # Lógica para agrupar palabras por respuesta
        agrupadas = {}
        for conf in configuraciones:
            r_id = conf['respuesta_id']
            if r_id not in agrupadas:
                agrupadas[r_id] = {"contenido": conf['respuestas']['contenido'], "palabras": [], "ids": []}
            agrupadas[r_id]["palabras"].append(conf['palabra_clave'])
            agrupadas[r_id]["ids"].append(conf['id'])

        for r_id, datos in agrupadas.items():
            with st.expander(f"Regla: {', '.join(datos['palabras'])}"):
                nueva_lista = st.text_input("Palabras clave (separadas por coma)", 
                                            value=", ".join(datos['palabras']), 
                                            key=f"input_{r_id}")
                st.write(f"**Respuesta:** {datos['contenido']}")
                
                col1, col2 = st.columns(2)
                if col1.button("Actualizar grupo", key=f"btn_{r_id}"):
                    for id_a_borrar in datos['ids']:
                        eliminar_configuracion(id_a_borrar)
                    for p in nueva_lista.split(','):
                        guardar_palabra_individual(p.strip(), r_id)
                    st.rerun()
                if col2.button("🗑️ Eliminar todo el grupo", key=f"del_{r_id}"):
                    for id_a_borrar in datos['ids']:
                        eliminar_configuracion(id_a_borrar)
                    st.rerun()

    with tab2:
        # (Tu código de pagos existente)
        pass
