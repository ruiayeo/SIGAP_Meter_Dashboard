"""Halaman analisis dan perbandingan antar ULP."""

import streamlit as st

from src.analytics import build_ulp_summary, top_label
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
from src.visualizer import plot_distribution_by_ulp, plot_monthly_trend, plot_ulp_comparison, plot_status_proses_ulp


st.set_page_config(page_title="Analisis per ULP | SIGAP Meter", page_icon="M", layout="wide")
render_app_style()
render_sidebar_uploader()

data = require_data()
render_page_header(
    "domain",
    "Analisis per ULP",
    "Perbandingan volume gangguan, layanan, fasa, dan progres penanganan pada setiap unit layanan.",
)
render_global_filter_bar(data)
filtered = apply_global_filters(data)
st.markdown(f'<div class="filter-caption">{filter_caption(filtered)}</div>', unsafe_allow_html=True)

if filtered.empty:
    st.warning("Tidak ada data yang sesuai dengan kombinasi filter.")
    st.stop()

ulp_summary = build_ulp_summary(filtered)
top_ulp = str(ulp_summary.iloc[0]["ULP"]) if not ulp_summary.empty else "-"
top_ulp_total = int(ulp_summary.iloc[0]["Total Gangguan"]) if not ulp_summary.empty else 0
prepaid = int((filtered["JENIS LAYANAN"] == "PRABAYAR").sum())
prepaid_share = prepaid / len(filtered) * 100 if len(filtered) else 0
three_phase = int((filtered["PENGAWATAN"] == "3 FASA").sum())
replaced = int((filtered["STATUS PROSES"] == "SUDAH DIGANTI").sum())
replacement_share = replaced / len(filtered) * 100 if len(filtered) else 0

render_section_heading("monitoring", "Ringkasan Unit Layanan", "Sesuai dengan filter yang dipilih")
kpi1, kpi2, kpi3 = st.columns(3)
with kpi1:
    render_kpi_card("ULP Terpilih", f"{filtered['NAMA ULP'].nunique():,}", "Unit dengan data aktif", "domain")
with kpi2:
    render_kpi_card("Gangguan Terbanyak", top_ulp, f"{top_ulp_total:,} gangguan", "trending_up", "#ba1a1a", "#ffebee")
with kpi3:
    render_kpi_card("Persentase Prabayar", f"{prepaid_share:.1f}%", f"{prepaid:,} laporan", "credit_card", "#087f5b", "#e7f7f1")
kpi4, kpi5 = st.columns(2)
with kpi4:
    render_kpi_card("Gangguan 3 Fasa", f"{three_phase:,}", "Laporan 3 fasa", "electrical_services", "#7357b8", "#f0ebff")
with kpi5:
    render_kpi_card("Sudah Diganti", f"{replacement_share:.1f}%", f"{replaced:,} laporan", "published_with_changes", "#e07800", "#fff2df")

st.markdown("---")
render_section_heading("compare_arrows", "Perbandingan Antar ULP", "Jumlah gangguan dan karakteristik pelanggan")
left, right = st.columns([1.05, 1])
with left:
    st.plotly_chart(plot_ulp_comparison(filtered), width="stretch")
with right:
    st.plotly_chart(
        plot_distribution_by_ulp(
            filtered,
            "JENIS LAYANAN",
            "Perbandingan Jenis Layanan per ULP",
            ["#00288e", "#00a7b5"],
        ),
        width="stretch",
    )

left, right = st.columns(2)
with left:
    st.plotly_chart(
        plot_distribution_by_ulp(
            filtered,
            "PENGAWATAN",
            "Perbandingan Fasa per ULP",
            ["#7357b8", "#e07800"],
        ),
        width="stretch",
    )
with right:
    st.plotly_chart(
        plot_status_proses_ulp(filtered),
        use_container_width=True,
    )

st.markdown("---")
render_section_heading("timeline", "Tren Bulanan per Unit", "Total UP3 dan garis masing-masing ULP")
st.plotly_chart(plot_monthly_trend(filtered), width="stretch")

st.markdown("---")
render_section_heading("table_chart", "Tabel Ringkasan ULP", "Rincian indikator operasional")
st.dataframe(
    ulp_summary,
    width="stretch",
    hide_index=True,
    column_config={
        "Total Gangguan": st.column_config.NumberColumn(format="%,d"),
        "Prabayar": st.column_config.NumberColumn(format="%,d"),
        "Pascabayar": st.column_config.NumberColumn(format="%,d"),
        "1 Fasa": st.column_config.NumberColumn(format="%,d"),
        "3 Fasa": st.column_config.NumberColumn(format="%,d"),
        "Sudah Diganti": st.column_config.NumberColumn(format="%,d"),
    },
)
