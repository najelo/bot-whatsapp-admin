import streamlit as st
from auth_utils import verificar_login

st.title("🤖 Panel de Control")

# 1. Gestión de estado
if "logueado" not in st.session_state:
    st.session_state["logueado"] = False

# 2. Si no está logueado, mostrar formulario simple
if not st.session_state["logueado"]:
    username = st.text_input("Usuario")
    password = st.text_input("Contraseña", type="password")
    
    if st.button("Entrar"):
        valido, mensaje = verificar_login(username, password)
        if valido:
            st.session_state["logueado"] = True
            st.rerun()
        else:
            st.error(mensaje)
else:
    st.success("¡Bienvenido al panel!")
    if st.button("Cerrar sesión"):
        st.session_state["logueado"] = False
        st.rerun()
