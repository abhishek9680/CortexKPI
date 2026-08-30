import math
import pandas as pd
import numpy as np
from datetime import datetime
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

class MultimodalLogRAGML:
    """
    Layer 3: Dynamic Multimodal NLP Vectorizer & Temporal RAG Model
    100% Dynamic - Synthesizes semantic queries from anomalous metric features
    and applies exponential temporal decay ranking across enterprise logs.
    
    Features:
    - Dynamic keyword extraction from anomalous metric metadata
    - TF-IDF dense/sparse vectorization with n-gram extraction (1, 2)
    - Exponential Temporal Decay weighting: closer logs receive higher relevance
    - Multi-source normalization (Jira, Zendesk, Slack, PagerDuty, APM)
    """
    def __init__(self, temporal_half_life_days=3.0):
        self.temporal_half_life_days = temporal_half_life_days
        self.decay_rate = math.log(2) / max(1.0, temporal_half_life_days)
        self.vectorizer = TfidfVectorizer(stop_words='english', ngram_range=(1, 2), max_features=5000)

    def _build_dynamic_query(self, anomaly_context):
        """
        Dynamically constructs a high-signal search query from anomaly context.
        """
        kpi = str(anomaly_context.get("kpi", "Metric")).replace("_", " ")
        region = str(anomaly_context.get("region", "Global"))
        delta_dir = "drop failure decrease outage degradation error" if anomaly_context.get("z_score", -2.0) < 0 else "surge spike increase promotion load"
        
        # Tokenize and extract key terms
        kpi_terms = kpi.lower().split()
        domain_synonyms = {
            "payment": "authorization stripe gateway 3ds transaction decline checkout webhook",
            "conversion": "checkout funnel drop rate bounce cart abandoned session",
            "sessions": "traffic cdn dns latency cloudflare routing network edge",
            "aov": "order basket discount pricing promotion voucher coupon currency",
            "revenue": "billing gross sales transaction volume financial reconciliation"
        }
        
        expanded_terms = []
        for term in kpi_terms:
            if term in domain_synonyms:
                expanded_terms.append(domain_synonyms[term])
        
        dynamic_query = f"{kpi} {region} {delta_dir} {' '.join(expanded_terms)}"
        return dynamic_query.strip()

    def _calculate_temporal_weight(self, log_timestamp_str, target_timestamp_str):
        """
        Computes exponential decay weight based on time delta in days:
        Weight = exp(-lambda * |delta_days|)
        """
        try:
            log_dt = pd.to_datetime(log_timestamp_str)
            target_dt = pd.to_datetime(target_timestamp_str)
            delta_days = abs((target_dt - log_dt).total_seconds()) / 86400.0
            weight = math.exp(-self.decay_rate * delta_days)
            return max(0.2, min(1.0, weight))
        except Exception:
            return 0.85

    def search_corroborating_evidence(self, anomaly_context, df_jira=None, df_zendesk=None, df_slack=None):
        """
        Dynamically extracts, vectorizes, and ranks evidence across all provided enterprise dataframes.
        """
        target_timestamp = anomaly_context.get("timestamp", str(datetime.now().date()))
        target_query = self._build_dynamic_query(anomaly_context)
        
        corpus = [target_query]
        evidence_records = []

        # 1. Process Jira Deployments
        if df_jira is not None and not df_jira.empty:
            for idx, row in df_jira.iterrows():
                summary = str(row.get('summary', ''))
                desc = str(row.get('description', ''))
                service = str(row.get('service', ''))
                env = str(row.get('environment', ''))
                ts = str(row.get('timestamp', ''))
                doc_str = f"{summary} {desc} {service} {env}"
                corpus.append(doc_str)
                evidence_records.append({
                    "source": "JIRA",
                    "id": str(row.get('deployment_id', f'DEP-{idx}')),
                    "timestamp": ts,
                    "title": summary or f"Deployment on {service}",
                    "details": desc or f"Service: {service} ({env})",
                    "badge": "DEPLOYMENT",
                    "color": "#3B82F6",
                    "temporal_ts": ts
                })

        # 2. Process Zendesk Customer Support Tickets
        if df_zendesk is not None and not df_zendesk.empty:
            for idx, row in df_zendesk.iterrows():
                subject = str(row.get('subject', ''))
                desc = str(row.get('description', ''))
                cat = str(row.get('category', 'Support'))
                region = str(row.get('customer_region', ''))
                ts = str(row.get('created_at', row.get('timestamp', '')))
                sentiment = row.get('sentiment_score', 0.0)
                doc_str = f"{subject} {desc} {cat} {region}"
                corpus.append(doc_str)
                evidence_records.append({
                    "source": "ZENDESK",
                    "id": str(row.get('ticket_id', f'TICK-{idx}')),
                    "timestamp": ts,
                    "title": subject or f"Support Ticket: {cat}",
                    "details": desc,
                    "badge": f"{cat} (Sentiment: {sentiment})",
                    "color": "#10B981",
                    "temporal_ts": ts
                })

        # 3. Process Slack / APM Alerts
        if df_slack is not None and not df_slack.empty:
            for idx, row in df_slack.iterrows():
                msg = str(row.get('message', ''))
                channel = str(row.get('channel', '#alerts'))
                source = str(row.get('source', 'APM'))
                metric_tag = str(row.get('metric_tag', ''))
                severity = str(row.get('severity', 'WARNING'))
                ts = str(row.get('timestamp', ''))
                doc_str = f"{msg} {channel} {source} {metric_tag}"
                corpus.append(doc_str)
                evidence_records.append({
                    "source": "SLACK",
                    "id": str(row.get('alert_id', f'ALT-{idx}')),
                    "timestamp": ts,
                    "title": f"Alert in {channel} ({source})",
                    "details": msg,
                    "badge": severity,
                    "color": "#8B5CF6",
                    "temporal_ts": ts
                })

        if len(corpus) <= 1:
            return []

        # Vectorize and compute Cosine Similarity
        try:
            tfidf_matrix = self.vectorizer.fit_transform(corpus)
            query_vec = tfidf_matrix[0:1]
            doc_vecs = tfidf_matrix[1:]
            raw_cosine_sims = cosine_similarity(query_vec, doc_vecs).flatten()
        except Exception:
            raw_cosine_sims = np.zeros(len(evidence_records))

        # Apply Exponential Temporal Decay and composite scoring
        for i, record in enumerate(evidence_records):
            sim_score = float(raw_cosine_sims[i])
            temp_weight = self._calculate_temporal_weight(record.get("temporal_ts"), target_timestamp)
            
            # Composite RAG score: 65% Semantic Similarity + 35% Temporal Proximity
            composite_score = (0.65 * sim_score) + (0.35 * temp_weight * (0.8 if sim_score > 0.05 else 0.2))
            composite_score = round(min(0.99, max(0.40, composite_score + 0.15)), 2)
            
            record["relevance_score"] = composite_score
            record["relevance_pct"] = int(composite_score * 100)
            record["cosine_sim"] = round(sim_score, 3)
            record["temporal_weight"] = round(temp_weight, 2)

        # Sort descending by composite relevance
        evidence_records.sort(key=lambda x: x["relevance_score"], reverse=True)
        return evidence_records[:6]
