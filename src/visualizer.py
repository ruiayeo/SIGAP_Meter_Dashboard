"""Seluruh visualisasi Plotly dashboard monitoring gangguan."""

from __future__ import annotations

import pandas as pd
import plotly.graph_objects as go


PRIMARY = "#00288e"
BLUE = "#2f65d9"
CYAN = "#00a7b5"
GREEN = "#087f5b"
ORANGE = "#e07800"
RED = "#ba1a1a"
PURPLE = "#7357b8"
TEXT = "#191c1e"
MUTED = "#5f6368"
GRID = "#e7eaf0"
PALETTE = [PRIMARY, CYAN, ORANGE, PURPLE, GREEN, RED, "#5470c6", "#91cc75"]


def _base_layout(fig: go.Figure, height: int = 410, legend: bool = True) -> go.Figure:
    fig.update_layout(
        height=height,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="#ffffff",
        font=dict(family="Arial, sans-serif", color=TEXT, size=14),
        title_font=dict(size=18, color=TEXT),
        margin=dict(l=24, r=24, t=64, b=42),
        hoverlabel=dict(bgcolor="#ffffff", font_color=TEXT, font_size=14),
        legend=dict(
            orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1,
            font=dict(size=13, color=MUTED),
        ),
        showlegend=legend,
    )
    fig.update_xaxes(
        showgrid=True,
        gridcolor=GRID,
        zeroline=False,
        title_font=dict(color=MUTED, size=14),
        tickfont=dict(size=13),
    )
    fig.update_yaxes(
        showgrid=False,
        zeroline=False,
        title_font=dict(color=MUTED, size=14),
        tickfont=dict(size=13),
    )
    return fig


def empty_figure(message: str = "Data tidak tersedia") -> go.Figure:
    fig = go.Figure()
    fig.add_annotation(text=message, x=0.5, y=0.5, showarrow=False, font=dict(color=MUTED, size=14))
    fig.update_xaxes(visible=False)
    fig.update_yaxes(visible=False)
    return _base_layout(fig, height=370, legend=False)


def plot_monthly_trend(df: pd.DataFrame) -> go.Figure:
    valid = df.dropna(subset=["PERIODE"])
    if valid.empty:
        return empty_figure("Tanggal input tidak tersedia")

    total = valid.groupby("PERIODE").size().rename("Total").reset_index()
    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=total["PERIODE"], y=total["Total"], name="Total UP3",
            mode="lines+markers+text", text=total["Total"], textposition="top center",
            line=dict(color=PRIMARY, width=4), marker=dict(size=9),
            hovertemplate="%{x|%b %Y}<br>Total UP3: %{y:,}<extra></extra>",
        )
    )
    for index, (ulp, group) in enumerate(valid.groupby("NAMA ULP")):
        series = group.groupby("PERIODE").size().reindex(total["PERIODE"], fill_value=0)
        fig.add_trace(
            go.Scatter(
                x=total["PERIODE"], y=series.values, name=str(ulp), mode="lines+markers",
                line=dict(color=PALETTE[(index + 1) % len(PALETTE)], width=2, dash="dot"),
                marker=dict(size=6),
                hovertemplate=f"%{{x|%b %Y}}<br>{ulp}: %{{y:,}}<extra></extra>",
            )
        )
    fig.update_layout(title="Tren Gangguan Bulanan", hovermode="x unified")
    fig.update_xaxes(tickformat="%b\n%Y", title="Periode")
    fig.update_yaxes(title="Jumlah Gangguan", rangemode="tozero")
    return _base_layout(fig, height=460, legend=True)


def plot_top_categories(
    df: pd.DataFrame,
    column: str,
    title: str,
    top_n: int = 5,
    color: str = PRIMARY,
) -> go.Figure:
    if df.empty or column not in df.columns:
        return empty_figure()
    counts = df[column].dropna().astype(str).value_counts().head(top_n).sort_values()
    if counts.empty:
        return empty_figure()
    fig = go.Figure(
        go.Bar(
            x=counts.values, y=counts.index, orientation="h",
            marker=dict(color=color, line=dict(width=0)),
            text=counts.values, textposition="outside", cliponaxis=False,
            hovertemplate="%{y}<br>%{x:,} gangguan<extra></extra>",
        )
    )
    fig.update_layout(title=title)
    fig.update_xaxes(title="Jumlah Gangguan", rangemode="tozero")
    fig.update_yaxes(title="", automargin=True)
    return _base_layout(fig, height=max(380, 64 * len(counts)), legend=False)


def plot_ulp_comparison(df: pd.DataFrame) -> go.Figure:
    if df.empty:
        return empty_figure()
    counts = df["NAMA ULP"].value_counts().sort_values(ascending=False)
    fig = go.Figure(
        go.Bar(
            x=counts.index, y=counts.values,
            marker=dict(color=counts.values, colorscale=[[0, "#b9ccff"], [1, PRIMARY]], showscale=False),
            text=counts.values, textposition="outside",
            hovertemplate="%{x}<br>%{y:,} gangguan<extra></extra>",
        )
    )
    fig.update_layout(title="Perbandingan Total Gangguan Antar ULP")
    fig.update_xaxes(title="ULP")
    fig.update_yaxes(title="Jumlah Gangguan", rangemode="tozero")
    return _base_layout(fig, height=390, legend=False)


