select
    order_id,
    product,
    price,
    quantity,
    price * quantity as order_total,
    is_refund,
    event_time,
    date_trunc('minute', event_time) as event_minute
from {{ source('raw', 'raw_orders') }}