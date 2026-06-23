import streamlit as st
import uuid
from auth_utils import get_supabase

# Definición de pestañas (debe ir antes de usar tab1)
tab1, tab2 = st.tabs(["Configurar Bot", "Configurar Pagos"])

with tab1:
    st.subheader("Nueva Regla (Texto o PDF)")
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
                    # GENERAR NOMBRE ÚNICO CON UUID
                    nombre_base = c.lower().replace(' ', '_')
                    identificador = str(uuid.uuid4())[:8]
                    nombre = f"{nombre_base}_{identificador}.pdf"
                    
                    supabase.storage.from_("recetarios-helado").upload(
                        path=nombre,
                        file=archivo.getvalue(),
                        file_options={"content-type": "application/pdf"}
                    )
                    
                    url = supabase.storage.from_("recetarios-helado").get_public_url(nombre)
                    guardar_configuracion(c, url)
                    st.success("PDF subido correctamente"); st.rerun()
                except Exception as e:
                    st.error(f"Error al subir: {e}")
