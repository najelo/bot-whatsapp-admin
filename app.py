import streamlit as st
from ui_components import mostrar_formulario_nueva_regla, mostrar_lista_reglas
from auth_manager import gestionar_login
from db_utils import obtener_configuraciones, guardar_configuracion, subir_archivo_al_storage, eliminar_regla, actualizar_configuracion

# --- AQUÍ DEBES DEFINIR O IMPORTAR abrir_editor ---
@st.dialog("Editar Regla")
def abrir_editor(conf):
    # Lógica de edición que definimos antes
    resp = conf.get('respuestas') or {}
    nuevo_tipo = st.radio("Tipo", ["text", "document"], index=0 if resp.get('tipo_contenido') == 'text' else 1)
    
    if nuevo_tipo == "text":
        nuevo_cont = st.text_area("Contenido", value=resp.get('contenido', ''))
    else:
        nuevo_cont = st.text_input("URL del archivo", value=resp.get('contenido', ''))
    
    if st.button("Guardar Cambios"):
        if actualizar_configuracion(resp['id'], nuevo_cont, nuevo_tipo):
            st.success("Guardado"); st.rerun()

# --- FLUJO PRINCIPAL ---
st.set_page_config(layout="wide")
gestionar_login()

st.title("🤖 Panel de Control")
mostrar_formulario_nueva_regla(subir_archivo_al_storage, guardar_configuracion)

# Ahora abrir_editor ya está definida y no dará error
mostrar_lista_reglas(obtener_configuraciones(), abrir_editor, eliminar_regla)