def plot_distribution_by_ulp(
    df: pd.DataFrame,
    category: str,
    title: str,
    colors: list[str] | None = None,
) -> go.Figure:
    if df.empty:
        return empty_figure()
    pivot = pd.crosstab(df["NAMA ULP"], df[category])
    if pivot.empty:
        return empty_figure()
    fig = go.Figure()
    chart_colors = colors or PALETTE
    for index, value in enumerate(pivot.columns):
        fig.add_trace(
            go.Bar(
                x=pivot.index, y=pivot[value], name=str(value),
                marker_color=chart_colors[index % len(chart_colors)],
                hovertemplate=f"%{{x}}<br>{value}: %{{y:,}}<extra></extra>",
            )
        )
    fig.update_layout(title=title, barmode="stack")
    fig.update_xaxes(title="ULP")
    fig.update_yaxes(title="Jumlah Gangguan", rangemode="tozero")
    return _base_layout(fig, height=400, legend=True)


def plot_brand_cause_heatmap(df: pd.DataFrame, top_brands: int = 10, top_causes: int = 10) -> go.Figure:
    if df.empty:
        return empty_figure()
    brands = df["MERK"].value_counts().head(top_brands).index
    causes = df["PENYEBAB KERUSAKAN"].value_counts().head(top_causes).index
    scope = df[df["MERK"].isin(brands) & df["PENYEBAB KERUSAKAN"].isin(causes)]
    matrix = pd.crosstab(scope["PENYEBAB KERUSAKAN"], scope["MERK"]).reindex(index=causes, columns=brands, fill_value=0)
    if matrix.empty:
        return empty_figure()
    fig = go.Figure(
        go.Heatmap(
            z=matrix.values, x=matrix.columns, y=matrix.index,
            colorscale=[[0, "#f1f5ff"], [0.35, "#88a9ef"], [1, PRIMARY]],
            colorbar=dict(title="Jumlah"),
            hovertemplate="Merek: %{x}<br>Kerusakan: %{y}<br>Jumlah: %{z:,}<extra></extra>",
        )
    )
    fig.update_layout(title="Pola Kerusakan Menurut Merek kWh")
    fig.update_xaxes(title="Merek kWh", side="top")
    fig.update_yaxes(title="", autorange="reversed", automargin=True)
    return _base_layout(fig, height=max(460, 36 * len(matrix)), legend=False)


def plot_officer_leaderboard(summary: pd.DataFrame, top_n: int = 20) -> go.Figure:
    if summary.empty:
        return empty_figure()
    data = summary.head(top_n).sort_values("Total Gangguan")
    colors = [PRIMARY if rank <= 3 else "#7d9de2" for rank in data["Peringkat"]]
    fig = go.Figure(
        go.Bar(
            x=data["Total Gangguan"], y=data["Petugas"], orientation="h",
            marker_color=colors, text=data["Total Gangguan"], textposition="outside",
            customdata=data[["Peringkat", "Kontribusi (%)", "ULP Dominan"]],
            hovertemplate="Peringkat #%{customdata[0]}<br>%{y}<br>%{x:,} laporan<br>Kontribusi %{customdata[1]}%<br>ULP dominan: %{customdata[2]}<extra></extra>",
            cliponaxis=False,
        )
    )
    fig.update_layout(title=f"{min(top_n, len(summary))} Petugas dengan Input Terbanyak")
    fig.update_xaxes(title="Jumlah Laporan", rangemode="tozero")
    fig.update_yaxes(title="", automargin=True)
    return _base_layout(fig, height=max(420, 31 * len(data)), legend=False)


def plot_daily_trend(df: pd.DataFrame, title: str = "Tren Input Harian") -> go.Figure:
    valid = df.dropna(subset=["TANGGAL_INPUT"])
    if valid.empty:
        return empty_figure()
    counts = valid.groupby("TANGGAL_INPUT").size().rename("Total").reset_index()
    fig = go.Figure(
        go.Scatter(
            x=counts["TANGGAL_INPUT"], y=counts["Total"], mode="lines+markers",
            line=dict(color=PRIMARY, width=3), marker=dict(size=7),
            fill="tozeroy", fillcolor="rgba(0,40,142,.08)",
            hovertemplate="%{x|%d %b %Y}<br>%{y:,} laporan<extra></extra>",
        )
    )
    fig.update_layout(title=title)
    fig.update_xaxes(title="Tanggal", tickformat="%d %b")
    fig.update_yaxes(title="Jumlah Laporan", rangemode="tozero")
    return _base_layout(fig, height=370, legend=False)


def plot_process_donut(df: pd.DataFrame) -> go.Figure:
    if df.empty:
        return empty_figure()
    counts = df["STATUS PROSES"].value_counts()
    fig = go.Figure(
        go.Pie(
            labels=counts.index, values=counts.values, hole=0.58,
            marker=dict(colors=PALETTE), textinfo="percent+label", textposition="outside",
            hovertemplate="%{label}<br>%{value:,} laporan (%{percent})<extra></extra>",
        )
    )
    fig.update_layout(title="Perbandingan Status Proses")
    return _base_layout(fig, height=390, legend=False)
