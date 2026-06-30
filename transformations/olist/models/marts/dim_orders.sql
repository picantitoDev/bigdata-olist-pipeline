with orders as (
    select * from {{ ref('int_orders_delivery_metrics') }}
),

final as (
    select
        {{ dbt_utils.generate_surrogate_key(['order_id']) }} as order_key,
        order_id,
        order_status,
        order_purchase_timestamp,
        cast(order_purchase_timestamp as date) as order_purchase_date,
        order_approved_at,
        order_delivered_carrier_date,
        order_delivered_customer_date,
        order_estimated_delivery_date,
        delivery_days,
        delivery_vs_estimate_days,
        is_delivered_on_time
    from orders
)

select * from final