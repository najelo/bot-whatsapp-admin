import streamlit as st
from auth_utils import get_supabase
from db_utils import guardar_respuesta_pdf, guardar_palabra_individual

st.title("🤖 Panel de Control: Recetarios")

# Asegúrate de haber creado el bucket 'recetarios' en Supabase Storage
archivo_pdf = st.file_uploader("Subir PDF de Recetario", type="pdf")
palabra_clave = st.text_input("Palabra clave para el bot (ej: recetario)")

if st.button("Subir y Guardar en Bot"):
    if archivo_pdf and palabra_clave:
        supabase = get_supabase()
        # Subir al Storage
        nombre_archivo = f"{palabra_clave.lower()}.pdf"
        try:
            supabase.storage.from_("recetarios").upload(nombre_archivo, archivo_pdf.getvalue(), {"content-type": "application/pdf"})
            # Obtener URL pública
            url_publica = supabase.storage.from_("recetarios").get_public_url(nombre_archivo)
            
            # Guardar URL en tabla 'respuestas'
            exito, r_id = guardar_respuesta_pdf(url_publica)
            if exito:
                guardar_palabra_individual(palabra_clave.lower(), r_id)
                st.success("¡Recetario subido con éxito!")
        except Exception as e:
            st.error(f"Error al subir: {e}")
