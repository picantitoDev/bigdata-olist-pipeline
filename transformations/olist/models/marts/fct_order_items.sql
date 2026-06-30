with order_items as (
    select * from {{ ref('stg_order_items') }}
),

orders as (
    select * from {{ ref('stg_orders') }}
),

final as (
    select
        {{ dbt_utils.generate_surrogate_key(['order_items.order_id', 'order_items.order_item_id']) }}
            as order_item_key,

        {{ dbt_utils.generate_surrogate_key(['order_items.order_id']) }} as order_key,
        {{ dbt_utils.generate_surrogate_key(['order_items.product_id']) }} as product_key,
        {{ dbt_utils.generate_surrogate_key(['order_items.seller_id']) }} as seller_key,
        {{ dbt_utils.generate_surrogate_key(['orders.customer_id']) }} as customer_key,
        cast(orders.order_purchase_timestamp as date) as order_date_key,

        order_items.order_id,
        order_items.order_item_id,
        order_items.shipping_limit_date,

        order_items.price,
        order_items.freight_value,
        (order_items.price + order_items.freight_value) as total_item_value

    from order_items
    inner join orders
        on order_items.order_id = orders.order_id
)

select * from final