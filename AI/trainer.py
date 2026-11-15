"""Offline, consent-only training and guarded promotion of recommendation models."""

import json
import logging
import os
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

from AI.dataset import build_training_dataset
from AI.evaluator import evaluate_model, evaluate_rules, promotion_is_better
from AI.predictor import load_active_model

MIN_TRAINING_USERS = 20
MIN_TRAINING_ROWS = 40
MODEL_DIR = Path(__file__).resolve().parent / "models"


def _fit_candidate(dataset):
    features = dataset["features"]
    labels = dataset["labels"]
    groups = dataset["groups"]
    if len(features) < MIN_TRAINING_ROWS or dataset["user_count"] < MIN_TRAINING_USERS:
        return None, None, "Not enough distinct consenting users or labeled feedback."
    if len(set(labels)) < 2:
        return None, None, "Feedback must include both liked and rejected careers."

    try:
        from sklearn.feature_extraction import DictVectorizer
        from sklearn.linear_model import LogisticRegression
        from sklearn.pipeline import Pipeline
        from sklearn.model_selection import GroupShuffleSplit
    except ImportError as exc:
        raise RuntimeError(
            "Install the optional AI dependency with: python -m pip install -r requirements-ai.txt"
        ) from exc

    splitter = GroupShuffleSplit(n_splits=30, test_size=0.25, random_state=17)
    split = None
    for train_indices, test_indices in splitter.split(features, labels, groups):
        if (
            len(set(groups[index] for index in train_indices)) >= 2
            and len(set(groups[index] for index in test_indices)) >= 2
            and len({labels[index] for index in train_indices}) == 2
            and len({labels[index] for index in test_indices}) == 2
        ):
            split = train_indices, test_indices
            break
    if split is None:
        return None, None, "Could not create a user-disjoint split with both feedback labels."

    train_indices, test_indices = split
    model = Pipeline([
        ("features", DictVectorizer()),
        ("classifier", LogisticRegression(max_iter=1000, random_state=17)),
    ])
    model.fit(
        [features[index] for index in train_indices],
        [labels[index] for index in train_indices],
        classifier__sample_weight=[
            dataset["sample_weights"][index] for index in train_indices
        ],
    )
    held_out_users = {groups[index] for index in test_indices}
    training_users = {groups[index] for index in train_indices}
    if held_out_users & training_users:
        raise RuntimeError("Recommendation model split leaked a user across partitions")
    held_out_cases = [
        case for case in dataset["cases"] if case["group"] in held_out_users
    ]
    return model, held_out_cases, None


def _write_json_atomically(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary_path = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            dir=path.parent,
            prefix=path.name + ".",
            suffix=".tmp",
            delete=False,
        ) as temporary:
            temporary_path = Path(temporary.name)
            json.dump(value, temporary, sort_keys=True)
            temporary.write("\n")
        os.replace(temporary_path, path)
    finally:
        if temporary_path is not None and temporary_path.exists():
            temporary_path.unlink()


def train_and_promote(records=None, model_dir=None):
    if records is None:
        from config.db import career_feedback

        records = list(career_feedback.find({"training_consent": True}))
    dataset = build_training_dataset(records)
    model, held_out_cases, reason = _fit_candidate(dataset)
    if model is None:
        return {
            "status": "insufficient_data",
            "reason": reason,
            "users": dataset["user_count"],
            "labeled_examples": len(dataset["features"]),
        }

    candidate_metrics = evaluate_model(model, held_out_cases)
    baseline_metrics = evaluate_rules(held_out_cases)
    model_dir = Path(model_dir) if model_dir else MODEL_DIR
    active_model, active_version, _ = load_active_model(model_dir)
    if not promotion_is_better(candidate_metrics, baseline_metrics):
        return {
            "status": "not_promoted",
            "reason": "The candidate did not improve the rule-based baseline safely.",
            "candidate": candidate_metrics,
            "rule_baseline": baseline_metrics,
        }
    if active_model is not None:
        active_metrics = evaluate_model(active_model, held_out_cases)
        if not promotion_is_better(candidate_metrics, active_metrics):
            return {
                "status": "not_promoted",
                "reason": "The candidate did not safely improve the active model.",
                "candidate": candidate_metrics,
                "active_model": active_metrics,
                "active_version": active_version,
            }

    model_dir.mkdir(parents=True, exist_ok=True)
    version = datetime.now(timezone.utc).strftime("careerpath-%Y%m%dT%H%M%SZ")
    version = f"{version}-{uuid4().hex[:8]}"
    try:
        import joblib
    except ImportError as exc:
        raise RuntimeError(
            "Install the optional AI dependency with: python -m pip install -r requirements-ai.txt"
        ) from exc
    model_path = model_dir / f"{version}.joblib"
    joblib.dump(model, model_path)
    metadata = {
        "version": version,
        "algorithm": "scikit-learn LogisticRegression with DictVectorizer",
        "trained_at": datetime.now(timezone.utc).isoformat(),
        "users": dataset["user_count"],
        "labeled_examples": len(dataset["features"]),
        "candidate_metrics": candidate_metrics,
        "rule_baseline_metrics": baseline_metrics,
    }
    try:
        _write_json_atomically(model_dir / "active.json", metadata)
    except OSError:
        model_path.unlink(missing_ok=True)
        logging.exception("Could not activate the evaluated recommendation model")
        raise
    return {"status": "promoted", **metadata}


if __name__ == "__main__":
    print(json.dumps(train_and_promote(), indent=2, sort_keys=True))
