import os
import random
from datetime import timedelta
from faker import Faker
import pandas as pd

fake = Faker()
Faker.seed(42)
random.seed(42)

N_REQS = 40
N_CANDIDATES = 600
DEPARTMENTS = ["Engineering", "Sales", "Product", "People", "Design", "Data"]

# Canonical recruiting sources, each with the messy real-world spellings an
# ATS export tends to contain (manual entry, integrations with inconsistent
# casing, stray whitespace, etc.).
SOURCE_VARIANTS = {
    "LinkedIn": ["LinkedIn", "linkedin", "Linked In"],
    "Referral": ["Referral", "referral", "REFERRAL"],
    "Job Board": ["Job Board", "job board", "JobBoard"],
    "Career Site": ["Career Site", "career site"],
    "Recruiter Outreach": ["Recruiter Outreach", "recruiter outreach"],
}
SOURCES = list(SOURCE_VARIANTS.keys())


def messy_source(canonical):
    # ~5% of rows never had a source captured at intake.
    if random.random() < 0.05:
        return None
    variant = random.choice(SOURCE_VARIANTS[canonical])
    # ~15% of rows carry stray whitespace, common with manual data entry.
    if random.random() < 0.15:
        variant = f"  {variant}  "
    return variant


def gen_requisitions():
    rows = []
    for i in range(N_REQS):
        opened = fake.date_between(start_date="-9M", end_date="-2M")
        closed = opened + timedelta(days=random.randint(20, 90))
        rows.append({
            "req_id": f"REQ-{i+1:03d}",
            "title": fake.job(),
            "department": random.choice(DEPARTMENTS),
            # ~5% of requisitions are missing a hiring manager (e.g. an
            # interim req opened before one was assigned).
            "hiring_manager": fake.name() if random.random() > 0.05 else None,
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
        name = fake.name()
        # ~5% of names carry stray leading/trailing whitespace.
        if random.random() < 0.05:
            name = f"  {name}  "
        rows.append({
            "candidate_id": f"CAND-{i+1:04d}",
            "name": name,
            "source": messy_source(random.choice(SOURCES)),
            "req_id": req["req_id"],
            "applied_date": applied,
        })
    df = pd.DataFrame(rows)

    # Simulate a known ATS export quirk: a handful of candidates get
    # exported twice (e.g. a sync re-ran without deduping).
    duplicate_sample = df.sample(frac=0.03, random_state=7)
    df = pd.concat([df, duplicate_sample], ignore_index=True)
    return df


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

    # Simulate a small number of orphan funnel records: stages logged for a
    # candidate_id that no longer exists in the candidates table (e.g. a
    # candidate record purged for a data-retention/GDPR request, while
    # their funnel history wasn't cleaned up downstream). This is a
    # realistic referential-integrity issue, deliberately left in raw data
    # and caught by a dbt relationships test instead of hidden here.
    sample_req_ids = candidates["req_id"].drop_duplicates().sample(3, random_state=11)
    for i, req_id in enumerate(sample_req_ids):
        rows.append({
            "application_id": f"CAND-ORPHAN-{i+1:02d}-{req_id}",
            "candidate_id": f"CAND-ORPHAN-{i+1:02d}",
            "req_id": req_id,
            "stage": "Applied",
            "stage_date": fake.date_between(start_date="-2M", end_date="today"),
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
            # ~5% of offers are missing a recorded salary (e.g. equity-only
            # or not-yet-finalized offers).
            "salary": random.randint(45000, 130000) if random.random() > 0.05 else None,
        })
    return pd.DataFrame(rows)


if __name__ == "__main__":
    reqs = gen_requisitions()
    candidates = gen_candidates(reqs)
    pipeline = gen_pipeline(candidates)
    offers = gen_offers(pipeline)

    os.makedirs("data/raw", exist_ok=True)
    reqs.to_csv("data/raw/job_requisitions.csv", index=False)
    candidates.to_csv("data/raw/candidates.csv", index=False)
    pipeline.to_csv("data/raw/pipeline_stages.csv", index=False)
    offers.to_csv("data/raw/offers.csv", index=False)
    print("Data generated in data/raw/")
