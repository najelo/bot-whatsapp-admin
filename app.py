import streamlit as st
from supabase import create_client

# Configuración
supabase = create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])

st.set_page_config(page_title="Admin Bot WhatsApp", layout="wide")
st.title("🤖 Panel de Administración del Bot")

# --- PESTAÑA 1: GESTIÓN DE PAGOS ---
tab1, tab2 = st.tabs(["Verificación de Pagos", "Respuestas Automáticas (FAQ)"])

with tab1:
    st.subheader("Configurar Pago Esperado")
    with st.form("form_pago"):
        nueva_cedula = st.text_input("Cédula/RIF esperado:")
        nuevo_telefono = st.text_input("Teléfono esperado (ej: 04121234567):")
        
        if st.form_submit_button("Actualizar Pago"):
            try:
                # Desactivar anteriores
                supabase.table("configuracion_pago").update({"activo": False}).eq("activo", True).execute()
                # Insertar nuevo
                supabase.table("configuracion_pago").insert({
                    "cedula_esperada": nueva_cedula,
                    "telefono_esperado": nuevo_telefono,
                    "activo": True
                }).execute()
                st.success("✅ Configuración de pago actualizada correctamente.")
            except Exception as e:
                st.error(f"Error: {e}")

# --- PESTAÑA 2: GESTIÓN DE PALABRAS CLAVE ---
with tab2:
    st.subheader("Gestionar Reglas de Respuesta")
    
    # Formulario para nueva regla
    with st.form("nueva_regla"):
        col1, col2 = st.columns(2)
        clave = col1.text_input("Palabra clave (ej: 'horario'):")
        texto = col2.text_area("Respuesta asociada:")
        
        if st.form_submit_button("Guardar nueva regla"):
            if clave and texto:
                supabase.table("respuestas_automaticas").insert({
                    "palabra_clave": clave.lower(),
                    "respuesta_texto": texto
                }).execute()
                st.success(f"Regla '{clave}' guardada.")
    
    # Mostrar reglas actuales
    st.write("---")
    st.subheader("Reglas existentes")
    try:
        reglas = supabase.table("respuestas_automaticas").select("*").execute().data
        for r in reglas:
            col_k, col_r, col_d = st.columns([1, 3, 1])
            col_k.text(r['palabra_clave'])
            col_r.text(r['respuesta_texto'])
            if col_d.button("🗑️", key=f"del_{r['id']}"):
                supabase.table("respuestas_automaticas").delete().eq("id", r['id']).execute()
                st.rerun()
    except Exception as e:
        st.write("No hay reglas guardadas aún.")

# --- SIDEBAR: HISTORIAL ---
if st.sidebar.button("Ver último historial de mensajes"):
    historial = supabase.table("mensajes").select("*").order("created_at", desc=True).limit(5).execute()
    st.sidebar.write(historial.data)
