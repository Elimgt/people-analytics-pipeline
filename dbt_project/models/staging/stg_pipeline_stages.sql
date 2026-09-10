select
    application_id,
    candidate_id,
    req_id,
    stage,
    stage_date::date as stage_date
from {{ source('raw', 'pipeline_stages') }}
