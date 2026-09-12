select
    req_id,
    title,
    department,
    coalesce(hiring_manager, 'Unknown') as hiring_manager,
    opened_date::date as opened_date,
    closed_date::date as closed_date,
    status
from {{ source('raw', 'job_requisitions') }}
