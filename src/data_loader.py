"""Pembacaan, validasi, dan penggabungan file data gangguan."""

from __future__ import annotations

import base64
import hashlib
import io
import re
from pathlib import Path
from typing import Any

import pandas as pd
import streamlit as st

from src.preprocessor import clean_and_preprocess_data


# =========================================================
# STRUKTUR KOLOM
# =========================================================

REQUIRED_COLUMNS = [
    "TANGGAL INPUT",
    "JAM INPUT",
    "NAMA PELAPOR",
    "ALAMAT",
    "NO. HP",
    "ID PELANGGAN",
    "PENGAWATAN",
    "MERK",
    "JENIS LAYANAN",
    "NO. METER",
    "STAN",
    "DAYA",
    "NO. STROOK DG",
    "PROGRAM GANTI METER",
    "PETUGAS",
    "KOORDINAT",
    "PENYEBAB KERUSAKAN",
    "ARUS",
    "TEGANGAN",
    "STATUS",
    "STATUS PROSES",
    "KODE ULP",
    "NAMA ULP",
    "NAMA UP3",
]


HEADER_ALIASES = {
    "NO HP": "NO. HP",
    "NO.HP": "NO. HP",
    "NO METER": "NO. METER",
    "NO.METER": "NO. METER",
    "NO STROOK DG": "NO. STROOK DG",
    "NO. STROK DG": "NO. STROOK DG",
    "IDPEL": "ID PELANGGAN",
    "ID_PELANGGAN": "ID PELANGGAN",
    "JENIS_LAYANAN": "JENIS LAYANAN",
    "PENYEBAB_KERUSAKAN": "PENYEBAB KERUSAKAN",
    "STATUS_PROSES": "STATUS PROSES",
    "KODE_ULP": "KODE ULP",
    "NAMA_ULP": "NAMA ULP",
    "NAMA_UP3": "NAMA UP3",
}


# =========================================================
# NORMALISASI HEADER
# =========================================================

def _normalise_headers(
    columns: pd.Index,
) -> list[str]:
    """Menyeragamkan penulisan nama kolom."""

    normalised = []

    for column in columns:
        name = str(column)
        name = name.replace("\n", " ")
        name = name.strip().upper()
        name = re.sub(r"\s+", " ", name)

        normalised.append(
            HEADER_ALIASES.get(name, name)
        )

    return normalised


# =========================================================
# MEMBACA FILE
# =========================================================

def _read_payload(
    file_name: str,
    file_bytes: bytes,
) -> pd.DataFrame:
    """Membaca file Excel atau CSV."""

    buffer = io.BytesIO(file_bytes)
    extension = file_name.lower().rsplit(".", 1)[-1]

    if extension == "csv":
        try:
            return pd.read_csv(buffer)

        except UnicodeDecodeError:
            buffer.seek(0)

            return pd.read_csv(
                buffer,
                encoding="latin-1",
            )

    try:
        return pd.read_excel(
            buffer,
            engine="calamine",
        )

    except Exception:
        buffer.seek(0)

        return pd.read_excel(
            buffer,
            engine="openpyxl",
        )


# =========================================================
# VALIDASI DAN PENGGABUNGAN FILE
# =========================================================

