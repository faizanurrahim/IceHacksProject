"""Short, optional questions that distinguish close career matches."""

from config.career_catalog import CAREER_STYLES
from config.careers import careers

CAREER_ID_BY_NAME = careers
NAME_BY_CAREER_ID = {career_id: name for name, career_id in careers.items()}


def _named_ids(*terms):
    normalized_terms = tuple(term.casefold() for term in terms)
    return {
        career_id
        for name, career_id in careers.items()
        if any(term in name.casefold() for term in normalized_terms)
    }


def _style_ids(style):
    return {
        careers[name]
        for name, styles in CAREER_STYLES.items()
        if style in styles and name in careers
    }


QUESTION_BANK = (
    {
        "id": "software-or-data",
        "prompt": "Which activity would you rather spend time on?",
        "why": "This helps distinguish building technology from finding patterns in information.",
        "choices": (
            {
                "id": "build_software",
                "label": "Building and improving software",
                "career_ids": _named_ids("software", "web developer", "app developer", "programmer"),
            },
            {
                "id": "analyze_data",
                "label": "Analyzing data to answer questions",
                "career_ids": _named_ids("data", "statistician", "business intelligence"),
            },
        ),
    },
    {
        "id": "visual-or-user-centered-design",
        "prompt": "What sounds more satisfying?",
        "why": "Design careers can focus on visual expression or on making products easier to use.",
        "choices": (
            {
                "id": "visual_design",
                "label": "Creating visual identities, illustrations, or layouts",
                "career_ids": _named_ids("graphic designer", "illustrator", "animator", "artist"),
            },
            {
                "id": "user_centered_design",
                "label": "Understanding people and improving how a product works",
                "career_ids": _named_ids("ux", "user experience", "product designer"),
            },
        ),
    },
    {
        "id": "patient-care-or-research",
        "prompt": "Which part of healthcare interests you more?",
        "why": "This separates direct patient support from investigation and laboratory work.",
        "choices": (
            {
                "id": "direct_patient_care",
                "label": "Supporting and caring for patients directly",
                "career_ids": _named_ids("doctor", "nurse", "dentist", "therapist", "physician"),
            },
            {
                "id": "health_research",
                "label": "Investigating health questions or working in a lab",
                "career_ids": _named_ids("laboratory", "biomedical", "research scientist", "biochemist"),
            },
        ),
    },
    {
        "id": "flight-or-space",
        "prompt": "Which challenge would you choose?",
        "why": "Both fields involve technical learning, but their day-to-day settings differ.",
        "choices": (
            {
                "id": "operate_aircraft",
                "label": "Learning to operate and navigate aircraft",
                "career_ids": _named_ids("pilot", "aviation"),
            },
            {
                "id": "explore_space",
                "label": "Studying space systems and exploration",
                "career_ids": _named_ids("astronaut", "astrophysic", "space"),
            },
        ),
    },
    {
        "id": "hands-on-or-analytical",
        "prompt": "What kind of problem-solving feels more natural?",
        "why": "This adds a work-style signal when your other answers leave several paths open.",
        "choices": (
            {
                "id": "make_or_repair",
                "label": "Making, building, or repairing something",
                "career_ids": _style_ids("hands_on"),
            },
            {
                "id": "investigate_and_explain",
                "label": "Investigating evidence and explaining what it means",
                "career_ids": _style_ids("analytical"),
            },
        ),
    },
)

QUESTIONS_BY_ID = {question["id"]: question for question in QUESTION_BANK}


def question_ids():
    return set(QUESTIONS_BY_ID)


def is_valid_answer(question_id, choice_id):
    question = QUESTIONS_BY_ID.get(question_id)
    return bool(
        question
        and any(choice["id"] == choice_id for choice in question["choices"])
    )


def answer_bias(answers, career_id):
    score = 0
    explanations = []
    for answer in answers.get("follow_up_answers", []):
        question = QUESTIONS_BY_ID[answer["question_id"]]
        selected = next(
            choice for choice in question["choices"]
            if choice["id"] == answer["choice_id"]
        )
        if career_id in selected["career_ids"]:
            score += 8
            explanations.append(selected["label"])
        elif any(career_id in choice["career_ids"] for choice in question["choices"]):
            score -= 2
    return score, explanations


def select_next_question(answers, recommendations):
    asked = set(answers.get("asked_questions", []))
    if len(asked) >= 3:
        return None
    signal_count = sum(
        len(answers.get(field, []))
        for field in ("subjects", "interests", "skills", "work_styles")
    )
    if len(recommendations) > 1:
        margin = recommendations[0]["score"] - recommendations[1]["score"]
        if signal_count >= 5 and margin >= 15:
            return None

    top_ids = {item["id"] for item in recommendations[:3]}
    candidates = [
        question for question in QUESTION_BANK
        if question["id"] not in asked
    ]
    if not candidates:
        return None
    question = max(
        candidates,
        key=lambda item: (
            sum(
                career_id in top_ids
                for choice in item["choices"]
                for career_id in choice["career_ids"]
            ),
            -QUESTION_BANK.index(item),
        ),
    )
    if recommendations and not any(
        career_id in top_ids
        for choice in question["choices"]
        for career_id in choice["career_ids"]
    ):
        return None
    return {
        "id": question["id"],
        "prompt": question["prompt"],
        "why": question["why"],
        "choices": [
            {"id": choice["id"], "label": choice["label"]}
            for choice in question["choices"]
        ],
    }
