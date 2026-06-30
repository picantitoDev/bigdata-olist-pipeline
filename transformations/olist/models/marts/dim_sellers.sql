with sellers as (
    select * from {{ ref('stg_sellers') }}
),

geo as (
    select * from {{ ref('stg_geolocation') }}
),

joined as (
    select
        {{ dbt_utils.generate_surrogate_key(['sellers.seller_id']) }} as seller_key,
        sellers.seller_id,
        sellers.seller_zip_code_prefix,
        sellers.seller_city,
        sellers.seller_state,
        geo.latitude as seller_latitude,
        geo.longitude as seller_longitude
    from sellers
    left join geo
        on sellers.seller_zip_code_prefix = geo.zip_code_prefix
)

select * from joined