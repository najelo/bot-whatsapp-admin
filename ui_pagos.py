import streamlit as st
from pagos_utils import obtener_configuracion_pagos, guardar_contacto, activar_contacto

def render_pagos_tab():
    st.subheader("Configuración de Pago Móvil")
    with st.form("pago_form"):
        ced, tel = st.text_input("Cédula"), st.text_input("Teléfono")
        if st.form_submit_button("Agregar"):
            guardar_contacto(ced, tel); st.rerun()
            
    for p in obtener_configuracion_pagos():
        with st.container(border=True):
            c1, c2 = st.columns([3, 1])
            c1.write(f"**{p['cedula_esperada']}** - {p['telefono_esperado']}")
            if not p['activo'] and c2.button("Activar", key=f"act_{p['id']}"):
                activar_contacto(p['id']); st.rerun()
