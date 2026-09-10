select
    candidate_id,
    name,
    source,
    req_id,
    applied_date::date as applied_date
from {{ source('raw', 'candidates') }}
