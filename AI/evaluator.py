"""User-grouped ranking metrics for learned and rule-based recommendations."""

import math

from AI.dataset import feature_vector
from config.career_catalog import quiz_recommendations
from config.careers import careers


def ranking_metrics(ranked_ids, relevant_ids, k=5):
    relevant = set(relevant_ids)
    if not relevant or k < 1:
        return {"precision@5": 0.0, "recall@5": 0.0, "ndcg@5": 0.0}
    top = list(ranked_ids[:k])
    hits = sum(career_id in relevant for career_id in top)
    dcg = sum(
        1 / math.log2(position + 2)
        for position, career_id in enumerate(top)
        if career_id in relevant
    )
    ideal_hits = min(len(relevant), k)
    ideal_dcg = sum(1 / math.log2(position + 2) for position in range(ideal_hits))
    return {
        "precision@5": round(hits / k, 4),
        "recall@5": round(hits / len(relevant), 4),
        "ndcg@5": round(dcg / ideal_dcg, 4) if ideal_dcg else 0.0,
    }


def _aggregate(case_metrics):
    if not case_metrics:
        return {
            "precision@5": 0.0,
            "recall@5": 0.0,
            "ndcg@5": 0.0,
            "cases": 0,
        }
    per_group = {}
    for group, metrics in case_metrics:
        per_group.setdefault(group, []).append(metrics)
    group_metrics = [
        {
            key: sum(item[key] for item in metrics) / len(metrics)
            for key in ("precision@5", "recall@5", "ndcg@5")
        }
        for metrics in per_group.values()
    ]
    return {
        key: round(sum(item[key] for item in group_metrics) / len(group_metrics), 4)
        for key in ("precision@5", "recall@5", "ndcg@5")
    } | {"cases": len(case_metrics), "users": len(group_metrics)}


def evaluate_rules(cases):
    metrics = []
    for case in cases:
        results = quiz_recommendations(case["answers"], limit=65)
        score_by_id = {item["id"]: item["score"] for item in results}
        ranked = sorted(
            case["candidate_ids"],
            key=lambda career_id: (
                -score_by_id.get(career_id, 0),
                next(name.casefold() for name, value in careers.items() if value == career_id),
                career_id,
            ),
        )
        metrics.append((case["group"], ranking_metrics(ranked, case["relevant_ids"])))
    return _aggregate(metrics)


def evaluate_model(model, cases):
    metrics = []
    for case in cases:
        base_results = quiz_recommendations(case["answers"], limit=65)
        rule_scores = {item["id"]: item["score"] for item in base_results}
        ids = case["candidate_ids"]
        rows = [feature_vector(case["answers"], career_id) for career_id in ids]
        probabilities = model.predict_proba(rows)
        classes = list(model.classes_)
        if 1 not in classes:
            raise ValueError("Recommendation model has no positive feedback class")
        positive_index = classes.index(1)
        scores = {
            career_id: 0.75 * rule_scores.get(career_id, 0)
            + 0.25 * float(probabilities[index][positive_index]) * 100
            for index, career_id in enumerate(ids)
        }
        ranked = sorted(
            ids,
            key=lambda career_id: (
                -scores[career_id],
                next(name.casefold() for name, value in careers.items() if value == career_id),
                career_id,
            ),
        )
        metrics.append((case["group"], ranking_metrics(ranked, case["relevant_ids"])))
    return _aggregate(metrics)


def promotion_is_better(candidate, baseline, minimum_ndcg_gain=0.01):
    return (
        candidate["ndcg@5"] >= baseline["ndcg@5"] + minimum_ndcg_gain
        and candidate["precision@5"] >= baseline["precision@5"] - 0.02
        and candidate["recall@5"] >= baseline["recall@5"] - 0.02
    )
