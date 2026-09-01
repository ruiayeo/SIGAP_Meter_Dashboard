"""Agregasi terpusat untuk KPI, tabel, dan ekspor."""

from __future__ import annotations

import pandas as pd


def top_label(df: pd.DataFrame, column: str, default: str = "-") -> tuple[str, int]:
    if df.empty or column not in df.columns:
        return default, 0
    counts = df[column].dropna().astype(str).value_counts()
    if counts.empty:
        return default, 0
    return str(counts.index[0]), int(counts.iloc[0])


def _mode_label(series: pd.Series) -> str:
    values = series.dropna().astype(str)
    if values.empty:
        return "-"
    modes = values.mode()
    return str(modes.iloc[0]) if not modes.empty else "-"


def build_officer_summary(df: pd.DataFrame) -> pd.DataFrame:
    columns = [
        "Peringkat", "Petugas", "Total Gangguan", "Kontribusi (%)", "ULP Ditangani",
        "Hari Aktif", "Rata-rata per Hari", "ULP Dominan", "Gangguan Dominan",
        "Input Pertama", "Input Terakhir",
    ]
    if df.empty:
        return pd.DataFrame(columns=columns)

    summary = (
        df.groupby("PETUGAS", dropna=False)
        .agg(
            **{
                "Total Gangguan": ("PETUGAS", "size"),
                "ULP Ditangani": ("NAMA ULP", "nunique"),
                "Hari Aktif": ("TANGGAL_INPUT", "nunique"),
                "ULP Dominan": ("NAMA ULP", _mode_label),
                "Gangguan Dominan": ("PENYEBAB KERUSAKAN", _mode_label),
                "Input Pertama": ("DATETIME_INPUT", "min"),
                "Input Terakhir": ("DATETIME_INPUT", "max"),
            }
        )
        .reset_index()
        .rename(columns={"PETUGAS": "Petugas"})
    )
    summary["Hari Aktif"] = summary["Hari Aktif"].replace(0, 1)
    summary["Rata-rata per Hari"] = (
        summary["Total Gangguan"] / summary["Hari Aktif"]
    ).round(1)
    summary["Kontribusi (%)"] = (
        summary["Total Gangguan"] / summary["Total Gangguan"].sum() * 100
    ).round(2)
    summary = summary.sort_values(
        ["Total Gangguan", "Petugas"], ascending=[False, True]
    ).reset_index(drop=True)
    summary.insert(0, "Peringkat", range(1, len(summary) + 1))
    return summary[columns]


def build_ulp_summary(df: pd.DataFrame) -> pd.DataFrame:
    columns = [
        "ULP", "Total Gangguan", "Prabayar", "Pascabayar", "1 Fasa", "3 Fasa",
        "Petugas Aktif", "Merek Dominan", "Penyebab Dominan", "Sudah Diganti",
    ]
    if df.empty:
        return pd.DataFrame(columns=columns)

    rows = []
    for ulp, group in df.groupby("NAMA ULP", dropna=False):
        brand, _ = top_label(group, "MERK")
        cause, _ = top_label(group, "PENYEBAB KERUSAKAN")
        service = group["JENIS LAYANAN"].astype(str)
        phase = group["PENGAWATAN"].astype(str)
        process = group["STATUS PROSES"].astype(str)
        rows.append(
            {
                "ULP": ulp,
                "Total Gangguan": len(group),
                "Prabayar": int((service == "PRABAYAR").sum()),
                "Pascabayar": int((service == "PASCABAYAR").sum()),
                "1 Fasa": int((phase == "1 FASA").sum()),
                "3 Fasa": int((phase == "3 FASA").sum()),
                "Petugas Aktif": int(group["PETUGAS"].nunique()),
                "Merek Dominan": brand,
                "Penyebab Dominan": cause,
                "Sudah Diganti": int((process == "SUDAH DIGANTI").sum()),
            }
        )
    return pd.DataFrame(rows).sort_values("Total Gangguan", ascending=False).reset_index(drop=True)


def build_category_summary(df: pd.DataFrame, column: str, label: str) -> pd.DataFrame:
    if df.empty:
        return pd.DataFrame(columns=[label, "Total Gangguan", "Persentase (%)"])
    result = df[column].value_counts(dropna=False).rename_axis(label).reset_index(name="Total Gangguan")
    result["Persentase (%)"] = (result["Total Gangguan"] / len(df) * 100).round(2)
    return result
