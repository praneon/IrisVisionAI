import pandas as pd
import json
from pathlib import Path
import numpy as np

# -------------------------
# CONFIG (v0.3.1 LOCKED)
# -------------------------
SEED = 69
TRAIN_RATIO = 0.70
VAL_RATIO = 0.15
TEST_RATIO = 0.15

METADATA_PATH = Path("data/metadata/metadata.csv")
SPLIT_DIR = Path("data/splits")

# -------------------------
# LOAD METADATA
# -------------------------
df = pd.read_csv(METADATA_PATH)

assert "subject_id" in df.columns, "subject_id column missing"
assert "split" in df.columns, "split column missing"

# -------------------------
# UNIQUE SUBJECTS
# -------------------------
subjects = sorted(df["subject_id"].unique())
num_subjects = len(subjects)

rng = np.random.default_rng(SEED)
rng.shuffle(subjects)

# -------------------------
# SPLIT CALCULATION
# -------------------------
n_train = int(num_subjects * TRAIN_RATIO)
n_val = int(num_subjects * VAL_RATIO)

train_subjects = subjects[:n_train]
val_subjects = subjects[n_train:n_train + n_val]
test_subjects = subjects[n_train + n_val:]

# -------------------------
# SAFETY CHECK
# -------------------------
assert len(set(train_subjects) & set(val_subjects)) == 0
assert len(set(train_subjects) & set(test_subjects)) == 0
assert len(set(val_subjects) & set(test_subjects)) == 0

# -------------------------
# ASSIGN SPLITS
# -------------------------
def assign_split(subject):
    if subject in train_subjects:
        return "train"
    elif subject in val_subjects:
        return "val"
    elif subject in test_subjects:
        return "test"
    else:
        raise ValueError("Unknown subject")

df["split"] = df["subject_id"].apply(assign_split)

# -------------------------
# OUTPUT DIRECTORIES
# -------------------------
SPLIT_DIR.mkdir(parents=True, exist_ok=True)

# -------------------------
# WRITE MANIFEST FILES
# -------------------------
(Path(SPLIT_DIR / "train_subjects.txt")
 .write_text("\n".join(map(str, train_subjects))))

(Path(SPLIT_DIR / "val_subjects.txt")
 .write_text("\n".join(map(str, val_subjects))))

(Path(SPLIT_DIR / "test_subjects.txt")
 .write_text("\n".join(map(str, test_subjects))))

# -------------------------
# SPLIT SUMMARY
# -------------------------
summary = {
    "seed": SEED,
    "total_subjects": num_subjects,
    "train_subjects": len(train_subjects),
    "val_subjects": len(val_subjects),
    "test_subjects": len(test_subjects),
    "total_images": len(df),
    "train_images": int((df["split"] == "train").sum()),
    "val_images": int((df["split"] == "val").sum()),
    "test_images": int((df["split"] == "test").sum())
}

with open(SPLIT_DIR / "split_summary.json", "w") as f:
    json.dump(summary, f, indent=2)

# -------------------------
# SAVE UPDATED METADATA
# -------------------------
df.to_csv(METADATA_PATH, index=False)

print("✅ v0.3.2 COMPLETE — Subject-disjoint split frozen.")
print(json.dumps(summary, indent=2))

