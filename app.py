import streamlit as st
from auth_utils import get_supabase
from db_utils import guardar_respuesta_pdf, guardar_palabra_individual

st.title("🤖 Panel de Control: Recetarios")

archivo_pdf = st.file_uploader("Subir PDF del Recetario", type="pdf")
palabra_clave = st.text_input("Palabra clave para el bot (ej: recetario)")

if st.button("Subir y Guardar en Bot"):
    if archivo_pdf and palabra_clave:
        try:
            supabase = get_supabase()
            nombre_archivo = f"{palabra_clave.lower()}.pdf"
            
            # 1. Subir el archivo físico al Storage
            supabase.storage.from_("recetarios").upload(
                nombre_archivo, 
                archivo_pdf.getvalue(), 
                {"content-type": "application/pdf"}
            )
            
            # 2. Obtener la URL pública del archivo
            url = supabase.storage.from_("recetarios").get_public_url(nombre_archivo)
            
            # 3. Guardar solo el link en la tabla 'respuestas'
            exito, r_id = guardar_respuesta_pdf(url) 
            if exito:
                guardar_palabra_individual(palabra_clave.lower(), r_id)
                st.success("¡Recetario subido y vinculado correctamente!")
            else:
                st.error("Error al guardar en base de datos: " + str(r_id))
                
        except Exception as e:
            st.error(f"Error al subir: {e}")
