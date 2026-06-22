import streamlit as st
from supabase import create_client

supabase = create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])

st.title("Admin Bot WhatsApp")
tab1, tab2 = st.tabs(["Pagos", "Info Negocio"])

with tab1: # Gestión de Pagos
    ced = st.text_input("Cédula:")
    tel = st.text_input("Teléfono:")
    if st.button("Actualizar Pago"):
        supabase.table("configuracion_pago").update({"activo": False}).eq("activo", True).execute()
        supabase.table("configuracion_pago").insert({"cedula_esperada": ced, "telefono_esperado": tel, "activo": True}).execute()
        st.success("Pago actualizado")

with tab2: # Gestión de Información
    info = st.text_area("Información oficial (horario, ubicación):")
    if st.button("Actualizar Info"):
        supabase.table("informacion_negocio").delete().neq("id", 0).execute()
        supabase.table("informacion_negocio").insert({"contenido": info}).execute()
        st.success("Info actualizada")
