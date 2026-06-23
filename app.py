import streamlit as st
import uuid
from auth_utils import verificar_login, get_supabase
from db_utils import obtener_configuraciones, guardar_configuracion
from pagos_utils import obtener_configuracion_pagos, guardar_contacto, activar_contacto

# --- Función para el Modal de Edición ---
@st.dialog("Editar Regla")
def abrir_editor(conf):
    st.write(f"Editando la regla para: **{conf['palabra_clave']}**")
    
    # Edición de Palabra
    nueva_palabra = st.text_input("Palabra clave", value=conf['palabra_clave'])
    
    # Edición de Respuesta/PDF
    st.write("---")
    contenido_actual = conf['respuestas']['contenido']
    st.write(f"Contenido actual: `{contenido_actual[:30]}...`")
    nuevo_contenido = st.text_area("Nuevo contenido de respuesta", value=contenido_actual)
    
    if st.button("Guardar Cambios"):
        # Lógica de actualización (usar tus funciones de db_utils)
        get_supabase().table("configuracion").update({"palabra_clave": nueva_palabra}).eq("id", conf['id']).execute()
        get_supabase().table("respuestas").update({"contenido": nuevo_contenido}).eq("id", conf['respuestas']['id']).execute()
        st.success("¡Guardado!")
        st.rerun()

    if st.button("🗑️ Borrar todo este registro", type="primary"):
        get_supabase().table("configuracion").delete().eq("id", conf['id']).execute()
        st.rerun()

# --- Configuración y Login (mismo de siempre) ---
st.set_page_config(layout="wide")
if "logueado" not in st.session_state: st.session_state["logueado"] = False

if not st.session_state["logueado"]:
    # ... (tu código de login) ...
    pass
else:
    # --- Interfaz Principal ---
    menu = st.sidebar.radio("Opciones", ["🤖 Gestión de Respuestas", "💳 Gestión de Pagos"])
    
    if menu == "🤖 Gestión de Respuestas":
        st.subheader("Reglas Activas")
        for conf in obtener_configuraciones():
            with st.container(border=True):
                col1, col2, col3 = st.columns([3, 1, 1])
                col1.write(f"🔑 **{conf['palabra_clave']}**")
                col2.write(f"💬 {conf['respuestas']['contenido'][:20]}...")
                
                if col3.button("✏️ Editar", key=f"edit_{conf['id']}"):
                    abrir_editor(conf)
