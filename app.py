import streamlit as st
from auth_utils import verificar_login, get_supabase
from db_utils import obtener_configuraciones, guardar_configuracion, subir_archivo_al_storage, eliminar_regla
from pagos_utils import obtener_configuracion_pagos, guardar_contacto, activar_contacto

st.set_page_config(page_title="Admin Bot Pro", layout="wide")

# --- LOGIN ---
if "logueado" not in st.session_state: st.session_state["logueado"] = False
if not st.session_state["logueado"]:
    st.title("🔐 Iniciar Sesión")
    user, pwd = st.text_input("Usuario"), st.text_input("Contraseña", type="password")
    if st.button("Entrar"):
        valido, msg = verificar_login(user, pwd)
        if valido: st.session_state["logueado"] = True; st.rerun()
        else: st.error(msg)
    st.stop()

st.title("🤖 Panel de Control")
st.button("Cerrar sesión", on_click=lambda: st.session_state.update(logueado=False))

tab1, tab2 = st.tabs(["⚙️ Reglas de Bot", "💳 Gestión de Pagos"])

# --- TAB 1: REGLAS (PDF y Texto) ---
with tab1:
    with st.expander("➕ Nueva Regla"):
        palabras = st.text_input("Palabras clave (ej: recetario, hola)")
        # Permitimos subir cualquier archivo, no solo PDF
        archivo = st.file_uploader("Subir archivo (PDF, imagen, etc.)")
        res_texto = st.text_area("O escribe una respuesta de texto")
        
        if st.button("Guardar Regla"):
            if archivo:
                with st.spinner("Subiendo..."):
                    cont = subir_archivo_al_storage(archivo.getvalue(), archivo.name)
                    if cont: 
                        guardar_configuracion(palabras, cont, tipo="document")
                        st.success("Archivo guardado")
            elif res_texto:
                guardar_configuracion(palabras, res_texto, tipo="text")
                st.success("Texto guardado")
            st.rerun()

    for conf in obtener_configuraciones():
        with st.container(border=True):
            c1, c2 = st.columns([4, 1])
            c1.write(f"🔑 **{conf.get('palabra_clave')}**")
            resp = conf.get('respuestas', {})
            c1.caption(f"Contenido: {resp.get('contenido', '')[:50]}...")
            if c2.button("🗑️ Borrar", key=f"del_{conf['id']}"):
                eliminar_regla(conf['id'], resp.get('id'))
                st.rerun()

# --- TAB 2: PAGOS ---
with tab2:
    st.subheader("Configuración de Pago Móvil")
    with st.form("nuevo_pago"):
        ced = st.text_input("Cédula")
        tel = st.text_input("Teléfono")
        if st.form_submit_button("Agregar Cuenta"):
            guardar_contacto(ced, tel)
            st.success("Guardado")
            st.rerun()

    for p in obtener_configuracion_pagos():
        col1, col2 = st.columns([3, 1])
        estado = "✅ Activa" if p['activo'] else "⚪ Inactiva"
        col1.write(f"**{p['cedula_esperada']}** - {p['telefono_esperado']} ({estado})")
        if not p['activo']:
            if col2.button("Activar", key=f"act_{p['id']}"):
                activar_contacto(p['id'])
                st.rerun()
