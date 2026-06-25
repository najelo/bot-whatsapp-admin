import streamlit as st
from auth_utils import verificar_login, get_supabase
from db_utils import obtener_configuraciones, guardar_configuracion, subir_archivo_al_storage, listar_archivos_storage, eliminar_regla
from pagos_utils import obtener_configuracion_pagos, guardar_contacto, activar_contacto, eliminar_contacto

st.set_page_config(page_title="Admin Bot", layout="wide")

# --- LOGIN ---
if "logueado" not in st.session_state: 
    st.session_state["logueado"] = False

if not st.session_state["logueado"]:
    st.title("🔐 Iniciar Sesión")
    user, pwd = st.text_input("Usuario"), st.text_input("Contraseña", type="password")
    if st.button("Entrar"):
        valido, msg = verificar_login(user, pwd)
        if valido: 
            st.session_state["logueado"] = True
            st.rerun()
        else: 
            st.error(msg)
    st.stop()

# --- DIÁLOGO EDICIÓN ---
@st.dialog("Editar Regla de Bot", width="large")
def abrir_editor(conf):
    resp_data = conf.get('respuestas') or {}
    contenido_actual = resp_data.get('contenido', '')
    tipo_actual = resp_data.get('tipo_contenido', 'texto')
    
    st.markdown(f"### ✏️ Editando Palabra: `{conf.get('palabra_clave')}`")
    nueva_palabra = st.text_input("Palabra clave para el bot", value=conf.get('palabra_clave', ''))
    
    st.markdown("---")
    st.write(f"#### 📂 Contenido Actual ({tipo_actual.upper()})")
    if contenido_actual.startswith("http"):
        if tipo_actual == "audio":
            st.audio(contenido_actual)
        else:
            st.markdown(f"[Ver archivo adjunto actual]({contenido_actual})")
    else:
        st.text_area("Texto actual", value=contenido_actual, disabled=True)
    st.markdown("---")
    
    nuevo_archivo = None
    if tipo_actual != "texto":
        # Formatos extendidos para soportar audios también en la edición
        nuevo_archivo = st.file_uploader("Subir archivo nuevo para reemplazar el anterior", type=["pdf", "png", "jpg", "jpeg", "mp4", "mp3", "wav", "ogg", "m4a"])
    else:
        nuevo_contenido_texto = st.text_area("Modificar el texto de respuesta", value=contenido_actual)

    col_save, col_del = st.columns([3, 1])
    with col_save:
        if st.button("💾 Guardar Cambios", use_container_width=True, type="primary"):
            try:
                if tipo_actual != "texto":
                    final_content = subir_archivo_al_storage(nuevo_archivo.getvalue(), nuevo_archivo.name) if nuevo_archivo else contenido_actual
                else:
                    final_content = nuevo_contenido_texto

                get_supabase().table("clientes").update({"palabra_clave": nueva_palabra.strip().lower()}).eq("id", conf['id']).execute()
                get_supabase().table("respuestas").update({"contenido": final_content}).eq("id", resp_data['id']).execute()
                st.toast("¡Cambios guardados con éxito!", icon="✅")
                st.rerun()
            except Exception as e: 
                st.error(f"Error al actualizar: {e}")
                
    with col_del:
        if st.button("🗑️ Borrar Regla", use_container_width=True):
            if eliminar_regla(conf['id'], resp_data['id']): 
                st.toast("Regla eliminada", icon="🗑️")
                st.rerun()

# --- PANTALLA PRINCIPAL ---
st.title("🤖 Panel de Control")
st.button("Cerrar sesión", on_click=lambda: st.session_state.update(logueado=False))

tab1, tab2 = st.tabs(["⚙️ Reglas", "💳 Pagos"])

