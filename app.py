import streamlit as st
from auth_utils import get_supabase # Asegúrate de que tu auth_utils tenga esta función

def mostrar_dashboard():
    st.title("🤖 Panel de Configuración del Bot")
    supabase = get_supabase()

    # Pestañas para organizar
    tab1, tab2 = st.tabs(["Configurar Bot", "Verificar Pagos"])

    with tab1:
        st.subheader("Palabras clave y respuestas")
        # Obtener datos actuales
        config = supabase.table("config_bot").select("*").execute()
        
        if config.data:
            item = config.data[0] # Tomamos el primero para el ejemplo
            nueva_clave = st.text_input("Palabra clave", value=item['clave_busqueda'])
            nueva_respuesta = st.text_area("Respuesta del bot", value=item['respuesta_bot'])
            nuevo_num = st.text_input("Número de teléfono/Cuenta", value=item['numero_telefono'])
            nueva_id = st.text_input("Identificación a verificar", value=item['identificacion_pago'])

            if st.button("Guardar cambios"):
                supabase.table("config_bot").update({
                    "clave_busqueda": nueva_clave,
                    "respuesta_bot": nueva_respuesta,
                    "numero_telefono": nuevo_num,
                    "identificacion_pago": nueva_id
                }).eq("id", item['id']).execute()
                st.success("Configuración actualizada")

    with tab2:
        st.subheader("Verificación de Pagos")
        # Aquí crearías la lógica para verificar pagos con la IA
        st.info("Aquí podrás ver los pagos recibidos y verificar la identidad.")

    if st.button("Cerrar sesión"):
        st.session_state["logueado"] = False
        st.rerun()
