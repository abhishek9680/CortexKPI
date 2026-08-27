import os
import csv
import math
import random
from datetime import datetime, timedelta

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
os.makedirs(DATA_DIR, exist_ok=True)

def generate_datasets():
    print("Generating Enterprise Multi-Table Datasets for CortexKPI...")
    
    # -------------------------------------------------------------
    # 1. GENERATE METRICS TIME SERIES (metrics_timeseries.csv)
    # -------------------------------------------------------------
    start_date = datetime.now() - timedelta(days=90)
    metrics_file = os.path.join(DATA_DIR, "metrics_timeseries.csv")
    
    # KPIs in the dependency tree
    # Revenue = Sessions * Conv_Rate * AOV
    # Conv_Rate = Payment_Success_Rate * Checkout_CVR
    
    rows_metrics = []
    
    # Generate 90 days of daily metric points
    for day in range(90):
        current_time = start_date + timedelta(days=day)
        date_str = current_time.strftime("%Y-%m-%d")
        day_of_week = current_time.weekday()
        
        # Base seasonal factor (weekends -15%)
        seasonality = 0.85 if day_of_week in [5, 6] else 1.0
        
        # --- SCENARIO 1: Day 85 has APAC Revenue Drop (Payment 3DS Gateway Failure) ---
        # --- SCENARIO 2: Day 70 has SaaS Signup Slump (Ad Campaign vs DNS Jitter) ---
        # --- SCENARIO 3: Day 45 has Flash Sale Surge (Growth Outlier) ---
        
        # Base values
        base_sessions = 120000 * seasonality
        base_conv_rate = 0.028 * (1.0 + random.uniform(-0.02, 0.02))
        base_aov = 185.0 * (1.0 + random.uniform(-0.01, 0.01))
        base_payment_auth = 0.98 * (1.0 + random.uniform(-0.005, 0.005))
        base_checkout_cvr = 0.0286
        
        # Apply Anomalies
        if day == 85: # Scenario 1 Peak
            base_payment_auth *= 0.55  # 45% drop in payment auth rate!
            base_conv_rate *= 0.58     # Conversion drops sharply
        elif day == 70: # Scenario 2 Peak
            base_checkout_cvr *= 0.62   # Landing page conversion drop
            base_conv_rate *= 0.65
        elif day == 45: # Scenario 3 Peak
            base_sessions *= 1.48      # Flash sale surge
            base_conv_rate *= 1.18
            base_aov *= 1.06
            
        sessions = round(base_sessions * (1.0 + random.gauss(0, 0.02)))
        payment_auth = round(base_payment_auth, 4)
        conv_rate = round(base_conv_rate, 4)
        aov = round(base_aov, 2)
        revenue = round(sessions * conv_rate * aov, 2)
        
        # Scenario tags
        scenario_id = "SCENARIO_1" if day >= 80 else ("SCENARIO_2" if 65 <= day < 80 else "SCENARIO_3")
        
        # Write rows for each metric
        rows_metrics.append({
            "timestamp": date_str,
            "scenario_id": scenario_id,
            "kpi_name": "Revenue",
            "value": revenue,
            "unit": "USD",
            "region": "APAC" if day >= 80 else "GLOBAL"
        })
        rows_metrics.append({
            "timestamp": date_str,
            "scenario_id": scenario_id,
            "kpi_name": "Sessions",
            "value": sessions,
            "unit": "count",
            "region": "APAC" if day >= 80 else "GLOBAL"
        })
        rows_metrics.append({
            "timestamp": date_str,
            "scenario_id": scenario_id,
            "kpi_name": "Conversion_Rate",
            "value": conv_rate * 100, # percentage
            "unit": "%",
            "region": "APAC" if day >= 80 else "GLOBAL"
        })
        rows_metrics.append({
            "timestamp": date_str,
            "scenario_id": scenario_id,
            "kpi_name": "AOV",
            "value": aov,
            "unit": "USD",
            "region": "APAC" if day >= 80 else "GLOBAL"
        })
        rows_metrics.append({
            "timestamp": date_str,
            "scenario_id": scenario_id,
            "kpi_name": "Payment_Success_Rate",
            "value": payment_auth * 100, # percentage
            "unit": "%",
            "region": "APAC" if day >= 80 else "GLOBAL"
        })

    with open(metrics_file, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["timestamp", "scenario_id", "kpi_name", "value", "unit", "region"])
        writer.writeheader()
        writer.writerows(rows_metrics)
    print(f"-> Generated {len(rows_metrics)} metric records in {metrics_file}")

    # -------------------------------------------------------------
    # 2. GENERATE JIRA DEPLOYMENTS (jira_deployments.csv)
    # -------------------------------------------------------------
    jira_file = os.path.join(DATA_DIR, "jira_deployments.csv")
    day85_date = (start_date + timedelta(days=85)).strftime("%Y-%m-%d")
    day70_date = (start_date + timedelta(days=70)).strftime("%Y-%m-%d")
    day45_date = (start_date + timedelta(days=45)).strftime("%Y-%m-%d")
    
    jira_rows = [
        {
            "deployment_id": "DEPLOY-8492",
            "timestamp": f"{day85_date} 14:15:00",
            "service": "payment-gateway-service",
            "commit_hash": "a8f3b92",
            "author": "devops-lead@company.com",
            "summary": "Stripe 3DS OTP Authentication Gateway v3.2.0 Upgrade",
            "description": "Upgraded Stripe 3DS SDK to v3.2.0 for APAC region compliance. Enforces strict SHA256 OTP validation protocol.",
            "status": "COMPLETED",
            "environment": "production-apac"
        },
        {
            "deployment_id": "MKT-1102",
            "timestamp": f"{day70_date} 09:30:00",
            "service": "marketing-landing-page",
            "commit_hash": "c4d7e11",
            "author": "growth-dev@company.com",
            "summary": "Google Ads Campaign Creative & Form Revamp v2.1",
            "description": "Updated sign-up funnel step 2 layout and added strict CAPTCHA verification component.",
            "status": "COMPLETED",
            "environment": "production-global"
        },
        {
            "deployment_id": "PROMO-4040",
            "timestamp": f"{day45_date} 00:01:00",
            "service": "checkout-promo-engine",
            "commit_hash": "e991a04",
            "author": "promo-bot@company.com",
            "summary": "Cyber Week Flash Sale Promo Code FLASH40 Enabler",
            "description": "Activated 40% discount promo rules across all NA merchandise categories.",
            "status": "COMPLETED",
            "environment": "production-na"
        }
    ]
    
    with open(jira_file, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["deployment_id", "timestamp", "service", "commit_hash", "author", "summary", "description", "status", "environment"])
        writer.writeheader()
        writer.writerows(jira_rows)
    print(f"-> Generated {len(jira_rows)} Jira records in {jira_file}")

    # -------------------------------------------------------------
    # 3. GENERATE ZENDESK TICKETS (zendesk_tickets.csv)
    # -------------------------------------------------------------
    zendesk_file = os.path.join(DATA_DIR, "zendesk_tickets.csv")
    zendesk_rows = [
        # Scenario 1 tickets
        {
            "ticket_id": f"ZD-908{i}",
            "created_at": f"{day85_date} {14 + (i%4):02d}:{random.randint(10,59):02d}:00",
            "category": "Payment Failure",
            "customer_region": "APAC",
            "subject": "Payment checkout hangs on OTP spinner",
            "description": "Attempted to complete purchase on APAC store. Credit card authorization modal remains stuck on 3DS OTP confirmation step indefinitely.",
            "sentiment_score": -0.88
        } for i in range(15)
    ] + [
        # Scenario 2 tickets
        {
            "ticket_id": f"ZD-412{i}",
            "created_at": f"{day70_date} {10 + (i%5):02d}:{random.randint(10,59):02d}:00",
            "category": "Sign-up Issue",
            "customer_region": "EU",
            "subject": "CAPTCHA validation error on sign up form",
            "description": "Cannot complete demo request form. CAPTCHA fails to load or gives invalid token error.",
            "sentiment_score": -0.65
        } for i in range(4)
    ]
    
    with open(zendesk_file, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["ticket_id", "created_at", "category", "customer_region", "subject", "description", "sentiment_score"])
        writer.writeheader()
        writer.writerows(zendesk_rows)
    print(f"-> Generated {len(zendesk_rows)} Zendesk records in {zendesk_file}")

    # -------------------------------------------------------------
    # 4. GENERATE SLACK ALERTS (slack_alerts.csv)
    # -------------------------------------------------------------
    slack_file = os.path.join(DATA_DIR, "slack_alerts.csv")
    slack_rows = [
        {
            "alert_id": "ALT-9901",
            "channel": "#war-room-checkout",
            "timestamp": f"{day85_date} 14:32:10",
            "severity": "CRITICAL",
            "source": "Datadog-APM",
            "message": "p99 Gateway Latency Spike: Stripe 3DS token handshake latency rose to 4,850ms (Normal baseline: 320ms). 502 Bad Gateway error rate 42.1%.",
            "metric_tag": "Payment_Success_Rate"
        },
        {
            "alert_id": "ALT-8812",
            "channel": "#infra-alerts",
            "timestamp": f"{day70_date} 09:45:00",
            "severity": "WARNING",
            "source": "Cloudflare-DNS",
            "message": "Cloudflare DNS resolving latency spike in EU-West region (220ms vs 18ms baseline).",
            "metric_tag": "Conversion_Rate"
        },
        {
            "alert_id": "ALT-7703",
            "channel": "#growth-marketing",
            "timestamp": f"{day45_date} 10:15:00",
            "severity": "INFO",
            "source": "Google-Analytics",
            "message": "Viral surge detected on TikTok promo code FLASH40. Concurrent active sessions hit 85,000.",
            "metric_tag": "Sessions"
        }
    ]
    
    with open(slack_file, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["alert_id", "channel", "timestamp", "severity", "source", "message", "metric_tag"])
        writer.writeheader()
        writer.writerows(slack_rows)
    print(f"-> Generated {len(slack_rows)} Slack records in {slack_file}")

    print("[SUCCESS] All enterprise dataset files generated successfully!")

if __name__ == "__main__":
    generate_datasets()
