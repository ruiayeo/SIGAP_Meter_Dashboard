"""Komponen UI, tema, dan filter global dashboard."""

from __future__ import annotations

from html import escape

import pandas as pd
import streamlit as st

from src.preprocessor import MONTH_NAMES


PRIMARY = "#00288e"
PRIMARY_LIGHT = "#e8efff"
TEXT = "#191c1e"
MUTED = "#5f6368"
BORDER = "#d9dde5"
SUCCESS = "#087f5b"
WARNING = "#b45309"


def render_app_style() -> None:
    """Memuat Material Symbols dan CSS global dashboard."""

    st.markdown(
        """
        <link
            href="https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:wght,FILL@100..700,0..1"
            rel="stylesheet"
        >

        <style>
        .material-symbols-outlined {
            font-variation-settings:
                'FILL' 0,
                'wght' 450,
                'GRAD' 0,
                'opsz' 24;
            vertical-align: middle;
        }

        /* WARNA HALAMAN */

        [data-testid="stAppViewContainer"] {
            background-color: #f7f9fb;
        }

        [data-testid="stSidebar"] {
            background-color: #ffffff;
            border-right: 1px solid #e2e6ee;
        }

        html,
        body,
        [class*="st-"] {
            font-size: 16px;
        }

        /* TEKS UMUM */

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
            margin-bottom: 0.45rem;
            font-size: 15px;
        }

        /* TOMBOL NAVIGASI SIDEBAR */

        [data-testid="stSidebar"]
        a[data-testid="stPageLink-NavLink"] {
            min-height: 52px;
            padding: 11px 14px;
            margin-bottom: 7px;
            border: 1px solid transparent;
            border-radius: 10px;
            display: flex;
            align-items: center;
            gap: 11px;
            color: #303238;
            transition:
                background-color 0.2s ease,
                border-color 0.2s ease,
                color 0.2s ease,
                transform 0.2s ease;
        }

        /* Teks tombol navigasi */

        [data-testid="stSidebar"]
        a[data-testid="stPageLink-NavLink"] p {
            margin: 0 !important;
            font-size: 16px !important;
            font-weight: 650 !important;
            line-height: 1.35 !important;
        }

        /* Ikon tombol navigasi */

        [data-testid="stSidebar"]
        a[data-testid="stPageLink-NavLink"]
        span {
            font-size: 24px !important;
        }

        /* Efek ketika kursor diarahkan */

        [data-testid="stSidebar"]
        a[data-testid="stPageLink-NavLink"]:hover {
            color: #00288e;
            background-color: #eef3ff;
            border-color: #c7d5f7;
            transform: translateX(2px);
        }

        /* Menu yang sedang aktif */

        [data-testid="stSidebar"]
        a[data-testid="stPageLink-NavLink"][aria-current="page"] {
            color: #00288e;
            background-color: #e8efff;
            border-color: #a9bff0;
            box-shadow: 0 2px 5px rgba(0, 40, 142, 0.08);
        }

        [data-testid="stSidebar"]
        a[data-testid="stPageLink-NavLink"][aria-current="page"] p {
            color: #00288e !important;
            font-weight: 750 !important;
        }

        /* Judul Navigasi Menu dan Manajemen File */

        [data-testid="stSidebar"] h3 {
            margin-top: 9px !important;
            margin-bottom: 11px !important;
            font-size: 17px !important;
            font-weight: 750 !important;
        }

        /* INPUT DAN BUTTON */

        [data-baseweb="select"] {
            min-height: 42px;
            font-size: 15px;
        }

        .stButton button,
        .stDownloadButton button {
            min-height: 43px;
            border-radius: 9px;
            font-size: 15px;
            font-weight: 650;
        }

        /* TABEL */

        [data-testid="stDataFrame"] {
            overflow: hidden;
            border: 1px solid #d9dde5;
            border-radius: 10px;
        }

        [data-testid="stDataFrame"] * {
            font-size: 14px;
        }

        /* METRIC STREAMLIT */

        [data-testid="stMetric"] {
            padding: 16px 18px;
            background-color: #ffffff;
            border: 1px solid #d9dde5;
            border-radius: 12px;
            box-shadow: 0 2px 7px rgba(25, 28, 30, 0.04);
        }

        /* UKURAN HALAMAN */

        .block-container {
            max-width: 1440px;
            padding-top: 2rem;
            padding-bottom: 3rem;
        }

        h1,
        h2,
        h3 {
            color: #191c1e;
            letter-spacing: -0.02em;
        }

        h1 {
            font-size: 2.15rem !important;
            line-height: 1.25 !important;
        }

        h2 {
            font-size: 1.75rem !important;
        }

        h3 {
            font-size: 1.35rem !important;
        }

        hr {
            border-color: #e2e6ee !important;
        }

        /* LOGO DAN NAMA DASHBOARD */

        .brand-block {
            display: flex;
            align-items: center;
            gap: 13px;
            padding: 5px 0 16px;
        }

        .brand-logo {
            width: 48px;
            height: 48px;
            object-fit: contain;
            border-radius: 7px;
            box-shadow: 0 2px 6px rgba(25, 28, 30, 0.14);
        }

        .brand-title {
            color: #191c1e;
            font-size: 19px;
            font-weight: 780;
            line-height: 1.2;
        }

        .brand-subtitle {
            margin-top: 3px;
            color: #5f6368;
            font-size: 13px;
        }

        .sidebar-rule {
            margin: 0 0 15px;
            border: 0;
            border-top: 1px solid #d9dde5;
        }

        /* HERO BERANDA */

        .hero-panel {
            padding: 34px 36px;
            margin: 8px 0 24px;
            color: #ffffff;
            background:
                linear-gradient(
                    135deg,
                    #00288e 0%,
                    #1649b8 100%
                );
            border-radius: 16px;
            box-shadow: 0 8px 24px rgba(0, 40, 142, 0.16);
        }

        .hero-eyebrow {
            font-size: 14px;
            font-weight: 700;
            letter-spacing: 0.07em;
            text-transform: uppercase;
            opacity: 0.86;
        }

        .hero-title {
            margin: 9px 0;
            font-size: 34px;
            font-weight: 780;
            line-height: 1.22;
        }

        .hero-copy {
            max-width: 880px;
            font-size: 17px;
            line-height: 1.65;
            opacity: 0.95;
        }

        /* JUDUL BAGIAN */

        .section-heading {
            display: flex;
            align-items: center;
            gap: 9px;
            margin: 7px 0 12px;
        }

        .section-heading .material-symbols-outlined {
            color: #00288e;
        }

        .section-heading-title {
            color: #191c1e;
            font-size: 21px;
            font-weight: 740;
        }

        .section-heading-copy {
            margin-left: auto;
            color: #5f6368;
            font-size: 14px;
        }

        /* KARTU KPI */

        .kpi-card {
            --accent: #00288e;
            --soft: #e8efff;

            position: relative;
            min-height: 142px;
            padding: 20px 21px;
            overflow: hidden;
            background-color: #ffffff;
            border: 1px solid #d9dde5;
            border-radius: 12px;
            box-shadow: 0 2px 7px rgba(25, 28, 30, 0.04);
        }

        .kpi-card::before {
            position: absolute;
            top: 0;
            bottom: 0;
            left: 0;
            width: 4px;
            background-color: var(--accent);
            content: "";
        }

        .kpi-top {
            display: flex;
            align-items: center;
            justify-content: space-between;
            gap: 10px;
        }

        .kpi-label {
            color: #5f6368;
            font-size: 13px;
            font-weight: 720;
            letter-spacing: 0.035em;
            text-transform: uppercase;
        }

        .kpi-icon {
            width: 38px;
            height: 38px;
            color: var(--accent);
            background-color: var(--soft);
            border-radius: 9px;
            display: flex;
            align-items: center;
            justify-content: center;
        }

        .kpi-value {
            margin-top: 13px;
            overflow: hidden;
            color: #191c1e;
            font-size: 28px;
            font-weight: 780;
            line-height: 1.22;
            text-overflow: ellipsis;
            white-space: nowrap;
        }

        .kpi-note {
            margin-top: 7px;
            overflow: hidden;
            color: #5f6368;
            font-size: 13px;
            text-overflow: ellipsis;
            white-space: nowrap;
        }

        /* KETERANGAN FILTER */

        .filter-caption {
            margin: 5px 0 20px;
            color: #5f6368;
            font-size: 14px;
        }

        /* KARTU INFORMASI */

        .info-card {
            min-height: 158px;
            padding: 21px;
            background-color: #ffffff;
            border: 1px solid #d9dde5;
            border-radius: 12px;
        }

        .info-card-icon {
            margin-bottom: 9px;
            color: #00288e;
        }

        .info-card-title {
            margin-bottom: 7px;
            color: #191c1e;
            font-size: 17px;
            font-weight: 740;
        }

        .info-card-copy {
            color: #5f6368;
            font-size: 14px;
            line-height: 1.6;
        }

        /* KARTU PERINGKAT */

        .rank-card {
            padding: 23px;
            text-align: center;
            background-color: #ffffff;
            border: 1px solid #d9dde5;
            border-radius: 12px;
        }

        .rank-number {
            width: 34px;
            height: 34px;
            color: #00288e;
            font-weight: 800;
            background-color: #e8efff;
            border-radius: 50%;
            display: inline-flex;
            align-items: center;
            justify-content: center;
        }

        .rank-name {
            margin: 11px 0 5px;
            overflow: hidden;
            color: #191c1e;
            font-size: 18px;
            font-weight: 750;
            text-overflow: ellipsis;
            white-space: nowrap;
        }

        .rank-value {
            color: #00288e;
            font-size: 28px;
            font-weight: 790;
        }

        .rank-note {
            color: #5f6368;
            font-size: 13px;
        }

        /* RESPONSIVE */

        @media (max-width: 900px) {
            [data-testid="stSidebar"]
            a[data-testid="stPageLink-NavLink"] {
                min-height: 48px;
                padding: 10px 12px;
            }

            [data-testid="stSidebar"]
            a[data-testid="stPageLink-NavLink"] p {
                font-size: 15px !important;
            }

            .hero-title {
                font-size: 29px;
            }

            .hero-copy {
                font-size: 15px;
            }

            .section-heading {
                align-items: flex-start;
                flex-direction: column;
            }

            .section-heading-copy {
                margin-left: 0;
            }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_page_header(
    icon: str,
    title: str,
    description: str,
) -> None:
    """Menampilkan judul halaman."""

    st.title(f":material/{icon}: {title}")
    st.caption(description)


def render_section_heading(
    icon: str,
    title: str,
    copy: str = "",
) -> None:
    """Menampilkan judul setiap bagian."""

    st.markdown(
        f"### :material/{icon}: {title}"
    )

    if copy:
        st.caption(copy)


def render_kpi_card(
    label: str,
    value: str,
    note: str,
    icon: str,
    accent: str = PRIMARY,
    soft: str = PRIMARY_LIGHT,
) -> None:
    """Menampilkan kartu KPI tanpa HTML bertingkat."""

    safe_label = escape(str(label))
    safe_value = escape(str(value))
    safe_note = escape(str(note))
    safe_accent = escape(str(accent))
    safe_soft = escape(str(soft))

    with st.container(border=True):
        st.markdown(
            f":material/{icon}: **{safe_label}**"
        )

        st.markdown(
            (
                f'<div style="'
                f'color:#191c1e;'
                f'font-size:28px;'
                f'font-weight:780;'
                f'line-height:1.25;'
                f'margin-top:8px;'
                f'margin-bottom:6px;'
                f'overflow:hidden;'
                f'text-overflow:ellipsis;'
                f'white-space:nowrap;'
                f'border-left:4px solid {safe_accent};'
                f'background-color:{safe_soft};'
                f'padding:10px 14px;'
                f'border-radius:8px;'
                f'">'
                f'{safe_value}'
                f'</div>'
            ),
            unsafe_allow_html=True,
        )

        st.caption(safe_note)


def render_info_card(
    icon: str,
    title: str,
    copy: str,
) -> None:
    """Menampilkan kartu informasi dashboard."""

    with st.container(border=True):
        st.markdown(
            f"#### :material/{icon}: {title}"
        )

        st.write(copy)


def render_rank_card(
    rank: int,
    name: str,
    value: int,
    note: str,
) -> None:
    """Menampilkan kartu peringkat petugas."""

    safe_name = escape(str(name))
    safe_note = escape(str(note))

    with st.container(border=True):
        st.markdown(
            f"#### :material/workspace_premium: Peringkat {rank}"
        )

        st.markdown(
            (
                f'<div style="'
                f'color:#191c1e;'
                f'font-size:18px;'
                f'font-weight:750;'
                f'margin-top:6px;'
                f'margin-bottom:8px;'
                f'overflow:hidden;'
                f'text-overflow:ellipsis;'
                f'white-space:nowrap;'
                f'">'
                f'{safe_name}'
                f'</div>'
            ),
            unsafe_allow_html=True,
        )

        st.markdown(
            (
                f'<div style="'
                f'color:#00288e;'
                f'font-size:28px;'
                f'font-weight:790;'
                f'line-height:1.2;'
                f'">'
                f'{value:,}'
                f'</div>'
            ),
            unsafe_allow_html=True,
        )

        st.caption(safe_note)


def _ensure_select_state(
    key: str,
    options: list[object],
    default: object,
) -> None:
    """Menjamin nilai selectbox tersedia pada pilihan."""

    if st.session_state.get(key) not in options:
        st.session_state[key] = default


def _ensure_multi_state(
    key: str,
    options: list[object],
    default: list[object] | None = None,
) -> None:
    """Menjamin nilai multiselect tersedia pada pilihan."""

    current = st.session_state.get(key)

    if current is None:
        st.session_state[key] = default or []
        return

    st.session_state[key] = [
        value
        for value in current
        if value in options
    ]


def render_global_filter_bar(
    df: pd.DataFrame,
) -> None:
    """Menampilkan filter global dashboard."""

    render_section_heading(
        "filter_alt",
        "Filter Data",
        "Pilihan berlaku pada seluruh isi halaman",
    )

    with st.container(border=True):
        years = sorted(
            df["TAHUN"]
            .dropna()
            .astype(int)
            .unique()
            .tolist(),
            reverse=True,
        )

        year_options: list[object] = [
            "Semua Tahun",
            *years,
        ]

        _ensure_select_state(
            "global_year",
            year_options,
            year_options[0],
        )

        col_year, col_month, col_up3 = st.columns(
            [0.8, 1.2, 1]
        )

        with col_year:
            st.selectbox(
                "Tahun",
                year_options,
                key="global_year",
            )

        period_scope = df

        selected_year = st.session_state["global_year"]

        if selected_year != "Semua Tahun":
            period_scope = period_scope[
                period_scope["TAHUN"] == int(selected_year)
            ]

        months = sorted(
            period_scope["BULAN_NUM"]
            .dropna()
            .astype(int)
            .unique()
            .tolist()
        )

        _ensure_multi_state(
            "global_months",
            months,
            months,
        )

        with col_month:
            st.multiselect(
                "Bulan",
                months,
                key="global_months",
                format_func=lambda value: MONTH_NAMES.get(
                    int(value),
                    str(value),
                ),
                placeholder="Semua bulan",
            )

        scope = period_scope

        selected_months = st.session_state.get(
            "global_months",
            [],
        )

        if selected_months:
            scope = scope[
                scope["BULAN_NUM"].isin(selected_months)
            ]

        up3_values = sorted(
            scope["NAMA UP3"]
            .dropna()
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
            up3_options[0],
        )

        with col_up3:
            st.selectbox(
                "Wilayah UP3",
                up3_options,
                key="global_up3",
            )

        selected_up3 = st.session_state["global_up3"]

        if selected_up3 != "Semua UP3":
            scope = scope[
                scope["NAMA UP3"] == selected_up3
            ]

        col_ulp, col_officer = st.columns(2)

        ulp_values = sorted(
            scope["NAMA ULP"]
            .dropna()
            .unique()
            .tolist()
        )

        _ensure_multi_state(
            "global_ulps",
            ulp_values,
        )

        with col_ulp:
            st.multiselect(
                "Unit Layanan (ULP)",
                ulp_values,
                key="global_ulps",
                placeholder="Semua ULP",
            )

        selected_ulps = st.session_state.get(
            "global_ulps",
            [],
        )

        if selected_ulps:
            scope = scope[
                scope["NAMA ULP"].isin(selected_ulps)
            ]

        officer_values = sorted(
            scope["PETUGAS"]
            .dropna()
            .unique()
            .tolist()
        )

        _ensure_multi_state(
            "global_officers",
            officer_values,
        )

        with col_officer:
            st.multiselect(
                "Nama Petugas",
                officer_values,
                key="global_officers",
                placeholder="Semua petugas",
            )


def apply_global_filters(
    df: pd.DataFrame,
) -> pd.DataFrame:
    """Menerapkan filter global pada data."""

    filtered = df.copy()

    year = st.session_state.get(
        "global_year",
        "Semua Tahun",
    )

    if year != "Semua Tahun":
        filtered = filtered[
            filtered["TAHUN"] == int(year)
        ]

    months = st.session_state.get(
        "global_months",
        [],
    )

    if months:
        filtered = filtered[
            filtered["BULAN_NUM"].isin(months)
        ]

    up3 = st.session_state.get(
        "global_up3",
        "Semua UP3",
    )

    if up3 != "Semua UP3":
        filtered = filtered[
            filtered["NAMA UP3"] == up3
        ]

    ulps = st.session_state.get(
        "global_ulps",
        [],
    )

    if ulps:
        filtered = filtered[
            filtered["NAMA ULP"].isin(ulps)
        ]

    officers = st.session_state.get(
        "global_officers",
        [],
    )

    if officers:
        filtered = filtered[
            filtered["PETUGAS"].isin(officers)
        ]

    return filtered


def filter_caption(
    df: pd.DataFrame,
) -> str:
    """Membuat keterangan data setelah filter."""

    if df.empty:
        return "Tidak ada data yang sesuai dengan filter."

    valid_dates = df["TANGGAL_INPUT"].dropna()

    if valid_dates.empty:
        period = "periode tidak diketahui"
    else:
        minimum_date = valid_dates.min()
        maximum_date = valid_dates.max()

        period = (
            f"{minimum_date:%d %b %Y} "
            f"sampai "
            f"{maximum_date:%d %b %Y}"
        )

    total_rows = len(df)
    total_ulp = df["NAMA ULP"].nunique()

    return (
        f"Menampilkan {total_rows:,} gangguan · "
        f"{total_ulp} ULP · "
        f"{period}"
    )


def require_data() -> pd.DataFrame:
    """Menghentikan halaman jika data belum tersedia."""

    data_ready = st.session_state.get(
        "data_ready",
        False,
    )

    raw_data = st.session_state.get(
        "raw_data",
    )

    if not data_ready or raw_data is None:
        st.info(
            "Unggah satu atau beberapa file Excel "
            "melalui bagian Manajemen File di sidebar."
        )
        st.stop()

    return raw_data