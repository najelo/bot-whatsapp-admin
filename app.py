import streamlit as st
import uuid
from auth_utils import verificar_login, get_supabase
from db_utils import (
    obtener_configuraciones, guardar_configuracion, 
    eliminar_configuracion, guardar_palabra_individual,
    obtener_todas_las_respuestas
)
from pagos_utils import obtener_configuracion_pagos, guardar_contacto, activar_contacto

st.set_page_config(page_title="Admin Bot", page_icon="🤖", layout="wide")

# --- DIÁLOGO DE EDICIÓN ---
@st.dialog("Editar Regla")
def abrir_editor(conf):
    st.write(f"Editando palabra: **{conf['palabra_clave']}**")
    nueva_palabra = st.text_input("Palabra clave", value=conf['palabra_clave'])
    
    contenido_actual = conf['respuestas']['contenido']
    st.write(f"Contenido actual: `{contenido_actual[:40]}...`")
    nuevo_contenido = st.text_area("Editar contenido", value=contenido_actual)
    
    if st.button("Guardar Cambios"):
        try:
            get_supabase().table("configuracion").update({"palabra_clave": nueva_palabra}).eq("id", conf['id']).execute()
            get_supabase().table("respuestas").update({"contenido": nuevo_contenido}).eq("id", conf['respuestas']['id']).execute()
            st.success("¡Guardado!")
            st.rerun()
        except Exception as e:
            st.error(f"Error: {e}")

# --- LÓGICA PRINCIPAL ---
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
    st.title("🤖 Panel de Control del Bot")
    tab1, tab2 = st.tabs(["Configurar Bot", "Configurar Pagos"])
    
    with tab1:
        st.subheader("Nueva Regla de Respuesta")
        tipo = st.radio("Tipo de respuesta:", ["Texto", "PDF"])
        with st.form("nueva_config", clear_on_submit=True):
            c = st.text_input("Palabras clave")
            if tipo == "Texto":
                r = st.text_area("Respuesta")
                if st.form_submit_button("Guardar Texto"):
                    guardar_configuracion(c, r); st.rerun()
            else:
                archivo = st.file_uploader("Sube el PDF", type="pdf")
                if st.form_submit_button("Subir PDF"):
                    if archivo:
                        nombre_unico = f"{c.split(',')[0].strip()}_{uuid.uuid4().hex[:6]}.pdf"
                        get_supabase().storage.from_("recetarios-helado").upload(nombre_unico, archivo.getvalue())
                        url = get_supabase().storage.from_("recetarios-helado").get_public_url(nombre_unico)
                        guardar_configuracion(c, url); st.rerun()

        st.divider()
        st.subheader("Reglas Activas")
        for conf in obtener_configuraciones():
            with st.container(border=True):
                c1, c2, c3 = st.columns([3, 1, 1])
                c1.write(f"🔑 **{conf['palabra_clave']}**")
                c2.write("📄 PDF" if "http" in conf['respuestas']['contenido'] else "💬 Texto")
                if c3.button("✏️ Editar", key=f"edit_{conf['id']}"):
                    abrir_editor(conf)
    
    with tab2:
        st.subheader("Registrar pagos")
        with st.form("form_contacto", clear_on_submit=True):
            col_a, col_b = st.columns(2)
            ced = col_a.text_input("Cédula")
            tel = col_b.text_input("Teléfono")
            if st.form_submit_button("➕ Registrar"):
                guardar_contacto(ced, tel); st.rerun()
        
        for c in obtener_configuracion_pagos():
            with st.container(border=True):
                col1, col2 = st.columns([4, 1])
                col1.markdown(f"**Cédula:** `{c['cedula_esperada']}`")
                if c['activo']: col2.success("✅ Activo")
                elif col2.button("Activar", key=f"act_{c['id']}"):
                    activar_contacto(c['id']); st.rerun()

    if st.sidebar.button("Cerrar sesión"):
        st.session_state["logueado"] = False
        st.rerun()
