with products as (
    select * from {{ ref('stg_products') }}
),

translation as (
    select * from {{ ref('stg_product_category_translation') }}
),

joined as (
    select
        {{ dbt_utils.generate_surrogate_key(['products.product_id']) }} as product_key,
        products.product_id,
        products.product_category_name,
        coalesce(translation.product_category_name_english, products.product_category_name)
            as product_category,
        products.product_weight_g,
        products.product_length_cm,
        products.product_height_cm,
        products.product_width_cm,
        products.product_photos_qty,
        (products.product_length_cm
            * products.product_height_cm
            * products.product_width_cm) as product_volume_cm3
    from products
    left join translation
        on products.product_category_name = translation.product_category_name
)

select * from joined