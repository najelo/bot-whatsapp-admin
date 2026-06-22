import streamlit as st
from supabase import create_client

supabase = create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])

st.title("🤖 Panel de Administración del Bot")
tab1, tab2, tab3 = st.tabs(["💰 Pagos", "ℹ️ Info Negocio", "💬 FAQ Automáticas"])

with tab1: # Pagos
    ced = st.text_input("Cédula:")
    tel = st.text_input("Teléfono:")
    if st.button("Actualizar Pago"):
        supabase.table("configuracion_pago").update({"activo": False}).eq("activo", True).execute()
        supabase.table("configuracion_pago").insert({"cedula_esperada": ced, "telefono_esperado": tel, "activo": True}).execute()
        st.success("Pago configurado")

with tab2: # Info Negocio
    info = st.text_area("Información oficial (horario, ubicación):")
    if st.button("Actualizar Info"):
        supabase.table("informacion_negocio").delete().neq("id", 0).execute()
        supabase.table("informacion_negocio").insert({"contenido": info}).execute()
        st.success("Info actualizada")

with tab3: # FAQ (Respuestas Automáticas)
    st.subheader("Gestionar Reglas de Respuesta")
    with st.form("nueva_regla"):
        clave = st.text_input("Palabra clave:")
        respuesta = st.text_area("Respuesta asociada:")
        if st.form_submit_button("Guardar Regla"):
            supabase.table("respuestas_automaticas").insert({"palabra_clave": clave.lower(), "respuesta_texto": respuesta}).execute()
            st.success("Regla guardada")
    
    # Listar y borrar reglas
    reglas = supabase.table("respuestas_automaticas").select("*").execute().data
    for r in reglas:
        col1, col2 = st.columns([3, 1])
        col1.write(f"**{r['palabra_clave']}**: {r['respuesta_texto']}")
        if col2.button("🗑️", key=f"del_{r['id']}"):
            supabase.table("respuestas_automaticas").delete().eq("id", r['id']).execute()
            st.rerun()
