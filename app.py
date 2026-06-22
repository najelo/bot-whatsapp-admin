import streamlit as st
from auth_utils import verificar_login
from db_utils import obtener_configuraciones, guardar_configuracion
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
                st.success(msg) if exito else st.error(msg)
        
        if st.button("Actualizar lista de configuraciones"):
            datos = obtener_configuraciones()
            st.table([{"Palabra": i['palabra_clave'], "Respuesta": i.get('respuestas', {}).get('contenido')} for i in datos])

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
        
        # Iteración sobre los contactos registrados con diseño compacto
        for c in contactos:
            with st.container(border=True):
                # Proporción 4:1 para que el botón no sea gigante
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

    if st.sidebar.button("Cerrar sesión"):
        st.session_state["logueado"] = False
        st.rerun()
