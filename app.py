import streamlit as st
import pandas as pd
from datetime import datetime, time as datetime_time, timedelta
import io

# Importaciones locales personalizadas
from auth_utils import verificar_login, get_supabase
from pagos_utils import obtener_configuracion_pagos, guardar_contacto, activar_contacto

# Módulos del Motor de Flujos
from db_flow import obtener_todos_los_flujos, crear_nuevo_flujo, obtener_datos_lienzo

# Nuevos módulos divididos
from log_utils import obtener_metricas_del_dia, obtener_todos_los_logs
from pdf_utils import exportar_logs_a_pdf

st.set_page_config(page_title="Admin Bot - Flow Builder", layout="wide")
supabase = get_supabase()

# --- LOGIN ---
if "logueado" not in st.session_state: 
    st.session_state["logueado"] = False

if not st.session_state["logueado"]:
    _, col_login, _ = st.columns([1, 1.2, 1])
    with col_login:
        st.markdown("<br><br>", unsafe_allow_html=True)
        with st.container(border=True):
            st.title("🔐 Iniciar Sesión")
            with st.form("login_form", border=False):
                user = st.text_input("Usuario")
                pwd = st.text_input("Contraseña", type="password")
                if st.form_submit_button("Entrar", width='stretch', type="primary"):
                    valido, msg = verificar_login(user, pwd)
                    if valido: 
                        st.session_state["logueado"] = True
                        st.rerun()
                    else: 
                        st.error(msg)
    st.stop()

# --- MODALES FLOTANTES DE EDICIÓN Y CREACIÓN (ESTILO DIALOG) ---

@st.dialog("📝 Configurar Nuevo Bloque", width="medium")
def modal_crear_nodo(flujo_id, tipo_nodo):
    st.markdown(f"### 🧩 Nuevo Bloque: **{tipo_nodo.upper()}**")
    titulo_inicial = st.text_input("Asigna un nombre para identificar este bloque:", placeholder="Ej: Mensaje de Bienvenida")
    
    if tipo_nodo == "texto":
        mensaje_inicial = st.text_area("💬 Mensaje de WhatsApp que enviará el Bot:")
    
    st.markdown("---")
    if st.button("➕ Soltar en el Lienzo", width='stretch', type="primary"):
        if titulo_inicial:
            config = {"titulo": titulo_inicial}
            if tipo_nodo == "texto":
                config["mensaje"] = mensaje_inicial
            elif tipo_nodo == "condicion":
                config["regla"] = "Validar Pago Móvil"
            elif tipo_nodo == "media":
                config["url"] = ""

            nuevo_nodo = {
                "flujo_id": flujo_id,
                "tipo_nodo": tipo_nodo,
                "configuracion": config,
                "posicion_x": 350.0,
                "posicion_y": 220.0
            }
            try:
                supabase.table("nodos_flujo").insert(nuevo_nodo).execute()
                st.toast("¡Bloque añadido con éxito!", icon="🚀")
                st.rerun()
            except Exception as e:
                st.error(f"Error al guardar: {e}")
        else:
            st.warning("Debes asignarle un nombre al bloque.")

@st.dialog("⚙️ Editar Propiedades del Bloque", width="medium")
def modal_editar_nodo(nodo):
    st.markdown(f"### ✏️ Configurando: **{nodo['configuracion'].get('titulo', 'Bloque')}**")
    nuevo_titulo = st.text_input("Nombre del bloque (Label):", value=nodo['configuracion'].get('titulo', ''))
    
    config_actualizada = nodo['configuracion']
    
    if nodo['tipo_nodo'] == "texto":
        nuevo_mensaje = st.text_area("💬 Mensaje de respuesta (WhatsApp):", value=nodo['configuracion'].get('mensaje', ''))
        config_actualizada['mensaje'] = nuevo_mensaje
    elif nodo['tipo_nodo'] == "condicion":
        opciones_filtros = ["Validar Pago Móvil", "Comprobar Referencia Única", "Validar Monto Exacto"]
        filtro_actual = nodo['configuracion'].get('regla', 'Validar Pago Móvil')
        regla_sel = st.selectbox("🛠️ Regla de automatización:", opciones_filtros, index=opciones_filtros.index(filtro_actual) if filtro_actual in opciones_filtros else 0)
        config_actualizada['regla'] = regla_sel
    elif nodo['tipo_nodo'] == "media":
        url_media = st.text_input("🔗 URL del archivo multimedia:", value=nodo['configuracion'].get('url', ''))
        config_actualizada['url'] = url_media

    st.markdown("---")
    col_b1, col_b2 = st.columns([3, 1])
    with col_b1:
        if st.button("💾 Guardar Cambios", type="primary", width="stretch"):
            config_actualizada['titulo'] = nuevo_titulo
            try:
                supabase.table("nodos_flujo").update({"configuracion": config_actualizada}).eq("id", nodo['id']).execute()
                st.toast("¡Bloque guardado!", icon="✅")
                st.rerun()
            except Exception as e:
                st.error(f"Error: {e}")
    with col_b2:
        if st.button("🗑️ Eliminar", type="secondary", width="stretch"):
            if nodo['tipo_nodo'] == "inicio":
                st.error("No puedes borrar el Inicio.")
            else:
                try:
                    supabase.table("conexiones_flujo").delete().eq("nodo_origen_id", nodo['id']).execute()
                    supabase.table("conexiones_flujo").delete().eq("nodo_destino_id", nodo['id']).execute()
                    supabase.table("nodos_flujo").delete().eq("id", nodo['id']).execute()
                    st.toast("Bloque eliminado", icon="🗑️")
                    st.rerun()
                except Exception as e:
                    st.error(f"Error al eliminar: {e}")

