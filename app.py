import streamlit as st
from db_utils import obtener_configuraciones
from ui_reglas import render_crear_regla, render_lista_reglas
from ui_pagos import render_pagos_tab

st.set_page_config(page_title="Admin Bot", layout="wide")

# 1. Autenticación centralizada
# Aquí va tu bloque original de login tal y como lo tenías antes de mi cambio.

# 2. Interfaz principal (solo se muestra si el login pasó)
st.title("🤖 Panel de Control")
if st.button("Cerrar sesión"):
    st.session_state["logueado"] = False
    st.rerun()

tab1, tab2 = st.tabs(["⚙️ Reglas", "💳 Pagos"])

with tab1:
    render_crear_regla()
    render_lista_reglas(obtener_configuraciones())

with tab2:
    render_pagos_tab()
