import streamlit as st
from db_utils import guardar_configuracion, subir_archivo_al_storage, actualizar_configuracion, eliminar_regla

@st.dialog("Editar Regla", width="large")
def abrir_editor(conf):
    """Diálogo para editar una regla existente."""
    resp = conf.get('respuestas') or {}
    st.write(f"Editando palabra clave: **{conf.get('palabra_clave')}**")
    
    # Selector de tipo: Texto o Archivo
    tipo = st.radio(
        "Tipo de contenido", 
        ["text", "document"], 
        index=0 if resp.get('tipo_contenido') == 'text' else 1
    )
    
    # Campo de contenido según el tipo
    if tipo == "text":
        nuevo_cont = st.text_area("Contenido", value=resp.get('contenido', ''))
    else:
        st.info(f"Archivo actual: {resp.get('contenido')}")
        nuevo_cont = st.text_input("URL del archivo", value=resp.get('contenido', ''))
    
    if st.button("Guardar Cambios"):
        if actualizar_configuracion(resp.get('id'), nuevo_cont, tipo):
            st.success("¡Regla actualizada exitosamente!")
            st.rerun()

def render_crear_regla():
    """Formulario para crear nuevas reglas."""
    with st.expander("➕ Nueva Regla"):
        palabras = st.text_input("Palabras clave (separadas por coma)")
        archivo = st.file_uploader("Subir PDF", type=['pdf', 'jpg', 'png'])
        res_texto = st.text_area("O escribe una respuesta de texto")
        
        if st.button("Guardar Regla"):
            if archivo:
                with st.spinner("Subiendo archivo..."):
                    cont = subir_archivo_al_storage(archivo.getvalue(), archivo.name)
                    if cont:
                        guardar_configuracion(palabras, cont, "document")
                        st.success("Archivo guardado correctamente")
            elif res_texto:
                guardar_configuracion(palabras, res_texto, "text")
                st.success("Texto guardado correctamente")
            else:
                st.warning("Por favor, ingresa texto o sube un archivo.")
            st.rerun()

def render_lista_reglas(configuraciones):
    """Lista las reglas existentes con opciones de edición y borrado."""
    st.subheader("Reglas configuradas")
    if not configuraciones:
        st.info("No hay reglas configuradas aún.")
        return

    for conf in configuraciones:
        with st.container(border=True):
            col1, col2 = st.columns([3, 1])
            col1.write(f"🔑 **{conf.get('palabra_clave')}**")
            resp = conf.get('respuestas', {})
            col1.caption(f"Tipo: {resp.get('tipo_contenido', 'n/a')} | Contenido: {resp.get('contenido', '')[:30]}...")
            
            c_edit, c_del = col2.columns(2)
            if c_edit.button("✏️", key=f"edit_{conf['id']}", help="Editar"):
                abrir_editor(conf)
            if c_del.button("🗑️", key=f"del_{conf['id']}", help="Borrar"):
                eliminar_regla(conf['id'], resp.get('id'))
                st.rerun()
