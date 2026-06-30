with payments as (
    select * from {{ ref('stg_order_payments') }}
),

orders as (
    select * from {{ ref('stg_orders') }}
),

final as (
    select
        {{ dbt_utils.generate_surrogate_key(['payments.order_id', 'payments.payment_sequential']) }}
            as payment_key,

        {{ dbt_utils.generate_surrogate_key(['payments.order_id']) }} as order_key,
        {{ dbt_utils.generate_surrogate_key(['orders.customer_id']) }} as customer_key,
        cast(orders.order_purchase_timestamp as date) as order_date_key,

        payments.order_id,
        payments.payment_sequential,
        payments.payment_type,
        payments.payment_installments,
        payments.payment_value

    from payments
    inner join orders
        on payments.order_id = orders.order_id
)

select * from final