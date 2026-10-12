select
    event_minute,
    count(*) as order_count,
    sum(order_total) as revenue,
    sum(case when is_refund then 1 else 0 end) as refund_count
from {{ ref('stg_orders') }}
group by 1
order by 1