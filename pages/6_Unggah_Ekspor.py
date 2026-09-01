"""Halaman status unggahan, kualitas data, pratinjau, dan ekspor."""

from datetime import datetime

import streamlit as st

from src.data_loader import REQUIRED_COLUMNS, render_sidebar_uploader
from src.export_report import generate_excel_report
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


st.set_page_config(page_title="Unggah Data & Ekspor | SIGAP Meter", page_icon="M", layout="wide")
render_app_style()
render_sidebar_uploader()

data = require_data()
quality = st.session_state.get("data_quality", {})
file_summary = st.session_state.get("file_summary")

render_page_header(
    "cloud_download",
    "Unggah Data & Ekspor",
    "Memeriksa file aktif, kualitas data gabungan, serta mengunduh laporan yang mengikuti filter.",
)

render_section_heading("folder_open", "Status File", "Setiap file diperiksa secara terpisah")
kpi1, kpi2, kpi3 = st.columns(3)
with kpi1:
    render_kpi_card("File Diunggah", f"{quality.get('total_files', 0):,}", "Seluruh file yang dipilih", "upload_file")
with kpi2:
    render_kpi_card("File Berhasil", f"{quality.get('valid_files', 0):,}", "Sudah digabungkan", "check_circle", "#087f5b", "#e7f7f1")
with kpi3:
    render_kpi_card("File Gagal", f"{quality.get('failed_files', 0):,}", "Tidak digunakan", "error", "#ba1a1a", "#ffebee")
kpi4, kpi5 = st.columns(2)
with kpi4:
    render_kpi_card("Baris Bersih", f"{quality.get('clean_rows', 0):,}", f"Dari {quality.get('raw_rows', 0):,} baris", "table_rows", "#2f65d9", "#e8efff")
with kpi5:
    render_kpi_card("Data Sama Dihapus", f"{quality.get('duplicates_removed', 0):,}", "Hanya baris yang identik", "content_copy", "#e07800", "#fff2df")

if file_summary is not None:
    st.dataframe(
        file_summary,
        width="stretch",
        hide_index=True,
        column_config={
            "Baris": st.column_config.NumberColumn(format="%,d"),
            "Status": st.column_config.TextColumn(width="small"),
            "Keterangan": st.column_config.TextColumn(width="large"),
        },
    )

with st.expander("Lihat 24 kolom wajib"):
    st.markdown("\n".join(f"- `{column}`" for column in REQUIRED_COLUMNS))

st.markdown("---")
render_section_heading("fact_check", "Pemeriksaan Kualitas Data", "Tidak menghalangi analisis, tetapi perlu ditinjau")
q1, q2, q3, q4 = st.columns(4)
with q1:
    render_kpi_card("Sel Kosong", f"{quality.get('missing_cells', 0):,}", "Pada 24 kolom wajib", "data_alert")
with q2:
    render_kpi_card("Tanggal Tidak Valid", f"{quality.get('invalid_dates', 0):,}", "Tidak masuk filter periode", "event_busy", "#ba1a1a", "#ffebee")
with q3:
    render_kpi_card("Jam Tidak Valid", f"{quality.get('invalid_times', 0):,}", "Tidak masuk analisis waktu", "schedule", "#e07800", "#fff2df")
with q4:
    render_kpi_card("Koordinat Tidak Valid", f"{quality.get('invalid_coordinates', 0):,}", "Tidak memengaruhi grafik utama", "location_off", "#7357b8", "#f0ebff")

st.markdown("---")
render_section_heading("filter_alt", "Data untuk Diekspor", "Ekspor mengikuti filter di bawah")
render_global_filter_bar(data)
filtered = apply_global_filters(data)
st.markdown(f'<div class="filter-caption">{filter_caption(filtered)}</div>', unsafe_allow_html=True)

if filtered.empty:
    st.warning("Tidak ada data yang dapat diekspor pada kombinasi filter ini.")
    st.stop()

preview_columns = [
    "TANGGAL_INPUT", "JAM_INPUT_FORMAT", "NAMA UP3", "NAMA ULP", "ID PELANGGAN",
    "MERK", "JENIS LAYANAN", "PENGAWATAN", "DAYA", "PENYEBAB KERUSAKAN",
    "STATUS PROSES", "PETUGAS", "SUMBER FILE",
]
preview = filtered[preview_columns].rename(
    columns={
        "TANGGAL_INPUT": "Tanggal", "JAM_INPUT_FORMAT": "Jam", "NAMA UP3": "UP3",
        "NAMA ULP": "ULP", "ID PELANGGAN": "ID Pelanggan",
        "JENIS LAYANAN": "Jenis Layanan", "PENGAWATAN": "Fasa",
        "PENYEBAB KERUSAKAN": "Penyebab Kerusakan", "STATUS PROSES": "Status Proses",
        "SUMBER FILE": "Sumber File",
    }
).sort_values(["Tanggal", "Jam"], ascending=[False, False])
st.dataframe(
    preview.head(1000),
    width="stretch",
    hide_index=True,
    height=440,
    column_config={"Tanggal": st.column_config.DateColumn(format="DD MMM YYYY")},
)
if len(preview) > 1000:
    st.caption(f"Pratinjau dibatasi 1.000 dari {len(preview):,} baris. Seluruh baris tetap disertakan pada ekspor.")

excel_bytes = generate_excel_report(filtered)
timestamp = datetime.now().strftime("%Y%m%d_%H%M")
st.download_button(
    "Unduh Laporan Monitoring Gangguan",
    data=excel_bytes,
    file_name=f"Laporan_SIGAP_Meter_{timestamp}.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    icon=":material/download:",
    width="stretch",
)
st.caption("Laporan berisi ringkasan, analisis ULP, merek, jenis kerusakan, petugas, dan data detail terfilter.")
