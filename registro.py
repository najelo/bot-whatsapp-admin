import streamlit as st
from auth_utils import registrar_usuario_seguro

st.title("🔐 Registro de Administrador")

username = st.text_input("Usuario")
password = st.text_input("Contraseña", type="password")

if st.button("Registrarme"):
    if username and password:
        try:
            registrar_usuario_seguro(username, password)
            st.success("¡Usuario creado exitosamente! Ahora borra este archivo.")
        except Exception as e:
            st.error(f"Error: {e}")
    else:
        st.warning("Por favor llena todos los campos.")
