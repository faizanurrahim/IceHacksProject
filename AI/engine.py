"""Orchestrates CareerPath's rule-based and optional learned recommendations."""

import logging

from AI.active_learning import select_next_question
from AI.predictor import (
    load_active_model,
    model_ranking_is_confident,
    rank_recommendations,
)
from config.career_catalog import quiz_recommendations
from config.recommendations import recommend_careers

CONFIDENCE_NOTE = (
    "Match scores are exploration aids. Confidence is a heuristic, not a probability "
    "or a claim about career success."
)


def _include_preferred_and_liked(
    ranked,
    limit,
    preferred_names,
    preferences,
    preserve_all_preferred=False,
):
    selected = ranked[:limit]
    required_names = set(preferred_names)
    for name in preferred_names:
        preferred = next((item for item in ranked if item["career"] == name), None)
        if preferred and all(item["id"] != preferred["id"] for item in selected):
            if preserve_all_preferred or len(selected) < limit:
                selected.append(preferred)
            elif selected:
                selected[-1] = preferred

    liked_ids = (preferences or {}).get("liked_career_ids", [])
    liked = next(
        (
            item for item in ranked
            if item["id"] in liked_ids
            and all(selected_item["id"] != item["id"] for selected_item in selected)
        ),
        None,
    )
    if liked:
        if len(selected) < limit:
            selected.append(liked)
        elif selected and selected[-1]["career"] not in required_names:
            selected[-1] = liked
    selected.sort(key=lambda item: (-item["score"], item["career"].casefold()))
    return selected


def _rank(base_results, answers, preferences, model):
    try:
        ranked = rank_recommendations(
            base_results,
            answers,
            preferences=preferences,
            model=model,
            limit=65,
        )
    except (AttributeError, IndexError, TypeError, ValueError):
        if model is None:
            raise
        logging.exception("Active recommendation model failed; using the rule engine")
        return (
            rank_recommendations(base_results, answers, preferences=preferences, limit=65),
            False,
            "The local model could not rank this quiz; rule-based recommendations are in use.",
        )
    if model is not None and not model_ranking_is_confident(ranked):
        return (
            rank_recommendations(base_results, answers, preferences=preferences, limit=65),
            False,
            "The local model did not clearly separate its leading candidates; rule-based recommendations are in use.",
        )
    return ranked, model is not None, None


def recommend(answers, preferences=None, limit=5):
    base_results = quiz_recommendations(answers, limit=65)
    model, model_version, model_notice = load_active_model()
    ranked, model_used, fallback_notice = _rank(
        base_results,
        answers,
        preferences,
        model,
    )
    preferred_career = answers.get("preferred_career")
    recommendations = _include_preferred_and_liked(
        ranked,
        limit,
        [preferred_career] if preferred_career else [],
        preferences,
    )
    follow_up_question = select_next_question(answers, recommendations)
    mode = (
        "hybrid" if model_used
        else "personalized_rules" if preferences
        else "rules"
    )
    return {
        "recommendations": recommendations,
        "recommendation_engine": {
            "mode": mode,
            "model_version": model_version if model_used else None,
            "notice": fallback_notice or model_notice or CONFIDENCE_NOTE,
        },
        "follow_up_question": follow_up_question,
    }


def recommend_profile(description, preferences=None, limit=5):
    profile_answers = {
        "education": description.get("education", ""),
        "country": "Other / not listed",
        "subjects": description.get("subjects", []),
        "interests": description.get("interests", []),
        "skills": description.get("skills", []),
        "work_styles": [],
        "preferred_career": (description.get("preferred_careers") or [""])[0],
        "asked_questions": [],
        "follow_up_answers": [],
    }
    base_results = recommend_careers(description, limit=65)
    model, model_version, model_notice = load_active_model()
    ranked, model_used, fallback_notice = _rank(
        base_results,
        profile_answers,
        preferences,
        model,
    )
    recommendations = _include_preferred_and_liked(
        ranked,
        limit,
        description.get("preferred_careers", []),
        preferences,
        preserve_all_preferred=True,
    )
    mode = (
        "hybrid" if model_used
        else "personalized_rules" if preferences
        else "rules"
    )
    return {
        "recommendations": recommendations,
        "recommendation_engine": {
            "mode": mode,
            "model_version": model_version if model_used else None,
            "notice": fallback_notice or model_notice or CONFIDENCE_NOTE,
        },
    }
