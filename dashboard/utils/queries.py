"""Queries SQL centralizadas. Toda la agregación ocurre en BigQuery,
no en pandas — el warehouse hace el trabajo pesado (escalabilidad)."""

MARTS = "big-data-495719.olist_marts"

# ------------------------------------------------------------------
# Executive Summary
# ------------------------------------------------------------------

KPIS_GLOBALES = f"""
with por_cliente as (
    select c.customer_unique_id, count(distinct f.order_id) as n_orders
    from `{MARTS}.fct_order_items` f
    join `{MARTS}.dim_customers` c on f.customer_key = c.customer_key
    group by 1
)
select
    count(distinct f.order_id)                    as total_orders,
    round(sum(f.total_item_value), 2)             as total_revenue,
    round(sum(f.total_item_value)
        / count(distinct f.order_id), 2)          as avg_order_value,
    count(distinct f.customer_key)                as total_customers,
    (select round(100 * countif(n_orders >= 2) / count(*), 1)
     from por_cliente)                             as tasa_recompra
from `{MARTS}.fct_order_items` f
"""

NPS_APROXIMADO = f"""
select
    round(100 * countif(review_score >= 4) / count(*), 1) as pct_positive,
    round(avg(review_score), 2)                            as avg_score
from `{MARTS}.fct_order_reviews`
"""

REVENUE_MENSUAL = f"""
select
    d.year,
    d.month,
    format_date('%Y-%m', f.order_date_key)   as year_month,
    round(sum(f.total_item_value), 2)        as revenue,
    count(distinct f.order_id)               as orders
from `{MARTS}.fct_order_items` f
join `{MARTS}.dim_dates` d on f.order_date_key = d.date_key
group by 1, 2, 3
order by 1, 2
"""

ESTADO_CRECIMIENTO_ALERTAS = f"""
-- Ingresos por estado + % de entregas tardías, para la vista de
-- "estado general" con alertas en el resumen ejecutivo.
with base as (
    select
        c.customer_state                                   as estado,
        f.order_id,
        f.total_item_value,
        o.is_delivered_on_time
    from `{MARTS}.fct_order_items` f
    join `{MARTS}.dim_customers` c on f.customer_key = c.customer_key
    join `{MARTS}.dim_orders`    o on f.order_key    = o.order_key
    where o.delivery_days is not null
)
select
    estado,
    round(sum(total_item_value), 2)                              as ingresos,
    count(distinct order_id)                                     as ordenes,
    round(100 * countif(not is_delivered_on_time) / count(*), 1) as pct_tardias
from base
group by 1
having count(distinct order_id) > 100
order by ingresos desc
"""

# ------------------------------------------------------------------
# Ventas y Clientes
# ------------------------------------------------------------------

REVENUE_POR_ESTADO = f"""
select
    c.customer_state,
    count(distinct f.order_id)            as orders,
    round(sum(f.total_item_value), 2)     as revenue,
    round(sum(f.total_item_value)
        / count(distinct f.order_id), 2)  as revenue_per_order
from `{MARTS}.fct_order_items` f
join `{MARTS}.dim_customers` c on f.customer_key = c.customer_key
group by 1
order by revenue desc
"""

RETENCION_CLIENTES = f"""
with customer_orders as (
    select
        c.customer_unique_id,
        count(distinct f.order_id)        as order_count,
        round(sum(f.total_item_value), 2) as lifetime_value
    from `{MARTS}.fct_order_items` f
    join `{MARTS}.dim_customers` c on f.customer_key = c.customer_key
    group by 1
)
select
    case when order_count = 1 then 'Una compra' else 'Recurrente (2+)' end as segment,
    count(*)                       as customers,
    round(avg(lifetime_value), 2)  as avg_ltv,
    round(sum(lifetime_value), 2)  as total_value
from customer_orders
group by 1
"""

