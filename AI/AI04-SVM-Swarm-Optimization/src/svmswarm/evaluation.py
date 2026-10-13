"""Final evaluation on the sealed MADELON validation set.

Per README: the validation set is *never* used during search.  Once a candidate
(mask, C, gamma) is chosen, we refit scaler+SVM on the full training set (with
that mask) and evaluate once on validation.
"""
from __future__ import annotations

import numpy as np
from sklearn.metrics import (accuracy_score, confusion_matrix, f1_score,
                             precision_score, recall_score)
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVC

POS = 1.0


def classification_metrics(y_true: np.ndarray, y_pred: np.ndarray) -> dict[str, float]:
    """accuracy / precision / recall / f1 (positive class = +1)."""
    return {
        "accuracy": float(accuracy_score(y_true, y_pred)),
        "precision": float(precision_score(y_true, y_pred, pos_label=POS, zero_division=0)),
        "recall": float(recall_score(y_true, y_pred, pos_label=POS, zero_division=0)),
        "f1": float(f1_score(y_true, y_pred, pos_label=POS, zero_division=0)),
    }


def final_evaluate(X_train: np.ndarray, y_train: np.ndarray,
                   X_valid: np.ndarray, y_valid: np.ndarray,
                   C: float, gamma: float,
                   mask: np.ndarray | None = None) -> dict:
    """Refit on the full training set (masked columns) and score on validation.

    ``mask`` is an optional boolean / 0-1 array over the d features; None keeps
    every feature.  The scaler is fitted on training rows only.
    """
    sel = np.arange(X_train.shape[1]) if mask is None else np.flatnonzero(mask > 0.5)
    X_tr = X_train[:, sel]
    X_va = X_valid[:, sel]
    pipe = Pipeline([("scaler", StandardScaler()),
                     ("svm", SVC(kernel="rbf", C=C, gamma=gamma))])
    pipe.fit(X_tr, y_train)
    y_pred = pipe.predict(X_va)
    svc = pipe.named_steps["svm"]
    return {
        **classification_metrics(y_valid, y_pred),
        "n_selected": int(sel.size),
        "n_support_vector": int(getattr(svc, "n_support_", [0])[0])
        if hasattr(svc, "n_support_") else int(svc.support_.size),
        "confusion_matrix": confusion_matrix(y_valid, y_pred, labels=[-1.0, 1.0]).tolist(),
    }


def default_svm_evaluate(X_train: np.ndarray, y_train: np.ndarray,
                         X_valid: np.ndarray, y_valid: np.ndarray) -> dict:
    """sklearn defaults (C=1, kernel='rbf', gamma='scale') on all features."""
    pipe = Pipeline([("scaler", StandardScaler()),
                     ("svm", SVC())])
    pipe.fit(X_train, y_train)
    y_pred = pipe.predict(X_valid)
    return classification_metrics(y_valid, y_pred)
