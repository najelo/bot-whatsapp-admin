import streamlit as st
from auth_utils import verificar_login
from db_utils import (
    obtener_configuraciones, 
    guardar_configuracion, 
    eliminar_configuracion, 
    actualizar_configuracion, 
    obtener_todas_las_respuestas
)
from pagos_utils import obtener_configuracion_pagos, guardar_contacto, activar_contacto

st.set_page_config(page_title="Admin Bot", page_icon="🤖")

if "logueado" not in st.session_state: 
    st.session_state["logueado"] = False

if not st.session_state["logueado"]:
    st.title("🔐 Acceso al Sistema")
    user = st.text_input("Usuario")
    pwd = st.text_input("Contraseña", type="password")
    if st.button("Ingresar"):
        exito, msg = verificar_login(user, pwd)
        if exito:
            st.session_state["logueado"] = True
            st.rerun()
        else: 
            st.error(msg)
else:
    st.title("🤖 Panel de Control del Bot")
    tab1, tab2 = st.tabs(["Configurar Bot", "Configurar Pagos"])
    
    with tab1:
        st.subheader("Configuración de Respuestas")
        with st.form("nueva_config", clear_on_submit=True):
            c = st.text_input("Palabra clave")
            r = st.text_area("Respuesta automática")
            if st.form_submit_button("Guardar"):
                exito, msg = guardar_configuracion(c, r)
                if exito: st.success(msg)
                else: st.error(msg)
                st.rerun()

        st.divider()
        st.subheader("Reglas Guardadas")
        configuraciones = obtener_configuraciones()
        todas_respuestas = obtener_todas_las_respuestas()

        for conf in configuraciones:
            with st.expander(f"Regla: {conf['palabra_clave']}"):
                nueva_palabra = st.text_input(f"Palabra", value=conf['palabra_clave'], key=f"p_{conf['id']}")
                
                opciones = {r['contenido']: r['id'] for r in todas_respuestas}
                resp_actual = conf.get('respuestas', {}).get('contenido', '')
                sel_respuesta = st.selectbox("Vincular respuesta:", list(opciones.keys()), 
                                             index=list(opciones.keys()).index(resp_actual) if resp_actual in opciones else 0,
                                             key=f"s_{conf['id']}")
                
                col1, col2 = st.columns(2)
                if col1.button("Guardar Cambios", key=f"upd_{conf['id']}"):
                    actualizar_configuracion(conf['id'], nueva_palabra, opciones[sel_respuesta])
                    st.rerun()
                
                if col2.button("🗑️ Eliminar", key=f"del_{conf['id']}"):
                    eliminar_configuracion(conf['id'])
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
        
        for c in contactos:
            with st.container(border=True):
                col1, col2 = st.columns([4, 1], vertical_alignment="center")
                estado_texto = "🟢 Activo" if c['activo'] else "⚪ Inactivo"
                col1.markdown(f"**Cédula:** `{c['cedula_esperada']}`  |  **Tel:** `{c['telefono_esperado']}`")
                col1.caption(f"Estado: {estado_texto}")
                
                if c['activo']:
                    col2.success("✅ Activo")
                else:
                    if col2.button("Activar", key=f"btn_{c['id']}"):
                        activar_contacto(c['id'])
                        st.rerun()