METODOS_PAGO = f"""
select
    payment_type,
    count(*)                          as transactions,
    round(sum(payment_value), 2)      as total_value,
    round(avg(payment_installments), 1) as avg_installments
from `{MARTS}.fct_payments`
group by 1
order by total_value desc
"""

# ------------------------------------------------------------------
# Logística
# ------------------------------------------------------------------

DELIVERY_VS_SATISFACCION = f"""
select
    case
        when o.delivery_vs_estimate_days <= 0  then '1. A tiempo o antes'
        when o.delivery_vs_estimate_days <= 5  then '2. 1-5 dias tarde'
        when o.delivery_vs_estimate_days <= 15 then '3. 6-15 dias tarde'
        else '4. Mas de 15 dias tarde'
    end                                        as delivery_bucket,
    count(*)                                   as reviews,
    round(avg(r.review_score), 2)              as avg_score,
    round(100 * countif(r.is_positive_review) / count(*), 1) as pct_positive
from `{MARTS}.fct_order_reviews` r
join `{MARTS}.dim_orders` o on r.order_key = o.order_key
where o.delivery_vs_estimate_days is not null
group by 1
order by 1
"""

ONTIME_POR_ESTADO = f"""
select
    c.customer_state,
    count(*)                                              as delivered_orders,
    round(avg(o.delivery_days), 1)                        as avg_delivery_days,
    round(100 * countif(o.is_delivered_on_time) / count(*), 1) as pct_on_time
from `{MARTS}.fct_order_items` f
join `{MARTS}.dim_orders`    o on f.order_key    = o.order_key
join `{MARTS}.dim_customers` c on f.customer_key = c.customer_key
where o.delivery_days is not null
group by 1
having count(*) > 100
order by pct_on_time desc
"""

DISTRIBUCION_DELIVERY = f"""
select
    delivery_days,
    count(*) as orders
from `{MARTS}.dim_orders`
where delivery_days is not null and delivery_days between 0 and 60
group by 1
order by 1
"""

# ------------------------------------------------------------------
# Productos
# ------------------------------------------------------------------

TOP_CATEGORIAS = f"""
select
    p.product_category,
    count(*)                          as items_sold,
    round(sum(f.price), 2)            as product_revenue,
    round(sum(f.freight_value), 2)    as freight_revenue,
    round(avg(f.price), 2)            as avg_price
from `{MARTS}.fct_order_items` f
join `{MARTS}.dim_products` p on f.product_key = p.product_key
where p.product_category is not null
group by 1
order by product_revenue desc
limit 20
"""

FREIGHT_VS_PESO = f"""
select
    p.product_category,
    round(avg(p.product_weight_g) / 1000, 2)  as avg_weight_kg,
    round(avg(f.freight_value), 2)            as avg_freight,
    count(*)                                  as items
from `{MARTS}.fct_order_items` f
join `{MARTS}.dim_products` p on f.product_key = p.product_key
where p.product_weight_g is not null and p.product_category is not null
group by 1
having count(*) > 500
order by avg_freight desc
"""

# ------------------------------------------------------------------
# Segmentación IA (RFM)
# ------------------------------------------------------------------

RFM_BASE = f"""
with max_date as (
    select max(order_date_key) as anchor from `{MARTS}.fct_order_items`
)
select
    c.customer_unique_id,
    date_diff((select anchor from max_date), max(f.order_date_key), day) as recency_days,
    count(distinct f.order_id)                                           as frequency,
    round(sum(f.total_item_value), 2)                                    as monetary
from `{MARTS}.fct_order_items` f
join `{MARTS}.dim_customers` c on f.customer_key = c.customer_key
group by 1
"""


# ==================================================================
# QUERIES PARAMETRIZADAS (filtros globales: fechas + estados)
# ==================================================================

def _fstates(states: tuple) -> str:
    if not states:
        return ""
    vals = ",".join(f"'{s}'" for s in states)
    return f" and c.customer_state in ({vals})"


def _fdates(dates: tuple, col: str = "f.order_date_key") -> str:
    return f"{col} between '{dates[0]}' and '{dates[1]}'"


