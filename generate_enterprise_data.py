import csv
import random
import uuid
import os
from datetime import datetime, timedelta

DATA_DIR = r"e:\accenture hackathon development\data"
os.makedirs(DATA_DIR, exist_ok=True)

JIRA_FILE = os.path.join(DATA_DIR, "jira_deployments.csv")
ZENDESK_FILE = os.path.join(DATA_DIR, "zendesk_tickets.csv")
SLACK_FILE = os.path.join(DATA_DIR, "slack_alerts.csv")

BASE_DATE = datetime(2025, 8, 29)
TOTAL_DAYS = 365

# JIRA Data Definitions
JIRA_SERVICES = [
    "payment-gateway-service", "checkout-auth-service", "cart-microservice", 
    "order-fulfillment-service", "user-auth-service", "inventory-service", 
    "notification-service", "search-service", "recommendation-engine", 
    "cdn-edge-service", "api-gateway", "database-migration-service"
]
JIRA_ENVIRONMENTS = ["production-apac", "production-eu", "production-na", "production-latam", "production-emea", "staging", "canary"]
JIRA_STATUS = ["COMPLETED", "FAILED", "ROLLED_BACK", "IN_PROGRESS"]

# Zendesk Data Definitions
ZENDESK_CATEGORIES = [
    "Payment Failure", "Checkout Error", "Performance Issue", "Account Access", 
    "Order Tracking", "Refund Request", "Mobile App Bug", "General Support", 
    "API Integration", "Billing Inquiry"
]
ZENDESK_REGIONS = ["APAC", "EU", "NA", "LATAM", "EMEA", "GLOBAL"]

# Slack Data Definitions
SLACK_CHANNELS = [
    "#war-room-checkout", "#infra-alerts", "#ops-monitoring", "#growth-marketing", 
    "#security-incidents", "#db-alerts", "#api-health", "#release-pipeline", 
    "#incident-response", "#platform-stability"
]
SLACK_SEVERITY = ["CRITICAL", "WARNING", "INFO", "RESOLVED"]
SLACK_SOURCES = [
    "Datadog-APM", "Cloudflare-DNS", "PagerDuty", "Grafana-Prometheus", 
    "AWS-CloudWatch", "Sentry", "New-Relic", "Google-Analytics", "ElasticSearch-APM", "StatusPage"
]
SLACK_METRICS = ["Payment_Success_Rate", "Conversion_Rate", "Sessions", "AOV", "Revenue", "Latency", "Error_Rate", "CPU_Usage", "Memory_Usage", "Disk_IO"]

def random_date(start_date, days):
    return start_date + timedelta(days=random.randint(0, days - 1), hours=random.randint(0, 23), minutes=random.randint(0, 59))

