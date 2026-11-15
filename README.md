# CareerPath

CareerPath is a career exploration app built on Nexa.py, PyMongo, Argon2, JWT, and browser-based HTML/CSS/JavaScript. Career suggestions are deterministic rule-based matches for exploration, not career or employment predictions.

Visitors can explore the existing career catalog, take a career finder quiz, view free learning roadmaps, and compare careers without registering. Accounts are optional and add career favorites, saved roadmaps, skill progress, and saved quiz-result history.

The interface includes three saved appearance choices: light (white and purple), dark (black and blue), and special edition (dark blue and purple). The navigation theme button cycles between the three; Settings also offers system-preference mode.

## Setup and run

Use Python and a virtual environment. These commands work from the repository root in PowerShell, Command Prompt, macOS, or Linux:

```text
python -m venv .venv
```

Activate the environment:

```powershell
# Windows PowerShell
.\.venv\Scripts\Activate.ps1
```

```sh
# macOS / Linux
source .venv/bin/activate
```

Install the project dependencies and Nexa.py into that environment. Follow the [Nexa.py installation instructions](https://github.com/faizanurrahim/Nexa.py) for the framework:

```text
python -m pip install --upgrade pip
python -m pip install pymongo argon2-cffi PyJWT python-dotenv
```

Create a root `.env` file with the following variables:

- `MONGO_URI` — MongoDB Atlas connection URI (required).
- `JWT_SECRET` — random secret of at least 32 characters (required).
- `APP_ENV` — set to `production` to disable debug and require Secure session cookies.
- `DEBUG` — optional development switch; defaults on outside production. Production always disables debug.
- `COOKIE_SECURE` — optional explicit `true`/`false` override; use `true` behind HTTPS.

Keep `.env` out of Git and never commit credentials. For local HTTP development, leave `COOKIE_SECURE` unset; production always uses Secure cookies and HTTPS.

Start the application:

```text
python index.py
```

Open `http://127.0.0.1:3000`.

## Authentication and storage

Passwords are hashed with Argon2. Signup and ordinary login use the existing 24-hour JWT session. Login's optional “Remember this device” option creates a 30-day JWT session, stored as a SHA-256 token hash in `persistent_sessions` so logout can revoke it. Both session types use `HttpOnly; SameSite=Lax` cookies; browser JavaScript never receives or stores the token. Protected browser pages require a valid session cookie, and APIs also accept an `Authorization: Bearer` token. Legacy API clients may still submit `{ "token": "..." }` for compatibility.

Logout expires the browser cookie and revokes a remembered session. Ordinary 24-hour JWT sessions remain stateless for backward compatibility and cannot be revoked server-side before expiry. Use HTTPS and Secure cookies in production.

## API

Responses are JSON. Errors have `success: false`, `error`, and `statusCDE`.

| Method | Path | Auth | Purpose |
|---|---|---|---|
| GET | `/api/v1/health` | No | Health check |
| GET | `/api/v1/careers` | No | Career names and existing IDs |
| GET | `/api/v1/career/<id>` | No | One career by ID |
| POST | `/api/v1/auth/sign-up` | No | Create Argon2-protected account and session cookie (`201`) |
| POST | `/api/v1/auth/login` | No | Validate credentials; optional `remember_me: true` requests a 30-day revocable cookie (default: 24 hours) |
| POST | `/api/v1/auth/logout` | No | Expire cookie and revoke a remembered session |
| GET | `/api/v1/auth/me` | Yes | Current account details |
| DELETE | `/api/v1/auth/account` | Yes | Delete account; requires JSON `{"confirmation":"DELETE","password":"..."}` |
| POST | `/api/v1/discription` | Yes | Save onboarding profile (legacy route/spelling) |
| GET | `/api/v1/profile` | Yes | Retrieve profile; returns `completed: false` when none exists |
| PUT | `/api/v1/profile` | Yes | Update profile |
| GET or POST | `/api/v1/dash` | Yes | Dashboard data (POST retains legacy token-body support) |
| GET | `/api/v1/recommendations` | Yes | Rule-based career matches |
| GET | `/api/v1/explore/careers?search=<text>&category=<category>` | No | Search/filter the detailed 65-career catalog |
| GET | `/api/v1/career/<id>/roadmap` | No | Career detail, education, skills, staged roadmap, projects, and free resources |
| POST | `/api/v1/careers/compare` | No | Compare 2–4 careers using `{"career_ids":[1,2]}` |
| POST | `/api/v1/career-quiz` | No | Rule-based recommendations, optionally blended with an evaluated local model; accepts quiz answers and bounded follow-up responses |
| POST | `/api/v1/career-quiz/feedback` | Yes | Save per-account feedback and preferences; shared training use requires explicit `training_consent: true` |
| DELETE | `/api/v1/career-quiz/feedback/training-consent` | Yes | Delete this account's previously opted-in source feedback from future training datasets |
| GET | `/api/v1/learning` | Yes | Retrieve favorites, saved roadmaps, completed skills, and quiz-result history |
| POST | `/api/v1/learning/favorites` | Yes | Add/remove favorite using `{"career_id":1,"favorite":true}` |
| POST | `/api/v1/learning/roadmaps` | Yes | Save/remove roadmap using `{"career_id":1,"saved":true}` |
| PUT | `/api/v1/learning/progress` | Yes | Set skill status using `{"career_id":1,"skill":"Python","completed":true}` |
| POST | `/api/v1/learning/quiz-results` | Yes | Save 1–5 recommended career IDs |

Public pages are `/explore`, `/career-quiz`, `/compare`, and `/career?id=<id>`. `/my-learning` requires a session. Career score components are partial proportions of configured signals, weighted by subjects (25), interests (30), skills (25), dream-career preference (15), and broad education-stage compatibility (5). Quiz work-style answers use a separate 15-point contribution while scaling other components to 85. Careers without matching subject, interest, skill, or explicit dream-career evidence are omitted. The quiz can ask up to three optional follow-up questions when the available answers leave competing paths open. Scores and confidence labels are exploration aids, not probabilities or claims of career-fit accuracy.

The quiz provides broad pathway notes for Pakistan, India, the United States, the United Kingdom, Canada, and Australia, plus general guidance for other locations. These are not admission, certification, or licensing requirements; confirm current rules with local institutions and regulators.

Profile fields are `education` (string) and `subjects`, `interests`, `skills`, `preferred_careers` (non-empty arrays of at most 20 strings, each at most 80 characters). Profile updates are upserts keyed by the authenticated user ID.

## Recommendation scoring

Each career is defined using subject, interest, and skill signals. The baseline uses the proportion of each career's configured signals that matched: subjects 25 points, interests 30, related skills 25, an explicitly preferred career 15, and broad education-stage compatibility 5. Quiz work styles contribute separately. User feedback can adjust that user's later rankings; other users' feedback is never used for personalization. The API response adds `recommendation_engine` and `follow_up_question` metadata without removing the existing `recommendations` field. In the default setup, recommendations remain rule-based.

### Optional offline recommendation model

The application does not send feedback to a hosted AI service and does not train a model during web requests. Install the optional dependency only if you intend to run the local trainer:

```text
python -m pip install -r requirements-ai.txt
```

Feedback is account-bound and idempotent by submission ID. It updates that account's `career_learning.recommendation_preferences` whether or not training consent is given. The unchecked-by-default consent box controls whether a feedback record may be considered by the offline trainer; the trainer queries only `training_consent: true`. Account deletion also removes the account's source feedback. The training feature builder accepts only the quiz's predefined answer choices, excludes direct identifiers and free text from model features, and uses a keyed pseudonymous account group solely for user-disjoint evaluation. Set `AI_GROUP_HASH_SECRET` to a random secret of at least 32 characters for offline training; if absent, the configured `JWT_SECRET` is used for group hashing. Neither secret becomes a model feature.

The feedback endpoint expects `submission_id` (UUID), the submitted `answers`, `recommended_career_ids`, `liked_career_ids`, `rejected_career_ids`, optional `alternate_career_id`, `overall_feedback`, `reason`, `preferred_work_styles`, `priorities`, and a boolean `training_consent`. Career selections must use valid catalog IDs, and a career cannot be both liked and rejected. Submitting with consent unchecked still updates only the signed-in user's preferences. `DELETE /api/v1/career-quiz/feedback/training-consent` removes that account's consented source records; already-promoted aggregate model files are not automatically unlearned and require a new offline evaluation to replace.

Example request shape:

```json
{
  "submission_id": "a-valid-uuid",
  "answers": {
    "education": "Grade 12",
    "country": "Pakistan",
    "preferred_career": "",
    "subjects": ["Computer Science"],
    "interests": ["Technology and programming"],
    "skills": ["Programming"],
    "work_styles": [],
    "asked_questions": [],
    "follow_up_answers": []
  },
  "recommended_career_ids": [3, 5],
  "liked_career_ids": [3],
  "rejected_career_ids": [5],
  "alternate_career_id": null,
  "overall_feedback": "some_relevant",
  "reason": "work_style",
  "preferred_work_styles": [],
  "priorities": [],
  "training_consent": false
}
```

Run training manually from the project root:

```text
python -m AI.trainer
```

Training requires at least 20 consenting users, 40 labeled career reactions, both feedback labels, and a user-disjoint holdout containing both labels. The candidate is evaluated using Precision@5, Recall@5, and NDCG@5 against the current rule engine (and the active model, if one exists). Promotion requires at least a 0.01 NDCG@5 improvement without Precision@5 or Recall@5 dropping by more than 0.02. Insufficient data or a weaker candidate leaves the rule-based model in use. Accepted model files and the active-version pointer are local and git-ignored; no model is checked into the repository.

## MongoDB

The app connects to the `icehacks` database using `MONGO_URI`; create the Atlas database user and allow the app host in Atlas network access. The app creates its collections/indexes on startup:

- `users`: unique index on `email`.
- `career_profiles`: unique index on `user_id`.
- `career_learning`: unique index on `user_id`.
- `persistent_sessions`: unique index on `token_hash`, an index on `user_id`, and an expiry TTL index on `expires_at`.
- `career_feedback`: unique index on `(user_id, submission_id)` for idempotent submissions and an index on `(training_consent, created_at)` for offline collection.

Learning state remains one document per user, including personal recommendation preferences. Account deletion removes profile, learning, feedback, and remembered-session records in a MongoDB transaction; the Atlas deployment must support transactions (replica set).

## Verify

Run the test suite from the activated environment at the project root:

```powershell
python -m unittest discover -s tests -v
```
