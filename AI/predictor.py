"""Rule-first ranking with optional locally trained model scores."""

import json
import logging
import re
from pathlib import Path

from AI.active_learning import answer_bias
from AI.dataset import feature_vector
from AI.learner import preference_adjustment
from config.careers import careers
from config.recommendations import CAREER_SIGNALS

MODEL_DIR = Path(__file__).resolve().parent / "models"
ACTIVE_MODEL_FILE = MODEL_DIR / "active.json"


def load_active_model(model_dir=None):
    model_dir = Path(model_dir) if model_dir else MODEL_DIR
    active_model_file = model_dir / "active.json"
    if not active_model_file.is_file():
        return None, None, None
    try:
        pointer = json.loads(active_model_file.read_text(encoding="utf-8"))
        version = pointer.get("version")
        if not isinstance(version, str) or not re.fullmatch(r"[A-Za-z0-9._-]{1,120}", version):
            raise ValueError("Active model version is invalid")
        model_path = model_dir / f"{version}.joblib"
        if not model_path.is_file():
            raise FileNotFoundError("Active recommendation model file is missing")
        import joblib

        model = joblib.load(model_path)
        return model, version, None
    except (OSError, ImportError, ValueError):
        logging.exception("Unable to load the active career recommendation model")
        return None, None, "A stored model is unavailable; rule-based recommendations are in use."


def _empty_result(career_id):
    name = next(name for name, value in careers.items() if value == career_id)
    learning_skills = list(CAREER_SIGNALS[name][3])
    return {
        "id": career_id,
        "career": name,
        "name": name,
        "score": 0,
        "match_percentage": 0,
        "reasons": [
            "Included from your saved preferences; current answers do not yet match configured signals."
        ],
        "matched_subjects": [],
        "matched_interests": [],
        "relevant_skills": [],
        "matched_skills": [],
        "skill_gaps": learning_skills,
        "suggested_skills": learning_skills,
        "next_steps": ["Explore the career roadmap and check local guidance."],
        "preferred_career": False,
        "component_scores": {
            "subjects": 0,
            "interests": 0,
            "skills": 0,
            "preferred_career": 0,
            "education": 0,
        },
    }


def rank_recommendations(base_results, answers, preferences=None, model=None, limit=5):
    results_by_id = {item["id"]: dict(item) for item in base_results}
    for career_id in (preferences or {}).get("liked_career_ids", []):
        results_by_id.setdefault(career_id, _empty_result(career_id))
    results = list(results_by_id.values())
    model_scores = {}
    if model is not None and results:
        feature_rows = [feature_vector(answers, item["id"]) for item in results]
        probabilities = model.predict_proba(feature_rows)
        classes = list(model.classes_)
        if 1 not in classes:
            raise ValueError("Active recommendation model has no positive feedback class")
        positive_index = classes.index(1)
        model_scores = {
            item["id"]: round(float(probabilities[index][positive_index]) * 100, 1)
            for index, item in enumerate(results)
        }

    for item in results:
        rule_score = float(item.get("score", 0))
        preference_score, preference_reasons = preference_adjustment(
            preferences, item["id"]
        )
        answer_score, answer_reasons = answer_bias(answers, item["id"])
        learned_score = model_scores.get(item["id"], 0)
        combined = (
            0.75 * rule_score + 0.25 * learned_score
            if model is not None
            else rule_score
        )
        score = max(0, min(100, round(combined + preference_score + answer_score)))
        item["rule_score"] = round(rule_score)
        item["score"] = score
        item["match_percentage"] = score
        item["preference_adjustment"] = preference_score
        item["model_rank_score"] = model_scores.get(item["id"])
        item.setdefault("reasons", [])
        item["reasons"] = list(item["reasons"])
        item["reasons"].extend(preference_reasons)
        if answer_reasons:
            item["reasons"].append(
                "Your follow-up answer favored: " + ", ".join(answer_reasons) + "."
            )
        components = dict(item.get("component_scores", {}))
        components["learned_preference"] = preference_score + answer_score
        if model is not None:
            components["model_rank"] = learned_score
        item["component_scores"] = components

    results.sort(key=lambda item: (-item["score"], item["career"].casefold(), item["id"]))
    for index, item in enumerate(results):
        next_score = results[index + 1]["score"] if index + 1 < len(results) else 0
        margin = max(0, item["score"] - next_score)
        matched_groups = sum(
            bool(item.get(field))
            for field in ("matched_subjects", "matched_interests", "matched_skills")
        )
        if item.get("preferred_career"):
            matched_groups += 1
        if item.get("preference_adjustment"):
            matched_groups += 1
        uncertainty = max(
            0.0,
            min(1.0, 1 - min(1.0, matched_groups / 3) * 0.7 - min(1.0, margin / 25) * 0.3),
        )
        item["uncertainty"] = round(uncertainty, 2)
        item["confidence"] = (
            "higher" if uncertainty < 0.35
            else "moderate" if uncertainty < 0.7
            else "limited"
        )
        item["confidence_note"] = (
            "A heuristic based on answer coverage and ranking separation, not a probability."
        )
    return results[:limit]


def model_ranking_is_confident(results, minimum_margin=5.0):
    scores = sorted(
        (
            item["model_rank_score"]
            for item in results
            if item.get("model_rank_score") is not None
        ),
        reverse=True,
    )
    return len(scores) >= 2 and scores[0] - scores[1] >= minimum_margin
