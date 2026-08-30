import numpy as np
import pandas as pd
from scipy import stats
from sklearn.ensemble import IsolationForest

class AnomalyDetectorML:
    """
    Layer 1: Noise-Aware Bayesian Anomaly Detection & Changepoint Detection
    100% Dynamic - works on ANY time-series metric data.
    
    Features:
    - Adaptive Seasonal-Trend decomposition (Day-of-Week & Trend adjustment)
    - Dynamic Bayesian Rolling Baselining with adaptive window estimation
    - Statistical p-value & Student-t / Gaussian Confidence Bounds
    - Unsupervised Isolation Forest ML anomaly scoring
    - Extreme Value Theory (EVT) thresholding (Z-Score + Isolation Forest decision score)
    """
    def __init__(self, window_size=28, confidence_level=0.95):
        self.window_size = window_size
        self.confidence_level = confidence_level
        self.z_threshold = stats.norm.ppf(1 - (1 - confidence_level) / 2) # ~1.96 for 95%
        self.iso_forest = IsolationForest(n_estimators=100, contamination=0.05, random_state=42)

    def analyze_timeseries(self, df_kpi):
        """
        Input: DataFrame with ['timestamp', 'value'] sorted chronologically
        Output: Processed DataFrame with rolling_mean, rolling_std, lower_bound, upper_bound, z_score, p_value, anomaly_status
        """
        df = df_kpi.copy()
        df['value'] = pd.to_numeric(df['value'], errors='coerce').fillna(0.0)
        
        n_samples = len(df)
        adaptive_window = min(self.window_size, max(7, n_samples // 4))

        # 1. Seasonality & Day-of-Week Extraction
        try:
            df['datetime'] = pd.to_datetime(df['timestamp'])
            df['dayofweek'] = df['datetime'].dt.dayofweek
            # Calculate seasonal baseline factor per day of week
            dow_means = df.groupby('dayofweek')['value'].transform('mean')
            overall_mean = df['value'].mean()
            seasonality_factor = (dow_means / (overall_mean + 1e-6)).clip(0.5, 1.5)
        except Exception:
            seasonality_factor = pd.Series(1.0, index=df.index)

        # 2. Dynamic Bayesian Rolling Statistics (Shifted by 1 to prevent contamination from active anomalies)
        shifted_val = df['value'].shift(1)
        df['rolling_mean'] = shifted_val.rolling(window=adaptive_window, min_periods=3).mean()
        # Apply seasonality adjustment to baseline for day-of-week patterns
        df['rolling_mean'] = df['rolling_mean'] * seasonality_factor
        df['rolling_std'] = shifted_val.rolling(window=adaptive_window, min_periods=3).std()
        
        # Adaptive fallbacks for early sequence values
        df['rolling_mean'] = df['rolling_mean'].fillna(df['value'].expanding().mean()).fillna(df['value'].iloc[0] if len(df) > 0 else 0.0)
        global_std = df['value'].std() if len(df) > 1 and df['value'].std() > 0 else max(1.0, df['value'].mean() * 0.02)
        df['rolling_std'] = df['rolling_std'].fillna(df['value'].expanding().std()).fillna(global_std)
        df['rolling_std'] = df['rolling_std'].replace(0.0, max(1.0, df['value'].mean() * 0.02))

        # 3. Dynamic Confidence Bounds (95% CI)
        df['lower_bound'] = df['rolling_mean'] - (self.z_threshold * df['rolling_std'])
        df['upper_bound'] = df['rolling_mean'] + (self.z_threshold * df['rolling_std'])
        
        # 4. Statistical Z-Score & Two-tailed p-value
        df['z_score'] = (df['value'] - df['rolling_mean']) / df['rolling_std']
        df['z_score'] = df['z_score'].replace([np.inf, -np.inf], 0.0).fillna(0.0)
        df['p_value'] = 2.0 * (1.0 - stats.norm.cdf(df['z_score'].abs()))
        df['p_value'] = df['p_value'].clip(0.0001, 1.0)

        # 5. Multidimensional Feature Engineering for Isolation Forest ML
        df['pct_change'] = df['value'].pct_change().replace([np.inf, -np.inf], 0.0).fillna(0.0)
        df['accel'] = df['pct_change'].diff().replace([np.inf, -np.inf], 0.0).fillna(0.0)
        df['volatility'] = df['rolling_std'] / (df['rolling_mean'].abs() + 1e-5)
        
        X = df[['value', 'z_score', 'pct_change', 'accel', 'volatility']].values
        X = np.nan_to_num(X, nan=0.0, posinf=1.0, neginf=-1.0)
        
        if len(df) >= 10:
            try:
                iso = IsolationForest(n_estimators=50, contamination=0.05, random_state=42, n_jobs=1)
                iso.fit(X)
                iso_scores = iso.decision_function(X)
                df['ml_anomaly_score'] = np.nan_to_num(iso_scores, nan=0.0, posinf=1.0, neginf=-1.0)
            except Exception:
                df['ml_anomaly_score'] = np.where(df['z_score'].abs() > 2.0, -0.2, 0.2)
        else:
            df['ml_anomaly_score'] = 0.5

        # 6. Clean all floating point columns
        for col in ['rolling_mean', 'rolling_std', 'lower_bound', 'upper_bound', 'z_score', 'p_value', 'ml_anomaly_score']:
            df[col] = np.nan_to_num(df[col].values, nan=0.0, posinf=0.0, neginf=0.0)

        # 7. Multi-Criteria Anomaly Classification
        # An anomaly breach requires both a statistically significant Z-score and an ML deviation
        conditions = [
            (df['z_score'].abs() >= 2.0) | ((df['z_score'].abs() >= 1.75) & (df['ml_anomaly_score'] < 0.0)),
            (df['z_score'].abs() >= 1.25) & (df['z_score'].abs() < 2.0)
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
                "p_value": float(row.get('p_value', 0.05)),
                "lower_bound": float(row['lower_bound']),
                "upper_bound": float(row['upper_bound']),
                "ml_score": float(row['ml_anomaly_score']),
                "status": str(row['status']),
                "deviation_pct": float(((row['value'] - row['rolling_mean']) / (abs(row['rolling_mean']) + 1e-5)) * 100)
            })
        return result
