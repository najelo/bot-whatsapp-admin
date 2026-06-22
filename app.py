import streamlit as st
from auth_utils import verificar_login
from db_utils import obtener_configuraciones, guardar_configuracion

st.set_page_config(page_title="Admin Bot", page_icon="🤖")

if "logueado" not in st.session_state:
    st.session_state["logueado"] = False

if not st.session_state["logueado"]:
    st.title("🔐 Acceso al Sistema")
    user = st.text_input("Usuario")
    pwd = st.text_input("Contraseña", type="password")
    if st.button("Ingresar"):
        exito, mensaje = verificar_login(user, pwd)
        if exito:
            st.session_state["logueado"] = True
            st.rerun()
        else:
            st.error(mensaje)
else:
    st.title("🤖 Panel de Control del Bot")
    tab1, tab2 = st.tabs(["Configurar Bot", "Verificar Pagos"])
    
    with tab1:
        st.subheader("Configuración de Respuestas")
        with st.form("nueva_config"):
            c = st.text_input("Palabra clave")
            r = st.text_area("Respuesta automática")
            if st.form_submit_button("Guardar"):
                exito, msg = guardar_configuracion(c, r)
                if exito: st.success(msg)
                else: st.error(msg)
        
        if st.button("Actualizar lista"):
            datos = obtener_configuraciones()
            if datos: st.table(datos)
            else: st.info("No hay configuraciones.")

    with tab2:
        st.write("Sección en desarrollo...")
    
    if st.sidebar.button("Cerrar sesión"):
        st.session_state["logueado"] = False
        st.rerun()