# =========================================================
# TAB 1: GESTIÓN DE REGLAS (TEXTO, PDF, MULTIMEDIA Y AUDIO)
# =========================================================
with tab1:
    st.subheader("⚙️ Configuración de Respuestas Automáticas")
    
    with st.expander("➕ Crear Nueva Regla de Bot", expanded=False):
        palabras = st.text_input("Palabras clave (Sepáralas por comas si son varias. Ej: audio, nota, sonido)")
        
        # Selector dinámico expandido con la opción de Audio
        tipo_accion = st.selectbox(
            "¿Qué tipo de respuesta enviará el bot?",
            ["Texto Simple 📝", "Documento PDF 📄", "Multimedia (Imagen/Video) 🖼️", "Audio / Nota de Voz 🎵"]
        )
        
        contenido_final = None
        tipo_db = "texto"
        
        if tipo_accion == "Texto Simple 📝":
            contenido_final = st.text_area("Escribe el mensaje de texto que enviará el bot")
            tipo_db = "texto"
            
        elif tipo_accion == "Documento PDF 📄":
            archivo_pdf = st.file_uploader("Sube el archivo PDF corporativo", type=["pdf"])
            if archivo_pdf:
                with st.spinner("Subiendo PDF al Storage..."):
                    contenido_final = subir_archivo_al_storage(archivo_pdf.getvalue(), archivo_pdf.name)
            tipo_db = "documento"
            
        elif tipo_accion == "Multimedia (Imagen/Video) 🖼️":
            archivo_multi = st.file_uploader("Sube la imagen o video de respuesta", type=["png", "jpg", "jpeg", "mp4"])
            if archivo_multi:
                with st.spinner("Subiendo archivo multimedia al Storage..."):
                    contenido_final = subir_archivo_al_storage(archivo_multi.getvalue(), archivo_multi.name)
            tipo_db = "multimedia"
            
        elif tipo_accion == "Audio / Nota de Voz 🎵":
            archivo_audio = st.file_uploader("Sube el archivo de sonido", type=["mp3", "wav", "ogg", "m4a"])
            if archivo_audio:
                with st.spinner("Subiendo archivo de audio al Storage..."):
                    contenido_final = subir_archivo_al_storage(archivo_audio.getvalue(), archivo_audio.name)
            tipo_db = "audio"

        st.write(" ")
        if st.button("💾 Guardar Regla Automatizada", type="primary", use_container_width=True):
            if not palabras.strip():
                st.error("Por favor, ingresa al menos una palabra clave.")
            elif not contenido_final:
                st.error("Por favor, agrega el texto o sube un archivo válido para la respuesta.")
            else:
                exito = guardar_configuracion(palabras, contenido_final, tipo_db)
                if exito:
                    st.success("¡Regla configurada e indexada con éxito!")
                    st.rerun()
                else:
                    st.error("Hubo un error al guardar en la base de datos.")
    
    st.markdown("### 📋 Reglas Activas Actualmente")
    configuraciones = obtener_configuraciones()
    
    if not configuraciones:
        st.info("No hay reglas registradas todavía.")
    else:
        for conf in configuraciones:
            with st.container(border=True):
                c1, c2 = st.columns([4, 1])
                resp_data = conf.get('respuestas') or {}
                tipo_badge = resp_data.get('tipo_contenido', 'texto').upper()
                
                with c1:
                    st.markdown(f"🔑 Palabra clave: **`{conf.get('palabra_clave')}`** |  `[{tipo_badge}]`")
                    cont_preview = resp_data.get('contenido', '')
                    if cont_preview.startswith("http"):
                        if tipo_badge == "AUDIO":
                            # Agrega un reproductor directo en la lista de reglas para auditar el sonido
                            st.audio(cont_preview)
                        else:
                            st.caption(f"🔗 Archivo enlazado: [Ver elemento público]({cont_preview})")
                    else:
                        st.caption(f"💬 Texto: {cont_preview[:100]}...")
                        
                with c2:
                    st.write(" ")
                    if st.button("✏️ Editar / Borrar", key=f"edit_{conf['id']}", use_container_width=True):
                        abrir_editor(conf)

# =========================================================
# TAB 2: GESTIÓN DE PAGOS
# =========================================================
with tab2:
    st.subheader("💳 Gestión de Pasarelas y Contactos de Pago")
    
    subtab_registrar, subtab_administrar = st.tabs(["➕ Registrar Nuevo Contacto", "📂 Datos Guardados y Control"])
    
    with subtab_registrar:
        st.markdown("### 📝 Ingresar nuevos datos de validación")
        st.info("Al registrar un nuevo contacto, este iniciará en estado **Inactivo** de forma predeterminada.")
        
        with st.form("nuevo_pago_form", clear_on_submit=True):
            ced = st.text_input("Cédula / Identificación Fiscal")
            tel = st.text_input("Número de Teléfono (WhatsApp)")
            
            if st.form_submit_button("💾 Guardar y Registrar Pago", use_container_width=True, type="primary"):
                if ced.strip() and tel.strip():
                    guardar_contacto(ced, tel)
                    st.toast("Contacto registrado con éxito", icon="📥")
                    st.rerun()
                else:
                    st.error("Por favor, rellena ambos campos antes de enviar.")

    with subtab_administrar:
        st.markdown("### 🗃️ Registros en Base de Datos (`configuracion_pago`)")
        lista_pagos = obtener_configuracion_pagos()
        
        if not lista_pagos:
            st.info("No se encontraron registros de pago guardados en Supabase.")
        else:
            for c in lista_pagos:
                with st.container(border=True):
                    col_info, col_estado, col_acciones = st.columns([2, 1, 1])
                    
                    with col_info:
                        st.markdown(f"**🪪 Cédula:** `{c.get('cedula_esperada')}`")
                        st.markdown(f"**📞 Teléfono:** `{c.get('telefono_esperado')}`")
                    
                    with col_estado:
                        st.write("  \n")
                        if c.get('activo'):
                            st.success("🟢 ACTIVO")
                        else:
                            st.caption("⚪ Inactivo")
                    
                    with col_acciones:
                        st.write("  \n")
                        if not c.get('activo'):
                            col_b1, col_b2 = st.columns(2)
                            with col_b1:
                                if st.button("⚡ Activar", key=f"act_{c['id']}", use_container_width=True):
                                    activar_contacto(c['id'])
                                    st.toast("Contacto activo correctamente", icon="🔥")
                                    st.rerun()
                            with col_b2:
                                if st.button("🗑️", key=f"del_{c['id']}", use_container_width=True, type="secondary"):
                                    if eliminar_contacto(c['id']):
                                        st.toast("Registro eliminado", icon="🗑️")
                                        st.rerun()
                        else:
                            st.button("⚙️ En Uso", key=f"using_{c['id']}", disabled=True, use_container_width=True)
