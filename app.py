import streamlit as st
from auth_utils import get_supabase
from db_utils import guardar_respuesta_pdf, guardar_palabra_individual

st.title("Panel de Control: Recetarios")

archivo_pdf = st.file_uploader("Selecciona el PDF", type="pdf")
palabra = st.text_input("Palabra clave (ej: recetario)")

if st.button("Guardar"):
    if archivo_pdf and palabra:
        supabase = get_supabase()
        nombre = f"{palabra.lower()}.pdf"
        
        # 1. Subir al Storage (se guarda el archivo físico)
        supabase.storage.from_("recetarios").upload(
            nombre, archivo_pdf.getvalue(), {"content-type": "application/pdf"}
        )
        
        # 2. Obtener el link público
        url = supabase.storage.from_("recetarios").get_public_url(nombre)
        
        # 3. Guardar solo el link en tu tabla existente
        exito, r_id = guardar_respuesta_pdf(url) 
        if exito:
            guardar_palabra_individual(palabra.lower(), r_id)
            st.success("Recetario guardado con éxito")
