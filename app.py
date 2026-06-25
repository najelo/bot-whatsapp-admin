import streamlit as st
from auth_utils import verificar_login
from db_utils import obtener_configuraciones
from ui_reglas import render_reglas_tab
from ui_pagos import render_pagos_tab

st.set_page_config(layout="wide")

# Login (Simplificado)
if "logueado" not in st.session_state: st.session_state["logueado"] = False
if not st.session_state["logueado"]:
    # ... tu lógica de login aquí ...
    st.stop()

st.title("🤖 Panel de Control")
tab1, tab2 = st.tabs(["⚙️ Reglas", "💳 Pagos"])

with tab1:
    render_reglas_tab(obtener_configuraciones())

with tab2:
    render_pagos_tab()
