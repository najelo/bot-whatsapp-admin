import os
import time
from datetime import datetime, time as datetime_time
from fastapi import FastAPI, Request, Response, BackgroundTasks
import streamlit as st
import pandas as pd

import ai_utils
import whatsapp_utils
from auth_utils import get_supabase  # Importamos tu cliente de Supabase
import log_utils

# =====================================================================
# 1. CONFIGURACIÓN DE FASTAPI (Para el Webhook de WhatsApp/Meta)
# =====================================================================
app = FastAPI()
supabase_client = get_supabase()
WEBHOOK_VERIFY_TOKEN = os.getenv("WEBHOOK_VERIFY_TOKEN", "tu_token_secreto_aqui")

def registrar_log_transaccion(telefono: str, monto: float, estado: str):
    try:
        data = {
            "phone": str(telefono),
            "monto": float(monto),
            "estado": str(estado).lower()
        }
        supabase_client.table("historial_pagos").insert(data).execute()
    except Exception as e:
        print(f"❌ Error al guardar log en Supabase desde el bot: {e}")

def enviar_respuestas_secuenciales(phone: str, respuestas_lista: list):
    for resp in respuestas_lista:
        if isinstance(resp, str):
            contenido = resp
            tipo = "texto"
        elif isinstance(resp, dict):
            contenido = resp.get("contenido")
            tipo = resp.get("tipo_contenido", "texto")
        else:
            continue
            
        if tipo == "texto":
            whatsapp_utils.send_whatsapp_message(phone, contenido)
        elif tipo == "documento":
            whatsapp_utils.send_whatsapp_document(phone, contenido, "Documento.pdf")
        elif tipo == "multimedia":
            whatsapp_utils.send_whatsapp_image(phone, contenido)
        elif tipo == "audio":
            whatsapp_utils.send_whatsapp_audio(phone, contenido)
            
        time.sleep(1.5)

def procesar_verificacion_pago_bg(phone: str, image_bytes: bytes, monto_esperado: float):
    try:
        exito, respuesta_ia = ai_utils.verificar_capture_con_gemini(image_bytes, monto_esperado)
        if exito:
            whatsapp_utils.send_whatsapp_message(phone, f"✅ Pago verificado con éxito:\n\n{respuesta_ia}")
            ai_utils.set_user_state(phone, "INICIO")
            registrar_log_transaccion(phone, monto_esperado, "aprobado")
        else:
            whatsapp_utils.send_whatsapp_message(phone, f"❌ {respuesta_ia}")
            registrar_log_transaccion(phone, monto_esperado, "alerta")
    except Exception as e:
        print(f"❌ Error en la verificación en segundo plano: {e}")
        whatsapp_utils.send_whatsapp_message(phone, "⚠️ Ocurrió un error interno al procesar tu imagen de pago.")
        registrar_log_transaccion(phone, 0.0, "error")

@app.get("/webhook")
async def verificar_webhook(request: Request):
    params = request.query_params
    mode = params.get("hub.mode")
    token = params.get("hub.verify_token")
    challenge = params.get("hub.challenge")
    if mode and token:
        if mode == "subscribe" and token == WEBHOOK_VERIFY_TOKEN:
            return Response(content=challenge, media_type="text/plain")
    return Response(content="Forbidden", status_code=403)

@app.post("/webhook")
async def recibir_notificacion(request: Request, background_tasks: BackgroundTasks):
    try:
        body = await request.json()
        entry = body.get("entry", [])[0]
        changes = entry.get("changes", [])[0]
        value = changes.get("value", {})
        messages = value.get("messages", [])

        if not messages:
            return "OK", 200

        msg = messages[0]
        phone = msg.get("from")
        estado = ai_utils.get_user_state(phone)

        # Regla de Estado Pendiente de Capture
        if estado and estado.startswith("ESPERANDO_CAPTURE_"):
            if msg.get("type") == "image":
                emoji_usado = estado.split("_")[2]
                monto_esperado = ai_utils.obtener_monto_por_emoji(emoji_usado)
                image_id = msg["image"]["id"]
                image_url = whatsapp_utils.get_media_url(image_id)
                if image_url:
                    image_bytes = whatsapp_utils.download_media(image_url)
                    background_tasks.add_task(procesar_verificacion_pago_bg, phone, image_bytes, monto_esperado)
                else:
                    whatsapp_utils.send_whatsapp_message(phone, "❌ No se pudo descargar la imagen de Meta.")
                return "OK", 200
            else:
                whatsapp_utils.send_whatsapp_message(phone, "⚠️ Tienes una verificación de pago pendiente.\nPor favor, envía únicamente el capture de tu Pago Móvil.")
                return "OK", 200

        # Reglas de Usuario Libre (Reacciones, Texto, Audio)
        if msg.get("type") == "reaction":
            emoji = msg["reaction"].get("emoji")
            ai_utils.set_user_state(phone, f"ESPERANDO_CAPTURE_{emoji}")
            whatsapp_utils.send_whatsapp_message(phone, f"Has elegido {emoji}. Envía el capture de tu pago para verificar.")
            return "OK", 200

        if msg.get("type") == "text":
            texto_usuario = msg["text"]["body"].strip()
            respuestas_encontradas = ai_utils.buscar_todas_las_respuestas(texto_usuario)
            if respuestas_encontradas:
                background_tasks.add_task(enviar_respuestas_secuenciales, phone, respuestas_encontradas)
            else:
                whatsapp_utils.send_whatsapp_message(phone, "Hola. Reacciona con un emoji a nuestros mensajes para iniciar la verificación de pago.")
            return "OK", 200

        if msg.get("type") == "audio":
            audio_id = msg["audio"]["id"]
            audio_url = whatsapp_utils.get_media_url(audio_id)
            audio_bytes = whatsapp_utils.download_media(audio_url)
            texto_transcrito = ai_utils.transcribir_audio_con_whisper(audio_bytes)
            if texto_transcrito:
                respuestas_encontradas = ai_utils.buscar_todas_las_respuestas(texto_transcrito)
                if respuestas_encontradas:
                    background_tasks.add_task(enviar_respuestas_secuenciales, phone, respuestas_encontradas)
            return "OK", 200

    except Exception as e:
        print(f"❌ Error procesando el webhook de Meta: {e}")
    return "OK", 200

