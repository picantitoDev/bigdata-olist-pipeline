"""Componentes de visualización reutilizables.

Paleta vibrante de alto contraste sobre modo oscuro, tipografía ampliada
y traducción centralizada de nombres de columnas al español.
"""

import plotly.express as px
import plotly.graph_objects as go

# ------------------------------------------------------------------ Paleta
PRIMARY   = "#00D4FF"   # cian eléctrico
ACCENT    = "#FFC947"   # ámbar
POSITIVE  = "#00E676"   # verde neón
NEGATIVE  = "#FF5252"   # rojo coral
PURPLE    = "#B388FF"

QUALITATIVE = ["#00D4FF", "#FFC947", "#FF5252", "#00E676", "#B388FF",
               "#FF8A65", "#4DD0E1", "#F06292"]

SEQUENTIAL = [[0.0, "#0D2137"], [0.35, "#1B6CA8"], [0.7, "#00D4FF"], [1.0, "#B2F7FF"]]

DARK_LAYOUT = dict(
    template="plotly_dark",
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(color="#F5F7FA", size=14, family="Source Sans Pro, sans-serif"),
    title_font=dict(size=18, color="#FFFFFF"),
    margin=dict(l=10, r=10, t=60, b=10),
    hoverlabel=dict(font_size=13),
    legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(size=12)),
)

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


def _apply(fig, height=420):
    fig.update_layout(**DARK_LAYOUT, height=height)
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

    layout = {
        **DARK_LAYOUT,
        "height": 620,
        "legend": dict(orientation="h", yanchor="bottom", y=0.0, font=dict(size=13)),
        "scene": dict(
            xaxis=dict(title="Recencia (días)", gridcolor="rgba(255,255,255,0.1)",
                       backgroundcolor="rgba(0,0,0,0)"),
            yaxis=dict(title="Frecuencia", gridcolor="rgba(255,255,255,0.1)",
                       backgroundcolor="rgba(0,0,0,0)"),
            zaxis=dict(title="Valor (R$)", gridcolor="rgba(255,255,255,0.1)",
                       backgroundcolor="rgba(0,0,0,0)"),
        ),
    }
    fig.update_layout(**layout)
    return fig
