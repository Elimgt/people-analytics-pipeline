-- Days from candidate application to hire
with hired as (
    select candidate_id, req_id, stage_date as hired_date
    from {{ ref('stg_pipeline_stages') }}
    where stage = 'Hired'
),
applied as (
    select candidate_id, applied_date
    from {{ ref('stg_candidates') }}
)
select
    h.candidate_id,
    h.req_id,
    a.applied_date,
    h.hired_date,
    h.hired_date - a.applied_date as days_to_hire
from hired h
join applied a using (candidate_id)
