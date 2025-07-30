import streamlit as st
from src.ui import render_ui
from datetime import date

def main():
    # Konfigurasi halaman
    st.set_page_config(page_title="Kalkulator Stunting Anak", page_icon="🧒", layout="wide")
    
    # Render antarmuka pengguna tanpa profil statis
    render_ui()

if __name__ == "__main__":
    main()