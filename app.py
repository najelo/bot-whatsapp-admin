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
            r = st.text_area("Respuesta")
            if st.form_submit_button("Guardar"):
                guardar_configuracion(c, r)
                st.rerun()

        st.divider()
        st.subheader("Subir Recetario (PDF)")
        archivo_pdf = st.file_uploader("Selecciona el PDF", type="pdf")
        palabra_clave_pdf = st.text_input("Palabra clave para el recetario")

        if st.button("Subir al Storage y Guardar"):
            if archivo_pdf and palabra_clave_pdf:
                try:
                    supabase = get_supabase()
                    nombre_archivo = f"{palabra_clave_pdf.lower().replace(' ', '_')}.pdf"
                    
                    # Subir al Storage
                    supabase.storage.from_("recetarios-helado").upload(
                        nombre_archivo, 
                        archivo_pdf.getvalue(), 
                        {"content-type": "application/pdf"}
                    )
                    
                    # Obtener URL pública
                    url_publica = supabase.storage.from_("recetarios-helado").get_public_url(nombre_archivo)
                    
                    # Guardar URL en tabla 'respuestas'
                    guardar_configuracion(palabra_clave_pdf, url_publica)
                    st.success("¡Recetario subido y guardado exitosamente!")
                except Exception as e:
                    st.error(f"Error: {e}")

        st.divider()
        st.subheader("Reglas Actuales")
        configuraciones = obtener_configuraciones()
        if configuraciones:
            agrupado = {}
            for item in configuraciones:
                rid = item['respuesta_id']
                if rid not in agrupado: agrupado[rid] = {"contenido": item['respuestas']['contenido'], "palabras": [], "ids": []}
                agrupado[rid]["palabras"].append(item['palabra_clave'])
                agrupado[rid]["ids"].append(item['id'])
            
            for rid, datos in agrupado.items():
                with st.expander(f"Palabras: {', '.join(datos['palabras'])}"):
                    st.write(f"Respuesta: `{datos['contenido']}`")
                    extra_sel = st.selectbox("Agregar palabra a esta respuesta", [""] + obtener_todas_las_respuestas(), key=f"sel_{rid}")
                    if st.button("Agregar", key=f"add_{rid}") and extra_sel:
                        guardar_palabra_individual(extra_sel, rid)
                        st.rerun()
                    if st.button("🗑️ Eliminar regla", key=f"del_{rid}"):
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
                col1, col2 = st.columns([4, 1])
                col1.markdown(f"**Cédula:** `{c['cedula_esperada']}` | **Tel:** `{c['telefono_esperado']}`")
                if c['activo']: col2.success("✅ Activo")
                else:
                    if col2.button("Activar", key=f"act_{c['id']}"):
                        activar_contacto(c['id'])
                        st.rerun()
