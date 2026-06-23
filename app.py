import streamlit as st
from auth_utils import verificar_login, get_supabase
from db_utils import (
    obtener_configuraciones, guardar_configuracion, 
    eliminar_configuracion, guardar_palabra_individual,
    obtener_todas_las_respuestas
)
from pagos_utils import obtener_configuracion_pagos, guardar_contacto, activar_contacto

st.set_page_config(page_title="Admin Bot", page_icon="🤖")

if "logueado" not in st.session_state: st.session_state["logueado"] = False
import streamlit as st
from auth_utils import verificar_login, get_supabase
from db_utils import (
    obtener_configuraciones, guardar_configuracion, 
    eliminar_configuracion, guardar_palabra_individual,
    obtener_todas_las_respuestas
)
from pagos_utils import obtener_configuracion_pagos, guardar_contacto, activar_contacto

# --- LÓGICA DE PDF PARA TODA LA LISTA ---
def obtener_todos_los_pdfs():
    # Asumiendo que subes los PDFs con un prefijo o los guardas en una tabla específica
    # Si quieres que se envíen TODOS los PDF al detectar una palabra:
    supabase = get_supabase()
    # Aquí consultarías tu tabla donde guardas las URLs de los PDFs
    return supabase.table("recetarios").select("url").execute().data

st.set_page_config(page_title="Admin Bot", page_icon="🤖")

if "logueado" not in st.session_state: st.session_state["logueado"] = False

if not st.session_state["logueado"]:
    st.title("🔐 Acceso al Sistema")
    user = st.text_input("Usuario")
    pwd = st.text_input("Contraseña", type="password")
    if st.button("Ingresar"):
        exito, msg = verificar_login(user, pwd)
        if exito:
            st.session_state["logueado"] = True
            st.rerun()
        else: st.error(msg)
else:
    st.title("🤖 Panel de Control del Bot")
    tab1, tab2 = st.tabs(["Configurar Bot", "Configurar Pagos"])
    
    with tab1:
        st.subheader("Nueva Regla de Respuesta")
        with st.form("nueva_config", clear_on_submit=True):
            c = st.text_input("Palabras clave (separadas por coma)")
            r = st.text_area("Respuesta automática")
            if st.form_submit_button("Guardar"):
                exito, msg = guardar_configuracion(c, r)
                if exito: st.success(msg); st.rerun()
                else: st.error(msg)

        # --- SECCIÓN NUEVA SOLICITADA ---
        st.divider()
        st.subheader("Subir PDF y Vincular a Palabra Clave")
        archivo_pdf = st.file_uploader("Subir PDF", type="pdf")
        palabra_vinculo = st.text_input("Palabra clave para activar este PDF")
        
        if st.button("Subir y Vincular"):
            if archivo_pdf and palabra_vinculo:
                supabase = get_supabase()
                # Subir al storage
                nombre_archivo = f"{palabra_vinculo}_{archivo_pdf.name}"
                supabase.storage.from_("recetarios").upload(nombre_archivo, archivo_pdf.getvalue())
                url = supabase.storage.from_("recetarios").get_public_url(nombre_archivo)
                # Guardar en BD para que el bot lo encuentre
                guardar_configuracion(palabra_vinculo, url)
                st.success("PDF subido y vinculado")
                st.rerun()

        st.divider()
        st.subheader("Reglas Actuales")
        # Aquí va tu lógica de visualización original...
        configuraciones = obtener_configuraciones()
        # ... (resto de tu código de visualización)
if not st.session_state["logueado"]:
    st.title("🔐 Acceso al Sistema")
    user = st.text_input("Usuario")
    pwd = st.text_input("Contraseña", type="password")
    if st.button("Ingresar"):
        exito, msg = verificar_login(user, pwd)
        if exito:
            st.session_state["logueado"] = True
            st.rerun()
        else: st.error(msg)
else:
    st.title("🤖 Panel de Control del Bot")
    tab1, tab2 = st.tabs(["Configurar Bot", "Configurar Pagos"])
    
    with tab1:
        st.subheader("Nueva Regla de Respuesta")
        with st.form("nueva_config", clear_on_submit=True):
            c = st.text_input("Palabras clave (separadas por coma)")
            r = st.text_area("Respuesta automática")
            if st.form_submit_button("Guardar"):
                exito, msg = guardar_configuracion(c, r)
                if exito: st.success(msg); st.rerun()
                else: st.error(msg)

        st.divider()
        st.subheader("Reglas Guardadas")
        configuraciones = obtener_configuraciones()
        todas_respuestas = obtener_todas_las_respuestas()
        
        # --- AGRUPACIÓN INTELIGENTE (Solución a duplicados) ---
        agrupadas = {}
        for conf in configuraciones:
            palabra = conf['palabra_clave'].strip()
            if palabra not in agrupadas:
                agrupadas[palabra] = {"respuestas": [], "ids": []}
            
            agrupadas[palabra]["respuestas"].append(conf['respuestas']['contenido'])
            agrupadas[palabra]["ids"].append(conf['id'])

        # Mostrar bloques consolidados
        for palabra, datos in agrupadas.items():
            with st.expander(f"Regla: {palabra}"):
                st.write("**Respuestas vinculadas:**")
                for res in datos["respuestas"]:
                    st.info(f"• {res}")
                
                # Selector para vincular una respuesta adicional
                opciones = {r['contenido']: r['id'] for r in todas_respuestas}
                extra_sel = st.selectbox("Agregar otra respuesta:", list(opciones.keys()), key=f"sel_{palabra}")
                
                if st.button("➕ Vincular respuesta", key=f"btn_link_{palabra}"):
                    # Al vincular, se añade la misma palabra con otro respuesta_id.
                    # En la próxima carga, el bucle 'agrupadas' lo meterá en este mismo expander.
                    guardar_palabra_individual(palabra, opciones[extra_sel])
                    st.rerun()

                if st.button("🗑️ Eliminar todas las respuestas de esta regla", key=f"del_{palabra}"):
                    for id_borrar in datos["ids"]: eliminar_configuracion(id_borrar)
                    st.rerun()
    
    with tab2:
        st.subheader("Registrar nuevos datos de pago")
        with st.form("form_contacto", clear_on_submit=True):
            col_a, col_b = st.columns(2)
            ced = col_a.text_input("Cédula Esperada")
            tel = col_b.text_input("Teléfono Esperado")
            if st.form_submit_button("➕ Registrar Datos"):
                guardar_contacto(ced, tel)
                st.rerun()

        st.divider()
        st.subheader("Seleccionar Registro Activo")
        contactos = obtener_configuracion_pagos()
        
        for i, c in enumerate(contactos):
            with st.container(border=True):
                col1, col2 = st.columns([4, 1], vertical_alignment="center")
                col1.markdown(f"**Cédula:** `{c['cedula_esperada']}`  |  **Tel:** `{c['telefono_esperado']}`")
                if c['activo']: col2.success("✅ Activo")
                else:
                    if col2.button("Activar", key=f"btn_activar_{c['id']}_{i}"):
                        activar_contacto(c['id'])
                        st.rerun()

    if st.sidebar.button("Cerrar sesión"):
        st.session_state["logueado"] = False
        st.rerun()
