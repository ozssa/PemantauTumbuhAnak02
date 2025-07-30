import streamlit as st
import plotly.express as px
import pandas as pd
from datetime import datetime, date
from src.calculations import interpolasi, hitung_z_score, tentukan_status, validasi_tinggi, validasi_berat, hitung_usia_hari, hitung_usia_bulan
from src.data_manager import baca_data, simpan_histori, baca_histori

def buat_grafik(df_histori):
    """Membuat grafik Z-score, berat badan, dan tinggi badan menggunakan Plotly Express."""
    if not df_histori.empty:
        df_plot = df_histori.copy()
        df_plot['Tanggal'] = pd.to_datetime(df_plot['Tanggal'])
        
        # Grafik Z-score
        fig_zscore = px.line(df_plot, x="Tanggal", y="Z-score", markers=True, 
                            title="Perkembangan Z-score Anak",
                            hover_data={"Usia (Hari)": True, "Usia (Bulan)": True, "Tinggi (cm)": True, "Berat (kg)": True, "Status": True})
        
        fig_zscore.add_hline(y=2, line_dash="dot", line_color="green", 
                            annotation_text="Normal (+2)", annotation_position="top left")
        fig_zscore.add_hline(y=-2, line_dash="dash", line_color="orange", 
                            annotation_text="Batas Stunting (-2)", annotation_position="top left")
        fig_zscore.add_hline(y=-3, line_dash="dash", line_color="red", 
                            annotation_text="Stunting Berat (-3)", annotation_position="top left")
        
        fig_zscore.add_hrect(y0=-3, y1=-2, fillcolor="red", opacity=0.1, line_width=0)
        fig_zscore.add_hrect(y0=-2, y1=2, fillcolor="green", opacity=0.1, line_width=0)
        
        fig_zscore.update_layout(
            xaxis_title="Tanggal Pengukuran", 
            yaxis_title="Z-score", 
            showlegend=False,
            yaxis=dict(range=[-5, 5])  # Diperluas dari [-4, 4] ke [-5, 5]
        )
        st.plotly_chart(fig_zscore, use_container_width=True)
        
        # Grafik Berat Badan
        fig_berat = px.line(df_plot, x="Tanggal", y="Berat (kg)", markers=True, 
                           title="Perkembangan Berat Badan Anak",
                           hover_data={"Usia (Hari)": True, "Usia (Bulan)": True, "Tinggi (cm)": True, "Z-score": True, "Status": True})
        
        fig_berat.update_layout(
            xaxis_title="Tanggal Pengukuran",
            yaxis_title="Berat Badan (kg)",
            showlegend=False,
            yaxis=dict(range=[0, max(df_plot['Berat (kg)']) * 1.2])
        )
        st.plotly_chart(fig_berat, use_container_width=True)
        
        # Grafik Tinggi Badan
        fig_tinggi = px.line(df_plot, x="Tanggal", y="Tinggi (cm)", markers=True, 
                            title="Perkembangan Tinggi Badan Anak",
                            hover_data={"Usia (Hari)": True, "Usia (Bulan)": True, "Berat (kg)": True, "Z-score": True, "Status": True})
        
        fig_tinggi.update_layout(
            xaxis_title="Tanggal Pengukuran",
            yaxis_title="Tinggi Badan (cm)",
            showlegend=False,
            yaxis=dict(range=[min(df_plot['Tinggi (cm)']) * 0.8, max(df_plot['Tinggi (cm)']) * 1.2])
        )
        st.plotly_chart(fig_tinggi, use_container_width=True)
        
        st.markdown("""
        **Interpretasi Z-score berdasarkan WHO:**
        - **Z > +2**: Tinggi (perlu pemantauan)
        - **+2 ≥ Z ≥ -2**: Normal
        - **-3 ≤ Z < -2**: Pendek/Stunting (perlu intervensi gizi)
        - **Z < -3**: Sangat Pendek/Severely Stunted (perlu intervensi medis segera)
        """)

