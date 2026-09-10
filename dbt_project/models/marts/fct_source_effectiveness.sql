-- How many hires each recruiting source produces
select
    c.source,
    count(distinct c.candidate_id) as total_candidates,
    count(distinct case when p.stage = 'Hired' then p.candidate_id end) as total_hired,
    round(
        100.0 * count(distinct case when p.stage = 'Hired' then p.candidate_id end)
        / nullif(count(distinct c.candidate_id), 0), 1
    ) as hire_rate_pct
from {{ ref('stg_candidates') }} c
left join {{ ref('stg_pipeline_stages') }} p using (candidate_id)
group by 1
order by total_hired desc
