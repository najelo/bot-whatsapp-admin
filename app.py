import streamlit as st
import uuid
from auth_utils import get_supabase

# IMPORTANTE: Definir pestañas ANTES de cualquier bloque 'with'
tab1, tab2 = st.tabs(["Configurar Bot", "Configurar Pagos"])

def guardar_configuracion(palabra, contenido):
    """Función local para evitar el error de 'no definido'."""
    supabase = get_supabase()
    res_resp = supabase.table("respuestas").insert({"contenido": contenido}).execute()
    nuevo_id = res_resp.data[0]['id']
    supabase.table("clientes").insert({"palabra_clave": palabra, "respuesta_id": nuevo_id}).execute()

with tab1:
    st.subheader("Nueva Regla (Texto o PDF)")
    tipo = st.radio("Tipo:", ["Texto", "PDF"], key="radio_tipo")
    
    with st.form("nueva_config", clear_on_submit=True):
        c = st.text_input("Palabra clave")
        if tipo == "Texto":
            r = st.text_area("Respuesta")
            if st.form_submit_button("Guardar"):
                guardar_configuracion(c, r); st.rerun()
        else:
            archivo = st.file_uploader("Sube PDF", type="pdf")
            if st.form_submit_button("Subir"):
                supabase = get_supabase()
                # Nombre único con UUID para que no se borren entre sí
                nombre = f"{c.replace(' ', '_')}_{str(uuid.uuid4())[:8]}.pdf"
                supabase.storage.from_("recetarios-helado").upload(nombre, archivo.getvalue())
                url = supabase.storage.from_("recetarios-helado").get_public_url(nombre)
                guardar_configuracion(c, url); st.rerun()

with tab2:
    st.subheader("Configurar Pagos")
    # Aquí iría tu lógica de pagos que mencionaste que también se vio afectada