def q_kpis_ventas(dates, states):
    return f"""
    with base as (
        select f.order_id, f.total_item_value, c.customer_unique_id
        from `{MARTS}.fct_order_items` f
        join `{MARTS}.dim_customers` c on f.customer_key = c.customer_key
        where {_fdates(dates)}{_fstates(states)}
    ),
    por_cliente as (
        select customer_unique_id, count(distinct order_id) as n_orders
        from base group by 1
    )
    select
        round(sum(b.total_item_value), 2)                     as ingresos,
        count(distinct b.order_id)                            as ordenes,
        count(distinct b.customer_unique_id)                  as clientes,
        round(sum(b.total_item_value)
            / count(distinct b.order_id), 2)                  as ticket_promedio,
        round(count(distinct b.order_id)
            / count(distinct b.customer_unique_id), 2)        as ordenes_por_cliente,
        round(100 * (select countif(n_orders >= 2) from por_cliente)
            / (select count(*) from por_cliente), 1)          as tasa_retencion
    from base b
    """


def q_ingresos_estado(dates, states):
    return f"""
    select
        c.customer_state as estado,
        round(sum(f.total_item_value), 2) as ingresos,
        round(sum(f.total_item_value)
            / count(distinct f.order_id), 2) as ticket_por_orden
    from `{MARTS}.fct_order_items` f
    join `{MARTS}.dim_customers` c on f.customer_key = c.customer_key
    where {_fdates(dates)}{_fstates(states)}
    group by 1 order by ingresos desc
    """


def q_evolucion(dates, states):
    return f"""
    select
        format_date('%Y-%m', f.order_date_key) as mes,
        round(sum(f.total_item_value), 2)      as ingresos,
        count(distinct f.order_id)             as ordenes
    from `{MARTS}.fct_order_items` f
    join `{MARTS}.dim_customers` c on f.customer_key = c.customer_key
    where {_fdates(dates)}{_fstates(states)}
    group by 1 order by 1
    """


def q_top_categorias(dates, states, limit=5):
    return f"""
    select
        p.product_category                 as categoria,
        round(sum(f.total_item_value), 2)  as ingresos
    from `{MARTS}.fct_order_items` f
    join `{MARTS}.dim_customers` c on f.customer_key = c.customer_key
    join `{MARTS}.dim_products`  p on f.product_key  = p.product_key
    where {_fdates(dates)}{_fstates(states)} and p.product_category is not null
    group by 1 order by ingresos desc limit {limit}
    """


def q_metodos_pago(dates, states):
    return f"""
    select
        pay.payment_type                     as metodo,
        round(sum(pay.payment_value), 2)     as valor,
        round(avg(pay.payment_installments), 1) as cuotas_prom
    from `{MARTS}.fct_payments` pay
    join `{MARTS}.dim_customers` c on pay.customer_key = c.customer_key
    where pay.order_date_key between '{dates[0]}' and '{dates[1]}'{_fstates(states)}
    group by 1 order by valor desc
    """


def q_una_compra(dates, states):
    return f"""
    with por_cliente as (
        select c.customer_unique_id,
               count(distinct f.order_id)        as n_orders,
               sum(f.total_item_value)           as ltv
        from `{MARTS}.fct_order_items` f
        join `{MARTS}.dim_customers` c on f.customer_key = c.customer_key
        where {_fdates(dates)}{_fstates(states)}
        group by 1
    )
    select
        round(100 * countif(n_orders = 1) / count(*), 1) as pct_una_compra,
        round(avg(if(n_orders = 1, ltv, null)), 2)       as ltv_una,
        round(avg(if(n_orders >= 2, ltv, null)), 2)      as ltv_recurrente
    from por_cliente
    """


# ------------------------------------------------------------------ Logística

