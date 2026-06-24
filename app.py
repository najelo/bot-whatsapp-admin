import streamlit as st
from auth_utils import verificar_login, get_supabase
from db_utils import obtener_configuraciones, guardar_configuracion
from pagos_utils import obtener_configuracion_pagos, guardar_contacto, activar_contacto

# --- LOGIN ---
if "logueado" not in st.session_state: st.session_state["logueado"] = False
if not st.session_state["logueado"]:
    user = st.text_input("Usuario"); pwd = st.text_input("Contraseña", type="password")
    if st.button("Entrar"):
        if verificar_login(user, pwd)[0]: st.session_state["logueado"] = True; st.rerun()
    st.stop()

# --- DIÁLOGOS ---
@st.dialog("Editar Regla")
def editar_regla(conf):
    resp = conf.get('respuestas') or {}
    val = st.text_area("Contenido:", value=resp.get('contenido', ''))
    if st.button("Guardar"):
        get_supabase().table("respuestas").update({"contenido": val}).eq("id", resp['id']).execute()
        st.rerun()

# --- PANTALLA ---
st.title("Panel de Control")
t1, t2 = st.tabs(["Reglas", "Pagos"])

with t1:
    for c in obtener_configuraciones():
        with st.container(border=True):
            st.write(f"🔑 **{c['palabra_clave']}**")
            st.code(c['respuestas']['contenido'] if c['respuestas'] else "Sin contenido")
            if st.button("Editar", key=f"e_{c['id']}"): editar_regla(c)

with t2:
    for p in obtener_configuracion_pagos():
        with st.container(border=True):
            st.write(f"Cédula: {p['cedula_esperada']} | Tel: {p['telefono_esperado']}")
            if not p['activo']:
                if st.button("Activar", key=f"a_{p['id']}"): activar_contacto(p['id']); st.rerun()
