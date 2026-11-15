# CareerPath Product Requirements

## Product

CareerPath helps students discover career options, understand common learning paths, and track personal exploration. Career suggestions use transparent rules by default; an optional local model can influence ranking only after it passes held-out evaluation. Neither mode predicts academic or career success.

## Users

- Visitors exploring careers without creating an account.
- Optional account holders saving careers and tracking learning progress.

## Current functionality

- Public catalog of 65 careers with keyword search, category filters, responsibilities, skills, general education guidance, and staged learning roadmaps.
- Free learning resources, practice project ideas, suggested next steps, and side-by-side comparison of two to four careers.
- Account-free career quiz using subjects, interests, skills, work styles, optional education level, dream career, and selected country.
- Deterministic rule-based recommendations with partial signal scoring, explanations, matched answers, skill gaps, and a modest dream-career preference boost.
- Up to three optional adaptive questions when answers leave several plausible paths open.
- Authenticated feedback that updates personal preferences. Training contribution is optional, unchecked by default, and uses only predefined quiz choices.
- An offline scikit-learn training/evaluation command that requires sufficient consented feedback, splits by user, compares ranking metrics with the rule baseline, and promotes only a demonstrably better model. The live app stays on rules until a model passes these checks.
- General education pathway guidance for selected countries; institution admission and professional licensing requirements must be verified locally.
- Optional Argon2-authenticated accounts with JWT sessions, profile onboarding, dashboard recommendations, favorites, saved roadmaps, completed skills, quiz history, and settings.
- Optional remembered login for 30 days using a revocable persistent session; ordinary login remains a 24-hour session.
- Light, dark, and special-edition appearance choices with system preference support.

## Technology and data

- Python backend using Nexa.py blueprints and templates.
- MongoDB Atlas through PyMongo.
- Argon2 password hashing and JWT authentication in HttpOnly cookies.
- Browser UI built with HTML, CSS, JavaScript, Bootstrap 5, and Font Awesome.
- MongoDB collections: `users`, `career_profiles`, `career_learning`, `persistent_sessions`, and `career_feedback`.

## Constraints

- Career browsing, comparison, and the quiz are available without registration.
- Saved learning and preference personalization require an account; public exploration and the quiz do not.
- Shared model training uses only feedback with explicit consent and is never run as part of a web request.
- Career requirements vary by location and institution; guidance must not imply guaranteed admission, certification, or employment.
- Production runs with debug disabled and uses HTTPS/Secure cookies.

## Success criteria

- Catalog, comparison, and quiz routes work for anonymous visitors.
- Rule-based recommendation results are deterministic, relevant to configured career signals, and explain their score inputs. Optional learned ranking is clearly identified and must pass held-out comparison before activation.
- Authenticated users can save and retrieve learning state, and remembered sessions expire or are revoked on logout.
- Existing unit and integration checks pass.
