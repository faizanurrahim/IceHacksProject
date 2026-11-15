import os
import unittest
from unittest.mock import patch
from uuid import uuid4

from AI.active_learning import is_valid_answer, select_next_question
from AI.dataset import (
    build_training_dataset,
    feature_vector,
    normalize_quiz_answers,
    validate_feedback,
)
from AI.engine import recommend, recommend_profile
from AI.evaluator import promotion_is_better, ranking_metrics
from AI.learner import merge_preferences, save_feedback
from AI.trainer import _fit_candidate, train_and_promote
from config.careers import careers


def quiz_answers(**updates):
    answers = {
        "education": "Grade 12",
        "country": "Pakistan",
        "preferred_career": "",
        "subjects": [],
        "interests": [],
        "skills": [],
        "work_styles": [],
        "asked_questions": [],
        "follow_up_answers": [],
    }
    answers.update(updates)
    return answers


class CareerRecommendationEngineTests(unittest.TestCase):
    def test_software_developer_matches_programming_math_and_technology(self):
        result = recommend(quiz_answers(
            subjects=["Mathematics", "Computer Science"],
            interests=["Technology and programming"],
            skills=["Programming", "Problem solving"],
        ))
        self.assertEqual(result["recommendations"][0]["career"], "Software Developer")
        self.assertIn("Matched interests", " ".join(result["recommendations"][0]["reasons"]))

    def test_graphic_designer_matches_art_and_creativity(self):
        result = recommend(quiz_answers(
            subjects=["Art and design"],
            interests=["Design and creativity"],
            skills=["Creativity and design"],
        ))
        names = [item["career"] for item in result["recommendations"]]
        self.assertIn("Graphic Designer", names[:3])

    def test_doctor_matches_biology_chemistry_and_healthcare(self):
        result = recommend(quiz_answers(
            subjects=["Biology", "Chemistry"],
            interests=["Health and helping people"],
            skills=["Communication", "Teamwork and empathy"],
        ))
        self.assertIn("Doctor", [item["career"] for item in result["recommendations"][:2]])

    def test_astronaut_matches_physics_math_and_space(self):
        result = recommend(quiz_answers(
            subjects=["Physics", "Mathematics"],
            interests=["Space exploration"],
            skills=["Problem solving", "Teamwork and empathy"],
        ))
        self.assertEqual(result["recommendations"][0]["career"], "Astronaut")

    def test_conflicting_answers_keep_distinct_plausible_paths_and_are_deterministic(self):
        answers = quiz_answers(
            subjects=["Biology", "Computer Science"],
            interests=["Health and helping people", "Technology and programming"],
            skills=["Communication", "Programming"],
        )
        first = recommend(answers)["recommendations"]
        second = recommend(answers)["recommendations"]
        self.assertEqual(first, second)
        names = [item["career"] for item in first]
        self.assertIn("Doctor", names)
        self.assertIn("Software Developer", names)

    def test_sparse_answers_do_not_fill_results_with_unrelated_careers(self):
        result = recommend(quiz_answers(
            education="",
            subjects=[],
            interests=["Space exploration"],
            skills=[],
        ))
        self.assertEqual([item["career"] for item in result["recommendations"]], ["Astronaut"])
        self.assertIsNotNone(result["follow_up_question"])

    def test_dream_career_is_included_without_overriding_contradictory_evidence(self):
        result = recommend(quiz_answers(
            subjects=["Mathematics", "Computer Science"],
            interests=["Technology and programming"],
            skills=["Programming"],
            preferred_career="Doctor",
        ))
        by_name = {item["career"]: item for item in result["recommendations"]}
        self.assertIn("Doctor", by_name)
        self.assertTrue(by_name["Doctor"]["preferred_career"])
        self.assertNotEqual(result["recommendations"][0]["career"], "Doctor")
        self.assertTrue(by_name["Doctor"]["reasons"])

    def test_saved_preferences_are_explained_and_bounded(self):
        career_id = careers["Graphic Designer"]
        result = recommend(
            quiz_answers(),
            preferences={"liked_career_ids": [career_id]},
        )
        designer = next(
            item for item in result["recommendations"]
            if item["id"] == career_id
        )
        self.assertIn("previously marked", " ".join(designer["reasons"]))
        self.assertLessEqual(designer["score"], 100)

    def test_low_confidence_model_falls_back_to_rule_scores(self):
        class FlatModel:
            classes_ = [0, 1]

            def predict_proba(self, rows):
                return [[0.5, 0.5] for _ in rows]

        with patch("AI.engine.load_active_model", return_value=(FlatModel(), "test-v1", None)):
            result = recommend(quiz_answers(
                subjects=["Mathematics", "Computer Science"],
                interests=["Technology and programming"],
                skills=["Programming"],
            ))
        self.assertEqual(result["recommendation_engine"]["mode"], "rules")
        self.assertIsNone(result["recommendation_engine"]["model_version"])
        self.assertIn("did not clearly separate", result["recommendation_engine"]["notice"])

    def test_dashboard_profile_can_include_saved_career_preferences(self):
        result = recommend_profile(
            {
                "education": "Bachelor's Degree",
                "subjects": ["Computer Science"],
                "interests": ["Technology"],
                "skills": ["Programming"],
                "preferred_careers": [],
            },
            preferences={"liked_career_ids": [careers["Graphic Designer"]]},
        )
        designer = next(
            item for item in result["recommendations"]
            if item["id"] == careers["Graphic Designer"]
        )
        self.assertIn("previously marked", " ".join(designer["reasons"]))
        self.assertIsInstance(designer["suggested_skills"], list)
        self.assertTrue(designer["next_steps"])


