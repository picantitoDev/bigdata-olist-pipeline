"""Componentes de visualización reutilizables.

Paleta vibrante de alto contraste sobre modo oscuro, tipografía ampliada
y traducción centralizada de nombres de columnas al español.
"""

import plotly.express as px
import plotly.graph_objects as go

# ------------------------------------------------------------------ Paleta
# Paleta única del proyecto: minimalista, violeta como identidad,
# rosa como acento, verde/rojo reservados para semántica (bien/mal).
PRIMARY   = "#7C6FE8"   # violeta — color de marca, series principales
ACCENT    = "#F06292"   # rosa — series secundarias / destacar
POSITIVE  = "#22C55E"   # verde — solo semántica positiva
NEGATIVE  = "#EF4444"   # rojo — solo semántica negativa
NEUTRAL   = "#64748B"   # gris azulado — contexto / referencias
PURPLE    = PRIMARY     # alias retrocompatible

QUALITATIVE = [PRIMARY, ACCENT, "#38BDF8", "#F59E0B", "#22C55E", "#A78BFA"]

SEQUENTIAL = [[0.0, "#211D3D"], [0.5, "#5B4FC4"], [1.0, "#C4BBFF"]]

DARK_LAYOUT = dict(
    template="plotly_dark",
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(color="#F5F7FA", size=14, family="Source Sans Pro, sans-serif"),
    title_font=dict(size=17, color="#FFFFFF"),
    margin=dict(l=10, r=10, t=20, b=10),
    hoverlabel=dict(font_size=13),
    legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(size=12)),
)


def _with_title_margin(layout: dict, title: str) -> dict:
    """Si no hay título, reduce el margen superior — evita hueco vacío."""
    layout = dict(layout)
    if not title:
        layout["margin"] = dict(layout.get("margin", {}), t=15)
    else:
        layout["margin"] = dict(layout.get("margin", {}), t=50)
    return layout

GRID = dict(gridcolor="rgba(255,255,255,0.08)", zerolinecolor="rgba(255,255,255,0.15)")

# ------------------------------------------------------------------ Etiquetas ES
LABELS = {
    "year_month": "Mes",
    "revenue": "Ingresos (R$)",
    "orders": "Órdenes",
    "customer_state": "Estado",
    "revenue_per_order": "Ingreso por orden (R$)",
    "segment": "Segmento",
    "customers": "Clientes",
    "avg_ltv": "LTV promedio (R$)",
    "total_value": "Valor total (R$)",
    "payment_type": "Método de pago",
    "transactions": "Transacciones",
    "avg_installments": "Cuotas promedio",
    "delivery_bucket": "Demora de entrega",
    "reviews": "Reseñas",
    "avg_score": "Score promedio",
    "pct_positive": "% reseñas positivas",
    "delivered_orders": "Órdenes entregadas",
    "avg_delivery_days": "Días de entrega prom.",
    "pct_on_time": "% entregas a tiempo",
    "delivery_days": "Días de entrega",
    "product_category": "Categoría",
    "items_sold": "Unidades vendidas",
    "product_revenue": "Ingresos por productos (R$)",
    "freight_revenue": "Ingresos por flete (R$)",
    "avg_price": "Precio promedio (R$)",
    "avg_weight_kg": "Peso promedio (kg)",
    "avg_freight": "Flete promedio (R$)",
    "items": "Unidades",
    "recency_days": "Recencia (días)",
    "frequency": "Frecuencia (órdenes)",
    "monetary": "Valor monetario (R$)",
    "segment_name": "Segmento",
}


def fmt_money(v: float) -> str:
    """R$ con escala adaptativa: evita '0.0M' en montos chicos."""
    if v >= 1e6:
        return f"R$ {v/1e6:,.1f}M"
    if v >= 1e3:
        return f"R$ {v/1e3:,.0f}K"
    return f"R$ {v:,.2f}"


def _apply(fig, height=420):
    title_text = (fig.layout.title.text or "") if fig.layout.title else ""
    layout = _with_title_margin(DARK_LAYOUT, title_text)
    fig.update_layout(**layout, height=height)
    fig.update_xaxes(**GRID)
    fig.update_yaxes(**GRID)
    return fig


# ------------------------------------------------------------------ Charts

