import streamlit as st
from auth_utils import verificar_login
from db_utils import obtener_configuraciones, guardar_configuracion, subir_archivo_al_storage, eliminar_regla, actualizar_configuracion

st.set_page_config(layout="wide")

# Login simplificado... (usa tu lógica actual)

@st.dialog("Editar Regla")
def abrir_editor(conf):
    resp = conf.get('respuestas') or {}
    nuevo_tipo = st.radio("Tipo", ["text", "document"], index=0 if resp.get('tipo_contenido') == 'text' else 1)
    
    if nuevo_tipo == "text":
        nuevo_cont = st.text_area("Contenido", value=resp.get('contenido', ''))
    else:
        nuevo_cont = st.text_input("URL del archivo", value=resp.get('contenido', ''))
    
    if st.button("Guardar Cambios"):
        if actualizar_configuracion(resp['id'], nuevo_cont, nuevo_tipo):
            st.success("Guardado"); st.rerun()

st.title("🤖 Panel de Control")

with st.expander("➕ Nueva Regla"):
    palabras = st.text_input("Palabras clave")
    archivo = st.file_uploader("Subir PDF")
    res_texto = st.text_area("O texto")
    if st.button("Guardar"):
        if archivo:
            cont = subir_archivo_al_storage(archivo.getvalue(), archivo.name)
            guardar_configuracion(palabras, cont, "document")
        elif res_texto:
            guardar_configuracion(palabras, res_texto, "text")
        st.rerun()

for conf in obtener_configuraciones():
    with st.container(border=True):
        col1, col2 = st.columns([4, 1])
        col1.write(f"🔑 **{conf['palabra_clave']}**")
        if col2.button("✏️ Editar", key=f"edit_{conf['id']}"): abrir_editor(conf)
