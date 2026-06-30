with source as (
    select * from {{ source('olist', 'olist_order_payments_dataset') }}
),

renamed as (
    select
        order_id,
        cast(payment_sequential as integer) as payment_sequential,
        trim(lower(payment_type)) as payment_type,
        cast(payment_installments as integer) as payment_installments,
        cast(payment_value as float64) as payment_value
    from source
)

select * from renamed