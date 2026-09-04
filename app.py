"""Beranda SIGAP Meter."""

import streamlit as st

from src.data_loader import render_sidebar_uploader
from src.ui import (
    render_app_style,
    render_info_card,
    render_kpi_card,
    require_data,
)


st.set_page_config(
    page_title="SIGAP Meter | PLN UP3 Garut",
    page_icon="M",
    layout="wide",
    initial_sidebar_state="expanded",
)

render_app_style()
render_sidebar_uploader()


# =========================================================
# JUDUL
# =========================================================

st.title(":material/electric_meter: SIGAP Meter")
st.caption("Monitoring gangguan kWh meter PLN UP3 Garut")


# =========================================================
# STATUS DATA
# =========================================================

if (
    st.session_state.get("data_ready")
    and st.session_state.get("raw_data") is not None
):
    data = require_data()
    quality = st.session_state.get("data_quality", {})

    st.markdown("### :material/database: Ringkasan Data")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        render_kpi_card(
            "File",
            f"{quality.get('valid_files', 0):,}",
            "File aktif",
            "folder_open",
        )

    with col2:
        render_kpi_card(
            "Total Data",
            f"{len(data):,}",
            "Laporan gangguan",
            "table_rows",
        )

    with col3:
        render_kpi_card(
            "Periode",
            f"{data['PERIODE'].nunique():,}",
            "Bulan tersedia",
            "calendar_month",
        )

    with col4:
        render_kpi_card(
            "ULP",
            f"{data['NAMA ULP'].nunique():,}",
            "Unit layanan",
            "domain",
        )

    st.page_link(
        "pages/2_Ringkasan_UP3.py",
        label="Lihat Ringkasan UP3",
        icon=":material/arrow_forward:",
        width="stretch",
    )

else:
    st.info("Unggah file Excel melalui menu Data di sidebar.")


# =========================================================
# MENU ANALISIS
# =========================================================

st.markdown("### :material/dashboard: Menu Analisis")

col1, col2 = st.columns(2)

with col1:
    render_info_card(
        "dashboard",
        "Ringkasan UP3",
        "KPI dan tren gangguan.",
    )

with col2:
    render_info_card(
        "domain",
        "Analisis ULP",
        "Perbandingan antar unit.",
    )

col3, col4 = st.columns(2)

with col3:
    render_info_card(
        "electric_meter",
        "Detail Kerusakan",
        "Merek, penyebab, dan status.",
    )

with col4:
    render_info_card(
        "leaderboard",
        "Aktivitas Petugas",
        "Jumlah laporan per petugas.",
    )

st.caption(
    "Peringkat menunjukkan aktivitas input laporan, bukan kualitas kerja."
)