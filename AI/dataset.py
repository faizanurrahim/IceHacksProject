"""Validation and feature preparation for consented career feedback."""

from collections import Counter
import hashlib
import hmac
import os

from config.career_catalog import CAREER_STYLES, COUNTRY_GUIDANCE
from config.careers import careers
from config.recommendations import CAREER_SIGNALS, _normalise

WORK_STYLES = {"people", "analytical", "hands_on", "creative", "structured", "independent"}
PRIORITIES = {
    "creative_work",
    "helping_people",
    "analytical_work",
    "hands_on_work",
    "independence",
    "structured_work",
}
TRAINING_VOCABULARY = {
    "education": {
        "middle school", "grade 9", "grade 10", "grade 11", "grade 12",
        "intermediate", "bachelor's degree", "master's degree", "doctorate",
    },
    "subjects": {
        "mathematics", "computer science", "biology", "chemistry", "physics",
        "english", "art and design", "business", "economics", "geography",
        "law and history", "physical education",
    },
    "interests": {
        "technology and programming", "health and helping people",
        "design and creativity", "science and research", "business and finance",
        "teaching and learning", "animals and environment", "building and engineering",
        "writing and storytelling", "justice and public service", "sports and fitness",
        "food and cooking",
    },
    "skills": {
        "problem solving", "communication", "programming", "creativity and design",
        "research and analysis", "teamwork and empathy", "organization and planning",
        "hands-on building", "writing",
    },
}
FEEDBACK_TYPES = {"suitable", "some_relevant", "not_suitable", "different_career"}
FEEDBACK_REASONS = {
    "unrelated",
    "missing_skills",
    "education_path",
    "work_style",
    "other",
}
ANSWER_FIELDS = {
    "education",
    "country",
    "subjects",
    "interests",
    "skills",
    "work_styles",
    "preferred_career",
}


def _career_ids(values, field, minimum=0, maximum=65):
    if (
        not isinstance(values, list)
        or not minimum <= len(values) <= maximum
        or not all(
            isinstance(value, int) and not isinstance(value, bool)
            and value in careers.values()
            for value in values
        )
        or len(set(values)) != len(values)
    ):
        raise ValueError(f"{field} must contain distinct career IDs")
    return values


def normalize_quiz_answers(raw, strict_training_vocabulary=False):
    if not isinstance(raw, dict):
        raise ValueError("Answers must be an object")
    allowed = ANSWER_FIELDS | {"follow_up_answers", "asked_questions"}
    if set(raw) - allowed:
        raise ValueError("One or more quiz fields are invalid")

    education = raw.get("education", "")
    if not isinstance(education, str) or len(education.strip()) > 80:
        raise ValueError("Choose a valid education level")
    if strict_training_vocabulary and education.strip().casefold() not in TRAINING_VOCABULARY["education"] | {""}:
        raise ValueError("Education answer is not in the supported quiz choices")
    country = raw.get("country", "Other / not listed")
    if not isinstance(country, str) or country not in COUNTRY_GUIDANCE:
        raise ValueError("Choose a supported country or Other / not listed")
    preferred_career = raw.get("preferred_career", "")
    if not isinstance(preferred_career, str) or len(preferred_career.strip()) > 100:
        raise ValueError("Choose a valid dream career")
    preferred_career = preferred_career.strip()
    if preferred_career:
        preferred_career = next(
            (name for name in careers if name.casefold() == preferred_career.casefold()),
            None,
        )
        if preferred_career is None:
            raise ValueError("Choose a career from the list")

    answers = {
        "education": education.strip(),
        "country": country,
        "preferred_career": preferred_career or "",
    }
    for field in ("subjects", "interests", "skills", "work_styles"):
        values = raw.get(field, [])
        if (
            not isinstance(values, list)
            or len(values) > 12
            or not all(
                isinstance(value, str) and value.strip() and len(value.strip()) <= 80
                for value in values
            )
        ):
            raise ValueError(f"Choose up to 12 valid {field.replace('_', ' ')}")
        answers[field] = list(dict.fromkeys(value.strip() for value in values))
        vocabulary_field = field if field in TRAINING_VOCABULARY else None
        if strict_training_vocabulary and vocabulary_field:
            if any(
                value.casefold() not in TRAINING_VOCABULARY[vocabulary_field]
                for value in answers[field]
            ):
                raise ValueError(f"{field.title()} answers must use supported quiz choices")
    if set(answers["work_styles"]) - WORK_STYLES:
        raise ValueError("One or more work styles are invalid")

    from AI.active_learning import is_valid_answer, question_ids

    asked = raw.get("asked_questions", [])
    if (
        not isinstance(asked, list)
        or len(asked) > 3
        or not all(isinstance(item, str) and item in question_ids() for item in asked)
        or len(set(asked)) != len(asked)
    ):
        raise ValueError("Follow-up question history is invalid")
    follow_up_answers = raw.get("follow_up_answers", [])
    if not isinstance(follow_up_answers, list) or len(follow_up_answers) > 3:
        raise ValueError("Answer up to three follow-up questions")
    normalized_follow_ups = []
    follow_up_ids = []
    for item in follow_up_answers:
        if (
            not isinstance(item, dict)
            or set(item) != {"question_id", "choice_id"}
            or not isinstance(item["question_id"], str)
            or not isinstance(item["choice_id"], str)
            or not is_valid_answer(item["question_id"], item["choice_id"])
        ):
            raise ValueError("One or more follow-up answers are invalid")
        if item["question_id"] not in asked:
            raise ValueError("Follow-up answer is missing its question history")
        if item["question_id"] in follow_up_ids:
            raise ValueError("A follow-up question can only be answered once")
        follow_up_ids.append(item["question_id"])
        normalized_follow_ups.append({
            "question_id": item["question_id"],
            "choice_id": item["choice_id"],
        })
    answers["asked_questions"] = asked
    answers["follow_up_answers"] = normalized_follow_ups
    return answers