def q_kpis_logistica(dates, states):
    return f"""
    with base as (
        select distinct f.order_id, f.order_key, f.customer_key,
               o.delivery_days, o.delivery_vs_estimate_days, o.is_delivered_on_time
        from `{MARTS}.fct_order_items` f
        join `{MARTS}.dim_orders`    o on f.order_key    = o.order_key
        join `{MARTS}.dim_customers` c on f.customer_key = c.customer_key
        where {_fdates(dates)}{_fstates(states)} and o.delivery_days is not null
    ),
    rev as (
        select o2.order_key, sum(f2.total_item_value) as order_value
        from `{MARTS}.fct_order_items` f2
        join `{MARTS}.dim_orders` o2 on f2.order_key = o2.order_key
        group by 1
    ),
    scores as (
        select o3.order_key, r.review_score, o3.delivery_vs_estimate_days
        from `{MARTS}.fct_order_reviews` r
        join `{MARTS}.dim_orders` o3 on r.order_key = o3.order_key
    )
    select
        round(100 * countif(b.is_delivered_on_time) / count(*), 1)      as pct_a_tiempo,
        round(avg(b.delivery_days), 1)                                   as dias_entrega_prom,
        round(avg(if(not b.is_delivered_on_time,
                     b.delivery_vs_estimate_days, null)), 1)             as retraso_prom,
        (select round(avg(review_score), 2) from scores
         where delivery_vs_estimate_days <= 0)                           as score_a_tiempo,
        (select round(avg(review_score), 2) from scores
         where delivery_vs_estimate_days > 15)                           as score_muy_tarde,
        round(sum(if(not b.is_delivered_on_time, r.order_value, 0)), 0)  as ingresos_tardias,
        round(100 * countif(not b.is_delivered_on_time) / count(*), 1)   as pct_tardias
    from base b
    join rev r on b.order_key = r.order_key
    """


def q_retraso_estado(dates, states):
    return f"""
    select
        c.customer_state                                              as estado,
        count(distinct f.order_id)                                    as ordenes,
        round(100 * countif(not o.is_delivered_on_time)
            / count(*), 1)                                            as pct_tardias
    from `{MARTS}.fct_order_items` f
    join `{MARTS}.dim_orders`    o on f.order_key    = o.order_key
    join `{MARTS}.dim_customers` c on f.customer_key = c.customer_key
    where {_fdates(dates)}{_fstates(states)} and o.delivery_days is not null
    group by 1 having count(distinct f.order_id) > 100
    order by pct_tardias desc
    """


def q_retraso_mensual(dates, states):
    return f"""
    select
        format_date('%Y-%m', f.order_date_key)                       as mes,
        round(100 * countif(not o.is_delivered_on_time)
            / count(*), 1)                                           as pct_tardias,
        round(avg(o.delivery_days), 1)                               as dias_prom
    from `{MARTS}.fct_order_items` f
    join `{MARTS}.dim_orders`    o on f.order_key    = o.order_key
    join `{MARTS}.dim_customers` c on f.customer_key = c.customer_key
    where {_fdates(dates)}{_fstates(states)} and o.delivery_days is not null
    group by 1 order by 1
    """


def q_score_por_retraso(dates, states):
    return f"""
    select
        case
            when o.delivery_vs_estimate_days <= 0  then 'A tiempo'
            when o.delivery_vs_estimate_days <= 5  then '1-5 días'
            when o.delivery_vs_estimate_days <= 15 then '6-15 días'
            else '+15 días'
        end                                as tramo,
        round(avg(r.review_score), 2)      as score_prom,
        count(*)                           as resenas
    from `{MARTS}.fct_order_reviews` r
    join `{MARTS}.dim_orders`    o on r.order_key    = o.order_key
    join `{MARTS}.dim_customers` c on r.customer_key = c.customer_key
    where r.order_date_key between '{dates[0]}' and '{dates[1]}'{_fstates(states)}
      and o.delivery_vs_estimate_days is not null
    group by 1
    order by min(o.delivery_vs_estimate_days)
    """


