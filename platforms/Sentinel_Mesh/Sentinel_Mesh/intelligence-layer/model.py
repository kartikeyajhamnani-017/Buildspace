"""
 ML Anomaly Detector (Layer 2)
Isolation Forest per-protocol anomaly detection.
"""

import os
import json
import pickle
import numpy as np
from datetime import datetime
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score,
    f1_score, confusion_matrix, classification_report
)
import config
from features import extract_all_features, get_feature_names, features_to_vector


class MLAnomalyDetector:
    """
    Layer 2: Isolation Forest anomaly detection.
    One instance per protocol (HTTP / SSH / DNS).
    """

    def __init__(self, model_path=None, protocol="HTTP"):
        self.protocol      = protocol.upper().strip()
        self.feature_names = get_feature_names(protocol=self.protocol)
        self.scaler        = StandardScaler()
        self.is_trained    = False
        self.stats         = {'total_predictions': 0, 'anomalies_detected': 0}

        if model_path and os.path.exists(model_path):
            self.load_model(model_path)
        else:
            self.model = IsolationForest(
                contamination=config.ISOLATION_FOREST_CONTAMINATION,
                n_estimators=config.ISOLATION_FOREST_N_ESTIMATORS,
                random_state=config.RANDOM_STATE,
                n_jobs=-1,
            )

    # ── Training ───────────────────────────────────────────────────────────────

    def train(self, payloads, labels=None):
        """
        Fit the Isolation Forest on a list of payload strings.

        Args:
            payloads (list[str]): Raw payload strings.
            labels   (list[int]): Optional ground-truth labels (1=malicious, 0=benign).

        Returns:
            dict: Basic training statistics.
        """
        X = self._extract_matrix(payloads)
        X_scaled = self.scaler.fit_transform(X)
        self.model.fit(X_scaled)
        self.is_trained = True

        if labels is not None:
            return self.evaluate(payloads, labels)

        return {'samples': len(payloads)}

    # ── Prediction ─────────────────────────────────────────────────────────────

    def predict(self, payload):
        """
        Score a single payload.

        Returns:
            dict: is_malicious, confidence, anomaly_score, features, layer.
        """
        if not self.is_trained:
            raise ValueError("Model not trained. Call train() or load_model() first.")

        self.stats['total_predictions'] += 1

        features       = extract_all_features(payload, protocol=self.protocol)
        feature_vector = features_to_vector(features, self.feature_names)
        X_scaled       = self.scaler.transform(np.array([feature_vector]))

        prediction    = self.model.predict(X_scaled)[0]          # -1 or 1
        anomaly_score = self.model.score_samples(X_scaled)[0]
        confidence    = max(0.0, min(1.0, -anomaly_score + 0.5))
        is_malicious  = prediction == -1

        if is_malicious:
            self.stats['anomalies_detected'] += 1

        return {
            'is_malicious':  is_malicious,
            'confidence':    confidence if is_malicious else 0.0,
            'anomaly_score': float(anomaly_score),
            'features':      features,
            'layer':         'ML Anomaly Detection (Layer 2)',
        }

    # ── Evaluation ─────────────────────────────────────────────────────────────

    def evaluate(self, payloads, labels):
        """
        Compute full classification metrics on a labelled dataset.

        Args:
            payloads (list[str]): Raw payload strings.
            labels   (list[int]): Ground-truth labels (1=malicious, 0=benign).

        Returns:
            dict: accuracy, precision, recall, f1, FPR, FNR,
                  confusion matrix, classification report, counts.
        """
        if not self.is_trained:
            raise ValueError("Model not trained. Call train() or load_model() first.")

        X        = self._extract_matrix(payloads)
        X_scaled = self.scaler.transform(X)
        raw_preds = self.model.predict(X_scaled)
        preds     = [1 if p == -1 else 0 for p in raw_preds]

        accuracy  = accuracy_score(labels, preds)
        precision = precision_score(labels, preds, zero_division=0)
        recall    = recall_score(labels, preds, zero_division=0)
        f1        = f1_score(labels, preds, zero_division=0)

        cm              = confusion_matrix(labels, preds)
        tn, fp, fn, tp  = cm.ravel()
        fpr = fp / (fp + tn) if (fp + tn) > 0 else 0.0
        fnr = fn / (fn + tp) if (fn + tp) > 0 else 0.0

        return {
            'protocol':          self.protocol,
            'samples':           len(payloads),
            'benign_count':      labels.count(0),
            'malicious_count':   labels.count(1),
            'accuracy':          round(accuracy,  4),
            'precision':         round(precision, 4),
            'recall':            round(recall,    4),
            'f1_score':          round(f1,        4),
            'false_positive_rate': round(fpr,     4),
            'false_negative_rate': round(fnr,     4),
            'true_positives':    int(tp),
            'true_negatives':    int(tn),
            'false_positives':   int(fp),
            'false_negatives':   int(fn),
            'confusion_matrix':  cm.tolist(),
            'classification_report': classification_report(
                labels, preds,
                target_names=['benign', 'malicious'],
                zero_division=0,
            ),
        }

    # ── Persistence ────────────────────────────────────────────────────────────

    def save_model(self, filename=None, model_path=None, scaler_path=None):
        """Save model and scaler .pkl pair."""
        model_path, scaler_path = self._resolve_paths(filename, model_path, scaler_path)
        os.makedirs(os.path.dirname(model_path), exist_ok=True)
        with open(model_path,  'wb') as f: pickle.dump(self.model,  f)
        with open(scaler_path, 'wb') as f: pickle.dump(self.scaler, f)

    def load_model(self, filename=None, model_path=None, scaler_path=None):
        """Load model and scaler .pkl pair."""
        model_path, scaler_path = self._resolve_paths(filename, model_path, scaler_path)
        with open(model_path,  'rb') as f: self.model  = pickle.load(f)
        with open(scaler_path, 'rb') as f: self.scaler = pickle.load(f)
        self.is_trained = True

    # ── Stats ──────────────────────────────────────────────────────────────────

    def get_stats(self):
        total = self.stats['total_predictions']
        return {
            'total_predictions':  total,
            'anomalies_detected': self.stats['anomalies_detected'],
            'anomaly_rate':       self.stats['anomalies_detected'] / total if total else 0.0,
        }

    # ── Internal helpers ───────────────────────────────────────────────────────

    def _extract_matrix(self, payloads):
        """Extract and stack feature vectors for a list of payloads."""
        X = []
        for payload in payloads:
            features = extract_all_features(payload, protocol=self.protocol)
            X.append(features_to_vector(features, self.feature_names))
        return np.array(X)

    def _resolve_paths(self, filename, model_path, scaler_path):
        """Resolve model and scaler file paths from arguments or config."""
        if filename:
            base        = os.path.join(config.MODEL_DIR, os.path.basename(filename).replace('.pkl', ''))
            model_path  = f"{base}.pkl"
            scaler_path = f"{base}_scaler.pkl"
        else:
            model_path  = model_path  or config.MODEL_PATHS[self.protocol]
            scaler_path = scaler_path or config.SCALER_PATHS[self.protocol]
        return model_path, scaler_path


