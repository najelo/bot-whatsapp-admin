import streamlit as st
from auth_utils import verificar_login, get_supabase
from db_utils import obtener_configuraciones, guardar_configuracion
from pagos_utils import obtener_configuracion_pagos, guardar_contacto, activar_contacto

st.set_page_config(page_title="Admin Bot", layout="wide")

# --- LOGIN ---
if "logueado" not in st.session_state: st.session_state["logueado"] = False
if not st.session_state["logueado"]:
    st.title("🔐 Iniciar Sesión")
    user = st.text_input("Usuario")
    pwd = st.text_input("Contraseña", type="password")
    if st.button("Entrar"):
        if verificar_login(user, pwd)[0]: st.session_state["logueado"] = True; st.rerun()
        else: st.error("Credenciales incorrectas")
    st.stop()

# --- DIÁLOGOS ---
@st.dialog("Editar Regla")
def editar_regla(conf):
    resp = conf.get('respuestas') or {}
    st.write(f"Editando: **{conf.get('palabra_clave')}**")
    val = st.text_area("Contenido (Texto o URL)", value=resp.get('contenido', ''))
    if st.button("Guardar Cambios"):
        get_supabase().table("respuestas").update({"contenido": val}).eq("id", resp['id']).execute()
        st.rerun()

@st.dialog("Editar Pago")
def editar_pago(c):
    nueva_ced = st.text_input("Cédula", value=c.get('cedula_esperada', ''))
    nuevo_tel = st.text_input("Teléfono", value=c.get('telefono_esperado', ''))
    if st.button("Guardar"):
        get_supabase().table("configuracion_pago").update({"cedula_esperada": nueva_ced, "telefono_esperado": nuevo_tel}).eq("id", c['id']).execute()
        st.rerun()

# --- INTERFAZ ---
st.title("🤖 Panel de Control")
if st.button("Cerrar sesión"): st.session_state["logueado"] = False; st.rerun()
t1, t2 = st.tabs(["⚙️ Reglas", "💳 Pagos"])

with t1:
    for c in obtener_configuraciones():
        with st.container(border=True):
            col1, col2 = st.columns([4, 1])
            col1.write(f"🔑 **{c.get('palabra_clave')}**")
            col1.code(c['respuestas']['contenido'] if c.get('respuestas') else "Sin contenido")
            if col2.button("✏️ Editar", key=f"e_{c['id']}"): editar_regla(c)

with t2:
    for p in obtener_configuracion_pagos():
        with st.container(border=True):
            st.write(f"Cédula: {p.get('cedula_esperada')} | Tel: {p.get('telefono_esperado')}")
            if p.get('activo'): st.success("✅ Activo")
            elif st.button("Activar", key=f"act_{p['id']}"): activar_contacto(p['id']); st.rerun()
            if st.button("✏️ Editar Pago", key=f"ep_{p['id']}"): editar_pago(p)