@st.dialog("Editar Cuenta de Pago", width="medium")
def abrir_editor_pago(cuenta):
    st.markdown(f"### ✏️ Editando Receptor ID: `{cuenta.get('id')}`")
    nueva_cedula = st.text_input("Nueva Cédula", value=cuenta.get('cedula_esperada', ''))
    nuevo_telefono = st.text_input("Nuevo Teléfono", value=cuenta.get('telefono_esperado', ''))
    st.markdown("---")
    if st.button("💾 Guardar Cambios Cuenta", width='stretch', type="primary"):
        try:
            supabase.table("configuracion_pago").update({"cedula_esperada": nueva_cedula, "telefono_esperado": nuevo_telefono}).eq("id", cuenta['id']).execute()
            st.toast("Cuenta actualizada con éxito", icon="✅")
            st.rerun()
        except Exception as e: 
            st.error(f"Error al actualizar: {e}")

# --- ESTRUCTURA PRINCIPAL ---
col_izq, col_centro, col_der = st.columns([1, 4, 1])

with col_centro:
    head1, head2 = st.columns([4, 1])
    with head1: 
        st.title("🤖 Panel de Control")
    with head2:
        st.markdown("<br>", unsafe_allow_html=True)
        st.button("Cerrar sesión", on_click=lambda: st.session_state.update(logueado=False), type="secondary", width='stretch')
    
    # 📊 DASHBOARD
    metricas = obtener_metricas_del_dia(supabase)
    with st.container(border=True):
        m1, m2, m3 = st.columns(3)
        with m1: st.metric(label="💰 Verificado Hoy", value=metricas["monto"])
        with m2: st.metric(label="🖼️ Capturas Leídas", value=metricas["procesados"])
        with m3: st.metric(label="🚨 Alertas / Fallas", value=metricas["alertas"])
            
    st.markdown("<br>", unsafe_allow_html=True)
    tab1, tab2, tab3 = st.tabs(["🛠️ Constructor de Flujos", "💳 Gestión de Pagos", "📋 Historial de Logs"])

    # --- TAB 1: CONSTRUCTOR DE FLUJOS ---
    with tab1:
        st.write("### 🔀 Constructor Visual de Flujos (Flow Builder)")
        flujos_actuales = obtener_todos_los_flujos()
        
        if flujos_actuales:
            opciones_flujo = {f"🗺️ {fl['nombre']} (Trigger: {fl['palabra_clave']})": fl for fl in flujos_actuales}
            seleccion = st.selectbox("Elige el flujo que deseas editar visualmente:", list(opciones_flujo.keys()))
            
            if seleccion:
                fl_seleccionado = opciones_flujo[seleccion]
                nodos, conexiones = obtener_datos_lienzo(fl_seleccionado['id'])
                
                st.markdown("---")
                col_paleta, col_canvas = st.columns([1.2, 3.8])
                
                with col_paleta:
                    st.markdown("### 🧩 Componentes")
                    st.write("Haz clic para configurar y soltar:")
                    
                    if st.button("📝 Contenido (Texto)", icon="💬", width="stretch"):
                        modal_crear_nodo(fl_seleccionado['id'], "texto")
                        
                    if st.button("🔀 Menú / Condición", icon="⚡", width="stretch"):
                        modal_crear_nodo(fl_seleccionado['id'], "condicion")
                        
                    if st.button("🖼️ Media (Imagen)", icon="📁", width="stretch"):
                        modal_crear_nodo(fl_seleccionado['id'], "media")

                # CORRECCIÓN DE IDENTACIÓN: Esta columna ahora está perfectamente dentro de 'if seleccion:'
                with col_canvas:
                    st.write(f"### 🎨 Lienzo Activo: `{fl_seleccionado['nombre']}`")
                    from streamlit_react_flow import react_flow
                    
                    flow_nodes = []
                    flow_edges = []
                    
                    for n in nodos:
                        color_bloque = "#2e3f7f"
                        if n['tipo_nodo'] == "inicio": color_bloque = "#1b4332"
                        elif n['tipo_nodo'] == "condicion": color_bloque = "#7400b8"
                        elif n['tipo_nodo'] == "media": color_bloque = "#ee6c4d"
                            
                        flow_nodes.append({
                            "id": str(n['id']),
                            "data": {"label": f"{n['configuracion'].get('titulo', 'Sin Nombre')}"},
                            "position": {"x": float(n.get('posicion_x', 100)), "y": float(n.get('posicion_y', 200))},
                            "style": {
                                "background": color_bloque,
                                "color": "white",
                                "border": "2px solid #ffffff",
                                "borderRadius": "10px",
                                "padding": "15px",
                                "fontWeight": "bold",
                                "textAlign": "center"
                            }
                        })
                    
                    for index, con in enumerate(conexiones):
                        flow_edges.append({
                            "id": f"edge_{index}",
                            "source": str(con['nodo_origen_id']),
                            "target": str(con['nodo_destino_id']),
                            "animated": True,
                            "style": {"stroke": "#00f2fe", "strokeWidth": 3}
                        })
                    
                    with st.container(border=True):
                        id_canvas = f"flow_{str(fl_seleccionado['id'])}"
                        elementos_canvas = flow_nodes + flow_edges
                        
                        try:
                            flow_action = react_flow(name=id_canvas, elements=elementos_canvas, flow_styles={"height": "500px", "width": "100%", "background": "#121214"})
                            
                            if flow_action:
                                id_nodo_detectado = None
                                
                                # Captura por click clásico o por selección del elemento
                                if "action" in flow_action and flow_action["action"] == "click":
                                    id_nodo_detectado = flow_action["node"].get("id")
                                elif "selectedElements" in flow_action and flow_action["selectedElements"]:
                                    primer_elemento = flow_action["selectedElements"][0]
                                    if primer_elemento.get("type") != "edge":
                                        id_nodo_detectado = primer_elemento.get("id")
                                
                                if id_nodo_detectado:
                                    nodo_encontrado = next((x for x in nodos if str(x['id']) == str(id_nodo_detectado)), None)
                                    if nodo_encontrado:
                                        modal_editar_nodo(nodo_encontrado)
                                
                                if "action" in flow_action and flow_action["action"] == "connect":
                                    origen = flow_action["edge"]["source"]
                                    destino = flow_action["edge"]["target"]
                                    supabase.table("conexiones_flujo").insert({
                                        "flujo_id": fl_seleccionado['id'],
                                        "nodo_origen_id": int(origen),
                                        "nodo_destino_id": int(destino)
                                    }).execute()
                                    st.rerun()
                                    
                        except Exception as e:
                            st.error(f"Error en el lienzo: {e}")

    # --- TAB 2: PAGOS ---
    with tab2:
        with st.expander("➕ Registrar Nuevo Pago Móvil (Receptor)"):
            with st.form("nuevo_pago_form", border=False, clear_on_submit=True):
                c_ced, c_tel = st.columns(2)
                with c_ced: ced = st.text_input("Cédula Receptor")
                with c_tel: tel = st.text_input("Teléfono Receptor")
                if st.form_submit_button("Registrar Pago Móvil"):
                    if ced and tel:
                        guardar_contacto(ced, tel)
                        st.toast("¡Pago Móvil registrado!", icon="✅")
                        st.rerun()

        st.write("#### 📋 Cuentas Registradas")
        for c in obtener_configuracion_pagos():
            with st.container(border=True):
                st.write(f"💳 **Cédula:** `{c.get('cedula_esperada')}` | **Tel:** `{c.get('telefono_esperado')}`")
                col_act, col_edit, col_del = st.columns([2, 1, 1])
                with col_act:
                    if not c.get('activo') and st.button("🚀 Activar", key=f"act_{c['id']}"):
                        activar_contacto(c['id'])
                        st.rerun()
                with col_edit:
                    if st.button("✏️ Editar", key=f"edit_{c['id']}"): abrir_editor_pago(c)
                with col_del:
                    if st.button("🗑️ Eliminar", key=f"del_{c['id']}"):
                        supabase.table("configuracion_pago").delete().eq("id", c['id']).execute()
                        st.rerun()

    # --- TAB 3: LOGS ---
    with tab3:
        st.subheader("📋 Historial de Transacciones")
        lista_logs = obtener_todos_los_logs(supabase)
        if lista_logs:
            df = pd.DataFrame(lista_logs)
            st.dataframe(df, width='stretch', hide_index=True)
