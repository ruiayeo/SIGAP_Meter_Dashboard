"""Halaman leaderboard produktivitas pencatatan petugas."""

import streamlit as st

from src.analytics import build_officer_summary
from src.data_loader import render_sidebar_uploader
from src.ui import (
    apply_global_filters,
    filter_caption,
    render_app_style,
    render_global_filter_bar,
    render_kpi_card,
    render_page_header,
    render_rank_card,
    render_section_heading,
    require_data,
)
from src.visualizer import plot_daily_trend, plot_officer_leaderboard, plot_process_donut


st.set_page_config(page_title="Leaderboard Petugas | SIGAP Meter", page_icon="M", layout="wide")
render_app_style()
render_sidebar_uploader()

data = require_data()
render_page_header(
    "leaderboard",
    "Leaderboard Petugas",
    "Peringkat kontribusi petugas berdasarkan jumlah laporan gangguan yang dicatat pada periode terpilih.",
)
render_global_filter_bar(data)
filtered = apply_global_filters(data)
st.markdown(f'<div class="filter-caption">{filter_caption(filtered)}</div>', unsafe_allow_html=True)

if filtered.empty:
    st.warning("Tidak ada data yang sesuai dengan kombinasi filter.")
    st.stop()

summary = build_officer_summary(filtered)
if summary.empty:
    st.warning("Data petugas belum tersedia.")
    st.stop()

render_section_heading("workspace_premium", "Tiga Petugas Teraktif", "Berdasarkan jumlah input laporan")
top_columns = st.columns(3)
for index, column in enumerate(top_columns):
    with column:
        if index < len(summary):
            row = summary.iloc[index]
            render_rank_card(
                int(row["Peringkat"]),
                str(row["Petugas"]),
                int(row["Total Gangguan"]),
                f"{row['Kontribusi (%)']:.2f}% dari seluruh laporan",
            )
        else:
            render_rank_card(index + 1, "Belum tersedia", 0, "Data belum mencukupi")

st.markdown("---")
render_section_heading("bar_chart", "Visualisasi Peringkat", "Produktivitas pencatatan, bukan penilaian kualitas kerja")
if len(summary) >= 5:
    top_n = st.slider(
        "Jumlah petugas yang ditampilkan",
        min_value=5,
        max_value=min(50, len(summary)),
        value=min(20, len(summary)),
        step=5 if len(summary) >= 10 else 1,
    )
else:
    top_n = len(summary)
st.plotly_chart(plot_officer_leaderboard(summary, top_n), width="stretch")

st.markdown("---")
render_section_heading("table_chart", "Tabel Peringkat Lengkap", "Klik kolom untuk mengurutkan")
display_summary = summary.copy()
display_summary["Input Pertama"] = display_summary["Input Pertama"].dt.strftime("%d %b %Y %H:%M")
display_summary["Input Terakhir"] = display_summary["Input Terakhir"].dt.strftime("%d %b %Y %H:%M")
st.dataframe(
    display_summary,
    width="stretch",
    hide_index=True,
    height=500,
    column_config={
        "Peringkat": st.column_config.NumberColumn(format="#%d"),
        "Total Gangguan": st.column_config.NumberColumn(format="%,d"),
        "Kontribusi (%)": st.column_config.ProgressColumn(format="%.2f%%", min_value=0, max_value=100),
        "Rata-rata per Hari": st.column_config.NumberColumn(format="%.1f"),
    },
)

st.markdown("---")
render_section_heading("person_search", "Rincian Aktivitas Petugas", "Pilih satu petugas untuk melihat detail")
selected_officer = st.selectbox("Pilih Petugas", summary["Petugas"].tolist())
officer_row = summary[summary["Petugas"] == selected_officer].iloc[0]
officer_data = filtered[filtered["PETUGAS"] == selected_officer].copy()

kpi1, kpi2, kpi3, kpi4 = st.columns(4)
with kpi1:
    render_kpi_card("Peringkat", f"#{int(officer_row['Peringkat'])}", "Pada filter saat ini", "workspace_premium")
with kpi2:
    render_kpi_card("Total Input", f"{int(officer_row['Total Gangguan']):,}", f"Kontribusi {officer_row['Kontribusi (%)']:.2f}%", "edit_note", "#087f5b", "#e7f7f1")
with kpi3:
    render_kpi_card("Hari Aktif", f"{int(officer_row['Hari Aktif']):,}", f"{officer_row['Rata-rata per Hari']:.1f} laporan per hari", "calendar_month", "#7357b8", "#f0ebff")
with kpi4:
    render_kpi_card("ULP Dominan", str(officer_row["ULP Dominan"]), f"Menangani {int(officer_row['ULP Ditangani'])} ULP", "domain", "#e07800", "#fff2df")

left, right = st.columns([1.35, 1])
with left:
    st.plotly_chart(plot_daily_trend(officer_data, f"Tren Harian · {selected_officer}"), width="stretch")
with right:
    st.plotly_chart(plot_process_donut(officer_data), width="stretch")

officer_table = officer_data[
    [
        "TANGGAL_INPUT", "JAM_INPUT_FORMAT", "NAMA ULP", "ID PELANGGAN", "MERK",
        "PENYEBAB KERUSAKAN", "STATUS", "STATUS PROSES",
    ]
].rename(
    columns={
        "TANGGAL_INPUT": "Tanggal", "JAM_INPUT_FORMAT": "Jam", "NAMA ULP": "ULP",
        "ID PELANGGAN": "ID Pelanggan", "PENYEBAB KERUSAKAN": "Penyebab Kerusakan",
        "STATUS PROSES": "Status Proses",
    }
).sort_values(["Tanggal", "Jam"], ascending=[False, False])
st.dataframe(
    officer_table,
    width="stretch",
    hide_index=True,
    height=420,
    column_config={"Tanggal": st.column_config.DateColumn(format="DD MMM YYYY")},
)

st.caption(
    "Peringkat hanya menunjukkan jumlah input laporan. Interpretasi kinerja perlu mempertimbangkan beban wilayah, kompleksitas gangguan, dan kualitas penyelesaian."
)
