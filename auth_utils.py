import os
import bcrypt
import streamlit as st
from supabase import create_client

# 1. Función de conexión optimizada y cacheada
@st.cache_resource
def get_supabase():
    url = os.environ.get("SUPABASE_URL")
    key = os.environ.get("SUPABASE_KEY")
    if not url or not key:
        raise ValueError("Variables SUPABASE_URL o SUPABASE_KEY no configuradas")
    return create_client
