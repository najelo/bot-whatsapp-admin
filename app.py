import streamlit as st
import uuid
from auth_utils import get_supabase

# 1. Definición de la función de base de datos (aquí mismo para evitar NameError)
def guardar_configuracion(palabra, contenido):
    supabase = get_supabase()
    # Insertar respuesta
    res_resp = supabase.table("respuestas").insert({"contenido": contenido}).execute()
    nuevo_id = res_resp.data[0]['id']
    # Vincular palabra clave
    supabase.table("clientes").insert({"palabra_clave": palabra, "respuesta_id": nuevo_id}).execute()

# 2. Definición de pestañas (debe ir antes de usar tab1)
st.title("🤖 Panel de Control")
tab1, tab2 = st.tabs(["Configurar Bot", "Configurar Pagos"])

# 3. Interfaz de la Pestaña 1
with tab1:
    st.subheader("Nueva Regla (Texto o PDF)")
    tipo = st.radio("Tipo:", ["Texto", "PDF"], key="radio_tipo")
    
    with st.form("nueva_config", clear_on_submit=True):
        c = st.text_input("Palabra clave")
        if tipo == "Texto":
            r = st.text_area("Respuesta")
            if st.form_submit_button("Guardar"):
                guardar_configuracion(c, r)
                st.success("Guardado correctamente")
                st.rerun()
        else:
            archivo = st.file_uploader("Sube PDF", type="pdf")
            if st.form_submit_button("Subir"):
                try:
                    supabase = get_supabase()
                    # Usamos UUID para que cada PDF tenga un nombre único y no se sobrescriban
                    nombre = f"{c.replace(' ', '_')}_{str(uuid.uuid4())[:8]}.pdf"
                    supabase.storage.from_("recetarios-helado").upload(nombre, archivo.getvalue())
                    url = supabase.storage.from_("recetarios-helado").get_public_url(nombre)
                    guardar_configuracion(c, url)
                    st.success(f"Subido: {nombre}")
                    st.rerun()
                except Exception as e:
                    st.error(f"Error al subir: {e}")

# 4. Interfaz de la Pestaña 2
with tab2:
    st.subheader("Configurar Pagos")
    st.write("Gestiona tus datos de pago aquí.")
