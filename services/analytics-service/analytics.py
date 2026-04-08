import os
import time
from datetime import datetime, timezone
from mysql_client import mysql_conn
from mongo_client import mongo_db

RUN_EVERY = int(os.environ.get("RUN_EVERY_SECONDS", "10"))

def compute():
    conn = mysql_conn()
    with conn.cursor() as cur:
        # totals per subject (across all users)
        cur.execute("SELECT subject, SUM(hours) AS total_hours, AVG(hours) AS avg_hours_per_entry FROM study_logs GROUP BY subject")
        per_subject = cur.fetchall()

        # overall average study time per entry
        cur.execute("SELECT AVG(hours) AS overall_avg FROM study_logs")
        overall_avg = cur.fetchone() or {}
    conn.close()

    totals = { row["subject"]: float(row["total_hours"] or 0) for row in per_subject }
    avg_study_time = float(overall_avg.get("overall_avg") or 0)

    most_subject = None
    least_subject = None
    if totals:
        most_subject = max(totals.items(), key=lambda x: x[1])[0]
        least_subject = min(totals.items(), key=lambda x: x[1])[0]

    doc = {
        "generated_at": datetime.now(timezone.utc),
        "totals_per_subject": totals,
        "average_study_time": avg_study_time,
        "most_studied_subject": most_subject,
        "least_studied_subject": least_subject,
        "subjects_count": len(totals),
    }
    return doc

def main():
    db = mongo_db()
    col = db["analytics"]

    while True:
        try:
            doc = compute()
            col.insert_one(doc)
            print(f"[analytics] wrote analytics at {doc['generated_at'].isoformat()} subjects={doc['subjects_count']}")
        except Exception as e:
            print(f"[analytics] error: {e}")
        time.sleep(RUN_EVERY)

if __name__ == "__main__":
    main()
