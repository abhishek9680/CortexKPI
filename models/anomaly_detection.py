import numpy as np
import pandas as pd
from scipy import stats
from sklearn.ensemble import IsolationForest

class AnomalyDetectorML:
    """
    Layer 1: Noise-Aware Anomaly Detection Model
    Implements Rolling Bayesian Dynamic Baselining and Isolation Forest ML.
    Safely handles NaN / Inf values for robust JSON serialization.
    """
    def __init__(self, window_size=28, confidence_level=0.95):
        self.window_size = window_size
        self.confidence_level = confidence_level
        self.z_threshold = stats.norm.ppf(1 - (1 - confidence_level) / 2) # ~1.96 for 95%
        self.iso_forest = IsolationForest(n_estimators=100, contamination=0.05, random_state=42)

    def analyze_timeseries(self, df_kpi):
        """
        Input: DataFrame with ['timestamp', 'value'] sorted chronologically
        Output: Processed DataFrame with rolling_mean, rolling_std, lower_bound, upper_bound, z_score, anomaly_status
        """
        df = df_kpi.copy()
        df['value'] = pd.to_numeric(df['value']).fillna(0.0)
        
        # 1. Bayesian Rolling Statistics
        df['rolling_mean'] = df['value'].shift(1).rolling(window=self.window_size, min_periods=3).mean()
        df['rolling_std'] = df['value'].shift(1).rolling(window=self.window_size, min_periods=3).std()
        
        # Fallback for initial points
        df['rolling_mean'] = df['rolling_mean'].fillna(df['value'].expanding().mean()).fillna(0.0)
        df['rolling_std'] = df['rolling_std'].fillna(df['value'].expanding().std()).fillna(1.0)
        df['rolling_std'] = df['rolling_std'].replace(0, 1.0)
        
        # 2. 95% Confidence Bounds
        df['lower_bound'] = df['rolling_mean'] - (self.z_threshold * df['rolling_std'])
        df['upper_bound'] = df['rolling_mean'] + (self.z_threshold * df['rolling_std'])
        
        # 3. Z-Score Calculation
        df['z_score'] = (df['value'] - df['rolling_mean']) / df['rolling_std']
        df['z_score'] = df['z_score'].replace([np.inf, -np.inf], 0.0).fillna(0.0)
        
        # 4. Feature engineering for Isolation Forest ML
        df['pct_change'] = df['value'].pct_change().replace([np.inf, -np.inf], 0.0).fillna(0.0)
        df['accel'] = df['pct_change'].diff().replace([np.inf, -np.inf], 0.0).fillna(0.0)
        
        X = df[['value', 'z_score', 'pct_change', 'accel']].values
        self.iso_forest.fit(X)
        iso_scores = self.iso_forest.decision_function(X)
        df['ml_anomaly_score'] = np.nan_to_num(iso_scores, nan=0.0, posinf=1.0, neginf=-1.0)
        
        # Clean all floating point columns
        for col in ['rolling_mean', 'rolling_std', 'lower_bound', 'upper_bound', 'z_score']:
            df[col] = np.nan_to_num(df[col].values, nan=0.0, posinf=0.0, neginf=0.0)

        # 5. Classification Logic
        conditions = [
            (df['z_score'].abs() > 2.0) & (df['ml_anomaly_score'] < 0.1),
            (df['z_score'].abs() > 1.5) & (df['z_score'].abs() <= 2.0),
        ]
        choices = ['ANOMALY_BREACH', 'WARNING']
        df['status'] = np.select(conditions, choices, default='NORMAL')
        
        return df

    def get_anomalies_summary(self, df_processed):
        anomalies = df_processed[df_processed['status'] == 'ANOMALY_BREACH'].copy()
        result = []
        for idx, row in anomalies.iterrows():
            result.append({
                "timestamp": str(row['timestamp']),
                "actual_value": float(row['value']),
                "baseline_mean": float(row['rolling_mean']),
                "z_score": float(row['z_score']),
                "lower_bound": float(row['lower_bound']),
                "upper_bound": float(row['upper_bound']),
                "ml_score": float(row['ml_anomaly_score']),
                "status": str(row['status']),
                "deviation_pct": float(((row['value'] - row['rolling_mean']) / (row['rolling_mean'] + 1e-5)) * 100)
            })
        return result
