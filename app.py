import streamlit as st
from ui_components import mostrar_formulario_nueva_regla, mostrar_lista_reglas
from auth_manager import gestionar_login
from db_utils import obtener_configuraciones, guardar_configuracion, subir_archivo_al_storage

st.set_page_config(layout="wide")

# 1. Seguridad
gestionar_login()

# 2. Interfaz
st.title("🤖 Panel de Control")
mostrar_formulario_nueva_regla(subir_archivo_al_storage, guardar_configuracion)
mostrar_lista_reglas(obtener_configuraciones(), abrir_editor, eliminar_regla)
