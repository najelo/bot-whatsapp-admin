import streamlit as st
from auth_utils import verificar_login

def gestionar_login():
    if "logueado" not in st.session_state: 
        st.session_state["logueado"] = False
    
    if not st.session_state["logueado"]:
        st.title("🔐 Iniciar Sesión")
        user = st.text_input("Usuario")
        pwd = st.text_input("Contraseña", type="password")
        
        if st.button("Entrar"):
            valido, msg = verificar_login(user, pwd)
            if valido: 
                st.session_state["logueado"] = True
                st.rerun()
            else: 
                st.error(msg)
        st.stop() # Detiene la ejecución si no está logueado
