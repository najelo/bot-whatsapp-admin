import streamlit as st
from supabase import create_client

# Configuración
supabase = create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])

st.title("Admin de Bot: Verificación de Pagos")

with st.form("configuracion_pago", clear_on_submit=False):
    st.subheader("Datos esperados para el próximo pago")
    nueva_cedula = st.text_input("Cédula/RIF esperado:")
    nuevo_telefono = st.text_input("Teléfono esperado (Ej: 04121234567):")
    
    if st.form_submit_button("Actualizar configuración"):
        # Desactivamos los anteriores y creamos el nuevo
        try:
            # 1. Ponemos todo en activo = false
            supabase.table("configuracion_pago").update({"activo": False}).eq("activo", True).execute()
            
            # 2. Insertamos el nuevo
            supabase.table("configuracion_pago").insert({
                "cedula_esperada": nueva_cedula,
                "telefono_esperado": nuevo_telefono,
                "activo": True
            }).execute()
            
            st.success("Configuración actualizada. El bot ya está esperando estos datos.")
        except Exception as e:
            st.error(f"Error al actualizar: {e}")