# ==============================================================================
# METRICS PERSISTENCE  (standalone — called from train_model.py)
# ==============================================================================

def save_metrics(protocol, metrics, metrics_dir=None):
    """
    Write evaluation metrics to disk as a timestamped JSON + TXT pair.

    Args:
        protocol    (str):  'HTTP', 'SSH', or 'DNS'.
        metrics     (dict): Output of MLAnomalyDetector.evaluate().
        metrics_dir (str):  Target directory (defaults to config.METRICS_DIR).

    Returns:
        tuple: (json_path, txt_path)
    """
    if metrics_dir is None:
        metrics_dir = getattr(
            config, 'METRICS_DIR',
            os.path.join(os.path.dirname(os.path.abspath(config.__file__)), 'metrics')
        )

    os.makedirs(metrics_dir, exist_ok=True)
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    base      = os.path.join(metrics_dir, f'metrics_{protocol.lower()}_{timestamp}')

    # JSON — machine-readable (exclude verbose classification_report string)
    json_path    = f"{base}.json"
    json_metrics = {k: v for k, v in metrics.items() if k != 'classification_report'}
    with open(json_path, 'w') as f:
        json.dump(json_metrics, f, indent=2)

    # TXT — human-readable
    txt_path = f"{base}.txt"
    with open(txt_path, 'w') as f:
        f.write("SENTINEL ML ENGINE v2.0 — METRICS REPORT\n")
        f.write(f"{'='*60}\n")
        f.write(f"Protocol  : {protocol}\n")
        f.write(f"Timestamp : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"{'='*60}\n\n")
        f.write("DATASET\n")
        f.write(f"  Total    : {metrics['samples']}\n")
        f.write(f"  Benign   : {metrics['benign_count']}\n")
        f.write(f"  Malicious: {metrics['malicious_count']}\n\n")
        f.write("PERFORMANCE\n")
        f.write(f"  Accuracy : {metrics['accuracy']:.1%}\n")
        f.write(f"  Precision: {metrics['precision']:.1%}\n")
        f.write(f"  Recall   : {metrics['recall']:.1%}\n")
        f.write(f"  F1 Score : {metrics['f1_score']:.1%}\n\n")
        f.write("ERROR RATES\n")
        f.write(f"  False Positive: {metrics['false_positive_rate']:.1%}\n")
        f.write(f"  False Negative: {metrics['false_negative_rate']:.1%}\n\n")
        f.write("CONFUSION MATRIX\n")
        f.write(f"  True  Positives: {metrics['true_positives']}\n")
        f.write(f"  True  Negatives: {metrics['true_negatives']}\n")
        f.write(f"  False Positives: {metrics['false_positives']}\n")
        f.write(f"  False Negatives: {metrics['false_negatives']}\n\n")
        f.write("CLASSIFICATION REPORT\n")
        f.write(metrics['classification_report'])

    return json_path, txt_path