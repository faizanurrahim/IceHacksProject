import unittest

from config.careers import careers
from config.profile import validate_description
from config.recommendations import CAREER_SIGNALS, recommend_careers


class ProfileValidationTests(unittest.TestCase):
    def setUp(self):
        self.description = {
            "education": " Bachelor's Degree ",
            "subjects": ["Computer Science", "Math"],
            "interests": ["Technology", "Programming"],
            "skills": ["Python", "Problem solving"],
            "preferred_careers": ["Software Developer"],
        }

    def test_normalizes_profile_values_and_removes_duplicates(self):
        self.description["skills"].append("Python")
        result, error = validate_description(self.description)
        self.assertIsNone(error)
        self.assertEqual(result["education"], "Bachelor's Degree")
        self.assertEqual(result["skills"], ["Python", "Problem solving"])

    def test_accepts_legacy_questionnaire_array(self):
        questionnaire = [
            {"field": key, "value": value}
            for key, value in self.description.items()
        ]
        result, error = validate_description(questionnaire)
        self.assertIsNone(error)
        self.assertEqual(result["preferred_careers"], ["Software Developer"])

    def test_rejects_unknown_fields_and_missing_answers(self):
        invalid = dict(self.description, unexpected="value")
        result, error = validate_description(invalid)
        self.assertIsNone(result)
        self.assertIn("Invalid fields", error)

        invalid = dict(self.description)
        invalid.pop("skills")
        result, error = validate_description(invalid)
        self.assertIsNone(result)
        self.assertIn("Missing fields", error)

    def test_rejects_invalid_and_oversized_lists(self):
        invalid = dict(self.description, skills=[" "])
        result, error = validate_description(invalid)
        self.assertIsNone(result)
        self.assertIn("strings", error)

        invalid = dict(self.description, skills=["skill"] * 21)
        result, error = validate_description(invalid)
        self.assertIsNone(result)
        self.assertIn("at most 20", error)

    def test_rejects_duplicate_and_untrusted_questionnaire_fields(self):
        questionnaire = [
            {"field": "education", "value": "Grade 12"},
            {"field": "education", "value": "Grade 11"},
        ]
        result, error = validate_description(questionnaire)
        self.assertIsNone(result)
        self.assertIn("Duplicate", error)

        result, error = validate_description([
            {"field": {"$ne": None}, "value": "anything"}
        ])
        self.assertIsNone(result)
        self.assertEqual(error, "Invalid description field")


class CareerRecommendationTests(unittest.TestCase):
    def test_every_existing_career_has_transparent_rules(self):
        self.assertEqual(set(careers), set(CAREER_SIGNALS))

    def test_recommendations_use_profile_and_include_explanations(self):
        profile = {
            "education": "Bachelor's Degree",
            "subjects": ["Computer Science", "Math"],
            "interests": ["Technology", "Programming"],
            "skills": ["Python", "Problem solving"],
            "preferred_careers": ["Software Developer"],
        }
        results = recommend_careers(profile)
        self.assertEqual(results[0]["name"], "Software Developer")
        self.assertEqual(results[0]["id"], careers["Software Developer"])
        self.assertEqual(results[0]["match_percentage"], 100)
        self.assertTrue(results[0]["reasons"])
        self.assertTrue(results[0]["suggested_skills"])
        self.assertTrue(results[0]["next_steps"])

    def test_scores_are_bounded_and_sorted(self):
        results = recommend_careers({
            "education": "Grade 9",
            "subjects": ["Art"],
            "interests": ["Fashion"],
            "skills": ["Drawing"],
            "preferred_careers": [],
        }, limit=10)
        scores = [item["score"] for item in results]
        self.assertEqual(scores, sorted(scores, reverse=True))
        self.assertTrue(all(0 <= score <= 100 for score in scores))


if __name__ == "__main__":
    unittest.main()
