import unittest
from pathlib import Path

from Nexa.nxscript import NXscriptTemplate


TEMPLATE_DIR = Path(__file__).resolve().parents[1] / "templates"


class AuthenticationNavigationTests(unittest.TestCase):
    def render(self, template_name, is_logged_in):
        source = (TEMPLATE_DIR / template_name).read_text(encoding="utf-8")
        return NXscriptTemplate(source, filename=template_name).render(
            IS_LOGGED_IN=is_logged_in
        )

    def test_guest_homepage_shows_login_and_signup_actions(self):
        html = self.render("index.html", False)

        self.assertIn('href="/login"', html)
        self.assertIn('href="/get-started"', html)
        self.assertNotIn("data-auth-logout", html)

    def test_authenticated_homepage_shows_dashboard_and_logout(self):
        html = self.render("index.html", True)

        self.assertIn('href="/dashboard"', html)
        self.assertIn("data-auth-logout", html)
        self.assertNotIn('href="/login"', html)
        self.assertNotIn("Create Account", html)

    def test_all_navigation_templates_render_both_auth_states(self):
        for path in TEMPLATE_DIR.iterdir():
            if path.suffix not in {".html", ".nxs"}:
                continue
            source = path.read_text(encoding="utf-8")
            if "IS_LOGGED_IN" not in source:
                continue

            for is_logged_in in (False, True):
                with self.subTest(template=path.name, logged_in=is_logged_in):
                    html = NXscriptTemplate(source, filename=path.name).render(
                        IS_LOGGED_IN=is_logged_in
                    )
                    self.assertNotIn("{%", html)


if __name__ == "__main__":
    unittest.main()
