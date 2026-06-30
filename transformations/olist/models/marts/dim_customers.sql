with customers as (
    select * from {{ ref('stg_customers') }}
),

geo as (
    select * from {{ ref('stg_geolocation') }}
),

joined as (
    select
        {{ dbt_utils.generate_surrogate_key(['customers.customer_id']) }} as customer_key,
        customers.customer_id,
        customers.customer_unique_id,
        customers.customer_zip_code_prefix,
        customers.customer_city,
        customers.customer_state,
        geo.latitude as customer_latitude,
        geo.longitude as customer_longitude
    from customers
    left join geo
        on customers.customer_zip_code_prefix = geo.zip_code_prefix
)

select * from joined