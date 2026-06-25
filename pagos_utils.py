from auth_utils import get_supabase

def obtener_configuracion_pagos():
    """Trae todos los registros de la tabla configuracion_pago."""
    try:
        # Ordenamos por id para que la lista sea consistente
        return get_supabase().table("configuracion_pago").select("*").order("id").execute().data
    except Exception:
        return []

def guardar_contacto(cedula, telefono):
    """Guarda un nuevo registro de pago (activo inicia en FALSE)."""
    try:
        return get_supabase().table("configuracion_pago").insert({
            "cedula_esperada": cedula,
            "telefono_esperado": telefono,
            "activo": False 
        }).execute()
    except Exception as e:
        return False, str(e)

def activar_contacto(id_a_activar):
    """Desactiva todos los registros y activa solo el seleccionado."""
    try:
        supabase = get_supabase()
        # 1. Desactivamos todos
        supabase.table("configuracion_pago").update({"activo": False}).neq("id", -1).execute()
        # 2. Activamos el seleccionado
        return supabase.table("configuracion_pago").update({"activo": True}).eq("id", id_a_activar).execute()
    except Exception as e:
        return False, str(e)
