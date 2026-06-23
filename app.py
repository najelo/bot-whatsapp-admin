import streamlit as st
import uuid
from auth_utils import verificar_login, get_supabase
from db_utils import (
    obtener_configuraciones, guardar_configuracion, eliminar_configuracion
)
from pagos_utils import obtener_configuracion_pagos, guardar_contacto, activar_contacto

st.set_page_config(page_title="Admin Bot", page_icon="🤖", layout="wide")

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
    st.sidebar.title("Navegación")
    menu = st.sidebar.radio("Opciones", ["🤖 Gestión de Respuestas", "💳 Gestión de Pagos"])
    st.sidebar.markdown("---")
    if st.sidebar.button("Cerrar sesión"):
        st.session_state["logueado"] = False
        st.rerun()

    st.title("🤖 Panel de Control")

    if menu == "🤖 Gestión de Respuestas":
        col_form, col_lista = st.columns([1, 2])
        
        with col_form:
            st.subheader("Nueva Regla")
            tipo = st.radio("Tipo:", ["Texto", "PDF"])
            with st.form("form_nueva_regla", clear_on_submit=True):
                palabras = st.text_input("Palabra clave")
                if tipo == "Texto":
                    respuesta = st.text_area("Contenido")
                else:
                    respuesta = st.file_uploader("Cargar PDF", type=["pdf"])
                
                if st.form_submit_button("Guardar"):
                    # Aquí tu lógica de guardado actual
                    if tipo == "PDF" and respuesta:
                        supabase = get_supabase()
                        nombre = f"{uuid.uuid4()}.pdf"
                        supabase.storage.from_("recetarios-helado").upload(nombre, respuesta.getvalue())
                        url = supabase.storage.from_("recetarios-helado").get_public_url(nombre)
                        guardar_configuracion(palabras, url)
                    else:
                        guardar_configuracion(palabras, respuesta)
                    st.rerun()
            
        with col_lista:
            st.subheader("Gestión Atómica de Reglas")
            for conf in obtener_configuraciones():
                with st.container(border=True):
                    # 1. Gestión de Palabra Clave
                    c1, c2 = st.columns([4, 1])
                    c1.write(f"🔑 **Palabra:** `{conf['palabra_clave']}`")
                    if c2.button("Borrar Palabra", key=f"del_p_{conf['id']}"):
                        get_supabase().table("configuracion").update({"palabra_clave": None}).eq("id", conf['id']).execute()
                        st.rerun()
                    
                    # 2. Gestión de Respuesta
                    c3, c4 = st.columns([4, 1])
                    contenido = conf['respuestas']['contenido']
                    if "http" in contenido:
                        c3.write(f"📄 **PDF:** [Ver archivo]({contenido})")
                    else:
                        c3.write(f"💬 **Respuesta:** {contenido}")
                    
                    if c4.button("Borrar Contenido", key=f"del_r_{conf['id']}"):
                        get_supabase().table("respuestas").update({"contenido": None}).eq("id", conf['respuestas']['id']).execute()
                        st.rerun()

    elif menu == "💳 Gestión de Pagos":
        st.subheader("💳 Gestión de Pagos")
        # ... (Mantén tu lógica de pagos aquí)
        for c in obtener_configuracion_pagos():
            with st.container(border=True):
                col1, col2, col3 = st.columns([3, 1, 1])
                col1.markdown(f"**Cédula:** `{c.get('cedula_esperada', 'N/A')}`")
                if col3.button("🗑️", key=f"del_pago_{c['id']}"):
                    get_supabase().table("configuracion_pago").delete().eq("id", c['id']).execute()
                    st.rerun()
