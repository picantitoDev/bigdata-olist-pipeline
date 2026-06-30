with payments as (
    select * from {{ ref('stg_order_payments') }}
),

aggregated as (
    select
        order_id,
        count(*) as payment_count,
        sum(payment_value) as total_payment_value,
        max(payment_installments) as max_installments,
        count(distinct payment_type) as distinct_payment_types,

        {{ dbt_utils.get_column_values_summary() if false else '' }}
        string_agg(distinct payment_type, ', ' order by payment_type)
            as payment_types

    from payments
    group by 1
)

select * from aggregated