def validate_feedback(raw):
    fields = {
        "submission_id",
        "answers",
        "recommended_career_ids",
        "liked_career_ids",
        "rejected_career_ids",
        "alternate_career_id",
        "overall_feedback",
        "reason",
        "preferred_work_styles",
        "priorities",
        "training_consent",
    }
    if not isinstance(raw, dict) or set(raw) != fields:
        raise ValueError("Feedback request fields are invalid")

    submission_id = raw["submission_id"]
    if (
        not isinstance(submission_id, str)
        or len(submission_id) != 36
        or submission_id.lower() != submission_id
    ):
        raise ValueError("A valid feedback submission ID is required")
    try:
        from uuid import UUID

        if str(UUID(submission_id)) != submission_id:
            raise ValueError("A valid feedback submission ID is required")
    except ValueError as exc:
        raise ValueError("A valid feedback submission ID is required") from exc

    answers = normalize_quiz_answers(raw["answers"], strict_training_vocabulary=True)
    recommended = _career_ids(
        raw["recommended_career_ids"], "recommended career IDs", minimum=1, maximum=5
    )
    liked = _career_ids(raw["liked_career_ids"], "liked career IDs")
    rejected = _career_ids(raw["rejected_career_ids"], "rejected career IDs")
    alternate = raw["alternate_career_id"]
    if alternate is not None and (
        not isinstance(alternate, int)
        or isinstance(alternate, bool)
        or alternate not in careers.values()
    ):
        raise ValueError("Alternate career ID is invalid")
    allowed_feedback_ids = set(recommended)
    if alternate is not None:
        allowed_feedback_ids.add(alternate)
        if alternate not in liked:
            liked.append(alternate)
    if (
        set(liked) & set(rejected)
        or not (set(liked) | set(rejected))
        or not (set(liked) | set(rejected)) <= allowed_feedback_ids
    ):
        raise ValueError("Select at least one career and do not both like and reject it")
    if not isinstance(raw["overall_feedback"], str) or raw["overall_feedback"] not in FEEDBACK_TYPES:
        raise ValueError("Overall feedback is invalid")
    if not isinstance(raw["reason"], str) or raw["reason"] not in FEEDBACK_REASONS:
        raise ValueError("Feedback reason is invalid")
    preferred_work_styles = raw["preferred_work_styles"]
    if (
        not isinstance(preferred_work_styles, list)
        or len(preferred_work_styles) > len(WORK_STYLES)
        or not all(isinstance(value, str) and value in WORK_STYLES for value in preferred_work_styles)
        or len(set(preferred_work_styles)) != len(preferred_work_styles)
    ):
        raise ValueError("Preferred work styles are invalid")
    priorities = raw["priorities"]
    if (
        not isinstance(priorities, list)
        or len(priorities) > len(PRIORITIES)
        or not all(isinstance(value, str) and value in PRIORITIES for value in priorities)
        or len(set(priorities)) != len(priorities)
    ):
        raise ValueError("Career priorities are invalid")
    if not isinstance(raw["training_consent"], bool):
        raise ValueError("Training consent must be true or false")

    return {
        "submission_id": submission_id,
        "answers": answers,
        "recommended_career_ids": recommended,
        "liked_career_ids": liked,
        "rejected_career_ids": rejected,
        "alternate_career_id": alternate,
        "overall_feedback": raw["overall_feedback"],
        "reason": raw["reason"],
        "preferred_work_styles": preferred_work_styles,
        "priorities": priorities,
        "training_consent": raw["training_consent"],
    }


