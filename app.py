import streamlit as st
import uuid
from auth_utils import get_supabase
from db_utils import guardar_configuracion # Importamos la función que creamos

st.title("🤖 Panel de Control del Bot")

# 1. Definición de pestañas (debe estar antes de usar tab1 o tab2)
tab1, tab2 = st.tabs(["Configurar Bot", "Configurar Pagos"])

with tab1:
    st.subheader("Nueva Regla (Texto o PDF)")
    
    # Radio button fuera del form para asegurar reactividad
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
                st.success("Regla de texto guardada")
                st.rerun()
            elif tipo == "PDF" and archivo:
                try:
                    supabase = get_supabase()
                    
                    # Generar nombre único usando uuid para evitar sobrescribir PDFs
                    nombre_base = c.lower().replace(' ', '_')
                    identificador = str(uuid.uuid4())[:8]
                    nombre = f"{nombre_base}_{identificador}.pdf"
                    
                    # Subir al bucket
                    supabase.storage.from_("recetarios-helado").upload(
                        path=nombre,
                        file=archivo.getvalue(),
                        file_options={"content-type": "application/pdf"}
                    )
                    
                    # Obtener URL y guardar en BD
                    url = supabase.storage.from_("recetarios-helado").get_public_url(nombre)
                    guardar_configuracion(c, url)
                    
                    st.success(f"PDF subido y vinculado: {nombre}")
                    st.rerun()
                except Exception as e:
                    st.error(f"Error técnico: {e}")

with tab2:
    st.subheader("Configuración de Pagos")
    st.write("Gestiona aquí los datos de verificación de pago.")
    # (Agrega aquí tu lógica de la pestaña 2)
