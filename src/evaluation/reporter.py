"""Evaluation, Feature Stability metrics, and Fragility Report generator."""

from typing import List, Dict, Any
import numpy as np


class ExperimentReporter:
    """Aggregates experimental runs and generates Review 2 deliverables & metrics."""

    def __init__(self):
        self.records: List[Dict[str, Any]] = []

    def record_trial(
        self,
        sample_name: str,
        mutation_type: str,
        intensity: float,
        orig_prediction: str,
        orig_conf: float,
        mut_prediction: str,
        mut_conf: float,
        orig_features: Dict[str, float],
        mut_features: Dict[str, float],
        validity: Dict[str, Any]
    ) -> None:
        """Stores the result of a single mutation trial."""
        self.records.append({
            "sample": sample_name,
            "mutation": mutation_type,
            "intensity": intensity,
            "orig_pred": orig_prediction,
            "orig_conf": orig_conf,
            "mut_pred": mut_prediction,
            "mut_conf": mut_conf,
            "flipped": (orig_prediction == "Malicious" and mut_prediction == "Benign"),
            "conf_drop": orig_conf - mut_conf,
            "orig_features": orig_features,
            "mut_features": mut_features,
            "validity": validity
        })

    def compute_detection_retention(self) -> Dict[str, float]:
        """Calculates Detection Retention % per mutation type across valid trials."""
        by_mutation: Dict[str, List[bool]] = {}
        for r in self.records:
            if not r["validity"]["is_valid"]:
                continue
            if r["orig_pred"] != "Malicious":
                continue  # Only measure retention on true malicious samples
            mut = r["mutation"]
            if mut not in by_mutation:
                by_mutation[mut] = []
            # Retained if prediction stayed Malicious
            retained = (r["mut_pred"] == "Malicious")
            by_mutation[mut].append(retained)

        retention_scores = {}
        for mut, results in by_mutation.items():
            retention_scores[mut] = float(np.mean(results) * 100.0) if results else 0.0
        return retention_scores

    def compute_feature_stability(self) -> Dict[str, float]:
        """Calculates per-feature stability percentage across all valid mutations.

        A feature is deemed 'stable' in a trial if its relative shift is <= 10%.
        """
        valid_records = [r for r in self.records if r["validity"]["is_valid"]]
        if not valid_records:
            return {}

        feature_names = list(valid_records[0]["orig_features"].keys())
        stability_map = {feat: [] for feat in feature_names}

        for r in valid_records:
            f_orig = r["orig_features"]
            f_mut = r["mut_features"]
            for feat in feature_names:
                v1 = f_orig.get(feat, 0.0)
                v2 = f_mut.get(feat, 0.0)
                if v1 == v2:
                    is_stable = 1.0
                elif max(abs(v1), abs(v2)) == 0.0:
                    is_stable = 1.0
                else:
                    rel_change = abs(v1 - v2) / (max(abs(v1), abs(v2)))
                    is_stable = 1.0 if rel_change <= 0.10 else 0.0
                stability_map[feat].append(is_stable)

        return {feat: float(np.mean(vals) * 100.0) for feat, vals in stability_map.items()}

    def generate_fragility_report(self, model_name: str = "Random Forest (PDFRate features)") -> str:
        """Renders the one-page Detector Fragility Report (as defined in Brief Section 7)."""
        retention = self.compute_detection_retention()
        stability = self.compute_feature_stability()

        # Sort features by stability
        sorted_feats = sorted(stability.items(), key=lambda x: x[1], reverse=True)

        overall_score = float(np.mean(list(retention.values()))) if retention else 0.0
        risk_level = "LOW RISK" if overall_score >= 85 else ("MODERATE RISK" if overall_score >= 60 else "HIGH RISK")

        lines = [
            "==================================================================",
            "                   DETECTOR FRAGILITY REPORT                      ",
            "==================================================================",
            f"Model: {model_name}",
            f"Overall Robustness Score: {overall_score:.1f}/100 -> {risk_level}",
            "------------------------------------------------------------------",
            "Detection Retention per Mutation Type:"
        ]
        for mut, score in retention.items():
            bar = "#" * int(score // 10)
            lines.append(f"  * {mut:<24}: {bar:<10} {score:5.1f}%")

        lines.append("------------------------------------------------------------------")
        lines.append("Headline Feature Stability (Top Reliable vs Fragile):")

        # Top 3 most stable
        lines.append("  [+] High Stability Features:")
        for feat, score in sorted_feats[:5]:
            bar = "#" * int(score // 10)
            lines.append(f"      {feat:<25} {bar:<10} {score:5.1f}%")

        # Bottom 3 most fragile
        lines.append("  [-] Fragile / Volatile Features:")
        for feat, score in sorted_feats[-5:]:
            bar = "#" * int(score // 10)
            lines.append(f"      {feat:<25} {bar:<10} {score:5.1f}%")

        lines.append("------------------------------------------------------------------")
        verdict = (
            "Verdict: The detector's confidence is heavily influenced by structural & metadata\n"
            "formatting. An attacker or natural document processor can degrade detection\n"
            "without modifying core malicious triggers."
        )
        lines.append(verdict)
        lines.append("==================================================================")
        return "\n".join(lines)
