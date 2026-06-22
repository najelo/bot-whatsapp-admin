from auth_utils import get_supabase

def obtener_configuracion_pagos():
    try:
        supabase = get_supabase()
        return supabase.table("configuracion_pago").select("*").execute().data
    except Exception:
        return []

def guardar_regla_pago(telefono, identidad, monto):
    try:
        supabase = get_supabase()
        supabase.table("configuracion_pago").insert({
            "telefono_activo": telefono,
            "identidad_activa": identidad,
            "monto_minimo_aprobacion": monto,
            "esta_activo": False # Por defecto empieza desactivado
        }).execute()
        return True, "Regla creada exitosamente"
    except Exception as e:
        return False, str(e)

def activar_regla_pago(id_a_activar):
    try:
        supabase = get_supabase()
        # Desactiva todos los demás
        supabase.table("configuracion_pago").update({"esta_activo": False}).neq("id", id_a_activar).execute()
        # Activa el seleccionado
        supabase.table("configuracion_pago").update({"esta_activo": True}).eq("id", id_a_activar).execute()
        return True, "Regla activada"
    except Exception as e:
        return False, str(e)
