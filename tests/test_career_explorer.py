import unittest

from config.career_catalog import (
    CAREER_CATEGORIES,
    CAREER_STYLES,
    get_career_catalog,
    quiz_recommendations,
)
from config.careers import careers


class CareerCatalogTests(unittest.TestCase):
    def test_every_existing_career_has_a_complete_public_roadmap(self):
        catalog = get_career_catalog()
        self.assertEqual(len(catalog), 65)
        self.assertEqual({career["id"] for career in catalog}, set(range(1, 66)))
        self.assertEqual({career["name"] for career in catalog}, set(careers))
        self.assertEqual({career["id"] for career in catalog}, set(careers.values()))

        for career in catalog:
            with self.subTest(career=career["name"]):
                self.assertIn(career["category"], CAREER_CATEGORIES)
                self.assertTrue(career["description"])
                self.assertTrue(career["responsibilities"])
                self.assertTrue(career["education"])
                self.assertTrue(career["required_skills"])
                self.assertEqual(len(career["roadmap"]), 4)
                self.assertTrue(all(stage["learn"] and stage["project"] for stage in career["roadmap"]))
                staged_learning = " ".join(
                    item
                    for stage in career["roadmap"]
                    for item in stage["learn"]
                ).casefold()
                self.assertTrue(all(skill.casefold() in staged_learning for skill in career["required_skills"]))
                self.assertTrue(career["resources"])
                self.assertTrue(all(resource["free"] and resource["url"] for resource in career["resources"]))
                self.assertTrue(career["career_paths"])

    def test_work_style_catalog_values_match_supported_styles(self):
        supported = {"people", "analytical", "hands_on", "creative", "structured", "independent"}
        self.assertTrue(all(set(styles) <= supported for styles in CAREER_STYLES.values()))

    def test_quiz_uses_work_style_answers_in_explanations_and_scores(self):
        answers = {
            "education": "Grade 12",
            "subjects": ["Mathematics", "Computer Science"],
            "interests": ["Technology and programming"],
            "skills": ["Programming", "Problem solving"],
            "work_styles": ["analytical", "creative"],
        }
        results = quiz_recommendations(answers, limit=10)
        developer = next(result for result in results if result["name"] == "Software Developer")

        self.assertIn("This role can include your preferred work style: Analytical, Creative", developer["reasons"])
        self.assertEqual(developer["match_percentage"], developer["score"])
        self.assertTrue(all(0 <= result["score"] <= 100 for result in results))
        self.assertEqual(len(results), 10)

    def test_quiz_country_guidance_and_dream_career_are_included(self):
        answers = {
            "country": "Pakistan",
            "education": "Grade 12",
            "preferred_career": "Doctor",
            "subjects": ["Mathematics"],
            "interests": ["Technology"],
            "skills": ["Programming"],
            "work_styles": [],
        }
        results = quiz_recommendations(answers)
        doctor = next(result for result in results if result["name"] == "Doctor")
        self.assertEqual(doctor["country_guidance"]["country"], "Pakistan")
        self.assertIn("intermediate", doctor["country_guidance"]["education_pathway"])
        self.assertTrue(doctor["preferred_career"])
        self.assertIn("do not overlap", " ".join(doctor["reasons"]))
        self.assertEqual(
            [item["score"] for item in results],
            sorted((item["score"] for item in results), reverse=True),
        )


if __name__ == "__main__":
    unittest.main()
