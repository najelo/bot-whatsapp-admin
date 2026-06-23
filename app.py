import streamlit as st
import uuid  # <--- IMPORTANTE: Importa esto al inicio de tu archivo
from auth_utils import get_supabase

# ... (resto de tu código)

with tab1:
    st.subheader("Nueva Regla (Texto o PDF)")
    
    # 1. Selector reactivo fuera del formulario
    tipo = st.radio("Tipo:", ["Texto", "PDF"], key="radio_tipo")
    
    with st.form("nueva_config", clear_on_submit=True):
        c = st.text_input("Palabra clave", key="input_palabra")
        
        if tipo == "Texto":
            r = st.text_area("Respuesta", key="input_resp")
            submit = st.form_submit_button("Guardar")
        else:
            archivo = st.file_uploader("Sube el PDF", type="pdf", key="uploader_pdf")
            submit = st.form_submit_button("Subir y Vincular")
        
        if submit:
            if tipo == "Texto":
                guardar_configuracion(c, r)
                st.success("Guardado"); st.rerun()
            elif tipo == "PDF" and archivo:
                try:
                    supabase = get_supabase()
                    # 2. GENERAR NOMBRE ÚNICO: Usamos uuid para que nunca se repita
                    # El nombre será: palabra_clave_randomID.pdf
                    nombre_base = c.lower().replace(' ', '_')
                    identificador = str(uuid.uuid4())[:8]
                    nombre = f"{nombre_base}_{identificador}.pdf"
                    
                    # 3. Subida a Supabase
                    supabase.storage.from_("recetarios-helado").upload(
                        path=nombre,
                        file=archivo.getvalue(),
                        file_options={"content-type": "application/pdf"}
                    )
                    
                    # 4. Obtener URL y guardar en BD
                    url = supabase.storage.from_("recetarios-helado").get_public_url(nombre)
                    guardar_configuracion(c, url)
                    
                    st.success(f"Archivo guardado como: {nombre}")
                    st.rerun()
                except Exception as e:
                    st.error(f"Error técnico: {e}")