# =====================================================================
# 2. CONFIGURACIÓN DE STREAMLIT (Para el Panel de Control Visual)
# =====================================================================
# Solo se ejecuta la parte de interfaz si se invoca mediante `streamlit run app.py`
if __name__ == "__main__" or st.runtime.exists():
    st.set_page_config(
        page_title="Panel de Control - Bot WhatsApp",
        page_icon="📊",
        layout="wide"
    )

    # BARRA LATERAL (SIDEBAR)
    st.sidebar.title("🤖 WhatsApp Admin")
    st.sidebar.markdown("---")

    st.sidebar.subheader("📅 Rango de Fechas")
    fecha_inicio = st.sidebar.date_input("Desde", datetime.now().date())
    fecha_fin = st.sidebar.date_input("Hasta", datetime.now().date())

    st.sidebar.markdown("---")

    st.sidebar.subheader("🔍 Filtrar Tabla por Estado")
    estado_filtro = st.sidebar.selectbox("Selecciona un estado:", ["Todos", "Aprobado", "Alerta", "Error"])

    st.sidebar.markdown("---")

    if st.sidebar.button("🔒 Cerrar Sesión", type="primary", use_container_width=True):
        st.session_state.clear()
        st.rerun()

    # CUERPO PRINCIPAL DEL PANEL
    st.title("📈 Dashboard de Verificación de Pagos")
    st.markdown(f"Monitoreo de transacciones desde **{fecha_inicio}** hasta **{fecha_fin}**")
    st.markdown("---")

    logs_reales = log_utils.obtener_todos_los_logs(supabase_client)

    if not logs_reales:
        st.info("No se encontraron registros en la base de datos.")
    else:
        df = pd.DataFrame(logs_reales)
        df["created_at"] = pd.to_datetime(df["created_at"]).dt.tz_localize(None)
        
        inicio_dt = datetime.combine(fecha_inicio, datetime_time.min)
        fin_dt = datetime.combine(fecha_fin, datetime_time.max)
        df_filtrado = df[(df["created_at"] >= inicio_dt) & (df["created_at"] <= fin_dt)]

        # Métricas
        aprobados = df_filtrado[df_filtrado["estado"] == "aprobado"]
        alertas = df_filtrado[df_filtrado["estado"] == "alerta"]
        errores = df_filtrado[df_filtrado["estado"] == "error"]
        
        monto_total = aprobados["monto"].sum()
        monto_retenido = alertas["monto"].sum()
        total_procesados = len(df_filtrado)

        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric(label="💰 Monto Procesado", value=f"Bs. {monto_total:,.2f}")
        with col2:
            st.metric(label="🛑 Monto Retenido / Alertas", value=f"Bs. {monto_retenido:,.2f}")
        with col3:
            st.metric(label="✅ Capturas Leídas", value=str(total_procesados))
        with col4:
            st.metric(label="🚨 Alertas Totales", value=str(len(alertas) + len(errores)))

        st.markdown("---")

        # Gráfico estético fijo de 24 horas
        st.subheader("📊 Tendencia de Pagos por Hora")
        if not aprobados.empty:
            aprobados["Hora"] = aprobados["created_at"].dt.hour
            grafico_data = aprobados.groupby("Hora")["monto"].sum().reset_index()
            todas_las_horas = pd.DataFrame({"Hora": range(24)})
            grafico_completo = pd.merge(todas_las_horas, grafico_data, on="Hora", how="left").fillna(0)
            st.bar_chart(data=grafico_completo, x="Hora", y="monto", color="#25D366")
        else:
            st.caption("No hay suficientes datos aprobados en este rango para armar el gráfico.")

        st.markdown("---")

        # Tabla e historial
        st.subheader("📋 Historial de Transacciones Recientes")
        busqueda_telefono = st.text_input("🔍 Buscar por número de teléfono:", "")
        
        if estado_filtro != "Todos":
            df_tabla = df_filtrado[df_filtrado["estado"] == estado_filtro.lower()]
        else:
            df_tabla = df_filtrado

        if busqueda_telefono.strip() != "":
            df_tabla = df_tabla[df_tabla["phone"].astype(str).str.contains(busqueda_telefono.strip())]

        df_visual = df_tabla.copy()
        if not df_visual.empty:
            df_visual["created_at"] = df_visual["created_at"].dt.strftime("%Y-%m-%d %H:%M:%S")
            df_visual["monto"] = df_visual["monto"].map("Bs. {:,.2f}".format)
            st.dataframe(df_visual[["id", "created_at", "phone", "monto", "estado"]], use_container_width=True)

            csv_data = df_tabla.to_csv(index=False).encode("utf-8")
            st.download_button(
                label="📥 Descargar Reporte (CSV)",
                data=csv_data,
                file_name=f"reporte_bot_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
                mime="text/csv"
            )
        else:
            st.caption("No hay datos para mostrar con los filtros seleccionados.")