@st.cache_data(
    show_spinner="Memeriksa dan menggabungkan file..."
)
def load_and_validate_files(
    payloads: tuple[tuple[str, bytes], ...],
) -> tuple[
    bool,
    str,
    pd.DataFrame | None,
    pd.DataFrame,
    dict[str, Any],
]:
    """Memvalidasi dan menggabungkan seluruh file."""

    valid_frames: list[pd.DataFrame] = []
    summaries: list[dict[str, Any]] = []

    for file_name, file_bytes in payloads:
        summary: dict[str, Any] = {
            "Nama File": file_name,
            "Status": "Gagal",
            "Baris": 0,
            "Periode": "-",
            "Keterangan": "",
        }

        try:
            frame = _read_payload(
                file_name,
                file_bytes,
            )

            frame.columns = _normalise_headers(
                frame.columns
            )

            if frame.columns.duplicated().any():
                duplicated_columns = (
                    frame.columns[
                        frame.columns.duplicated()
                    ]
                    .tolist()
                )

                raise ValueError(
                    "Nama kolom ganda: "
                    + ", ".join(duplicated_columns)
                )

            missing_columns = [
                column
                for column in REQUIRED_COLUMNS
                if column not in frame.columns
            ]

            if missing_columns:
                summary["Keterangan"] = (
                    "Kolom belum tersedia: "
                    + ", ".join(missing_columns)
                )

                summaries.append(summary)
                continue

            frame = frame[
                REQUIRED_COLUMNS
            ].copy()

            parsed_dates = pd.to_datetime(
                frame["TANGGAL INPUT"],
                errors="coerce",
                dayfirst=True,
            )

            valid_dates = parsed_dates.dropna()

            if valid_dates.empty:
                period_label = "Tanggal tidak valid"

            else:
                periods = (
                    valid_dates
                    .dt.to_period("M")
                    .astype(str)
                    .unique()
                    .tolist()
                )

                period_label = ", ".join(
                    sorted(periods)
                )

            frame["SUMBER FILE"] = file_name
            valid_frames.append(frame)

            summary.update(
                {
                    "Status": "Berhasil",
                    "Baris": len(frame),
                    "Periode": period_label,
                    "Keterangan": "Struktur sesuai",
                }
            )

        except Exception as error:
            summary["Keterangan"] = str(error)

        summaries.append(summary)

    summary_df = pd.DataFrame(summaries)

    if not valid_frames:
        return (
            False,
            "Tidak ada file dengan struktur yang sesuai.",
            None,
            summary_df,
            {},
        )

    combined = pd.concat(
        valid_frames,
        ignore_index=True,
    )

    duplicate_mask = combined.duplicated(
        subset=REQUIRED_COLUMNS,
        keep="first",
    )

    duplicates_removed = int(
        duplicate_mask.sum()
    )

    combined = combined.loc[
        ~duplicate_mask
    ].copy()

    cleaned = clean_and_preprocess_data(
        combined
    )

    quality = {
        "total_files": len(payloads),
        "valid_files": int(
            (
                summary_df["Status"]
                == "Berhasil"
            ).sum()
        ),
        "failed_files": int(
            (
                summary_df["Status"]
                == "Gagal"
            ).sum()
        ),
        "raw_rows": int(
            sum(
                len(frame)
                for frame in valid_frames
            )
        ),
        "clean_rows": len(cleaned),
        "duplicates_removed": duplicates_removed,
        "invalid_dates": int(
            cleaned["TANGGAL_INPUT"]
            .isna()
            .sum()
        ),
        "invalid_times": int(
            cleaned["JAM_INPUT_DETIK"]
            .isna()
            .sum()
        ),
        "invalid_coordinates": int(
            (
                cleaned["LATITUDE"].isna()
                | cleaned["LONGITUDE"].isna()
            ).sum()
        ),
        "missing_cells": int(
            cleaned[REQUIRED_COLUMNS]
            .isna()
            .sum()
            .sum()
        ),
    }

    message = (
        f"{quality['valid_files']} file berhasil dimuat. "
        f"Total {len(cleaned):,} data."
    )

    if quality["failed_files"] > 0:
        message += (
            f" {quality['failed_files']} file tidak digunakan."
        )

    return (
        True,
        message,
        cleaned,
        summary_df,
        quality,
    )


# =========================================================
# SESSION STATE
# =========================================================

def _initialise_data_state() -> None:
    """Menyiapkan penyimpanan data aplikasi."""

    defaults = {
        "raw_data": None,
        "data_ready": False,
        "file_summary": None,
        "data_quality": {},
        "loaded_file_names": [],
        "upload_version": 0,
    }

    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def _payload_signature(
    payloads: tuple[tuple[str, bytes], ...],
) -> str:
    """Membuat identitas unik untuk kumpulan file."""

    digest = hashlib.sha256()

    for file_name, file_bytes in payloads:
        digest.update(
            file_name.encode(
                "utf-8",
                errors="ignore",
            )
        )

        digest.update(file_bytes)

    return digest.hexdigest()


# =========================================================
# LOGO PLN
# =========================================================

def _pln_logo_data_uri() -> str | None:
    """Mencari dan mengubah logo menjadi data URI."""

    assets_directory = (
        Path(__file__).resolve().parent.parent
        / "assets"
    )

    possible_logos = [
        assets_directory / "Logo_PLN.png",
        assets_directory / "logo_pln.png",
        assets_directory / "pln_logo.png",
        assets_directory / "Logo_PLN.jpg",
        assets_directory / "Logo_PLN.jpeg",
        assets_directory / "pln_logo.svg",
    ]

    mime_types = {
        ".png": "image/png",
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
        ".svg": "image/svg+xml",
    }

    for logo_path in possible_logos:
        if not logo_path.is_file():
            continue

        mime_type = mime_types.get(
            logo_path.suffix.lower(),
            "image/png",
        )

        encoded_logo = base64.b64encode(
            logo_path.read_bytes()
        ).decode("ascii")

        return (
            f"data:{mime_type};"
            f"base64,{encoded_logo}"
        )

    return None


# =========================================================
# RESET DATA
# =========================================================

def reset_loaded_data() -> None:
    """Menghapus data dan filter yang sedang aktif."""

    data_keys = [
        "raw_data",
        "file_summary",
        "data_quality",
        "loaded_file_names",
        "loaded_signature",
    ]

    for key in data_keys:
        st.session_state.pop(key, None)

    st.session_state["data_ready"] = False

    st.session_state["upload_version"] = (
        st.session_state.get(
            "upload_version",
            0,
        )
        + 1
    )

    for key in list(st.session_state.keys()):
        if key.startswith("global_"):
            st.session_state.pop(key, None)


