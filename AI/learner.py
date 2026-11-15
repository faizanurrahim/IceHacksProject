"""Per-account recommendation preferences, separate from shared training data."""

from datetime import datetime, timezone

from pymongo.errors import DuplicateKeyError

from config.career_catalog import CAREER_STYLES
from config.careers import careers

PRIORITY_TO_STYLE = {
    "creative_work": "creative",
    "helping_people": "people",
    "analytical_work": "analytical",
    "hands_on_work": "hands_on",
    "independence": "independent",
    "structured_work": "structured",
}


def merge_preferences(current, feedback):
    current = current if isinstance(current, dict) else {}
    liked = set(current.get("liked_career_ids", []))
    rejected = set(current.get("rejected_career_ids", []))
    new_likes = set(feedback["liked_career_ids"])
    if feedback.get("alternate_career_id") is not None:
        new_likes.add(feedback["alternate_career_id"])
    new_rejections = set(feedback["rejected_career_ids"])
    liked.update(new_likes)
    rejected.update(new_rejections)
    liked.difference_update(new_rejections)
    rejected.difference_update(new_likes)

    preferred_work_styles = set(current.get("preferred_work_styles", []))
    preferred_work_styles.update(feedback.get("preferred_work_styles", []))
    priorities = set(current.get("priorities", []))
    priorities.update(feedback.get("priorities", []))
    return {
        "liked_career_ids": sorted(liked),
        "rejected_career_ids": sorted(rejected),
        "preferred_work_styles": sorted(preferred_work_styles),
        "priorities": sorted(priorities),
    }


def preference_adjustment(preferences, career_id):
    if not isinstance(preferences, dict):
        return 0, []
    score = 0
    reasons = []
    if career_id in preferences.get("liked_career_ids", []):
        score += 16
        reasons.append("You previously marked this career as interesting.")
    if career_id in preferences.get("rejected_career_ids", []):
        score -= 20
        reasons.append("You previously marked this career as not for you.")

    name = next((name for name, value in careers.items() if value == career_id), None)
    styles = set(CAREER_STYLES.get(name, ()))
    preferred_styles = set(preferences.get("preferred_work_styles", []))
    priorities = {
        PRIORITY_TO_STYLE[value]
        for value in preferences.get("priorities", [])
        if value in PRIORITY_TO_STYLE
    }
    matches = styles & (preferred_styles | priorities)
    if matches:
        score += min(6, 3 * len(matches))
        reasons.append("It fits work styles you said matter to you.")
    return score, reasons


def save_feedback(user_id, feedback, feedback_collection, learning_collection):
    record = {
        "user_id": user_id,
        **feedback,
        "created_at": datetime.now(timezone.utc),
        "preferences_applied": False,
    }
    query = {"user_id": user_id, "submission_id": feedback["submission_id"]}
    try:
        result = feedback_collection.update_one(
            query,
            {"$setOnInsert": record},
            upsert=True,
        )
    except DuplicateKeyError:
        existing = feedback_collection.find_one(query)
        if existing is None:
            raise
        if existing.get("preferences_applied") is True:
            return False
        is_new = False
    else:
        is_new = result.upserted_id is not None
        if not is_new:
            existing = feedback_collection.find_one(query)
            if existing is None:
                raise RuntimeError("Stored feedback record could not be retrieved")
            if existing.get("preferences_applied") is True:
                return False

    liked = feedback["liked_career_ids"] + (
        [feedback["alternate_career_id"]]
        if feedback["alternate_career_id"] is not None else []
    )
    updates = {"$addToSet": {}, "$pull": {}}
    if liked:
        updates["$addToSet"]["recommendation_preferences.liked_career_ids"] = {
            "$each": liked
        }
        updates["$pull"]["recommendation_preferences.rejected_career_ids"] = {
            "$in": liked
        }
    if feedback["rejected_career_ids"]:
        updates["$addToSet"]["recommendation_preferences.rejected_career_ids"] = {
            "$each": feedback["rejected_career_ids"]
        }
        updates["$pull"]["recommendation_preferences.liked_career_ids"] = {
            "$in": feedback["rejected_career_ids"]
        }
    if feedback["preferred_work_styles"]:
        updates["$addToSet"]["recommendation_preferences.preferred_work_styles"] = {
            "$each": feedback["preferred_work_styles"]
        }
    if feedback["priorities"]:
        updates["$addToSet"]["recommendation_preferences.priorities"] = {
            "$each": feedback["priorities"]
        }
    learning_collection.update_one(
        {"user_id": user_id},
        {"$setOnInsert": {"user_id": user_id}, **updates},
        upsert=True,
    )
    feedback_collection.update_one(
        query,
        {"$set": {"preferences_applied": True}},
    )
    return is_new


def withdraw_training_feedback(user_id, feedback_collection):
    result = feedback_collection.delete_many({
        "user_id": user_id,
        "training_consent": True,
    })
    return result.deleted_count