def generate_data():
    jira_data = []
    zendesk_data = []
    slack_data = []

    for day in range(TOTAL_DAYS):
        current_date = BASE_DATE + timedelta(days=day)
        
        # Determine scenario
        is_scenario_1 = 350 <= day <= 364
        is_scenario_2 = 320 <= day <= 349
        is_scenario_3 = 280 <= day <= 319
        
        multiplier = random.randint(3, 5) if (is_scenario_1 or is_scenario_2 or is_scenario_3) else 1

        # Jira Deployments (Normal 1-3 per day)
        for _ in range(random.randint(1 * multiplier, 3 * multiplier)):
            ts = current_date + timedelta(hours=random.randint(0, 23))
            
            service = random.choice(JIRA_SERVICES)
            env = random.choice(JIRA_ENVIRONMENTS)
            status = random.choice(JIRA_STATUS[:3]) # Mostly completed, sometimes failed/rolled_back
            if status != "COMPLETED" and random.random() > 0.3: status = "COMPLETED"
            
            summary = f"Deploy {service} v{random.randint(1,10)}.{random.randint(0,9)}.{random.randint(0,9)}"
            desc = f"PR #{random.randint(1000, 9999)} - Routine deployment. Dependency updates."

            if is_scenario_1 and random.random() > 0.5:
                service = "payment-gateway-service"
                env = "production-apac"
                status = "FAILED"
                summary = "Update Stripe 3DS SDK"
                desc = "PR #5532 - Upgrading Stripe 3DS SDK to latest version for APAC compliance."
            
            if is_scenario_2 and random.random() > 0.5:
                service = "cdn-edge-service"
                env = "production-eu"
                status = random.choice(["FAILED", "ROLLED_BACK"])
                summary = "Deploy new CDN routing rules"
                desc = "PR #8821 - Optimizing DNS resolution for EU edge nodes."
            
            if is_scenario_3 and random.random() > 0.5:
                service = "recommendation-engine"
                env = "production-na"
                summary = "Launch Summer Promo ML Model"
                desc = "PR #10211 - Integrating new promotional rules for NA summer campaign."

            jira_data.append({
                "deployment_id": f"DEP-{uuid.uuid4().hex[:8]}",
                "timestamp": ts.isoformat(),
                "service": service,
                "commit_hash": uuid.uuid4().hex[:40],
                "author": f"dev_{random.randint(1, 100)}@enterprise.com",
                "summary": summary,
                "description": desc,
                "status": status,
                "environment": env
            })

        # Zendesk Tickets (Normal 2-10 per day)
        for _ in range(random.randint(2 * multiplier, 10 * multiplier)):
            ts = current_date + timedelta(hours=random.randint(0, 23))
            
            category = random.choice(ZENDESK_CATEGORIES)
            region = random.choice(ZENDESK_REGIONS)
            sentiment = random.uniform(-0.5, 0.8)
            subject = f"Issue with {category.lower()}"
            desc = f"Customer reported a problem regarding {category.lower()} in {region}."
            
            if is_scenario_1 and random.random() > 0.3:
                category = "Payment Failure"
                region = "APAC"
                sentiment = random.uniform(-0.95, -0.6)
                subject = random.choice(["Payment declined after entering OTP", "Card rejected at checkout", "3DS verification failed repeatedly"])
                desc = "User tried to pay multiple times but gets stuck at the OTP screen or receives a decline error."
            
            if is_scenario_2 and random.random() > 0.3:
                category = "Performance Issue"
                region = "EU"
                sentiment = random.uniform(-0.8, -0.4)
                subject = random.choice(["Checkout spinner stuck on loading", "Site is very slow today", "Cannot complete purchase - 502 error"])
                desc = "The website takes over 30 seconds to load the cart, and sometimes throws a 502 Bad Gateway."
            
            zendesk_data.append({
                "ticket_id": f"ZD-{random.randint(100000, 999999)}",
                "created_at": ts.isoformat(),
                "category": category,
                "customer_region": region,
                "subject": subject,
                "description": desc,
                "sentiment_score": round(sentiment, 2)
            })
            
        # Slack Alerts (Normal 2-8 per day)
        for _ in range(random.randint(2 * multiplier, 8 * multiplier)):
            ts = current_date + timedelta(hours=random.randint(0, 23))
            
            channel = random.choice(SLACK_CHANNELS)
            severity = random.choice(["INFO", "WARNING"])
            source = random.choice(SLACK_SOURCES)
            metric = random.choice(SLACK_METRICS)
            msg = f"Routine alert: {metric} is behaving normally."
            
            if is_scenario_1 and random.random() > 0.3:
                channel = "#war-room-checkout"
                severity = "CRITICAL"
                source = "Datadog-APM"
                metric = "Payment_Success_Rate"
                msg = "[CRITICAL] Payment_Success_Rate dropped to 45% in APAC. High error rate on 3DS gateway."
            
            if is_scenario_2 and random.random() > 0.3:
                channel = "#infra-alerts"
                severity = random.choice(["WARNING", "CRITICAL"])
                source = "Cloudflare-DNS"
                metric = "Latency"
                msg = f"[{severity}] Edge latency spiked to 1200ms in EU. 502 errors detected on upstream."
            
            slack_data.append({
                "alert_id": f"ALRT-{uuid.uuid4().hex[:8]}",
                "channel": channel,
                "timestamp": ts.isoformat(),
                "severity": severity,
                "source": source,
                "message": msg,
                "metric_tag": metric
            })

    # Sort data by timestamp
    jira_data.sort(key=lambda x: x["timestamp"])
    zendesk_data.sort(key=lambda x: x["created_at"])
    slack_data.sort(key=lambda x: x["timestamp"])
    
    # Save Jira
    with open(JIRA_FILE, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=["deployment_id", "timestamp", "service", "commit_hash", "author", "summary", "description", "status", "environment"])
        writer.writeheader()
        writer.writerows(jira_data)

    # Save Zendesk
    with open(ZENDESK_FILE, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=["ticket_id", "created_at", "category", "customer_region", "subject", "description", "sentiment_score"])
        writer.writeheader()
        writer.writerows(zendesk_data)
        
    # Save Slack
    with open(SLACK_FILE, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=["alert_id", "channel", "timestamp", "severity", "source", "message", "metric_tag"])
        writer.writeheader()
        writer.writerows(slack_data)
        
    print(f"Generated {len(jira_data)} rows in {JIRA_FILE}")
    print(f"Generated {len(zendesk_data)} rows in {ZENDESK_FILE}")
    print(f"Generated {len(slack_data)} rows in {SLACK_FILE}")

if __name__ == '__main__':
    generate_data()
