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
        self.assertGreater(results[0]["match_percentage"], 0)
        self.assertLess(results[0]["match_percentage"], 100)
        self.assertTrue(results[0]["matched_interests"])
        self.assertTrue(results[0]["matched_subjects"])
        self.assertTrue(results[0]["matched_skills"])
        self.assertTrue(results[0]["preferred_career"])
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
        self.assertTrue(all(
            item["matched_subjects"] or item["matched_interests"] or item["matched_skills"]
            or item["preferred_career"]
            for item in results
        ))

    def test_returns_no_careers_for_education_alone(self):
        self.assertEqual(recommend_careers({"education": "Grade 12"}), [])

    def test_dream_career_is_included_and_explains_mismatched_answers(self):
        results = recommend_careers({
            "education": "Grade 12",
            "subjects": ["Mathematics"],
            "interests": ["Technology"],
            "skills": ["Programming"],
            "preferred_careers": ["Doctor"],
        })
        doctor = next(item for item in results if item["name"] == "Doctor")
        self.assertFalse(doctor["matched_subjects"] or doctor["matched_interests"] or doctor["matched_skills"])
        self.assertTrue(doctor["preferred_career"])
        self.assertTrue(any("do not overlap" in reason for reason in doctor["reasons"]))
        self.assertTrue(doctor["related_alternatives"])
        self.assertNotEqual(results[0]["name"], "Doctor")


class RecommendationScenarioTests(unittest.TestCase):
    def test_software_developer_matches_programming_math_and_technology(self):
        results = recommend_careers({
            "education": "Grade 12",
            "subjects": ["Mathematics", "Computer Science"],
            "interests": ["Technology", "Programming"],
            "skills": ["Programming", "Python"],
        })
        self.assertEqual(results[0]["name"], "Software Developer")

    def test_graphic_design_is_among_top_matches_for_art_and_creativity(self):
        results = recommend_careers({
            "subjects": ["Art", "Design"],
            "interests": ["Creativity", "Design"],
            "skills": ["Drawing", "Creativity"],
        })
        self.assertIn("Graphic Designer", [item["name"] for item in results[:3]])

    def test_doctor_matches_biology_chemistry_and_healthcare(self):
        results = recommend_careers({
            "subjects": ["Biology", "Chemistry"],
            "interests": ["Healthcare", "Medicine"],
            "skills": ["Empathy", "Communication"],
        })
        self.assertIn("Doctor", [item["name"] for item in results[:2]])

    def test_astronaut_matches_physics_math_and_space(self):
        results = recommend_careers({
            "subjects": ["Physics", "Mathematics"],
            "interests": ["Space", "Exploration"],
            "skills": ["Problem solving", "Teamwork"],
        })
        self.assertEqual(results[0]["name"], "Astronaut")

    def test_conflicting_answers_return_relevant_careers_deterministically(self):
        profile = {
            "subjects": ["Biology", "Computer Science"],
            "interests": ["Healthcare", "Technology"],
            "skills": ["Empathy", "Programming"],
        }
        results = recommend_careers(profile)
        self.assertIn("Doctor", [item["name"] for item in results])
        self.assertIn("Software Developer", [item["name"] for item in results])
        self.assertEqual(results, recommend_careers(profile))

    def test_sparse_answers_only_return_careers_with_signal_evidence(self):
        results = recommend_careers({
            "interests": ["Space exploration"],
            "subjects": [],
            "skills": [],
        })
        self.assertEqual([item["name"] for item in results], ["Astronaut"])


if __name__ == "__main__":
    unittest.main()