# =========================================================
# IDENTITAS SIDEBAR
# =========================================================

def _render_sidebar_brand() -> None:
    """Menampilkan logo dan nama dashboard."""

    logo_uri = _pln_logo_data_uri()

    if logo_uri:
        logo_html = (
            f'<img class="brand-logo" '
            f'src="{logo_uri}" '
            f'alt="Logo PLN">'
        )

    else:
        logo_html = ""

    st.sidebar.markdown(
        f"""
        <div class="brand-block">
            {logo_html}

            <div>
                <div class="brand-title">
                    SIGAP Meter
                </div>

                <div class="brand-subtitle">
                    Monitoring Gangguan Meter<br>
                    PLN UP3 Garut
                </div>
            </div>
        </div>

        <hr class="sidebar-rule">
        """,
        unsafe_allow_html=True,
    )

    if not logo_uri:
        st.sidebar.warning(
            "Logo tidak ditemukan. Pastikan file "
            "assets/Logo_PLN.png tersedia."
        )


# =========================================================
# MENU SIDEBAR
# =========================================================

def _render_sidebar_menu() -> None:
    """Menampilkan menu navigasi."""

    st.sidebar.markdown("### Menu")

    st.sidebar.page_link(
        "app.py",
        label="Beranda",
        icon=":material/home:",
    )

    st.sidebar.page_link(
        "pages/2_Ringkasan_UP3.py",
        label="Ringkasan UP3",
        icon=":material/dashboard:",
    )

    st.sidebar.page_link(
        "pages/3_Analisis_ULP.py",
        label="Analisis ULP",
        icon=":material/domain:",
    )

    st.sidebar.page_link(
        "pages/4_Detail_Kerusakan.py",
        label="Detail Kerusakan",
        icon=":material/electric_meter:",
    )

    st.sidebar.page_link(
        "pages/5_Leaderboard_Petugas.py",
        label="Aktivitas Petugas",
        icon=":material/leaderboard:",
    )

    st.sidebar.page_link(
        "pages/6_Unggah_Ekspor.py",
        label="Data dan Ekspor",
        icon=":material/database:",
    )

    st.sidebar.markdown(
        '<hr class="sidebar-rule">',
        unsafe_allow_html=True,
    )


# =========================================================
# UPLOAD FILE
# =========================================================

def _render_file_uploader() -> None:
    """Menampilkan uploader dan status data."""

    st.sidebar.markdown("### Data")

    data_ready = st.session_state.get(
        "data_ready",
        False,
    )

    if not data_ready:
        uploader_key = (
            "global_file_uploader_"
            f"{st.session_state['upload_version']}"
        )

        uploaded_files = st.sidebar.file_uploader(
            "Pilih file Excel",
            type=["xlsx", "xls", "csv"],
            accept_multiple_files=True,
            key=uploader_key,
            help=(
                "File yang sesuai akan "
                "digabungkan secara otomatis."
            ),
        )

        if not uploaded_files:
            st.sidebar.caption(
                "Bisa memilih beberapa file sekaligus."
            )

            return

        payloads = tuple(
            (
                uploaded_file.name,
                uploaded_file.getvalue(),
            )
            for uploaded_file in uploaded_files
        )

        signature = _payload_signature(
            payloads
        )

        if signature == st.session_state.get(
            "loaded_signature"
        ):
            return

        (
            success,
            message,
            data,
            summary,
            quality,
        ) = load_and_validate_files(payloads)

        st.session_state["file_summary"] = summary
        st.session_state["data_quality"] = quality
        st.session_state["loaded_signature"] = signature

        if success and data is not None:
            st.session_state["raw_data"] = data
            st.session_state["data_ready"] = True

            st.session_state[
                "loaded_file_names"
            ] = [
                file_name
                for file_name, _ in payloads
            ]

            st.sidebar.success(message)
            st.rerun()

        st.sidebar.error(message)

        return

    quality = st.session_state.get(
        "data_quality",
        {},
    )

    valid_files = quality.get(
        "valid_files",
        0,
    )

    clean_rows = quality.get(
        "clean_rows",
        0,
    )

    st.sidebar.success(
        f"{valid_files} file aktif | "
        f"{clean_rows:,} data"
    )

    failed_files = quality.get(
        "failed_files",
        0,
    )

    if failed_files > 0:
        st.sidebar.warning(
            f"{failed_files} file tidak digunakan."
        )

    if st.sidebar.button(
        "Ganti Data",
        icon=":material/restart_alt:",
        width="stretch",
    ):
        reset_loaded_data()
        st.rerun()


