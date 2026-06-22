import streamlit as st
from auth_utils import verificar_login

# Configuración de página
st.set_page_config(page_title="Panel de Administración Bot", page_icon="🤖")

# Inicializar estado de sesión
if "logueado" not in st.session_state:
    st.session_state["logueado"] = False

# --- Lógica de Login ---
def mostrar_login():
    st.title("🔐 Login de Administrador")
    username = st.text_input("Usuario")
    password = st.text_input("Contraseña", type="password")
    
    if st.button("Entrar"):
        es_valido, mensaje = verificar_login(username, password)
        if es_valido:
            st.session_state["logueado"] = True
            st.rerun()
        else:
            st.error(mensaje)

# --- Contenido Principal (Lo que ve el admin) ---
def mostrar_dashboard():
    st.title("🤖 Panel de Control del Bot")
    st.write("Bienvenido, administrador.")
    
    if st.button("Cerrar sesión"):
        st.session_state["logueado"] = False
        st.rerun()
    
    # AQUÍ VA LA LÓGICA DE TU BOT
    # Por ejemplo: gestionar mensajes, ver logs, etc.
    st.subheader("Configuración del Bot")
    st.text("Aquí irían tus controles de WhatsApp...")

# --- Control de flujo ---
if not st.session_state["logueado"]:
    mostrar_login()
else:
    mostrar_dashboard()
