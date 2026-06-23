import streamlit as st
import uuid
from auth_utils import verificar_login, get_supabase
from db_utils import (
    obtener_configuraciones, guardar_configuracion, 
    eliminar_configuracion
)
from pagos_utils import obtener_configuracion_pagos, guardar_contacto, activar_contacto

# Configuración inicial
st.set_page_config(page_title="Admin Bot", page_icon="🤖", layout="wide")

if "logueado" not in st.session_state: 
    st.session_state["logueado"] = False

# --- LÓGICA DE LOGIN ---
if not st.session_state["logueado"]:
    st.title("🔐 Acceso al Sistema")
    user = st.text_input("Usuario")
    pwd = st.text_input("Contraseña", type="password")
    if st.button("Ingresar"):
        exito, msg = verificar_login(user, pwd)
        if exito:
            st.session_state["logueado"] = True
            st.rerun()
        else: 
            st.error(msg)
else:
    # --- PANEL DE CONTROL ---
    
    # Navegación Lateral
    st.sidebar.title("Navegación")
    menu = st.sidebar.radio("Opciones", ["🤖 Gestión de Respuestas", "💳 Gestión de Pagos"])
    
    st.sidebar.markdown("---")
    if st.sidebar.button("Cerrar sesión"):
        st.session_state["logueado"] = False
        st.rerun()

    st.title("🤖 Panel de Control")

    # --- GESTIÓN DE RESPUESTAS ---
    if menu == "🤖 Gestión de Respuestas":
        col_form, col_lista = st.columns([1, 2])
        
        with col_form:
            st.subheader("Nueva Regla")
            tipo = st.radio("Tipo de respuesta:", ["Texto", "PDF"])
            with st.form("form_nueva_regla", clear_on_submit=True):
                palabras = st.text_input("Palabras clave (separadas por coma)")
                
                if tipo == "Texto":
                    respuesta = st.text_area("Contenido de la respuesta")
                else:
                    respuesta = st.file_uploader("Cargar archivo PDF", type=["pdf"])
                
                if st.form_submit_button("Guardar Regla"):
                    if tipo == "Texto":
                        exito, msg = guardar_configuracion(palabras, respuesta)
                        if exito: st.success(msg); st.rerun()
                        else: st.error(msg)
                    else:
                        if respuesta:
                            supabase = get_supabase()
                            nombre_archivo = f"{uuid.uuid4()}.pdf"
                            supabase.storage.from_("recetarios-helado").upload(nombre_archivo, respuesta.getvalue())
                            url = supabase.storage.from_("recetarios-helado").get_public_url(nombre_archivo)
                            exito, msg = guardar_configuracion(palabras, url)
                            if exito: st.success("PDF guardado correctamente"); st.rerun()
            
        with col_lista:
            st.subheader("Reglas Activas")
            for conf in obtener_configuraciones():
                with st.container(border=True):
                    # Visualización del registro
                    st.write(f"**Palabra:** `{conf['palabra_clave']}`")
                    st.write(f"**Contenido:** {conf['respuestas']['contenido']}")
                    
                    # Botón de eliminación selectiva
                    if st.button("🗑️ Eliminar esta regla", key=f"del_{conf['id']}"):
                        # Ejecuta la eliminación individual
                        eliminar_configuracion(conf['id'])
                        st.toast("Regla eliminada")
                        st.rerun()

    # --- GESTIÓN DE PAGOS ---
    elif menu == "💳 Gestión de Pagos":
        st.subheader("💳 Gestión de Pagos")
        
        with st.container(border=True):
            st.markdown("### ➕ Agregar Nueva Identidad")
            c1, c2, c3, c4 = st.columns([2, 2, 2, 1])
            ced = c1.text_input("Cédula")
            tel = c2.text_input("Teléfono")
            monto = c3.number_input("Monto Mín.", min_value=0.0)
            if c4.button("Registrar"):
                guardar_contacto(ced, tel)
                st.rerun()

        st.divider()
        st.subheader("Registros Guardados")
        for c in obtener_configuracion_pagos():
            with st.container(border=True):
                col1, col2, col3 = st.columns([3, 1, 1])
                col1.markdown(f"**Cédula:** `{c.get('cedula_esperada', 'N/A')}` | **Tel:** `{c.get('telefono_esperado', 'N/A')}`")
                
                if c.get('activo', False): 
                    col2.success("✅ Activo")
                else:
                    if col2.button("Activar", key=f"btn_act_{c['id']}"):
                        activar_contacto(c['id']); st.rerun()
                
                # Eliminación selectiva de pago
                if col3.button("🗑️", key=f"del_pago_{c['id']}"):
                    get_supabase().table("configuracion_pago").delete().eq("id", c['id']).execute()
                    st.toast("Pago eliminado")
                    st.rerun()
