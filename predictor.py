"""Numpy-only Random Forest inference (no scikit-learn needed at runtime)."""
import numpy as np


class CompactForest:
    def __init__(self, path):
        d = np.load(path)
        self.feature, self.threshold = d["feature"], d["threshold"]
        self.left, self.right = d["left"], d["right"]
        self.leaf_row, self.leaf_proba = d["leaf_row"], d["leaf_proba"]
        self.roots = d["roots"]

    def predict_proba(self, x):
        # sklearn casts inputs to float32 before comparing with thresholds
        x = np.asarray(x, dtype=np.float32).astype(np.float64)
        nodes = self.roots.copy()                      # one pointer per tree
        while True:
            lf = self.left[nodes]
            active = lf != -1
            if not active.any():
                break
            go_left = x[self.feature[nodes]] <= self.threshold[nodes]
            nxt = np.where(go_left, lf, self.right[nodes])
            nodes = np.where(active, nxt, nodes)
        return self.leaf_proba[self.leaf_row[nodes]].astype(np.float64).mean(axis=0)