class FeedbackDataTests(unittest.TestCase):
    def setUp(self):
        self.answers = quiz_answers(
            subjects=["Mathematics", "Computer Science"],
            interests=["Technology and programming"],
            skills=["Programming"],
            work_styles=["analytical"],
        )
        self.feedback = {
            "submission_id": str(uuid4()),
            "answers": self.answers,
            "recommended_career_ids": [
                careers["Software Developer"],
                careers["Data Scientist"],
            ],
            "liked_career_ids": [careers["Software Developer"]],
            "rejected_career_ids": [careers["Data Scientist"]],
            "alternate_career_id": None,
            "overall_feedback": "some_relevant",
            "reason": "work_style",
            "preferred_work_styles": ["analytical"],
            "priorities": ["analytical_work"],
            "training_consent": False,
        }

    def test_feedback_validation_requires_consent_boolean_and_known_careers(self):
        validated = validate_feedback(self.feedback)
        self.assertFalse(validated["training_consent"])
        self.assertNotIn("email", validated)

        invalid = dict(self.feedback, training_consent="yes")
        with self.assertRaises(ValueError):
            validate_feedback(invalid)
        invalid = dict(self.feedback, liked_career_ids=[999])
        with self.assertRaises(ValueError):
            validate_feedback(invalid)

    def test_feedback_rejects_personal_text_instead_of_training_it(self):
        invalid = dict(self.feedback)
        invalid["answers"] = quiz_answers(interests=["faizan@example.com"])
        with self.assertRaises(ValueError):
            validate_feedback(invalid)

    def test_repeated_follow_up_answers_are_rejected(self):
        answers = quiz_answers(
            asked_questions=["software-or-data"],
            follow_up_answers=[
                {"question_id": "software-or-data", "choice_id": "build_software"},
                {"question_id": "software-or-data", "choice_id": "build_software"},
            ],
        )
        with self.assertRaises(ValueError):
            normalize_quiz_answers(answers)
        self.assertTrue(is_valid_answer("software-or-data", "build_software"))
        self.assertFalse(is_valid_answer("software-or-data", "not-a-choice"))

    def test_consented_training_features_are_allowlisted_and_user_group_is_pseudonymous(self):
        record = {
            "user_id": "user-object-id",
            **validate_feedback(dict(self.feedback, training_consent=True)),
        }
        dataset = build_training_dataset([record], group_hash_secret=b"x" * 32)
        self.assertEqual(dataset["user_count"], 1)
        self.assertNotIn("user-object-id", dataset["groups"])
        self.assertTrue(all(
            "faizan@example.com" not in str(value)
            for row in dataset["features"]
            for value in row.values()
        ))
        unsafe_answers = quiz_answers(interests=["faizan@example.com"])
        unsafe_features = feature_vector(unsafe_answers, careers["Software Developer"])
        self.assertNotIn("interest:faizan@example.com", unsafe_features)

    def test_opted_out_feedback_is_not_added_to_shared_dataset(self):
        record = {
            "user_id": "user-object-id",
            **validate_feedback(self.feedback),
        }
        dataset = build_training_dataset([record], group_hash_secret=b"x" * 32)
        self.assertEqual(dataset["features"], [])
        self.assertEqual(dataset["cases"], [])

    def test_feedback_saves_personal_preferences_once(self):
        class FakeCollection:
            def __init__(self):
                self.records = {}
                self.learning = {}

            def update_one(self, query, update, upsert=False):
                key = query["user_id"]
                if "submission_id" in query:
                    key = (key, query["submission_id"])
                    if key in self.records:
                        if "$set" in update:
                            self.records[key].update(update["$set"])
                        return type("Result", (), {"upserted_id": None})()
                    self.records[key] = update["$setOnInsert"]
                    return type("Result", (), {"upserted_id": "inserted"})()
                state = self.learning.setdefault(key, {})
                for field, values in update.get("$addToSet", {}).items():
                    target = state.setdefault(field, [])
                    each = values.get("$each", [values])
                    for value in each:
                        if value not in target:
                            target.append(value)
                for field, selector in update.get("$pull", {}).items():
                    target = state.setdefault(field, [])
                    excluded = selector.get("$in", [])
                    state[field] = [value for value in target if value not in excluded]
                return type("Result", (), {"upserted_id": None})()

            def find_one(self, query):
                return self.records.get((query["user_id"], query["submission_id"]))

        feedback_collection = FakeCollection()
        learning_collection = FakeCollection()
        validated = validate_feedback(self.feedback)
        first = save_feedback("account-1", validated, feedback_collection, learning_collection)
        second = save_feedback("account-1", validated, feedback_collection, learning_collection)
        self.assertTrue(first)
        self.assertFalse(second)
        self.assertEqual(
            learning_collection.learning["account-1"][
                "recommendation_preferences.liked_career_ids"
            ],
            [careers["Software Developer"]],
        )
        self.assertTrue(next(iter(feedback_collection.records.values()))["preferences_applied"])

    def test_training_consent_withdrawal_deletes_only_opted_in_records(self):
        class FakeCollection:
            def delete_many(self, query):
                matches = [
                    key for key, record in self.records.items()
                    if record["user_id"] == query["user_id"]
                    and record["training_consent"] is query["training_consent"]
                ]
                for key in matches:
                    del self.records[key]
                return type("Result", (), {"deleted_count": len(matches)})()

            def __init__(self):
                self.records = {
                    1: {"user_id": "account-1", "training_consent": True},
                    2: {"user_id": "account-1", "training_consent": False},
                    3: {"user_id": "account-2", "training_consent": True},
                }

        from AI.learner import withdraw_training_feedback

        collection = FakeCollection()
        self.assertEqual(withdraw_training_feedback("account-1", collection), 1)
        self.assertEqual(set(collection.records), {2, 3})

    def test_preference_updates_resolve_conflicting_old_feedback(self):
        current = {
            "liked_career_ids": [careers["Software Developer"]],
            "rejected_career_ids": [],
        }
        feedback = validate_feedback(dict(
            self.feedback,
            liked_career_ids=[careers["Data Scientist"]],
            rejected_career_ids=[careers["Software Developer"]],
        ))
        merged = merge_preferences(current, feedback)
        self.assertIn(careers["Data Scientist"], merged["liked_career_ids"])
        self.assertIn(careers["Software Developer"], merged["rejected_career_ids"])
        self.assertNotIn(careers["Software Developer"], merged["liked_career_ids"])


