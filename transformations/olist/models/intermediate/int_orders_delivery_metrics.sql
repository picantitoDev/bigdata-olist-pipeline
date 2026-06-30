with orders as (
    select * from {{ ref('stg_orders') }}
),

metrics as (
    select
        order_id,
        customer_id,
        order_status,
        order_purchase_timestamp,
        order_approved_at,
        order_delivered_carrier_date,
        order_delivered_customer_date,
        order_estimated_delivery_date,

        {{ dbt.datediff('order_purchase_timestamp', 'order_delivered_customer_date', 'day') }} as delivery_days,

        {{ dbt.datediff('order_estimated_delivery_date', 'order_delivered_customer_date', 'day') }} as delivery_vs_estimate_days,

        case
            when order_delivered_customer_date is null then null
            when order_delivered_customer_date <= order_estimated_delivery_date then true
            else false
        end as is_delivered_on_time

    from orders
)

select * from metrics