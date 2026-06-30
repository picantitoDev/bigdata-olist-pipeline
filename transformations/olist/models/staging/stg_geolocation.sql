with source as (
    select * from {{ source('olist', 'olist_geolocation_dataset') }}
),

deduplicated as (
    select
        lpad(cast(geolocation_zip_code_prefix as string), 5, '0') as zip_code_prefix,
        round(avg(geolocation_lat), 6) as latitude,
        round(avg(geolocation_lng), 6) as longitude,
        max(trim(lower(geolocation_city))) as city,
        max(upper(trim(geolocation_state))) as state
    from source
    group by lpad(cast(geolocation_zip_code_prefix as string), 5, '0')
)

select * from deduplicated