def line_chart(df, x, y, title, y_label=None):
    fig = px.line(df, x=x, y=y, title=title, markers=True, labels=LABELS)
    fig.update_traces(
        line=dict(color=PRIMARY, width=3),
        marker=dict(color=ACCENT, size=7, line=dict(color=PRIMARY, width=1)),
    )
    if y_label:
        fig.update_yaxes(title_text=y_label)
    return _apply(fig)


def bar_chart(df, x, y, title, color=None, horizontal=False):
    fig = px.bar(
        df, x=x, y=y, title=title, labels=LABELS,
        orientation="h" if horizontal else "v",
        color=color,
        color_continuous_scale=SEQUENTIAL if color else None,
        text_auto=".2s" if not horizontal else False,
    )
    if not color:
        fig.update_traces(marker_color=PRIMARY)
    fig.update_traces(
        textfont_size=12, textposition="outside", cliponaxis=False,
        marker_line=dict(width=0),
    )
    if horizontal:
        fig.update_layout(yaxis=dict(dtick=1))
    fig.update_coloraxes(colorbar=dict(title=None, thickness=12))
    return _apply(fig, height=460 if horizontal else 420)


def scatter_chart(df, x, y, size, hover, title, x_label=None, y_label=None):
    fig = px.scatter(
        df, x=x, y=y, size=size, hover_name=hover, title=title, labels=LABELS,
        color=y, color_continuous_scale=SEQUENTIAL, size_max=45,
    )
    fig.update_traces(marker=dict(line=dict(color="rgba(255,255,255,0.3)", width=1)))
    if x_label:
        fig.update_xaxes(title_text=x_label)
    if y_label:
        fig.update_yaxes(title_text=y_label)
    fig.update_coloraxes(showscale=False)
    return _apply(fig, height=480)


def pie_chart(df, names, values, title):
    fig = px.pie(
        df, names=names, values=values, title=title, hole=0.5,
        labels=LABELS, color_discrete_sequence=QUALITATIVE,
    )
    fig.update_traces(
        textinfo="percent+label", textfont_size=13,
        marker=dict(line=dict(color="#0E1117", width=2)),
        pull=[0.03] * len(df),
    )
    fig.update_layout(showlegend=False)
    return _apply(fig)


def histogram(df, x, y, title, x_label=None):
    fig = go.Figure(go.Bar(
        x=df[x], y=df[y],
        marker=dict(color=df[y], colorscale=SEQUENTIAL, line=dict(width=0)),
    ))
    fig.update_layout(
        title=title,
        xaxis_title=x_label or LABELS.get(x, x),
        yaxis_title="Órdenes",
        bargap=0.08,
    )
    return _apply(fig)


def segment_scatter_3d(df, title):
    """Scatter 3D para visualizar clusters RFM."""
    fig = px.scatter_3d(
        df,
        x="recency_days", y="frequency", z="monetary",
        color="segment_name", title=title, labels=LABELS,
        opacity=0.65, color_discrete_sequence=QUALITATIVE,
    )
    fig.update_traces(marker=dict(size=3))
    fig.update_layout(
        **DARK_LAYOUT, height=620,
        scene=dict(
            xaxis=dict(title="Recencia (días)", gridcolor="rgba(255,255,255,0.1)",
                       backgroundcolor="rgba(0,0,0,0)"),
            yaxis=dict(title="Frecuencia", gridcolor="rgba(255,255,255,0.1)",
                       backgroundcolor="rgba(0,0,0,0)"),
            zaxis=dict(title="Valor (R$)", gridcolor="rgba(255,255,255,0.1)",
                       backgroundcolor="rgba(0,0,0,0)"),
        ),
        legend=dict(orientation="h", yanchor="bottom", y=0.0, font=dict(size=13)),
    )
    return fig


# ==================================================================
# COMPONENTES ADICIONALES (refactor visual)
# ==================================================================

from plotly.subplots import make_subplots


def _merged_layout(**overrides):
    return {**DARK_LAYOUT, **overrides}


def donut(labels, values, title, colors=None, center_text=None):
    fig = go.Figure(go.Pie(
        labels=labels, values=values, hole=0.62,
        marker=dict(colors=colors or [PRIMARY, NEGATIVE],
                    line=dict(color="#0E1117", width=2)),
        textinfo="label+percent", textfont_size=13,
    ))
    if center_text:
        fig.add_annotation(text=center_text, showarrow=False,
                           font=dict(size=22, color="#FFFFFF"))
    fig.update_layout(**_merged_layout(
        **_with_title_margin({}, title), title=title, height=380, showlegend=False,
    ))
    return fig


