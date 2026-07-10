"""Queries SQL centralizadas. Toda la agregación ocurre en BigQuery,
no en pandas — el warehouse hace el trabajo pesado (escalabilidad)."""

MARTS = "big-data-495719.olist_marts"

# ------------------------------------------------------------------
# Executive Summary
# ------------------------------------------------------------------

KPIS_GLOBALES = f"""
select
    count(distinct f.order_id)                    as total_orders,
    round(sum(f.total_item_value), 2)             as total_revenue,
    round(sum(f.total_item_value)
        / count(distinct f.order_id), 2)          as avg_order_value,
    count(distinct f.customer_key)                as total_customers
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
