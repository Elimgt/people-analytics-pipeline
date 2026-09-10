select
    offer_id,
    candidate_id,
    offer_date::date as offer_date,
    accepted,
    accepted_date::date as accepted_date,
    salary
from {{ source('raw', 'offers') }}
