import streamlit as st
from db_utils import guardar_configuracion, subir_archivo_al_storage, eliminar_regla, actualizar_configuracion

@st.dialog("Editar Regla", width="large")
def abrir_editor(conf):
    resp = conf.get('respuestas') or {}
    st.write(f"Editando: **{conf.get('palabra_clave')}**")
    tipo = st.radio("Tipo", ["text", "document"], index=0 if resp.get('tipo_contenido') == 'text' else 1)
    cont = st.text_area("Contenido", value=resp.get('contenido', ''))
    
    if st.button("Guardar Cambios"):
        if actualizar_configuracion(resp['id'], cont, tipo):
            st.success("Guardado"); st.rerun()

def render_reglas_tab(configuraciones):
    with st.expander("➕ Nueva Regla"):
        palabras = st.text_input("Palabras clave")
        archivo = st.file_uploader("Subir PDF")
        res_texto = st.text_area("O texto")
        if st.button("Guardar"):
            cont = subir_archivo_al_storage(archivo.getvalue(), archivo.name) if archivo else res_texto
            guardar_configuracion(palabras, cont, "document" if archivo else "text")
            st.rerun()
            
    for conf in configuraciones:
        with st.container(border=True):
            c1, c2 = st.columns([4, 1])
            c1.write(f"🔑 **{conf['palabra_clave']}**")
            if c2.button("✏️ Editar", key=f"edit_{conf['id']}"): abrir_editor(conf)
