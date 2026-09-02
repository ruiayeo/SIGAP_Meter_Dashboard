"""Pembuatan laporan Excel monitoring gangguan."""

from __future__ import annotations

import io

import pandas as pd

from src.analytics import build_category_summary, build_officer_summary, build_ulp_summary


DETAIL_EXPORT_COLUMNS = [
    "TANGGAL INPUT", "JAM INPUT", "ID PELANGGAN", "PENGAWATAN", "MERK",
    "JENIS LAYANAN", "NO. METER", "STAN", "DAYA", "NO. STROOK DG",
    "PROGRAM GANTI METER", "PETUGAS", "PENYEBAB KERUSAKAN", "ARUS",
    "TEGANGAN", "STATUS", "STATUS PROSES", "KODE ULP", "NAMA ULP",
    "NAMA UP3", "SUMBER FILE",
]


def _write_sheet(writer: pd.ExcelWriter, frame: pd.DataFrame, sheet_name: str) -> None:
    frame.to_excel(writer, sheet_name=sheet_name, index=False)
    workbook = writer.book
    worksheet = writer.sheets[sheet_name]
    header_format = workbook.add_format(
        {
            "bold": True,
            "font_color": "#ffffff",
            "bg_color": "#00288e",
            "border": 1,
            "align": "center",
            "valign": "vcenter",
        }
    )
    integer_format = workbook.add_format({"num_format": "#,##0"})
    decimal_format = workbook.add_format({"num_format": "#,##0.00"})

    for column_index, column in enumerate(frame.columns):
        worksheet.write(0, column_index, column, header_format)
        values = frame[column].astype(str) if not frame.empty else pd.Series(dtype=str)
        max_length = max([len(str(column))] + values.head(1000).map(len).tolist())
        width = min(max(max_length + 2, 12), 42)
        cell_format = None
        if pd.api.types.is_integer_dtype(frame[column]):
            cell_format = integer_format
        elif pd.api.types.is_float_dtype(frame[column]):
            cell_format = decimal_format
        worksheet.set_column(column_index, column_index, width, cell_format)
    worksheet.freeze_panes(1, 0)
    worksheet.autofilter(0, 0, max(len(frame), 1), max(len(frame.columns) - 1, 0))


def generate_excel_report(df: pd.DataFrame) -> bytes:
    """Menghasilkan workbook berisi ringkasan dan data detail terfilter."""
    output = io.BytesIO()
    total = len(df)
    date_values = df["TANGGAL_INPUT"].dropna()
    period_start = date_values.min().strftime("%d-%m-%Y") if not date_values.empty else "-"
    period_end = date_values.max().strftime("%d-%m-%Y") if not date_values.empty else "-"

    overview = pd.DataFrame(
        {
            "Metrik": [
                "Total Gangguan", "Periode Awal", "Periode Akhir", "Jumlah UP3",
                "Jumlah ULP", "Jumlah Petugas", "Jumlah Merek",
            ],
            "Nilai": [
                total, period_start, period_end, df["NAMA UP3"].nunique(),
                df["NAMA ULP"].nunique(), df["PETUGAS"].nunique(), df["MERK"].nunique(),
            ],
        }
    )

    detail_columns = [column for column in DETAIL_EXPORT_COLUMNS if column in df.columns]
    detail = df[detail_columns].copy()

    with pd.ExcelWriter(
        output,
        engine="xlsxwriter",
        datetime_format="dd-mm-yyyy hh:mm:ss",
        engine_kwargs={
            "options": {"strings_to_formulas": False, "strings_to_urls": False}
        },
    ) as writer:
        _write_sheet(writer, overview, "Ringkasan")
        _write_sheet(writer, build_ulp_summary(df), "Per ULP")
        _write_sheet(writer, build_category_summary(df, "MERK", "Merek"), "Per Merek")
        _write_sheet(
            writer,
            build_category_summary(df, "PENYEBAB KERUSAKAN", "Penyebab Kerusakan"),
            "Jenis Kerusakan",
        )
        _write_sheet(writer, build_officer_summary(df), "Petugas")
        _write_sheet(writer, detail, "Data Detail")
    return output.getvalue()
