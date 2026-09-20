"""
One-time export: converts the scikit-learn artifacts in ./original into light files
that the web server can load without scikit-learn.

    pip install scikit-learn==1.6.1 joblib numpy
    python build_assets.py

Outputs: model/forest.npz  (the Random Forest trees as plain numpy arrays)
         model/meta.json   (encoder classes, state->district/crop maps, remedies)
Why: a loaded sklearn forest needs ~350 MB RAM; this format needs ~100 MB, so it fits
on free hosting tiers (512 MB) and starts faster.
"""
import ast, json, re
from pathlib import Path
import joblib, numpy as np

SRC, OUT = Path("original"), Path("model")
OUT.mkdir(exist_ok=True)

model    = joblib.load(SRC / "pest_prediction_model.pkl")
enc      = joblib.load(SRC / "feature_encoders.pkl")
pest_enc = joblib.load(SRC / "target_encoder.pkl")

feature, thr, left, right, leaf_row, probas, roots = [], [], [], [], [], [], []
offset = row = 0
for est in model.estimators_:
    t = est.tree_
    is_leaf = t.children_left == -1
    roots.append(offset)
    feature.append(np.where(is_leaf, 0, t.feature).astype(np.int16))
    thr.append(t.threshold.astype(np.float64))
    left.append(np.where(is_leaf, -1, t.children_left + offset).astype(np.int32))
    right.append(np.where(is_leaf, -1, t.children_right + offset).astype(np.int32))
    v = t.value[is_leaf, 0, :]
    probas.append((v / v.sum(axis=1, keepdims=True)).astype(np.float32))
    lr = np.full(t.node_count, -1, dtype=np.int32)
    lr[is_leaf] = np.arange(row, row + is_leaf.sum())
    leaf_row.append(lr)
    offset += t.node_count
    row += int(is_leaf.sum())

np.savez_compressed(
    OUT / "forest.npz",
    feature=np.concatenate(feature), threshold=np.concatenate(thr),
    left=np.concatenate(left), right=np.concatenate(right),
    leaf_row=np.concatenate(leaf_row), leaf_proba=np.concatenate(probas),
    roots=np.array(roots, dtype=np.int32),
)

# ---- metadata: UI maps come from the old Streamlit file, remedies from the old API file
fe = Path(SRC / "frontend.py").read_text(encoding="utf-8")
maps = {}
exec(fe[fe.index("STATE_DISTRICT_MAP = {"):fe.index("# EXACT seasons")], maps)
be = Path(SRC / "app.py").read_text(encoding="utf-8")
remedies = ast.literal_eval(re.search(r"REMEDIES = (\{.*?\n\})", be, re.S).group(1))

valid_d = set(enc["district"].classes_)
state_districts = {s: [d for d in ds if d in valid_d] for s, ds in maps["STATE_DISTRICT_MAP"].items()}

meta = {
    "classes": {k: [str(c) for c in enc[k].classes_] for k in ("state", "district", "crop", "season")},
    "pests": [str(c) for c in pest_enc.classes_],
    "state_districts": state_districts,
    "state_crops": maps["STATE_CROPS_MAP"],
    "remedies": remedies,
}
(OUT / "meta.json").write_text(json.dumps(meta, ensure_ascii=False), encoding="utf-8")
print("done:", (OUT / "forest.npz").stat().st_size / 1e6, "MB")
