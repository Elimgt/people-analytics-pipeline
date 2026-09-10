-- Offer acceptance rate
select
    count(*) as total_offers,
    sum(case when accepted then 1 else 0 end) as accepted_offers,
    round(
        100.0 * sum(case when accepted then 1 else 0 end) / nullif(count(*), 0), 1
    ) as acceptance_rate_pct
from {{ ref('stg_offers') }}
