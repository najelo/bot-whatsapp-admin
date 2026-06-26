# --- DIÁLOGO EDICIÓN DE PAGO MÓVIL ---
    @st.dialog("Editar Cuenta de Pago", width="medium")
    def abrir_editor_pago(cuenta):
        st.markdown(f"### ✏️ Editando Receptor ID: `{cuenta.get('id')}`")
        nueva_cedula = st.text_input("Nueva Cédula", value=cuenta.get('cedula_esperada', ''))
        nuevo_telefono = st.text_input("Nuevo Teléfono", value=cuenta.get('telefono_esperado', ''))
        
        st.markdown("---")
        if st.button("💾 Guardar Cambios Cuenta", use_container_width=True, type="primary"):
            try:
                supabase.table("configuracion_pago").update({
                    "cedula_esperada": nueva_cedula,
                    "telefono_esperado": nuevo_telefono
                }).eq("id", cuenta['id']).execute()
                st.toast("Cuenta actualizada con éxito", icon="✅")
                st.rerun()
            except Exception as e:
                st.error(f"Error al actualizar: {e}")

    # --- LISTADO DE CUENTAS REGISTRADAS ---
    st.write("#### 📋 Cuentas registradas")
    for c in obtener_configuracion_pagos():
        with st.container(border=True):
            # Formateo de información principal
            st.write(f"**Cédula:** {c.get('cedula_esperada')} | **Tel:** {c.get('telefono_esperado')}")
            
            # Estado actual de la cuenta
            if c.get('activo'): 
                st.success("✅ Activo")
            else:
                st.warning("💤 Inactivo")
            
            # Fila de acciones (Activar, Editar, Eliminar)
            col_act, col_edit, col_del = st.columns([2, 1, 1])
            
            with col_act:
                if not c.get('activo'):
                    if st.button("🚀 Activar", key=f"act_{c['id']}", use_container_width=True): 
                        activar_contacto(c['id'])
                        st.rerun()
                else:
                    st.button("✨ Cuenta Principal", key=f"act_dis_{c['id']}", disabled=True, use_container_width=True)
            
            with col_edit:
                if st.button("✏️ Editar", key=f"edit_pago_{c['id']}", use_container_width=True):
                    abrir_editor_pago(c)
                    
            with col_del:
                if st.button("🗑️ Eliminar", key=f"del_pago_{c['id']}", use_container_width=True, type="secondary"):
                    try:
                        supabase.table("configuracion_pago").delete().eq("id", c['id']).execute()
                        st.toast("Cuenta eliminada", icon="🗑️")
                        st.rerun()
                    except Exception as e:
                        st.error(f"No se pudo eliminar: {e}")
