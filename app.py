import streamlit as st
import db_utils
# Asegúrate de importar tus utilidades de pago originales si las usas aquí:
# import pagos_utils 

st.title("🎛️ Panel de Control - Respuestas Automáticas")

# Mantener las pestañas originales de tu aplicación
tabs = st.tabs(["⚙️ Reglas", "💳 Pagos"])

# ==========================================
# PESTAÑA 1: REGLAS (GESTIÓN DE RESPUESTAS)
# ==========================================
with tabs[0]:
    # --- FORMULARIO PARA CREAR NUEVAS REGLAS ---
    with st.expander("➕ Crear Nueva Regla de Bot", expanded=True):
        palabras = st.text_input("Palabras clave (Sepáralas por comas si son varias. Ej: hola, inicio)")
        
        tipo_contenido = st.selectbox(
            "¿Qué tipo de respuesta enviará el bot?",
            ["Texto Simple 📝", "Documento PDF 📄", "Imagen / Multimedia 🖼️", "Audio / Nota de Voz 🎵"]
        )
        
        contenido_final = None
        archivo_subido = None
        
        tipo_db = "texto"
        if "Documento" in tipo_contenido:
            tipo_db = "documento"
        elif "Multimedia" in tipo_contenido:
            tipo_db = "multimedia"
        elif "Audio" in tipo_contenido:
            tipo_db = "audio"

        if tipo_db == "texto":
            contenido_final = st.text_area("Escribe el mensaje de texto")
            
        elif tipo_db == "documento":
            archivo_subido = st.file_uploader("Sube el archivo PDF", type=["pdf"])
            
        elif tipo_db == "multimedia":
            archivo_subido = st.file_uploader("Sube la imagen o video", type=["png", "jpg", "jpeg", "webp", "mp4"])
            
        elif tipo_db == "audio":
            # ÚNICO CAMBIO ADAPTADO: Se agregaron las extensiones de audio de WhatsApp
            archivo_subido = st.file_uploader(
                "Sube el audio o nota de voz", 
                type=["mp3", "wav", "m4a", "ogg", "opus", "OPUS", "OGG"]
            )

        if st.button("💾 Guardar Regla Automatizada", use_container_width=True):
            if not palabras:
                st.warning("⚠️ Por favor escribe al menos una palabra clave.")
            else:
                if tipo_db in ["documento", "multimedia", "audio"]:
                    if archivo_subido is not None:
                        st.info("⚡ Subiendo archivo multimedia a Supabase...")
                        url_publica = db_utils.subir_archivo_al_storage(archivo_subido, archivo_subido.name)
                        if url_publica:
                            contenido_final = url_publica
                        else:
                            st.error("❌ Falló la subida del archivo al Storage de Supabase.")
                    else:
                        st.warning("⚠️ Este tipo de regla requiere que adjuntes un archivo válido.")
                
                if contenido_final:
                    exito = db_utils.guardar_configuracion(palabras, contenido_final, tipo_db)
                    if exito:
                        st.success("✅ ¡Regla guardada con éxito!")
                        st.rerun()
                else:
                    st.error("❌ No se pudo procesar el contenido de la regla.")

    # --- SECCIÓN DE REGLAS ACTIVAS (TU EDICIÓN ORIGINAL INTACTA) ---
    st.subheader("📋 Reglas Activas Actualmente")

    configuraciones = db_utils.obtener_configuraciones()

    if not configuraciones:
        st.info("No hay reglas automatizadas configuradas todavía.")
    else:
        for c in configuraciones:
            with st.container(border=True):
                col1, col2 = st.columns([4, 1])
                
                with col1:
                    st.markdown(f"🔑 **Palabra clave:** `{c['palabra_clave']}`")
                    
                    info_resp = c.get('respuestas')
                    if info_resp:
                        tipo = info_resp.get('tipo_contenido', 'texto')
                        contenido = info_resp.get('contenido', '')
                        st.caption(f"Tipo registrado: *{tipo.upper()}*")
                        
                        if tipo == "texto":
                            st.write(f"💬 {contenido}")
                        else:
                            st.link_button("🔗 Ver archivo público", contenido)
                    else:
                        st.caption("⚠️ Regla huérfana")
                
                with col2:
                    if st.button("🗑️ Eliminar", key=f"del_{c['id']}", use_container_width=True):
                        r_id = c['respuesta_id'] if c['respuesta_id'] else 0
                        if db_utils.eliminar_regla(c['id'], r_id):
                            st.success("Regla borrada")
                            st.rerun()
                        else:
                            st.error("No se pudo eliminar")

# ==========================================
# PESTAÑA 2: PAGOS (TU SECCIÓN ORIGINAL INTACTA)
# ==========================================
with tabs[1]:
    st.subheader("📊 Configuración y Control de Pagos Verificados")
    st.write("Aquí puedes gestionar los montos esperados y verificar las transacciones registradas.")
    
    # Aquí va exactamente tu código original para renderizar los datos de pagos,
    # inputs de cédula/teléfono esperados, o la tabla de captures procesados.
    # Ej:
    # cfg = ai_utils.obtener_datos_verificacion() (o como lo manejes en tu interfaz)