def ranking_hbar(df, x, y, title, pct_col=None, color=PRIMARY, height=None):
    """Ranking horizontal: barras un solo tono + valor y % como texto."""
    d = df.sort_values(x)
    text = d[x].apply(lambda v: f"{v:,.0f}")
    if pct_col is not None:
        text = text + "  ·  " + d[pct_col].apply(lambda v: f"{v:.1f}%")
    fig = go.Figure(go.Bar(
        x=d[x], y=d[y], orientation="h",
        marker=dict(color=color, line=dict(width=0)),
        text=text, textposition="outside", cliponaxis=False,
        textfont=dict(size=12),
    ))
    top_margin = 50 if title else 15
    fig.update_layout(**_merged_layout(
        title=title,
        height=height or max(320, 34 * len(d) + 90),
        xaxis=dict(**GRID, title=LABELS.get(x, x)),
        yaxis=dict(dtick=1, title=None),
        margin=dict(l=10, r=90, t=top_margin, b=10),
    ))
    return fig


def dual_line(df, x, y1, y2, title, y1_label, y2_label):
    """Dos series con ejes independientes (ej. % tardías vs días)."""
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    fig.add_trace(go.Scatter(
        x=df[x], y=df[y1], name=y1_label, mode="lines+markers",
        line=dict(color=NEGATIVE, width=3), marker=dict(size=6),
    ), secondary_y=False)
    fig.add_trace(go.Scatter(
        x=df[x], y=df[y2], name=y2_label, mode="lines+markers",
        line=dict(color=PRIMARY, width=2, dash="dot"), marker=dict(size=5),
    ), secondary_y=True)
    top_margin = 70 if title else 45
    fig.update_layout(**_merged_layout(
        title=title, height=400,
        margin=dict(l=10, r=10, t=top_margin, b=10),
        legend=dict(orientation="h", yanchor="bottom", y=1.02,
                    bgcolor="rgba(0,0,0,0)"),
    ))
    fig.update_yaxes(title_text=y1_label, secondary_y=False, **GRID)
    fig.update_yaxes(title_text=y2_label, secondary_y=True,
                     gridcolor="rgba(0,0,0,0)")
    fig.update_xaxes(**GRID)
    return fig


def diverging_hbar(df, x, y, title, x_label):
    """Barras divergentes: positivo = sobrecosto (rojo), negativo = eficiente (cian)."""
    d = df.sort_values(x)
    colors = [NEGATIVE if v > 0 else PRIMARY for v in d[x]]
    fig = go.Figure(go.Bar(
        x=d[x], y=d[y], orientation="h",
        marker=dict(color=colors, line=dict(width=0)),
        text=d[x].apply(lambda v: f"{v:+.1f}%"),
        textposition="outside", cliponaxis=False, textfont=dict(size=12),
    ))
    fig.add_vline(x=0, line_color="rgba(255,255,255,0.35)", line_width=1)
    top_margin = 50 if title else 15
    fig.update_layout(**_merged_layout(
        title=title, height=max(340, 36 * len(d) + 90),
        xaxis=dict(**GRID, title=x_label, ticksuffix="%"),
        yaxis=dict(dtick=1, title=None),
        margin=dict(l=10, r=70, t=top_margin, b=10),
    ))
    return fig


def stacked_hbar(df, y, cols, names, title, colors, x_label):
    """Barras horizontales apiladas (ej. días vendedor vs tránsito)."""
    fig = go.Figure()
    for col, name, color in zip(cols, names, colors):
        fig.add_trace(go.Bar(
            x=df[col], y=df[y], orientation="h", name=name,
            marker=dict(color=color, line=dict(width=0)),
        ))
    fig.update_layout(**_merged_layout(
        title=title, barmode="stack",
        height=max(360, 36 * len(df) + 130),
        margin=dict(l=10, r=10, t=70, b=10),
        xaxis=dict(**GRID, title=x_label),
        yaxis=dict(dtick=1, title=None, autorange="reversed"),
        legend=dict(orientation="h", yanchor="bottom", y=1.06,
                    xanchor="left", x=0, bgcolor="rgba(0,0,0,0)"),
    ))
    return fig
