"""Komponen UI, tema, dan filter global SIGAP Meter."""

from __future__ import annotations

from html import escape

import pandas as pd
import streamlit as st

from src.preprocessor import MONTH_NAMES


# =========================================================
# WARNA UTAMA
# =========================================================

PRIMARY = "#00288e"
PRIMARY_LIGHT = "#e8efff"
TEXT = "#191c1e"
MUTED = "#5f6368"
BORDER = "#d9dde5"
SUCCESS = "#087f5b"
WARNING = "#b45309"


# =========================================================
# CSS GLOBAL
# =========================================================

def render_app_style() -> None:
    """Mengatur tampilan utama dashboard."""

    st.markdown(
        """
        <link
            href="https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:wght,FILL@100..700,0..1"
            rel="stylesheet"
        >

        <style>
        :root {
            --primary: #00288e;
            --primary-light: #e8efff;
            --text: #191c1e;
            --muted: #5f6368;
            --border: #d9dde5;
            --background: #f7f9fb;
            --surface: #ffffff;
        }

        .material-symbols-outlined {
            font-variation-settings:
                'FILL' 0,
                'wght' 450,
                'GRAD' 0,
                'opsz' 24;
            vertical-align: middle;
        }

        html,
        body,
        [class*="st-"] {
            font-size: 16px;
        }

        .stApp {
            color: var(--text);
        }

        [data-testid="stAppViewContainer"] {
            background: var(--background);
        }

        [data-testid="stSidebar"] {
            background: var(--surface);
            border-right: 1px solid #e2e6ee;
        }

        [data-testid="stMarkdownContainer"] p,
        [data-testid="stWidgetLabel"] p,
        [data-testid="stCaptionContainer"] p {
            font-size: 15px;
            line-height: 1.55;
        }

        [data-testid="stWidgetLabel"] p {
            color: #303238;
            font-weight: 650;
        }

        [data-testid="stSidebar"]
        [data-testid="stMarkdownContainer"] p {
            margin-bottom: 0.4rem;
            font-size: 15px;
        }

        .block-container {
            max-width: 1380px;
            padding-top: 1.7rem;
            padding-bottom: 2.5rem;
        }

        h1,
        h2,
        h3 {
            color: var(--text);
            letter-spacing: -0.02em;
        }

        h1 {
            margin-bottom: 4px !important;
            font-size: 32px !important;
            line-height: 1.25 !important;
        }

        h2 {
            font-size: 25px !important;
            line-height: 1.3 !important;
        }

        h3 {
            margin-top: 12px !important;
            margin-bottom: 10px !important;
            font-size: 20px !important;
            line-height: 1.35 !important;
        }

        hr {
            border-color: #e2e6ee !important;
        }

        [data-testid="stCaptionContainer"] p {
            color: var(--muted) !important;
            font-size: 15px !important;
        }


        /* SIDEBAR DAN LOGO */

        .brand-block {
            display: flex;
            align-items: center;
            gap: 13px;
            padding: 5px 0 16px;
        }

        .brand-logo {
            width: 48px;
            height: 48px;
            flex-shrink: 0;
            border-radius: 7px;
            object-fit: contain;
        }

        .brand-title {
            color: var(--primary);
            font-size: 19px;
            font-weight: 780;
            line-height: 1.2;
        }

        .brand-subtitle {
            margin-top: 3px;
            color: var(--muted);
            font-size: 13px;
            line-height: 1.4;
        }

        .sidebar-rule {
            margin: 0 0 15px;
            border: 0;
            border-top: 1px solid var(--border);
        }

        a[data-testid="stPageLink-NavLink"] {
            min-height: 50px;
            margin-bottom: 5px;
            padding: 10px 13px;
            border-radius: 9px;
        }

        a[data-testid="stPageLink-NavLink"] p {
            font-size: 15px !important;
            font-weight: 650 !important;
        }

        a[data-testid="stPageLink-NavLink"]:hover {
            background: var(--primary-light);
        }


        /* HERO LAMA */

        .hero-panel {
            margin: 6px 0 22px;
            padding: 25px 28px;
            color: #ffffff;
            background: linear-gradient(
                135deg,
                #00288e 0%,
                #1649b8 100%
            );
            border-radius: 14px;
            box-shadow: 0 6px 18px rgba(0, 40, 142, 0.14);
        }

        .hero-eyebrow {
            font-size: 13px;
            font-weight: 700;
            letter-spacing: 0.06em;
            text-transform: uppercase;
            opacity: 0.86;
        }

        .hero-title {
            margin: 6px 0;
            font-size: 30px;
            font-weight: 780;
            line-height: 1.22;
        }

        .hero-copy {
            max-width: 850px;
            font-size: 16px;
            line-height: 1.55;
            opacity: 0.95;
        }


        /* KARTU KPI */

        .kpi-card {
            position: relative;
            min-height: 124px;
            padding: 17px 18px;
            overflow: hidden;
            background: var(--surface);
            border: 1px solid var(--border);
            border-radius: 12px;
            box-shadow: 0 2px 7px rgba(25, 28, 30, 0.04);
        }

        .kpi-card::before {
            position: absolute;
            top: 0;
            bottom: 0;
            left: 0;
            width: 4px;
            background: var(--accent);
            content: "";
        }

        .kpi-top {
            display: flex;
            align-items: center;
            justify-content: space-between;
            gap: 10px;
        }

        .kpi-label {
            color: var(--muted);
            font-size: 13px;
            font-weight: 720;
            letter-spacing: 0.03em;
            text-transform: uppercase;
        }

        .kpi-icon {
            display: flex;
            align-items: center;
            justify-content: center;
            width: 36px;
            height: 36px;
            color: var(--accent);
            background: var(--soft);
            border-radius: 9px;
        }

        .kpi-value {
            margin-top: 9px;
            overflow: hidden;
            color: var(--text);
            font-size: 27px;
            font-weight: 780;
            line-height: 1.22;
            text-overflow: ellipsis;
            white-space: nowrap;
        }

        .kpi-note {
            margin-top: 5px;
            overflow: hidden;
            color: var(--muted);
            font-size: 13px;
            line-height: 1.4;
            text-overflow: ellipsis;
            white-space: nowrap;
        }


        /* KARTU INFORMASI */

        .info-card {
            min-height: 125px;
            padding: 18px;
            background: var(--surface);
            border: 1px solid var(--border);
            border-radius: 12px;
            box-shadow: 0 2px 7px rgba(25, 28, 30, 0.03);
        }

        .info-card-icon {
            margin-bottom: 7px;
            color: var(--primary);
        }

        .info-card-title {
            margin-bottom: 5px;
            color: var(--text);
            font-size: 17px;
            font-weight: 740;
        }

        .info-card-copy {
            color: var(--muted);
            font-size: 14px;
            line-height: 1.5;
        }


        /* KARTU PERINGKAT */

        .rank-card {
            padding: 20px;
            text-align: center;
            background: var(--surface);
            border: 1px solid var(--border);
            border-radius: 12px;
        }

        .rank-number {
            display: inline-flex;
            align-items: center;
            justify-content: center;
            width: 34px;
            height: 34px;
            color: var(--primary);
            font-weight: 800;
            background: var(--primary-light);
            border-radius: 50%;
        }

        .rank-name {
            margin: 10px 0 4px;
            overflow: hidden;
            color: var(--text);
            font-size: 17px;
            font-weight: 750;
            text-overflow: ellipsis;
            white-space: nowrap;
        }

        .rank-value {
            color: var(--primary);
            font-size: 27px;
            font-weight: 790;
        }

        .rank-note {
            color: var(--muted);
            font-size: 13px;
        }


        /* FILTER */

        [data-testid="stVerticalBlockBorderWrapper"] {
            background: var(--surface);
            border-radius: 12px;
        }

        [data-baseweb="select"] {
            font-size: 15px;
        }

        [data-baseweb="select"] > div {
            min-height: 44px;
            border-radius: 8px;
        }

        div[data-testid="stSelectbox"] label p {
            font-size: 15px !important;
            font-weight: 650 !important;
        }

        .filter-caption {
            margin: 5px 0 18px;
            color: var(--muted);
            font-size: 14px;
        }


        /* TOMBOL */

        .stButton button,
        .stDownloadButton button {
            min-height: 42px;
            border-radius: 8px;
            font-size: 15px;
            font-weight: 650;
        }


        /* TABEL */

        [data-testid="stDataFrame"] {
            overflow: hidden;
            border: 1px solid var(--border);
            border-radius: 10px;
        }

        [data-testid="stDataFrame"] * {
            font-size: 14px;
        }


        /* RESPONSIVE */

        @media (max-width: 900px) {
            .block-container {
                padding-top: 1.2rem;
            }

            h1 {
                font-size: 28px !important;
            }

            .kpi-card {
                min-height: 116px;
            }

            .hero-panel {
                padding: 21px;
            }

            .hero-title {
                font-size: 27px;
            }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


# =========================================================
# JUDUL HALAMAN
# =========================================================

def render_page_header(
    icon: str,
    title: str,
    description: str = "",
) -> None:
    """Menampilkan judul halaman."""

    st.title(f":material/{icon}: {title}")

    if description:
        st.caption(description)


def render_section_heading(
    icon: str,
    title: str,
    copy: str = "",
) -> None:
    """Menampilkan judul bagian tanpa penjelasan panjang."""

    st.markdown(
        f"### :material/{escape(icon)}: {escape(title)}"
    )


# =========================================================
# KARTU KPI
# =========================================================

def render_kpi_card(
    label: str,
    value: str,
    note: str,
    icon: str,
    accent: str = PRIMARY,
    soft: str = PRIMARY_LIGHT,
) -> None:
    """Menampilkan kartu KPI."""

    label_safe = escape(str(label))
    value_safe = escape(str(value))
    note_safe = escape(str(note))
    icon_safe = escape(str(icon))
    accent_safe = escape(str(accent))
    soft_safe = escape(str(soft))

    st.markdown(
        f"""
        <div
            class="kpi-card"
            style="--accent:{accent_safe};--soft:{soft_safe};"
        >
            <div class="kpi-top">
                <div class="kpi-label">{label_safe}</div>

                <div class="kpi-icon">
                    <span class="material-symbols-outlined">
                        {icon_safe}
                    </span>
                </div>
            </div>

            <div class="kpi-value" title="{value_safe}">
                {value_safe}
            </div>

            <div class="kpi-note" title="{note_safe}">
                {note_safe}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


# =========================================================
# KARTU INFORMASI
# =========================================================

def render_info_card(
    icon: str,
    title: str,
    copy: str,
) -> None:
    """Menampilkan kartu menu atau informasi."""

    icon_safe = escape(str(icon))
    title_safe = escape(str(title))
    copy_safe = escape(str(copy))

    st.markdown(
        f"""
        <div class="info-card">
            <div class="info-card-icon">
                <span class="material-symbols-outlined">
                    {icon_safe}
                </span>
            </div>

            <div class="info-card-title">
                {title_safe}
            </div>

            <div class="info-card-copy">
                {copy_safe}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


# =========================================================
# KARTU PERINGKAT
# =========================================================

def render_rank_card(
    rank: int,
    name: str,
    value: int,
    note: str,
) -> None:
    """Menampilkan kartu peringkat petugas."""

    name_safe = escape(str(name))
    note_safe = escape(str(note))

    st.markdown(
        f"""
        <div class="rank-card">
            <div class="rank-number">
                {rank}
            </div>

            <div class="rank-name" title="{name_safe}">
                {name_safe}
            </div>

            <div class="rank-value">
                {value:,}
            </div>

            <div class="rank-note">
                {note_safe}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


# =========================================================
# FUNGSI PENDUKUNG FILTER
# =========================================================

def _ensure_select_state(
    key: str,
    options: list[object],
    default: object,
) -> None:
    """Memastikan nilai filter tersedia dalam pilihan."""

    if st.session_state.get(key) not in options:
        st.session_state[key] = default


def _reset_global_filters() -> None:
    """Mengembalikan filter ke pilihan awal."""

    filter_keys = [
        "global_period",
        "global_up3",
        "global_ulp",
        "global_officer",
    ]

    for key in filter_keys:
        st.session_state.pop(key, None)


def _format_period(value: object) -> str:
    """Mengubah periode menjadi nama bulan dan tahun."""

    if value == "Semua Periode":
        return "Semua Periode"

    period = pd.Timestamp(value)
    month_name = MONTH_NAMES.get(
        period.month,
        str(period.month),
    )

    return f"{month_name} {period.year}"


# =========================================================
# FILTER GLOBAL
# =========================================================

def render_global_filter_bar(df: pd.DataFrame) -> None:
    """Menampilkan filter yang ringkas dan mudah digunakan."""

    st.markdown("### :material/filter_alt: Filter Data")

    period_values = sorted(
        {
            pd.Timestamp(value)
            for value in df["PERIODE"].dropna().unique()
        }
    )

    period_options: list[object] = [
        "Semua Periode",
        *period_values,
    ]

    _ensure_select_state(
        "global_period",
        period_options,
        "Semua Periode",
    )

    selected_period = st.session_state["global_period"]

    scope = df.copy()

    if selected_period != "Semua Periode":
        scope = scope[
            scope["PERIODE"] == pd.Timestamp(selected_period)
        ]

    up3_values = sorted(
        scope["NAMA UP3"]
        .dropna()
        .astype(str)
        .unique()
        .tolist()
    )

    up3_options = [
        "Semua UP3",
        *up3_values,
    ]

    _ensure_select_state(
        "global_up3",
        up3_options,
        "Semua UP3",
    )

    selected_up3 = st.session_state["global_up3"]

    if selected_up3 != "Semua UP3":
        scope = scope[
            scope["NAMA UP3"].astype(str) == selected_up3
        ]

    ulp_values = sorted(
        scope["NAMA ULP"]
        .dropna()
        .astype(str)
        .unique()
        .tolist()
    )

    ulp_options = [
        "Semua ULP",
        *ulp_values,
    ]

    _ensure_select_state(
        "global_ulp",
        ulp_options,
        "Semua ULP",
    )

    selected_ulp = st.session_state["global_ulp"]

    if selected_ulp != "Semua ULP":
        scope = scope[
            scope["NAMA ULP"].astype(str) == selected_ulp
        ]

    officer_values = sorted(
        scope["PETUGAS"]
        .dropna()
        .astype(str)
        .unique()
        .tolist()
    )

    officer_options = [
        "Semua Petugas",
        *officer_values,
    ]

    _ensure_select_state(
        "global_officer",
        officer_options,
        "Semua Petugas",
    )

    show_up3 = len(up3_values) > 1

    with st.container(border=True):
        if show_up3:
            columns = st.columns(4)

            with columns[0]:
                st.selectbox(
                    "Periode",
                    period_options,
                    key="global_period",
                    format_func=_format_period,
                )

            with columns[1]:
                st.selectbox(
                    "UP3",
                    up3_options,
                    key="global_up3",
                )

            with columns[2]:
                st.selectbox(
                    "ULP",
                    ulp_options,
                    key="global_ulp",
                )

            with columns[3]:
                st.selectbox(
                    "Petugas",
                    officer_options,
                    key="global_officer",
                )

        else:
            columns = st.columns(3)

            with columns[0]:
                st.selectbox(
                    "Periode",
                    period_options,
                    key="global_period",
                    format_func=_format_period,
                )

            with columns[1]:
                st.selectbox(
                    "ULP",
                    ulp_options,
                    key="global_ulp",
                )

            with columns[2]:
                st.selectbox(
                    "Petugas",
                    officer_options,
                    key="global_officer",
                )

        st.button(
            "Reset Filter",
            icon=":material/restart_alt:",
            key="reset_global_filter_button",
            on_click=_reset_global_filters,
        )


# =========================================================
# PENERAPAN FILTER
# =========================================================

def apply_global_filters(
    df: pd.DataFrame,
) -> pd.DataFrame:
    """Menerapkan pilihan filter ke seluruh data."""

    filtered = df.copy()

    selected_period = st.session_state.get(
        "global_period",
        "Semua Periode",
    )

    if selected_period != "Semua Periode":
        filtered = filtered[
            filtered["PERIODE"] == pd.Timestamp(selected_period)
        ]

    selected_up3 = st.session_state.get(
        "global_up3",
        "Semua UP3",
    )

    if selected_up3 != "Semua UP3":
        filtered = filtered[
            filtered["NAMA UP3"].astype(str) == selected_up3
        ]

    selected_ulp = st.session_state.get(
        "global_ulp",
        "Semua ULP",
    )

    if selected_ulp != "Semua ULP":
        filtered = filtered[
            filtered["NAMA ULP"].astype(str) == selected_ulp
        ]

    selected_officer = st.session_state.get(
        "global_officer",
        "Semua Petugas",
    )

    if selected_officer != "Semua Petugas":
        filtered = filtered[
            filtered["PETUGAS"].astype(str) == selected_officer
        ]

    return filtered


# =========================================================
# RINGKASAN FILTER
# =========================================================

def filter_caption(df: pd.DataFrame) -> str:
    """Menampilkan ringkasan hasil filter."""

    if df.empty:
        return "Tidak ada data yang sesuai."

    total_data = len(df)
    total_ulp = df["NAMA ULP"].nunique()
    total_officer = df["PETUGAS"].nunique()

    return (
        f"{total_data:,} data | "
        f"{total_ulp:,} ULP | "
        f"{total_officer:,} petugas"
    )


# =========================================================
# VALIDASI DATA
# =========================================================

def require_data() -> pd.DataFrame:
    """Menghentikan halaman jika data belum diunggah."""

    data = st.session_state.get("raw_data")
    data_ready = st.session_state.get(
        "data_ready",
        False,
    )

    if not data_ready or data is None:
        st.info(
            "Unggah file Excel melalui menu Data di sidebar."
        )
        st.stop()

    return data