def render_ui():
    """Merender antarmuka pengguna Streamlit."""
    st.title("Kalkulator Stunting Anak")
    st.markdown("**Standar WHO - Pemantauan Pertumbuhan**")
    st.write("Aplikasi untuk memantau pertumbuhan tinggi/panjang badan anak usia 0-5 tahun")
    
    st.info("Data WHO: Length/Height-for-Age Z-scores (0-1856 hari)")
    
    st.markdown("""
    <style>
    /* Light mode styles */
    .metric-container {
        background-color: var(--background-color, #f8f9fa);
        padding: 1.2rem;
        border-radius: 8px;
        margin: 0.5rem 0;
        text-align: center;
        border-left: 4px solid #007bff;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        color: var(--text-color, #333);
        transition: all 0.3s ease;
    }
    
    .metric-value {
        font-size: 2.2rem;
        font-weight: bold;
        color: #007bff;
        margin: 0.5rem 0;
    }
    
    .metric-label {
        font-size: 1rem;
        color: var(--secondary-text-color, #6c757d);
        margin-bottom: 0.5rem;
        font-weight: 500;
    }
    
    .status-normal { border-left-color: #28a745; }
    .status-normal .metric-value { color: #28a745; }
    .status-stunting { border-left-color: #ffc107; }
    .status-stunting .metric-value { color: #e67e22; }
    .status-severe { border-left-color: #dc3545; }
    .status-severe .metric-value { color: #dc3545; }
    
    .info-box {
        background-color: var(--background-color, #f8f9fa);
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #17a2b8;
        margin: 1rem 0;
        color: var(--text-color, #333);
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
    }
    
    .info-box h4 {
        color: var(--text-color, #333);
        margin-top: 0;
    }
    
    .info-box p {
        color: var(--text-color, #333);
        margin: 0.5rem 0;
    }
    
    @media (prefers-color-scheme: dark) {
        :root {
            --background-color: #262730;
            --text-color: #fafafa;
            --secondary-text-color: #a0a0a0;
        }
        
        .metric-container {
            background-color: #262730;
            border-color: rgba(255,255,255,0.1);
            box-shadow: 0 2px 4px rgba(0,0,0,0.3);
        }
        
        .info-box {
            background-color: #262730;
            border-color: rgba(255,255,255,0.1);
            box-shadow: 0 1px 3px rgba(0,0,0,0.3);
        }
        
        .status-stunting .metric-value { 
            color: #f39c12;
        }
    }
    
    [data-testid="stAppViewContainer"][data-theme="dark"] .metric-container,
    .stApp[data-theme="dark"] .metric-container {
        background-color: #262730 !important;
        color: #fafafa !important;
        border-color: rgba(255,255,255,0.1) !important;
        box-shadow: 0 2px 4px rgba(0,0,0,0.3) !important;
    }
    
    [data-testid="stAppViewContainer"][data-theme="dark"] .info-box,
    .stApp[data-theme="dark"] .info-box {
        background-color: #262730 !important;
        color: #fafafa !important;
        border-color: rgba(255,255,255,0.1) !important;
        box-shadow: 0 1px 3px rgba(0,0,0,0.3) !important;
    }
    
    [data-testid="stAppViewContainer"][data-theme="dark"] .info-box h4,
    [data-testid="stAppViewContainer"][data-theme="dark"] .info-box p,
    .stApp[data-theme="dark"] .info-box h4,
    .stApp[data-theme="dark"] .info-box p {
        color: #fafafa !important;
    }
    
    [data-testid="stAppViewContainer"][data-theme="dark"] .metric-label,
    .stApp[data-theme="dark"] .metric-label {
        color: #a0a0a0 !important;
    }
    
    [data-testid="stAppViewContainer"][data-theme="dark"] .status-stunting .metric-value,
    .stApp[data-theme="dark"] .status-stunting .metric-value {
        color: #f39c12 !important;
    }
    
    @media (max-width: 768px) {
        .metric-value { font-size: 1.8rem; }
        .metric-container { padding: 1rem; }
    }
    </style>
    """, unsafe_allow_html=True)
    
    with st.form("profil_form"):
        st.subheader("Input Profil Anak")
        nama = st.text_input("Nama Anak", value="Agus")
        jenis_kelamin = st.selectbox("Jenis Kelamin", ["Laki-laki", "Perempuan"])
        tanggal_lahir = st.date_input("Tanggal Lahir", value=date(2022, 1, 22), min_value=date(2015, 1, 1), max_value=date.today())
        tanggal_ukur = st.date_input("Tanggal Pengukuran", value=date.today(), min_value=date(2015, 1, 1), max_value=date.today())
        submit_profil = st.form_submit_button("Simpan Profil")
    
    if submit_profil:
        try:
            usia_hari = hitung_usia_hari(tanggal_lahir, tanggal_ukur)
            if usia_hari <= 0:
                st.error("Tanggal lahir tidak valid untuk pengukuran!")
                return
            usia_bulan = hitung_usia_bulan(usia_hari)
            
            st.markdown(f"""
            <div class="info-box">
                <h4 style="margin-top: 0; margin-bottom: 1rem;">Profil Anak</h4>
                <p style="margin: 0.5rem 0;"><strong>Nama:</strong> {nama}</p>
                <p style="margin: 0.5rem 0;"><strong>Jenis Kelamin:</strong> {jenis_kelamin}</p>
                <p style="margin: 0.5rem 0;"><strong>Tanggal Lahir:</strong> {tanggal_lahir.strftime('%d/%m/%Y')}</p>
                <p style="margin: 0.5rem 0;"><strong>Tanggal Pengukuran:</strong> {tanggal_ukur.strftime('%d/%m/%Y')}</p>
                <p style="margin: 0.5rem 0;"><strong>Usia:</strong> {usia_hari} hari (~{usia_bulan:.1f} bulan)</p>
            </div>
            """, unsafe_allow_html=True)
            
            if usia_hari > 1856:
                st.error(f"Usia anak ({usia_hari} hari) melebihi rentang data referensi WHO (maksimum 1856 hari). Aplikasi ini untuk anak 0-5 tahun.")
                return
        except ValueError as e:
            st.error(f"Error: {str(e)}")
            return
    
    with st.form("form_stunting"):
        st.subheader("Input Pengukuran")
        tinggi = st.number_input(
            "Tinggi/Panjang Badan (cm)", 
            min_value=30.0, 
            max_value=150.0, 
            value=70.0,
            step=0.1,
            help="Masukkan tinggi dalam cm (contoh: 75.5)"
        )
        berat = st.number_input(
            "Berat Badan (kg)", 
            min_value=1.0, 
            max_value=30.0, 
            value=10.0,
            step=0.1,
            help="Masukkan berat dalam kg (contoh: 10.5)"
        )
        submit_button = st.form_submit_button("Cek Status Pertumbuhan", use_container_width=True)

    if submit_button:
        try:
            usia_hari = hitung_usia_hari(tanggal_lahir, tanggal_ukur)
            usia_bulan = hitung_usia_bulan(usia_hari)
            
            if usia_hari <= 0:
                st.error("Tanggal lahir tidak valid untuk pengukuran!")
                return
            
            if usia_hari > 1856:
                st.error(f"Usia anak ({usia_hari} hari) melebihi rentang data referensi WHO (maksimum 1856 hari). Aplikasi ini untuk anak 0-5 tahun.")
                return

            valid_tinggi, pesan_validasi_tinggi = validasi_tinggi(tinggi, usia_bulan)
            valid_berat, pesan_validasi_berat = validasi_berat(berat, usia_bulan)
            
            if not valid_tinggi:
                st.error(f"Error: {pesan_validasi_tinggi}")
                return
            if not valid_berat:
                st.error(f"Error: {pesan_validasi_berat}")
                return

            file_path = f"data/lhfa-{'girls' if jenis_kelamin == 'Perempuan' else 'boys'}-zscore-expanded-tables.xlsx"
            
            df = baca_data(file_path)
            L, M, S = interpolasi(usia_hari, df)
            z_score = hitung_z_score(tinggi, L, M, S)
            status, pesan = tentukan_status(z_score)
            
            success, message = simpan_histori(tanggal_ukur, jenis_kelamin, usia_hari, usia_bulan, tinggi, berat, z_score, status, nama, "WARGA")
            if not success:
                st.error(f"Error: {message}")
                return
                
            st.success(f"Berhasil: {message}")
            
            with st.container():
                st.subheader("Hasil Analisis Pertumbuhan")
                
                status_class = "status-severe" if z_score < -3 else "status-stunting" if z_score < -2 else "status-normal"
                
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.markdown(f"""
                    <div class="metric-container {status_class}">
                        <div class="metric-label">Z-Score</div>
                        <div class="metric-value">{z_score:.2f}</div>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col2:
                    st.markdown(f"""
                    <div class="metric-container {status_class}">
                        <div class="metric-label">Status Pertumbuhan</div>
                        <div class="metric-value" style="font-size: 1.4rem;">{status}</div>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col3:
                    st.markdown(f"""
                    <div class="metric-container">
                        <div class="metric-label">Tinggi Badan</div>
                        <div class="metric-value">{tinggi} cm</div>
                    </div>
                    """, unsafe_allow_html=True)
                
                st.markdown(f"""
                <div class="metric-container">
                    <div class="metric-label">Berat Badan</div>
                    <div class="metric-value">{berat} kg</div>
                </div>
                """, unsafe_allow_html=True)
                
                with st.expander("Detail Pengukuran"):
                    st.write(f"**Nama:** {nama}")
                    st.write(f"**Jenis Penginput:** WARGA")
                    st.write(f"**Tanggal Pengukuran:** {tanggal_ukur.strftime('%Y-%m-%d')}")
                    st.write(f"**Jenis Kelamin:** {jenis_kelamin}")
                    st.write(f"**Parameter WHO:** L={L:.4f}, M={M:.2f}, S={S:.4f}")
                
                if z_score < -2:
                    st.error(f"Perhatian: {pesan}")
                elif z_score > 2:
                    st.warning(f"Catatan: {pesan}")
                else:
                    st.success(f"Status: {pesan}")
        
        except FileNotFoundError as e:
            st.error(f"File tidak ditemukan: {str(e)}")
            st.info("Pastikan file Excel 'lhfa-boys-zscore-expanded-tables.xlsx' dan 'lhfa-girls-zscore-expanded-tables.xlsx' ada di folder data/.")
        except Exception as e:
            st.error(f"Terjadi kesalahan: {str(e)}")

    st.markdown("---")
    st.subheader("Histori dan Grafik Pertumbuhan")
    
    df_histori = baca_histori()
    if not df_histori.empty:
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Pengukuran", len(df_histori))
        
        with col2:
            z_scores = df_histori['Z-score'].astype(float)
            st.metric("Z-score Terakhir", f"{z_scores.iloc[-1]:.2f}")
        
        with col3:
            stunting_count = len(df_histori[df_histori['Z-score'].astype(float) < -2])
            st.metric("Riwayat Stunting", f"{stunting_count} kali")
        
        with col4:
            berat_terakhir = df_histori['Berat (kg)'].astype(float).iloc[-1]
            st.metric("Berat Terakhir", f"{berat_terakhir:.1f} kg")
        
        st.subheader("Data Histori Pengukuran")
        st.dataframe(df_histori, use_container_width=True)
        
        st.subheader("Grafik Perkembangan Z-score, Berat Badan, dan Tinggi Badan")
        buat_grafik(df_histori)
        
        if len(df_histori) >= 2:
            z_scores = df_histori['Z-score'].astype(float)
            trend_z = "naik" if z_scores.iloc[-1] > z_scores.iloc[-2] else "turun"
            berat_values = df_histori['Berat (kg)'].astype(float)
            trend_berat = "naik" if berat_values.iloc[-1] > berat_values.iloc[-2] else "turun"
            tinggi_values = df_histori['Tinggi (cm)'].astype(float)
            trend_tinggi = "naik" if tinggi_values.iloc[-1] > tinggi_values.iloc[-2] else "turun"
            
            if trend_z == "naik":
                st.info("Tren Positif: Z-score meningkat dari pengukuran sebelumnya.")
            else:
                st.warning("Perhatian: Z-score menurun dari pengukuran sebelumnya. Pantau nutrisi anak.")
            
            if trend_berat == "naik":
                st.info("Tren Positif: Berat badan meningkat dari pengukuran sebelumnya.")
            else:
                st.warning("Perhatian: Berat badan menurun dari pengukuran sebelumnya. Pantau nutrisi anak.")
            
            if trend_tinggi == "naik":
                st.info("Tren Positif: Tinggi badan meningkat dari pengukuran sebelumnya.")
            else:
                st.warning("Perhatian: Tinggi badan menurun dari pengukuran sebelumnya. Pantau nutrisi anak.")
    else:
        st.info("Belum ada data histori pengukuran. Silakan lakukan pengukuran pertama.")
        
    st.markdown("---")
    with st.expander("Informasi Penting"):
        st.markdown("""
        **Catatan Penting:**
        - Aplikasi ini menggunakan standar WHO Growth Charts (Length/Height-for-Age Z-scores, 0-1856 hari)
        - Data referensi diambil dari tabel WHO resmi untuk anak laki-laki dan perempuan
        - Konsultasikan hasil dengan tenaga kesehatan untuk diagnosis akurat
        - Pemantauan rutin penting untuk deteksi dini stunting
        - Data histori disimpan di sesi aplikasi dan akan hilang saat aplikasi ditutup
        - Sumber data: WHO Child Growth Standards (https://www.who.int/childgrowth/standards)
        """)