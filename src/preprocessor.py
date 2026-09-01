"""Pembersihan dan pembentukan fitur data monitoring gangguan."""

from __future__ import annotations

import re
from datetime import datetime, time

import numpy as np
import pandas as pd
import streamlit as st


MONTH_NAMES = {
    1: "Januari",
    2: "Februari",
    3: "Maret",
    4: "April",
    5: "Mei",
    6: "Juni",
    7: "Juli",
    8: "Agustus",
    9: "September",
    10: "Oktober",
    11: "November",
    12: "Desember",
}

IDENTIFIER_COLUMNS = [
    "NO. HP",
    "ID PELANGGAN",
    "NO. METER",
    "NO. STROOK DG",
    "KODE ULP",
]

CATEGORY_COLUMNS = [
    "PENGAWATAN",
    "MERK",
    "JENIS LAYANAN",
    "DAYA",
    "PROGRAM GANTI METER",
    "PETUGAS",
    "PENYEBAB KERUSAKAN",
    "STATUS",
    "STATUS PROSES",
    "NAMA ULP",
    "NAMA UP3",
]


def _clean_identifier(series: pd.Series) -> pd.Series:
    """Menjaga identifier sebagai teks dan menghilangkan akhiran .0."""
    cleaned = series.astype("string").str.strip()
    cleaned = cleaned.str.replace(r"\.0$", "", regex=True)
    return cleaned.replace({"<NA>": pd.NA, "nan": pd.NA, "None": pd.NA})


def _time_to_seconds(value: object) -> float:
    """Mengubah variasi nilai jam Excel menjadi detik sejak tengah malam."""
    if pd.isna(value):
        return np.nan
    if isinstance(value, datetime):
        return float(value.hour * 3600 + value.minute * 60 + value.second)
    if isinstance(value, time):
        return float(value.hour * 3600 + value.minute * 60 + value.second)
    if isinstance(value, (int, float, np.number)):
        numeric = float(value)
        if 0 <= numeric < 1:
            return numeric * 86400
        if 0 <= numeric < 24:
            return numeric * 3600

    text = str(value).strip()
    if not text:
        return np.nan
    parsed = pd.to_datetime(text, errors="coerce")
    if pd.isna(parsed):
        return np.nan
    return float(parsed.hour * 3600 + parsed.minute * 60 + parsed.second)


def _format_seconds(seconds: float) -> object:
    if pd.isna(seconds):
        return pd.NA
    seconds = int(round(seconds)) % 86400
    hour, remainder = divmod(seconds, 3600)
    minute, second = divmod(remainder, 60)
    return f"{hour:02d}:{minute:02d}:{second:02d}"


def _extract_coordinate(value: object) -> tuple[float, float]:
    """Memisahkan koordinat berformat 'latitude, longitude'."""
    if pd.isna(value):
        return np.nan, np.nan
    numbers = re.findall(r"[-+]?\d+(?:[.,]\d+)?", str(value))
    if len(numbers) < 2:
        return np.nan, np.nan
    try:
        latitude = float(numbers[0].replace(",", "."))
        longitude = float(numbers[1].replace(",", "."))
    except ValueError:
        return np.nan, np.nan
    if not (-90 <= latitude <= 90 and -180 <= longitude <= 180):
        return np.nan, np.nan
    return latitude, longitude


@st.cache_data(show_spinner=False)
def clean_and_preprocess_data(df: pd.DataFrame) -> pd.DataFrame:
    """Membersihkan data gabungan dan menambahkan kolom analitis."""
    data = df.copy()

    for column in data.select_dtypes(include="object").columns:
        data[column] = data[column].astype("string").str.strip()

    for column in IDENTIFIER_COLUMNS:
        if column in data.columns:
            data[column] = _clean_identifier(data[column])

    for column in CATEGORY_COLUMNS:
        if column in data.columns:
            data[column] = (
                data[column]
                .astype("string")
                .str.replace(r"\s+", " ", regex=True)
                .str.strip()
                .str.upper()
            )

    data["MERK"] = data["MERK"].replace({"MECOINDO": "MELCOINDA"})
    data["JENIS LAYANAN"] = data["JENIS LAYANAN"].replace(
        {"PASKABAYAR": "PASCABAYAR"}
    )

    data["TANGGAL_INPUT"] = pd.to_datetime(
        data["TANGGAL INPUT"], errors="coerce", dayfirst=True
    ).dt.normalize()
    data["JAM_INPUT_DETIK"] = data["JAM INPUT"].map(_time_to_seconds)
    data["JAM_INPUT_FORMAT"] = data["JAM_INPUT_DETIK"].map(_format_seconds)
    data["JAM_INPUT_HOUR"] = np.floor(data["JAM_INPUT_DETIK"] / 3600)

    datetime_text = (
        data["TANGGAL_INPUT"].dt.strftime("%Y-%m-%d").fillna("")
        + " "
        + data["JAM_INPUT_FORMAT"].fillna("")
    )
    data["DATETIME_INPUT"] = pd.to_datetime(datetime_text, errors="coerce")
    data["TAHUN"] = data["TANGGAL_INPUT"].dt.year.astype("Int64")
    data["BULAN_NUM"] = data["TANGGAL_INPUT"].dt.month.astype("Int64")
    data["BULAN"] = data["BULAN_NUM"].map(MONTH_NAMES).astype("string")
    data["PERIODE"] = data["TANGGAL_INPUT"].dt.to_period("M").dt.to_timestamp()
    data["TANGGAL_LABEL"] = data["TANGGAL_INPUT"].dt.strftime("%d %b %Y")

    for column in ["STAN", "ARUS", "TEGANGAN"]:
        data[column] = pd.to_numeric(data[column], errors="coerce")

    data["DAYA_VA"] = pd.to_numeric(
        data["DAYA"].astype("string").str.extract(r"(\d+)", expand=False),
        errors="coerce",
    )

    coordinates = data["KOORDINAT"].map(_extract_coordinate)
    data["LATITUDE"] = coordinates.map(lambda item: item[0])
    data["LONGITUDE"] = coordinates.map(lambda item: item[1])

    for column in CATEGORY_COLUMNS:
        data[column] = data[column].fillna("TIDAK DIKETAHUI")

    return data.reset_index(drop=True)
