"""Beranda Dashboard Monitoring Gangguan Meter."""

import streamlit as st

from src.data_loader import render_sidebar_uploader
from src.ui import render_app_style, render_info_card, render_kpi_card, render_section_heading


st.set_page_config(
    page_title="SIGAP Meter | Monitoring Gangguan",
    page_icon="M",
    layout="wide",
    initial_sidebar_state="expanded",
)

render_app_style()
render_sidebar_uploader()

st.markdown(
    """
    <div class="hero-panel">
        <div class="hero-eyebrow">PLN UP3 GARUT · MONITORING GANGGUAN METER</div>
        <div class="hero-title">SIGAP Meter</div>
        <div class="hero-copy">
            Sistem informasi untuk menggabungkan data gangguan bulanan, melihat kerusakan
            kWh meter, membandingkan unit layanan, dan memantau aktivitas pencatatan petugas.
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

if st.session_state.get("data_ready") and st.session_state.get("raw_data") is not None:
    data = st.session_state["raw_data"]
    quality = st.session_state.get("data_quality", {})
    render_section_heading("database", "Status Data", "Data siap digunakan")
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        render_kpi_card(
            "File Berhasil", f"{quality.get('valid_files', 0):,}",
            f"{quality.get('failed_files', 0)} file tidak digunakan", "folder_open",
        )
    with col2:
        render_kpi_card(
            "Baris Data", f"{len(data):,}",
            f"{quality.get('duplicates_removed', 0)} duplikat identik dihapus", "table_rows",
        )
    with col3:
        render_kpi_card(
            "Periode", f"{data['PERIODE'].nunique():,} bulan",
            f"{data['TAHUN'].nunique()} tahun tersedia", "calendar_month",
        )
    with col4:
        render_kpi_card(
            "Unit Layanan", f"{data['NAMA ULP'].nunique():,} ULP",
            f"{data['PETUGAS'].nunique()} petugas tercatat", "domain",
        )

    st.success("Data berhasil dimuat. Buka Ringkasan UP3 untuk mulai melihat hasil analisis.")
    st.page_link(
        "pages/2_Ringkasan_UP3.py",
        label="Buka Ringkasan UP3",
        icon=":material/arrow_forward:",
        width="stretch",
    )
else:
    st.info("Unggah satu atau beberapa file Excel melalui bagian Manajemen File di sidebar.")

st.markdown("<br>", unsafe_allow_html=True)
render_section_heading("view_quilt", "Cakupan Dashboard", "Empat area analisis utama")
col1, col2, col3, col4 = st.columns(4)
with col1:
    render_info_card(
        "dashboard", "Ringkasan UP3",
        "KPI utama, tren bulanan, serta lima besar jenis kerusakan, merek, dan petugas.",
    )
with col2:
    render_info_card(
        "domain", "Analisis per ULP",
        "Perbandingan total gangguan, jenis layanan, pengawatan, dan ringkasan setiap unit.",
    )
with col3:
    render_info_card(
        "electric_meter", "Detail kWh & Kerusakan",
        "Analisis merek meter, penyebab kerusakan, status proses, dan rincian gangguan.",
    )
with col4:
    render_info_card(
        "leaderboard", "Leaderboard Petugas",
        "Peringkat produktivitas pencatatan berdasarkan jumlah laporan yang dimasukkan.",
    )

st.caption(
    "Leaderboard menunjukkan aktivitas pencatatan laporan dan tidak digunakan sebagai satu-satunya ukuran kualitas kerja petugas."
)
