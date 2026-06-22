import streamlit as st
from auth_utils import verificar_login

st.set_page_config(page_title="Admin Bot", page_icon="🤖")

# Inicializar sesión
if "logueado" not in st.session_state:
    st.session_state["logueado"] = False

# Lógica de Login
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
    # Si ya está logueado, mostrar el Dashboard
    st.title("🤖 Panel de Control del Bot")
    st.success("Acceso concedido")
    if st.button("Cerrar sesión"):
        st.session_state["logueado"] = False
        st.rerun()