# =========================================================
# SIDEBAR UTAMA
# =========================================================

def render_sidebar_uploader() -> None:
    """Menampilkan logo, menu navigasi, dan pengelolaan file."""

    _initialise_data_state()

    # =====================================================
    # LOGO DAN IDENTITAS
    # =====================================================

    logo_uri = _pln_logo_data_uri()

    if logo_uri:
        logo_html = (
            f'<img class="brand-logo" '
            f'src="{logo_uri}" '
            f'alt="Logo PLN">'
        )
    else:
        logo_html = ""

    st.sidebar.markdown(
        f"""
        <div class="brand-block">
            {logo_html}

            <div>
                <div class="brand-title">
                    SIGAP Meter
                </div>

                <div class="brand-subtitle">
                    Monitoring Gangguan Meter<br>
                    PLN UP3 Garut
                </div>
            </div>
        </div>

        <hr class="sidebar-rule">
        """,
        unsafe_allow_html=True,
    )

    if not logo_uri:
        st.sidebar.warning(
            "Logo tidak ditemukan. Pastikan file "
            "assets/Logo_PLN.png tersedia."
        )


    # =====================================================
    # MENU NAVIGASI
    # =====================================================

    st.sidebar.markdown("### Menu")

    st.sidebar.page_link(
        "app.py",
        label="Beranda",
        icon=":material/home:",
    )

    st.sidebar.page_link(
        "pages/2_Ringkasan_UP3.py",
        label="Ringkasan UP3",
        icon=":material/dashboard:",
    )

    st.sidebar.page_link(
        "pages/3_Analisis_ULP.py",
        label="Analisis ULP",
        icon=":material/domain:",
    )

    st.sidebar.page_link(
        "pages/4_Detail_Kerusakan.py",
        label="Detail Kerusakan",
        icon=":material/electric_meter:",
    )

    st.sidebar.page_link(
        "pages/5_Leaderboard_Petugas.py",
        label="Aktivitas Petugas",
        icon=":material/leaderboard:",
    )

    st.sidebar.page_link(
        "pages/6_Unggah_Ekspor.py",
        label="Data dan Ekspor",
        icon=":material/database:",
    )

    st.sidebar.markdown(
        '<hr class="sidebar-rule">',
        unsafe_allow_html=True,
    )


    # =====================================================
    # PENGELOLAAN DATA
    # =====================================================

    st.sidebar.markdown("### Data")

    data_ready = st.session_state.get(
        "data_ready",
        False,
    )

    if not data_ready:
        uploader_key = (
            "global_file_uploader_"
            f"{st.session_state['upload_version']}"
        )

        uploaded_files = st.sidebar.file_uploader(
            "Pilih file Excel",
            type=["xlsx", "xls", "csv"],
            accept_multiple_files=True,
            key=uploader_key,
            help=(
                "Pilih satu atau beberapa file. "
                "Data akan digabungkan secara otomatis."
            ),
        )

        if not uploaded_files:
            st.sidebar.caption(
                "Bisa memilih beberapa file sekaligus."
            )

        if uploaded_files:
            payloads = tuple(
                (
                    uploaded_file.name,
                    uploaded_file.getvalue(),
                )
                for uploaded_file in uploaded_files
            )

            signature = _payload_signature(
                payloads
            )

            previous_signature = (
                st.session_state.get(
                    "loaded_signature"
                )
            )

            if signature != previous_signature:
                (
                    success,
                    message,
                    data,
                    summary,
                    quality,
                ) = load_and_validate_files(
                    payloads
                )

                st.session_state[
                    "file_summary"
                ] = summary

                st.session_state[
                    "data_quality"
                ] = quality

                st.session_state[
                    "loaded_signature"
                ] = signature

                if success and data is not None:
                    st.session_state[
                        "raw_data"
                    ] = data

                    st.session_state[
                        "data_ready"
                    ] = True

                    st.session_state[
                        "loaded_file_names"
                    ] = [
                        file_name
                        for file_name, _ in payloads
                    ]

                    st.sidebar.success(
                        message
                    )

                    st.rerun()

                else:
                    st.sidebar.error(
                        message
                    )

    else:
        quality = st.session_state.get(
            "data_quality",
            {},
        )

        valid_files = quality.get(
            "valid_files",
            0,
        )

        clean_rows = quality.get(
            "clean_rows",
            0,
        )

        failed_files = quality.get(
            "failed_files",
            0,
        )

        st.sidebar.success(
            f"{valid_files} file aktif | "
            f"{clean_rows:,} data"
        )

        if failed_files > 0:
            st.sidebar.warning(
                f"{failed_files} file tidak digunakan."
            )

        if st.sidebar.button(
            "Ganti Data",
            icon=":material/restart_alt:",
            width="stretch",
        ):
            reset_loaded_data()
            st.rerun()