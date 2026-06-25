import streamlit as st

def mostrar_formulario_nueva_regla(subir_archivo_func, guardar_config_func):
    with st.expander("➕ Nueva Regla"):
        palabras = st.text_input("Palabras clave (separadas por coma)")
        archivo = st.file_uploader("Subir archivo")
        res_texto = st.text_area("O escribe respuesta de texto")
        
        if st.button("Guardar"):
            if archivo:
                cont = subir_archivo_func(archivo.getvalue(), archivo.name)
                if cont: guardar_config_func(palabras, cont, "document")
            elif res_texto:
                guardar_config_func(palabras, res_texto, "text")
            st.rerun()

def mostrar_lista_reglas(configuraciones, editar_func, borrar_func):
    st.subheader("Reglas configuradas")
    for conf in configuraciones:
        with st.container(border=True):
            col1, col2 = st.columns([4, 1])
            col1.write(f"🔑 **{conf['palabra_clave']}**")
            if col2.button("✏️ Editar", key=f"edit_{conf['id']}"):
                editar_func(conf)
