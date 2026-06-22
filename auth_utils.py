import os
import bcrypt
import streamlit as st
from supabase import create_client

@st.cache_resource
def get_supabase():
    url = os.environ.get("SUPABASE_URL")
    key = os.environ.get("SUPABASE_KEY")
    if not url or not key:
        raise ValueError("Configura SUPABASE_URL y SUPABASE_KEY en los Secrets")
    return create_client(url, key)

def verificar_login(username, password_input):
    try:
        supabase = get_supabase()
        response = supabase.table("usuarios").select("password_hash").eq("username", username).execute()
        
        if not response.data:
            return False, "Usuario no encontrado"

        hash_guardado = response.data[0]["password_hash"].encode('utf-8')
        if bcrypt.checkpw(password_input.encode('utf-8'), hash_guardado):
            return True, "Login exitoso"
        return False, "Contraseña incorrecta"
    except Exception as e:
        return False, f"Error técnico: {str(e)}"
