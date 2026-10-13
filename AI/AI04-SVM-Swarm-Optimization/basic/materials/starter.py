#!/usr/bin/env python3
"""Project 4 Basic starter. The test set is never used for model selection."""
from __future__ import annotations

import sys
import numpy as np
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVC


def read_dataset(tokens: list[str]):
    iterator = iter(tokens)
    n_train, n_dev, n_test, dimension = (int(next(iterator)) for _ in range(4))

    def read_labeled(count):
        features, labels = [], []
        for _ in range(count):
            features.append([float(next(iterator)) for _ in range(dimension)])
            labels.append(int(next(iterator)))
        return np.asarray(features), np.asarray(labels)

    x_train, y_train = read_labeled(n_train)
    x_dev, y_dev = read_labeled(n_dev)
    x_test = np.asarray([[float(next(iterator)) for _ in range(dimension)] for _ in range(n_test)])
    return x_train, y_train, x_dev, y_dev, x_test


def select_model(kernel: str, candidates: list[dict], x_train, y_train, x_dev, y_dev):
    """Select one candidate using development accuracy, then return the fitted model."""
    # TODO: for each candidate, create make_pipeline(StandardScaler(), SVC(...)).
    # Fit only on x_train/y_train and compare on x_dev/y_dev.
    raise NotImplementedError


def solve(tokens: list[str]):
    x_train, y_train, x_dev, y_dev, x_test = read_dataset(tokens)
    linear_candidates = [{"C": value} for value in (0.1, 1.0, 10.0)]
    rbf_candidates = [{"C": c, "gamma": gamma} for c in (0.5, 2.0, 10.0)
                      for gamma in (0.2, 1.0, 5.0)]
    linear = select_model("linear", linear_candidates, x_train, y_train, x_dev, y_dev)
    rbf = select_model("rbf", rbf_candidates, x_train, y_train, x_dev, y_dev)
    return np.concatenate((linear.predict(x_test), rbf.predict(x_test)))


if __name__ == "__main__":
    predictions = solve(sys.stdin.read().split())
    print(" ".join(str(int(value)) for value in predictions))
