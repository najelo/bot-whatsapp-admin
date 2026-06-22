import streamlit as st
from auth_utils import verificar_login

st.title("🔐 Login de Administrador")

username = st.text_input("Usuario")
password = st.text_input("Contraseña", type="password")

if st.button("Entrar"):
    es_valido, mensaje = verificar_login(username, password)
    
    if es_valido:
        st.success(mensaje)
        st.session_state["logueado"] = True  # Para mantener la sesión activa
        st.rerun() # Recarga la app para mostrar el contenido oculto
    else:
        st.error(mensaje)