class OfflineModelTests(unittest.TestCase):
    def test_training_refuses_empty_feedback(self):
        with patch.dict(os.environ, {"AI_GROUP_HASH_SECRET": "x" * 32}):
            result = train_and_promote(records=[], model_dir="unused-model-dir")
        self.assertEqual(result["status"], "insufficient_data")

    def test_model_training_uses_distinct_user_groups(self):
        records = []
        for index in range(20):
            tech_user = index % 2 == 0
            records.append({
                "user_id": f"account-{index}",
                "submission_id": str(uuid4()),
                "training_consent": True,
                "answers": quiz_answers(
                    subjects=["Computer Science"] if tech_user else ["Art and design"],
                    interests=["Technology and programming"] if tech_user else ["Design and creativity"],
                    skills=["Programming"] if tech_user else ["Creativity and design"],
                ),
                "liked_career_ids": [
                    careers["Software Developer"] if tech_user else careers["Graphic Designer"]
                ],
                "rejected_career_ids": [
                    careers["Graphic Designer"] if tech_user else careers["Software Developer"]
                ],
            })
        dataset = build_training_dataset(records, group_hash_secret=b"z" * 32)
        model, held_out_cases, reason = _fit_candidate(dataset)
        self.assertIsNone(reason)
        self.assertIsNotNone(model)
        self.assertTrue(held_out_cases)
        self.assertLess(
            len({case["group"] for case in held_out_cases}),
            dataset["user_count"],
        )

    def test_metrics_and_promotion_gate_are_explicit(self):
        metrics = ranking_metrics([careers["Software Developer"]], {careers["Software Developer"]})
        self.assertEqual(metrics["recall@5"], 1.0)
        self.assertFalse(promotion_is_better(
            {"precision@5": 0.2, "recall@5": 0.5, "ndcg@5": 0.5},
            {"precision@5": 0.2, "recall@5": 0.5, "ndcg@5": 0.6},
        ))

    def test_adaptive_questions_are_bounded_and_explain_their_purpose(self):
        result = recommend(quiz_answers(
            subjects=["Mathematics", "Computer Science"],
            interests=["Technology and programming"],
            skills=["Programming"],
        ))
        question = result["follow_up_question"]
        self.assertIsNotNone(question)
        self.assertTrue(question["why"])
        answered = quiz_answers(asked_questions=[
            "software-or-data", "visual-or-user-centered-design",
            "patient-care-or-research",
        ])
        self.assertIsNone(select_next_question(answered, []))


if __name__ == "__main__":
    unittest.main()
