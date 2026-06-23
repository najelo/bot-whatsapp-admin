import streamlit as st
from auth_utils import verificar_login, get_supabase
from db_utils import obtener_configuraciones, guardar_configuracion, eliminar_configuracion, actualizar_respuesta
from pagos_utils import obtener_configuracion_pagos, guardar_contacto, activar_contacto

st.set_page_config(page_title="Admin Bot", page_icon="🤖")

if "logueado" not in st.session_state: st.session_state["logueado"] = False

if not st.session_state["logueado"]:
    st.title("🔐 Acceso")
    user = st.text_input("Usuario", key="u")
    pwd = st.text_input("Contraseña", type="password", key="p")
    if st.button("Ingresar"):
        if verificar_login(user, pwd)[0]:
            st.session_state["logueado"] = True
            st.rerun()
else:
    tab1, tab2 = st.tabs(["Bot", "Pagos"])
    
    with tab1:
        st.subheader("Nueva Regla")
        # Usamos un contenedor para gestionar la visibilidad del formulario
        tipo = st.radio("Tipo:", ["Texto", "PDF"], key="radio_tipo")
        c = st.text_input("Palabra clave")
        
        if tipo == "Texto":
            r = st.text_area("Respuesta")
            if st.button("Guardar"):
                guardar_configuracion(c, r)
                st.rerun()
        else:
            archivo = st.file_uploader("Sube el PDF", type="pdf")
            if st.button("Subir y Vincular"):
                if archivo:
                    supabase = get_supabase()
                    nombre = f"{c.lower().replace(' ', '_')}.pdf"
                    supabase.storage.from_("recetarios-helado").upload(nombre, archivo.getvalue(), {"upsert": "true"})
                    url = supabase.storage.from_("recetarios-helado").get_public_url(nombre)
                    guardar_configuracion(c, url)
                    st.success("PDF vinculado"); st.rerun()

        st.divider()
        st.subheader("Reglas Actuales")
        configuraciones = obtener_configuraciones()
        
        # Agrupamos por ID de respuesta
        agrupadas = {}
        for conf in configuraciones:
            rid = conf['respuesta_id']
            if rid not in agrupadas:
                agrupadas[rid] = {"contenido": conf['respuestas']['contenido'], "palabras": [], "ids": []}
            agrupadas[rid]["palabras"].append(conf['palabra_clave'])
            agrupadas[rid]["ids"].append(conf['id'])

        for rid, datos in agrupadas.items():
            with st.expander(f"Palabras: {', '.join(datos['palabras'])}"):
                st.write(f"**Respuesta vinculada actualmente:**")
                st.code(datos['contenido'], language=None)
                
                with st.form(key=f"edit_{rid}"):
                    nuevo_texto = st.text_area("Cambiar respuesta:", value=datos['contenido'])
                    if st.form_submit_button("💾 Guardar cambios"):
                        actualizar_respuesta(rid, nuevo_texto)
                        st.rerun()
                
                if st.button("🗑️ Eliminar regla", key=f"del_{rid}"):
                    for id_borrar in datos["ids"]: eliminar_configuracion(id_borrar)
                    st.rerun()
    
    with tab2:
        # (Tu código de pagos aquí)
        pass
