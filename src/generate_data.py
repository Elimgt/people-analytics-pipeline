import random
from datetime import timedelta
from faker import Faker
import pandas as pd

fake = Faker()
Faker.seed(42)
random.seed(42)

N_REQS = 40
N_CANDIDATES = 600
SOURCES = ["LinkedIn", "Referral", "Job Board", "Career Site", "Recruiter Outreach"]
DEPARTMENTS = ["Engineering", "Sales", "Product", "People", "Design", "Data"]

def gen_requisitions():
    rows = []
    for i in range(N_REQS):
        opened = fake.date_between(start_date="-9M", end_date="-2M")
        closed = opened + timedelta(days=random.randint(20, 90))
        rows.append({
            "req_id": f"REQ-{i+1:03d}",
            "title": fake.job(),
            "department": random.choice(DEPARTMENTS),
            "hiring_manager": fake.name(),
            "opened_date": opened,
            "closed_date": closed,
            "status": random.choice(["Closed", "Open"]),
        })
    return pd.DataFrame(rows)

def gen_candidates(reqs):
    rows = []
    for i in range(N_CANDIDATES):
        req = reqs.sample(1).iloc[0]
        applied = fake.date_between(start_date=req["opened_date"], end_date="today")
        rows.append({
            "candidate_id": f"CAND-{i+1:04d}",
            "name": fake.name(),
            "source": random.choice(SOURCES),
            "req_id": req["req_id"],
            "applied_date": applied,
        })
    return pd.DataFrame(rows)

def gen_pipeline(candidates):
    rows = []
    for _, c in candidates.iterrows():
        date = c["applied_date"]
        stage_path = ["Applied", "Screening"]
        if random.random() < 0.55:
            stage_path.append("Interview")
        if len(stage_path) == 3 and random.random() < 0.4:
            stage_path.append("Offer")
        if "Offer" in stage_path and random.random() < 0.75:
            stage_path.append("Hired")
        elif random.random() < 0.5:
            stage_path.append("Rejected")

        for stage in stage_path:
            date = date + timedelta(days=random.randint(1, 12))
            rows.append({
                "application_id": f"{c['candidate_id']}-{c['req_id']}",
                "candidate_id": c["candidate_id"],
                "req_id": c["req_id"],
                "stage": stage,
                "stage_date": date,
            })
    return pd.DataFrame(rows)

def gen_offers(pipeline):
    offers = pipeline[pipeline["stage"] == "Offer"].copy()
    rows = []
    for i, (_, o) in enumerate(offers.iterrows()):
        accepted = random.random() < 0.7
        rows.append({
            "offer_id": f"OFFER-{i+1:04d}",
            "candidate_id": o["candidate_id"],
            "offer_date": o["stage_date"],
            "accepted": accepted,
            "accepted_date": o["stage_date"] + timedelta(days=random.randint(1, 10)) if accepted else None,
            "salary": random.randint(45000, 130000),
        })
    return pd.DataFrame(rows)

if __name__ == "__main__":
    reqs = gen_requisitions()
    candidates = gen_candidates(reqs)
    pipeline = gen_pipeline(candidates)
    offers = gen_offers(pipeline)

    reqs.to_csv("data/raw/job_requisitions.csv", index=False)
    candidates.to_csv("data/raw/candidates.csv", index=False)
    pipeline.to_csv("data/raw/pipeline_stages.csv", index=False)
    offers.to_csv("data/raw/offers.csv", index=False)
    print("Data generated in data/raw/")
