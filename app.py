import streamlit as st
from auth_utils import get_supabase, verificar_login

# Configuración de página
st.set_page_config(page_title="Admin Bot", page_icon="🤖")

# Conexión segura a Supabase
@st.cache_resource
def conectar_db():
    return get_supabase()

supabase = conectar_db()

# Inicializar sesión
if "logueado" not in st.session_state:
    st.session_state["logueado"] = False

# Lógica principal
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
    # AQUI EL DASHBOARD: Solo se ejecuta si está logueado
    st.title("🤖 Panel de Control del Bot")
    
    tab1, tab2 = st.tabs(["Configurar Bot", "Verificar Pagos"])
    
    with tab1:
        st.subheader("Palabras clave y respuestas")
        # Usamos try/except para capturar si la tabla 'config_bot' no existe
        try:
            response = supabase.table("config_bot").select("*").execute()
            st.write(response.data)
        except Exception as e:
            st.error(f"Error al leer 'config_bot': {e}")
            st.info("Asegúrate de que la tabla 'config_bot' existe en Supabase.")

    with tab2:
        st.write("Sección de pagos")
    
    if st.button("Cerrar sesión"):
        st.session_state["logueado"] = False
        st.rerun()
