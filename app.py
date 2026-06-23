import streamlit as st
from auth_utils import verificar_login, get_supabase
from db_utils import (
    obtener_configuraciones, guardar_configuracion, 
    eliminar_configuracion, actualizar_respuesta
)
from pagos_utils import obtener_configuracion_pagos, guardar_contacto, activar_contacto

st.set_page_config(page_title="Admin Bot", page_icon="🤖")

if "logueado" not in st.session_state: st.session_state["logueado"] = False

if not st.session_state["logueado"]:
    st.title("🔐 Acceso al Sistema")
    user = st.text_input("Usuario", key="login_u")
    pwd = st.text_input("Contraseña", type="password", key="login_p")
    if st.button("Ingresar", key="login_btn"):
        exito, msg = verificar_login(user, pwd)
        if exito:
            st.session_state["logueado"] = True
            st.rerun()
        else: st.error(msg)
else:
    st.title("🤖 Panel de Control")
    tab1, tab2 = st.tabs(["Configurar Bot", "Configurar Pagos"])
    
    with tab1:
        st.subheader("Nueva Regla (Texto o PDF)")
        with st.form("nueva_config", clear_on_submit=True):
            tipo = st.radio("Tipo:", ["Texto", "PDF"], key="radio_tipo")
            c = st.text_input("Palabra clave", key="input_palabra")
            
            if tipo == "Texto":
                r = st.text_area("Respuesta", key="input_resp")
                if st.form_submit_button("Guardar"):
                    guardar_configuracion(c, r)
                    st.success("Guardado"); st.rerun()
            else:
                archivo = st.file_uploader("Sube el PDF", type="pdf", key="uploader")
                if st.form_submit_button("Subir y Vincular"):
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
        
        agrupadas = {}
        for conf in configuraciones:
            rid = conf['respuesta_id']
            if rid not in agrupadas:
                agrupadas[rid] = {"contenido": conf['respuestas']['contenido'], "palabras": [], "ids": []}
            agrupadas[rid]["palabras"].append(conf['palabra_clave'])
            agrupadas[rid]["ids"].append(conf['id'])

        for rid, datos in agrupadas.items():
            with st.expander(f"Palabras: {', '.join(datos['palabras'])}", key=f"exp_{rid}"):
                with st.form(key=f"form_{rid}"):
                    nuevo_texto = st.text_area("Editar respuesta:", value=datos['contenido'], key=f"area_{rid}")
                    if st.form_submit_button("💾 Guardar cambios"):
                        actualizar_respuesta(rid, nuevo_texto)
                        st.success("Actualizado"); st.rerun()
                
                if st.button("🗑️ Eliminar regla completa", key=f"del_{rid}"):
                    for id_borrar in datos["ids"]: eliminar_configuracion(id_borrar)
                    st.rerun()
    
    with tab2:
        st.subheader("Datos de pago")
        with st.form("form_contacto", clear_on_submit=True):
            col_a, col_b = st.columns(2)
            ced = col_a.text_input("Cédula", key="ced_reg")
            tel = col_b.text_input("Teléfono", key="tel_reg")
            if st.form_submit_button("➕ Registrar"):
                guardar_contacto(ced, tel); st.rerun()

        for c in obtener_configuracion_pagos():
            with st.container(border=True):
                col1, col2 = st.columns([4, 1], vertical_alignment="center")
                col1.markdown(f"**Cédula:** `{c['cedula_esperada']}`")
                if c.get('activo'): col2.success("✅ Activo")
                elif col2.button("Activar", key=f"btn_{c['id']}"): activar_contacto(c['id']); st.rerun()
