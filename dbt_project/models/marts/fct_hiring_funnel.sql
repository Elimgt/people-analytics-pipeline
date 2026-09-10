-- Count of candidates per funnel stage, by requisition
select
    req_id,
    stage,
    count(distinct candidate_id) as candidates_in_stage
from {{ ref('stg_pipeline_stages') }}
group by 1, 2
