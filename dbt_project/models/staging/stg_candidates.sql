-- Cleans up known raw data-quality issues before anything downstream uses
-- this table: stray whitespace, inconsistent source spellings/casing, and
-- duplicate export rows for the same candidate_id.
with cleaned as (
    select
        candidate_id,
        trim(name) as name,
        case
            when lower(trim(source)) like '%linkedin%'
                or lower(trim(source)) like '%linked in%' then 'LinkedIn'
            when lower(trim(source)) like '%referral%' then 'Referral'
            when lower(trim(source)) like '%job board%'
                or lower(trim(source)) like '%jobboard%' then 'Job Board'
            when lower(trim(source)) like '%career site%' then 'Career Site'
            when lower(trim(source)) like '%recruiter%' then 'Recruiter Outreach'
            else 'Unknown'
        end as source,
        req_id,
        applied_date::date as applied_date,
        row_number() over (
            partition by candidate_id
            order by applied_date
        ) as row_num
    from {{ source('raw', 'candidates') }}
)

select
    candidate_id,
    name,
    source,
    req_id,
    applied_date
from cleaned
where row_num = 1
