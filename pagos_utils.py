import streamlit as st
from auth_utils import verificar_login, get_supabase
from db_utils import obtener_configuraciones, guardar_configuracion, subir_archivo_al_storage, listar_archivos_storage, eliminar_regla
from pagos_utils import obtener_configuracion_pagos, guardar_contacto, activar_contacto, eliminar_contacto

st.set_page_config(page_title="Admin Bot", layout="wide")

# --- LOGIN ---
if "logueado" not in st.session_state: st.session_state["logueado"] = False
if not st.session_state["logueado"]:
    st.title("🔐 Iniciar Sesión")
    user, pwd = st.text_input("Usuario"), st.text_input("Contraseña", type="password")
    if st.button("Entrar"):
        valido, msg = verificar_login(user, pwd)
        if valido: st.session_state["logueado"] = True; st.rerun()
        else: st.error(msg)
    st.stop()

# --- DIÁLOGO EDICIÓN ---
@st.dialog("Editar Regla de Bot", width="large")
def abrir_editor(conf):
    resp_data = conf.get('respuestas') or {}
    contenido_actual = resp_data.get('contenido', '')
    
    st.markdown(f"### ✏️ Editando: `{conf.get('palabra_clave')}`")
    nueva_palabra = st.text_input("Palabra clave para el bot", value=conf.get('palabra_clave', ''))
    
    st.markdown("---")
    st.write("#### 📂 Archivo actual")
    st.markdown(f"[{contenido_actual}]({contenido_actual})")
    st.markdown("---")
    
    col_select, col_upload = st.columns(2)
    with col_select:
        archivos = listar_archivos_storage()
        seleccion = st.selectbox("Cambiar por:", ["-- Mantener actual --"] + archivos)
    with col_upload:
        nuevo_archivo = st.file_uploader("Subir archivo NUEVO", type=["pdf"])
    
    col_save, col_del = st.columns([3, 1])
    with col_save:
        if st.button("💾 Guardar Cambios", use_container_width=True, type="primary"):
            try:
                final_content = subir_archivo_al_storage(nuevo_archivo.getvalue(), nuevo_archivo.name) if nuevo_archivo else (get_supabase().storage.from_("recetarios-helado").get_public_url(seleccion) if seleccion != "-- Mantener actual --" else contenido_actual)
                get_supabase().table("clientes").update({"palabra_clave": nueva_palabra}).eq("id", conf['id']).execute()
                get_supabase().table("respuestas").update({"contenido": final_content}).eq("id", resp_data['id']).execute()
                st.toast("Guardado", icon="✅"); st.rerun()
            except Exception as e: st.error(f"Error: {e}")
    with col_del:
        if st.button("🗑️ Borrar", use_container_width=True):
            if eliminar_regla(conf['id'], resp_data['id']): st.rerun()

# --- PANTALLA ---
st.title("🤖 Panel de Control"); st.button("Cerrar sesión", on_click=lambda: st.session_state.update(logueado=False))
tab1, tab2 = st.tabs(["⚙️ Reglas", "💳 Pagos"])

# --- TAB 1: REGLAS ---
with tab1:
    with st.expander("➕ Nueva Regla"):
        palabras = st.text_input("Palabra clave")
        archivo = st.file_uploader("Subir archivo")
        res_texto = st.text_area("Respuesta texto")
        if st.button("Guardar"):
            cont = subir_archivo_al_storage(archivo.getvalue(), archivo.name) if archivo else res_texto
            if cont: guardar_configuracion(palabras, cont); st.rerun()
    
    for conf in obtener_configuraciones():
        with st.container(border=True):
            c1, c2 = st.columns([4, 1])
            c1.write(f"🔑 **{conf.get('palabra_clave')}**")
            if c2.button("✏️ Editar", key=f"edit_{conf['id']}"): abrir_editor(conf)

# --- TAB 2: PAGOS (DIVIDIDO Y MEJORADO) ---
with tab2:
    st.subheader("💳 Gestión de Pasarelas y Contactos de Pago")
    
    # Creamos las dos sub-pestañas internas para separar el flujo
    subtab_registrar, subtab_administrar = st.tabs(["➕ Registrar Nuevo Contacto", "📂 Datos Guardados y Control"])
    
    # 1. Sub-pestaña para Registrar
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

    # 2. Sub-pestaña para Visualizar y Eliminar / Activar
    with subtab_administrar:
        st.markdown("### 🗃️ Registros en Base de Datos (`configuracion_pago`)")
        
        lista_pagos = obtener_configuracion_pagos()
        
        if not lista_pagos:
            st.info("No se encontraron registros de pago guardados en Supabase.")
        else:
            for c in lista_pagos:
                with st.container(border=True):
                    # Dividimos en 3 columnas limpias
                    col_info, col_estado, col_acciones = st.columns([2, 1, 1])
                    
                    with col_info:
                        st.markdown(f"**🪪 Cédula:** `{c.get('cedula_esperada')}`")
                        st.markdown(f"**📞 Teléfono:** `{c.get('telefono_esperado')}`")
                    
                    with col_estado:
                        st.write("  \n")  # Ajuste de espacio vertical para centrar
                        if c.get('activo'):
                            st.success("🟢 ACTIVO")
                        else:
                            st.caption("⚪ Inactivo")
                    
                    with col_acciones:
                        st.write("  \n")  # Ajuste de espacio vertical para centrar
                        
                        # Si está inactivo, habilitamos Activar y Eliminar
                        if not c.get('activo'):
                            col_b1, col_b2 = st.columns(2)
                            with col_b1:
                                if st.button("⚡ Activar", key=f"act_{c['id']}", use_container_width=True):
                                    activar_contacto(c['id'])
                                    st.toast("Contacto activado correctamente", icon="🔥")
                                    st.rerun()
                            with col_b2:
                                if st.button("🗑️", key=f"del_{c['id']}", use_container_width=True, type="secondary", help="Eliminar permanentemente"):
                                    if eliminar_contacto(c['id']):
                                        st.toast("Registro eliminado", icon="🗑️")
                                        st.rerun()
                        else:
                            # Si ya está activo, deshabilitamos el botón de uso para evitar accidentes
                            st.button("⚙️ En Uso", key=f"using_{c['id']}", disabled=True, use_container_width=True)
