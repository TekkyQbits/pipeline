import json
import random
import datetime
import boto3
import os

# Environment variables (Injected by Serverless Framework)
BUCKET_NAME = os.environ.get("BUCKET_NAME")
FILE_KEY = "dashboard/data.json"

s3 = boto3.client("s3")


def detect_anomalies(events):
    """
    Pure Python logic: Counts IPs and flags anomalies.
    Easy to unit test because it doesn't rely on AWS directly.
    """
    ip_counts = {}

    # Aggregation
    for event in events:
        ip = event["ip"]
        ip_counts[ip] = ip_counts.get(ip, 0) + 1

    results = []
    timestamp = datetime.datetime.now().isoformat()

    # Business Logic
    for ip, count in ip_counts.items():
        status = "Normal"
        if count > 20:
            status = "Critical - Bot Attack"
        elif count > 10:
            status = "Warning - High Traffic"

        results.append(
            {"ip": ip, "count": count, "status": status, "window_start": timestamp}
        )

    return results


def generate_mock_data():
    """Simulates a batch of raw web traffic"""
    ips = ["192.168.1.1", "192.168.1.2", "192.168.1.3", "10.0.0.5"]
    bot_ip = "66.66.66.66"
    events = []

    # Normal traffic
    for _ in range(50):
        events.append({"ip": random.choice(ips)})

    # Attack injection (random chance)
    if random.random() > 0.5:
        print("Injecting attack...")
        for _ in range(30):
            events.append({"ip": bot_ip})

    return events


def lambda_handler(event, context):
    """AWS Entry Point"""
    print("Starting pipeline...")

    # 1. Ingest (Simulation)
    raw_data = generate_mock_data()

    # 2. Transform & Detect
    anomalies = detect_anomalies(raw_data)

    # 3. Load (Save to S3 for React)
    # Filter for interesting data to keep payload small
    top_anomalies = sorted(anomalies, key=lambda x: x["count"], reverse=True)[:5]

    payload = {
        "last_updated": datetime.datetime.now().isoformat(),
        "total_events_processed": len(raw_data),
        "anomalies": top_anomalies,
    }

    try:
        s3.put_object(
            Bucket=BUCKET_NAME,
            Key=FILE_KEY,
            Body=json.dumps(payload),
            ContentType="application/json",
            ACL="public-read",  # Ensure bucket allows this or use CloudFront
        )
        return {"statusCode": 200, "body": "Pipeline Success"}
    except Exception as e:
        print(f"Error: {e}")
        return {"statusCode": 500, "body": str(e)}
