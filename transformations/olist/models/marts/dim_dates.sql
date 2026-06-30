with date_spine as (
    {{ dbt_utils.date_spine(
        datepart="day",
        start_date="cast('2016-01-01' as date)",
        end_date="cast('2019-01-01' as date)"
    ) }}
),

final as (
    select
        cast(date_day as date) as date_key,
        date_day as calendar_date,
        extract(year from date_day) as year,
        extract(quarter from date_day) as quarter,
        extract(month from date_day) as month,
        strftime(date_day, '%B') as month_name,
        extract(day from date_day) as day_of_month,
        extract(dayofweek from date_day) as day_of_week,
        strftime(date_day, '%A') as day_name,
        case when extract(dayofweek from date_day) in (0, 6) then true else false end
            as is_weekend
    from date_spine
)

select * from final