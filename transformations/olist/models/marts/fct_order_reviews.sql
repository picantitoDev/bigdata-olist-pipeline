with reviews as (
    select * from {{ ref('int_reviews_deduplicated') }}
),

orders as (
    select * from {{ ref('stg_orders') }}
),

final as (
    select
        {{ dbt_utils.generate_surrogate_key(['reviews.review_id']) }} as review_key,
        {{ dbt_utils.generate_surrogate_key(['reviews.order_id']) }} as order_key,
        {{ dbt_utils.generate_surrogate_key(['orders.customer_id']) }} as customer_key,
        cast(orders.order_purchase_timestamp as date) as order_date_key,

        reviews.review_id,
        reviews.order_id,
        reviews.review_score,
        reviews.review_comment_title,
        reviews.review_comment_message,
        reviews.review_creation_date,
        reviews.review_answer_timestamp,

        case when reviews.review_score >= 4 then true else false end as is_positive_review,
        case when reviews.review_comment_message is not null then true else false end
            as has_comment

    from reviews
    inner join orders
        on reviews.order_id = orders.order_id
)

select * from final