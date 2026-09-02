"""Halaman detail meter kWh dan kerusakan."""

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
from src.visualizer import (
    plot_brand_cause_heatmap,
    plot_distribution_by_ulp,
    plot_process_donut,
    plot_top_categories,
)


st.set_page_config(page_title="Detail kWh & Kerusakan | SIGAP Meter", page_icon="M", layout="wide")
render_app_style()
render_sidebar_uploader()

data = require_data()
render_page_header(
    "electric_meter",
    "Detail kWh & Kerusakan",
    "Analisis mendalam merek kWh meter, kategori kerusakan, dan status proses penanganan.",
)
render_global_filter_bar(data)
filtered = apply_global_filters(data)
st.markdown(f'<div class="filter-caption">{filter_caption(filtered)}</div>', unsafe_allow_html=True)

if filtered.empty:
    st.warning("Tidak ada data yang sesuai dengan kombinasi filter.")
    st.stop()

render_section_heading("tune", "Pilih Data yang Ingin Dilihat", "Pilih merek, penyebab, atau status proses")
filter1, filter2, filter3 = st.columns([1, 1.5, 1.1])
brand_options = sorted(filtered["MERK"].dropna().unique().tolist())
cause_options = sorted(filtered["PENYEBAB KERUSAKAN"].dropna().unique().tolist())
process_options = sorted(filtered["STATUS PROSES"].dropna().unique().tolist())
with filter1:
    selected_brands = st.multiselect("Merek kWh", brand_options, placeholder="Semua merek")
with filter2:
    selected_causes = st.multiselect("Penyebab Kerusakan", cause_options, placeholder="Semua penyebab")
with filter3:
    selected_processes = st.multiselect("Status Proses", process_options, placeholder="Semua status")

detail = filtered.copy()
if selected_brands:
    detail = detail[detail["MERK"].isin(selected_brands)]
if selected_causes:
    detail = detail[detail["PENYEBAB KERUSAKAN"].isin(selected_causes)]
if selected_processes:
    detail = detail[detail["STATUS PROSES"].isin(selected_processes)]

if detail.empty:
    st.warning("Tidak ada data yang cocok dengan filter detail.")
    st.stop()

top_brand, top_brand_count = top_label(detail, "MERK")
top_cause, top_cause_count = top_label(detail, "PENYEBAB KERUSAKAN")
avg_voltage = detail.loc[detail["TEGANGAN"] > 0, "TEGANGAN"].mean()
avg_voltage_label = f"{avg_voltage:.1f} V" if avg_voltage == avg_voltage else "-"
completed = int((detail["STATUS PROSES"] == "SUDAH DIGANTI").sum())

render_section_heading("monitoring", "Ringkasan Kerusakan", "Sesuai dengan filter detail")
kpi1, kpi2, kpi3 = st.columns(3)
with kpi1:
    render_kpi_card("Total Gangguan", f"{len(detail):,}", "Laporan pada detail terpilih", "warning")
with kpi2:
    render_kpi_card("Jumlah Merek", f"{detail['MERK'].nunique():,}", "Variasi merek meter", "electric_meter")
with kpi3:
    render_kpi_card("Merek Terbanyak", top_brand, f"{top_brand_count:,} gangguan", "bar_chart", "#e07800", "#fff2df")
kpi4, kpi5 = st.columns(2)
with kpi4:
    render_kpi_card("Penyebab Terbanyak", top_cause, f"{top_cause_count:,} gangguan", "report_problem", "#ba1a1a", "#ffebee")
with kpi5:
    render_kpi_card("Rata-rata Tegangan", avg_voltage_label, f"{completed:,} sudah diganti", "bolt", "#087f5b", "#e7f7f1")

st.markdown("---")
render_section_heading("bar_chart", "Frekuensi Kerusakan", "Peringkat merek dan kategori penyebab")
st.plotly_chart(
    plot_top_categories(detail, "MERK", "Merek kWh Paling Sering Rusak", 12, "#00288e"),
    width="stretch",
)
st.plotly_chart(
    plot_top_categories(detail, "PENYEBAB KERUSAKAN", "Penyebab Kerusakan Terbanyak", 12, "#ba1a1a"),
    width="stretch",
)

st.markdown("---")
render_section_heading("grid_view", "Hubungan Merek dan Penyebab", "Warna lebih gelap menunjukkan jumlah lebih banyak")
st.plotly_chart(plot_brand_cause_heatmap(detail), width="stretch")

left, right = st.columns(2)
with left:
    st.plotly_chart(plot_process_donut(detail), width="stretch")
with right:
    st.plotly_chart(
        plot_distribution_by_ulp(
            detail,
            "JENIS LAYANAN",
            "Jenis Layanan per ULP",
            ["#00288e", "#00a7b5"],
        ),
        width="stretch",
    )

st.markdown("---")
render_section_heading("table_chart", "Rincian Data Gangguan", "Nomor HP, alamat, dan koordinat tidak ditampilkan")
detail_columns = [
    "TANGGAL_INPUT", "JAM_INPUT_FORMAT", "NAMA UP3", "NAMA ULP", "ID PELANGGAN",
    "MERK", "JENIS LAYANAN", "PENGAWATAN", "DAYA", "PENYEBAB KERUSAKAN",
    "STATUS", "STATUS PROSES", "PETUGAS",
]
detail_table = detail[detail_columns].rename(
    columns={
        "TANGGAL_INPUT": "Tanggal", "JAM_INPUT_FORMAT": "Jam",
        "ID PELANGGAN": "ID Pelanggan", "NAMA UP3": "UP3", "NAMA ULP": "ULP",
        "JENIS LAYANAN": "Jenis Layanan", "PENGAWATAN": "Fasa",
        "PENYEBAB KERUSAKAN": "Penyebab Kerusakan", "STATUS PROSES": "Status Proses",
    }
).sort_values(["Tanggal", "Jam"], ascending=[False, False])
st.dataframe(
    detail_table,
    width="stretch",
    hide_index=True,
    height=500,
    column_config={"Tanggal": st.column_config.DateColumn(format="DD MMM YYYY")},
)