def q_seller_vs_transito(dates, states):
    return f"""
    select
        c.customer_state as estado,
        round(avg({{dd_prep}}), 1)    as dias_vendedor,
        round(avg({{dd_trans}}), 1)   as dias_transito,
        round(100 * countif(not o.is_delivered_on_time) / count(*), 1) as pct_tardias
    from `{MARTS}.fct_order_items` f
    join `{MARTS}.dim_orders`    o on f.order_key    = o.order_key
    join `{MARTS}.dim_customers` c on f.customer_key = c.customer_key
    where {_fdates(dates)}{_fstates(states)}
      and o.order_approved_at is not null
      and o.order_delivered_carrier_date is not null
      and o.order_delivered_customer_date is not null
    group by 1 having count(distinct f.order_id) > 100
    order by pct_tardias desc limit 8
    """.replace(
        "{dd_prep}",
        "date_diff(date(o.order_delivered_carrier_date), date(o.order_approved_at), day)"
    ).replace(
        "{dd_trans}",
        "date_diff(date(o.order_delivered_customer_date), date(o.order_delivered_carrier_date), day)"
    )


# ------------------------------------------------------------------ Productos

def q_kpis_productos(dates, states):
    return f"""
    with base as (
        select f.total_item_value, f.price, f.freight_value,
               p.product_id, p.product_category,
               p.product_weight_g, p.product_volume_cm3
        from `{MARTS}.fct_order_items` f
        join `{MARTS}.dim_customers` c on f.customer_key = c.customer_key
        join `{MARTS}.dim_products`  p on f.product_key  = p.product_key
        where {_fdates(dates)}{_fstates(states)}
    )
    select
        round(sum(total_item_value), 2)                       as ingreso_catalogo,
        count(*)                                              as unidades,
        count(distinct product_category)                      as categorias,
        count(distinct product_id)                            as skus,
        round(100 * sum(freight_value) / sum(price), 1)       as flete_sobre_ingreso,
        count(distinct if(product_weight_g is null
              or product_volume_cm3 is null, product_id, null)) as skus_sin_dimensiones
    from base
    """


def q_categoria_ranking(dates, states, limit=15):
    return f"""
    select
        p.product_category                as categoria,
        round(sum(f.total_item_value), 2) as ingresos,
        count(*)                          as unidades,
        round(avg(f.price), 2)            as ticket_prom
    from `{MARTS}.fct_order_items` f
    join `{MARTS}.dim_customers` c on f.customer_key = c.customer_key
    join `{MARTS}.dim_products`  p on f.product_key  = p.product_key
    where {_fdates(dates)}{_fstates(states)} and p.product_category is not null
    group by 1 order by ingresos desc limit {limit}
    """


def q_flete_eficiencia(dates, states):
    """Costo por kilo facturable vs media global. Kilo facturable =
    max(peso real, peso volumétrico cm3/6000) — estándar courier."""
    return f"""
    with base as (
        select
            p.product_category as categoria,
            f.freight_value,
            greatest(p.product_weight_g / 1000.0,
                     p.product_volume_cm3 / 6000.0) as kg_facturable
        from `{MARTS}.fct_order_items` f
        join `{MARTS}.dim_customers` c on f.customer_key = c.customer_key
        join `{MARTS}.dim_products`  p on f.product_key  = p.product_key
        where {_fdates(dates)}{_fstates(states)}
          and p.product_weight_g is not null
          and p.product_volume_cm3 is not null
          and p.product_weight_g > 0
    ),
    por_cat as (
        select categoria,
               sum(freight_value) / sum(kg_facturable) as costo_kg,
               count(*) as unidades
        from base group by 1 having count(*) > 500
    ),
    global_rate as (
        select sum(freight_value) / sum(kg_facturable) as media from base
    )
    select
        pc.categoria,
        round(pc.costo_kg, 2)                                   as costo_kg,
        round(100 * (pc.costo_kg / g.media - 1), 1)             as desviacion_pct,
        pc.unidades
    from por_cat pc cross join global_rate g
    order by desviacion_pct desc
    """