"""
IGRIS Phase 24 Language Quality Reporter
=========================================
Generates confusion matrices and classification reports from labeled test data.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Tuple


@dataclass
class ConfusionEntry:
    true_label: str
    pred_label: str
    count: int


@dataclass
class ClassificationReport:
    total: int
    correct: int
    accuracy: float
    per_class: Dict[str, Dict[str, float]]  # class -> {precision, recall, f1, support}
    confusion_matrix: List[ConfusionEntry]


class LanguageQualityReporter:
    """Generates classification reports from (true_label, pred_label) pairs."""

    def report(self, predictions: List[Tuple[str, str]]) -> ClassificationReport:
        total = len(predictions)
        correct = sum(1 for t, p in predictions if t == p)
        accuracy = correct / total if total > 0 else 0.0

        labels = sorted(set(t for t, _ in predictions) | set(p for _, p in predictions))
        cm: Dict[Tuple[str, str], int] = {}
        for t, p in predictions:
            cm[(t, p)] = cm.get((t, p), 0) + 1

        per_class: Dict[str, Dict[str, float]] = {}
        for label in labels:
            tp = cm.get((label, label), 0)
            fp = sum(cm.get((other, label), 0) for other in labels if other != label)
            fn = sum(cm.get((label, other), 0) for other in labels if other != label)
            support = tp + fn
            precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
            recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
            f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0.0
            per_class[label] = {"precision": round(precision, 4), "recall": round(recall, 4),
                                "f1": round(f1, 4), "support": support}

        confusion_entries = [ConfusionEntry(t, p, c) for (t, p), c in sorted(cm.items())]
        return ClassificationReport(total, correct, round(accuracy, 4), per_class, confusion_entries)
