import streamlit as st
from auth_utils import verificar_login
from db_utils import obtener_configuraciones, guardar_configuracion
from pagos_utils import obtener_configuracion_pagos, guardar_regla_pago

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
        with st.form("nueva_config"):
            c = st.text_input("Palabra clave")
            r = st.text_area("Respuesta automática")
            if st.form_submit_button("Guardar"):
                exito, msg = guardar_configuracion(c, r)
                st.success(msg) if exito else st.error(msg)
        if st.button("Ver configuraciones"):
            datos = obtener_configuraciones()
            st.table([{"Palabra": i['palabra_clave'], "Respuesta": i.get('respuestas', {}).get('contenido')} for i in datos])

    with tab2:
        with st.form("config_pagos"):
            tel = st.text_input("Teléfono de cobro")
            id_pagos = st.text_input("Identidad (ID)")
            monto = st.number_input("Monto mínimo de aprobación", min_value=0.0)
            if st.form_submit_button("Guardar Reglas"):
                exito, msg = guardar_regla_pago(tel, id_pagos, monto)
                st.success(msg) if exito else st.error(msg)
        if st.button("Ver reglas vigentes"):
            st.table(obtener_configuracion_pagos())

    if st.sidebar.button("Cerrar sesión"):
        st.session_state["logueado"] = False
        st.rerun()
