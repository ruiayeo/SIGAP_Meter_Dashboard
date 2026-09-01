"""Halaman Ringkasan UP3."""

import pandas as pd
import streamlit as st

from src.analytics import top_label
from src.data_loader import render_sidebar_uploader
from src.ui import (
    apply_global_filters,
    filter_caption,
    render_app_style,
    render_global_filter_bar,
    render_kpi_card,
    render_page_header,
    render_section_heading,
    require_data,
)
from src.visualizer import plot_monthly_trend, plot_top_categories


st.set_page_config(page_title="Ringkasan UP3 | SIGAP Meter", page_icon="M", layout="wide")
render_app_style()
render_sidebar_uploader()

data = require_data()
render_page_header(
    "dashboard",
    "Ringkasan UP3",
    "Gambaran menyeluruh jumlah gangguan, karakteristik layanan, merek meter, dan aktivitas petugas.",
)
render_global_filter_bar(data)
filtered = apply_global_filters(data)
st.markdown(f'<div class="filter-caption">{filter_caption(filtered)}</div>', unsafe_allow_html=True)

if filtered.empty:
    st.warning("Tidak ada data yang sesuai dengan kombinasi filter.")
    st.stop()

total = len(filtered)
service_counts = filtered["JENIS LAYANAN"].value_counts()
prepaid = int(service_counts.get("PRABAYAR", 0))
postpaid = int(service_counts.get("PASCABAYAR", 0))
phase_counts = filtered["PENGAWATAN"].value_counts()
one_phase = int(phase_counts.get("1 FASA", 0))
three_phase = int(phase_counts.get("3 FASA", 0))
top_brand, top_brand_count = top_label(filtered, "MERK")
top_officer, top_officer_count = top_label(filtered, "PETUGAS")

render_section_heading("monitoring", "Ringkasan Utama", "Sesuai dengan filter yang dipilih")
kpi1, kpi2, kpi3 = st.columns(3)
with kpi1:
    render_kpi_card("Total Gangguan", f"{total:,}", "Seluruh insiden terpilih", "warning")
with kpi2:
    render_kpi_card(
        "Rincian Layanan", f"{prepaid:,} / {postpaid:,}",
        "Prabayar / Pascabayar", "credit_card", "#087f5b", "#e7f7f1",
    )
with kpi3:
    render_kpi_card(
        "Rincian Fasa", f"{one_phase:,} / {three_phase:,}",
        "1 Fasa / 3 Fasa", "electrical_services", "#7357b8", "#f0ebff",
    )
kpi4, kpi5 = st.columns(2)
with kpi4:
    render_kpi_card(
        "Merek Terbanyak Rusak", top_brand,
        f"{top_brand_count:,} gangguan", "electric_meter", "#e07800", "#fff2df",
    )
with kpi5:
    render_kpi_card(
        "Petugas Teraktif", top_officer,
        f"{top_officer_count:,} input laporan", "person", "#2f65d9", "#e8efff",
    )

st.markdown("---")
render_section_heading("timeline", "Tren Gangguan", "Total UP3 dibandingkan per ULP")
st.plotly_chart(plot_monthly_trend(filtered), width="stretch")

st.markdown("---")
render_section_heading("bar_chart", "Kategori yang Paling Sering Muncul", "Lima besar pada data terpilih")
st.plotly_chart(
    plot_top_categories(filtered, "PENYEBAB KERUSAKAN", "5 Penyebab Kerusakan Terbanyak", 5, "#ba1a1a"),
    width="stretch",
)
chart2, chart3 = st.columns(2)
with chart2:
    st.plotly_chart(
        plot_top_categories(filtered, "MERK", "5 Merek kWh Paling Sering Rusak", 5, "#00288e"),
        width="stretch",
    )
with chart3:
    st.plotly_chart(
        plot_top_categories(filtered, "PETUGAS", "5 Petugas dengan Input Terbanyak", 5, "#087f5b"),
        width="stretch",
    )

st.markdown("---")
render_section_heading("table_chart", "Ringkasan Status Proses", "Jumlah laporan per tahap")
status_summary = (
    filtered["STATUS PROSES"]
    .value_counts()
    .rename_axis("Status Proses")
    .reset_index(name="Jumlah Gangguan")
)
status_summary["Persentase"] = (status_summary["Jumlah Gangguan"] / total * 100).round(2)
st.dataframe(
    status_summary,
    width="stretch",
    hide_index=True,
    column_config={"Persentase": st.column_config.ProgressColumn(format="%.2f%%", min_value=0, max_value=100)},
)