def feature_vector(answers, career_id):
    name = next((name for name, value in careers.items() if value == career_id), None)
    if name is None:
        raise ValueError("Unknown career ID in training example")
    subject_signals, interest_signals, skill_signals, _, _ = CAREER_SIGNALS[name]
    features = {
        "career_id": str(career_id),
        "education": (
            _normalise(answers.get("education", ""))
            if _normalise(answers.get("education", "")) in TRAINING_VOCABULARY["education"]
            else "not_provided"
        ),
        "country": _normalise(answers.get("country", "Other / not listed")),
    }
    for field in ("subjects", "interests", "skills", "work_styles"):
        for value in answers.get(field, []):
            vocabulary = TRAINING_VOCABULARY.get(field)
            if vocabulary is not None and value.casefold() not in vocabulary:
                continue
            features[f"{field[:-1] if field.endswith('s') else field}:{_normalise(value)}"] = 1
    preferred = answers.get("preferred_career")
    if preferred:
        features[f"preferred_career:{careers[preferred]}"] = 1
    for field, signals in (
        ("career_subject", subject_signals),
        ("career_interest", interest_signals),
        ("career_skill", skill_signals),
    ):
        for signal in signals:
            features[f"{field}:{_normalise(signal)}"] = 1
    for style in CAREER_STYLES.get(name, ()):
        features[f"career_work_style:{style}"] = 1
    for answer in answers.get("follow_up_answers", []):
        features[
            f"follow_up:{answer['question_id']}:{answer['choice_id']}"
        ] = 1
    return features


def build_training_dataset(records, group_hash_secret=None):
    secret = group_hash_secret or os.getenv("AI_GROUP_HASH_SECRET") or os.getenv("JWT_SECRET")
    if isinstance(secret, str):
        secret = secret.encode("utf-8")
    if not isinstance(secret, bytes) or len(secret) < 32:
        raise RuntimeError(
            "Set AI_GROUP_HASH_SECRET (32+ characters) or JWT_SECRET before offline training"
        )
    features = []
    labels = []
    groups = []
    source_cases = []
    seen = set()
    for record in records:
        if record.get("training_consent") is not True:
            continue
        sensitive_fields = {
            "email", "full_name", "name", "password", "password_hash",
            "token", "auth_token", "access_token", "authorization", "jwt",
        }
        if sensitive_fields & set(record):
            raise ValueError("Training records must not contain direct identifiers or secrets")
        user_id = record.get("user_id")
        if not isinstance(user_id, str) or not user_id:
            raise ValueError("Training record is missing its account group")
        group_id = hmac.new(secret, user_id.encode("utf-8"), hashlib.sha256).hexdigest()
        answers = normalize_quiz_answers(
            record.get("answers"), strict_training_vocabulary=True
        )
        liked = _career_ids(record.get("liked_career_ids"), "liked career IDs")
        rejected = _career_ids(record.get("rejected_career_ids"), "rejected career IDs")
        if set(liked) & set(rejected):
            raise ValueError("A career cannot be both liked and rejected in one record")
        candidate_ids = list(dict.fromkeys(liked + rejected))
        if not candidate_ids:
            continue
        source_cases.append({
            "group": group_id,
            "answers": answers,
            "candidate_ids": candidate_ids,
            "relevant_ids": set(liked),
        })
        for career_id, label in [(value, 1) for value in liked] + [
            (value, 0) for value in rejected
        ]:
            vector = feature_vector(answers, career_id)
            feature_key = tuple(sorted(vector.items()))
            record_key = (group_id, feature_key, label)
            if record_key in seen:
                continue
            seen.add(record_key)
            features.append(vector)
            labels.append(label)
            groups.append(group_id)

    user_counts = Counter(groups)
    sample_weights = [
        1.0 / user_counts[user_id]
        for user_id in groups
    ]
    return {
        "features": features,
        "labels": labels,
        "groups": groups,
        "sample_weights": sample_weights,
        "cases": source_cases,
        "user_count": len(set(groups)),
    }
