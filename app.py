import streamlit as st
from auth_utils import verificar_login, get_supabase
from db_utils import obtener_configuraciones, guardar_configuracion, subir_archivo_al_storage, eliminar_regla

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

# --- DIÁLOGO EDICIÓN (Simplificado) ---
@st.dialog("Editar Regla", width="large")
def abrir_editor(conf):
    st.write(f"Editando palabra: {conf.get('palabra_clave')}")
    # Aquí iría tu lógica de edición...

# --- PANTALLA PRINCIPAL ---
st.title("🤖 Panel de Control")
st.button("Cerrar sesión", on_click=lambda: st.session_state.update(logueado=False))

with st.expander("➕ Nueva Regla"):
    palabras = st.text_input("Palabras clave (separadas por coma)")
    archivo = st.file_uploader("Subir PDF", type=['pdf'])
    res_texto = st.text_area("O escribe una respuesta de texto")
    
    if st.button("Guardar"):
        if archivo:
            # Lógica para archivos
            with st.spinner("Subiendo archivo..."):
                cont = subir_archivo_al_storage(archivo.getvalue(), archivo.name)
                if cont:
                    # Guardamos especificando que es tipo "document"
                    if guardar_configuracion(palabras, cont, tipo="document"):
                        st.success("Archivo guardado correctamente")
                        st.rerun()
        elif res_texto:
            # Lógica para texto
            if guardar_configuracion(palabras, res_texto, tipo="text"):
                st.success("Texto guardado correctamente")
                st.rerun()
        else:
            st.warning("Debes subir un archivo o escribir un texto.")

# --- LISTADO DE REGLAS ---
st.subheader("Reglas configuradas")
for conf in obtener_configuraciones():
    with st.container(border=True):
        c1, c2 = st.columns([4, 1])
        c1.write(f"🔑 **{conf.get('palabra_clave')}**")
        if c2.button("🗑️ Borrar", key=f"del_{conf['id']}"):
            # Pasamos tanto el id de la palabra como el id de la respuesta
            resp_id = conf.get('respuestas', {}).get('id')
            if eliminar_regla(conf['id'], resp_id):
                st.rerun()
