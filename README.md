# CareerPath

CareerPath is a career exploration app built on Nexa.py, PyMongo, Argon2, JWT, and browser-based HTML/CSS/JavaScript. Career suggestions are deterministic rule-based matches for exploration, not career or employment predictions.

Visitors can explore the existing career catalog, take a career finder quiz, view free learning roadmaps, and compare careers without registering. Accounts are optional and add career favorites, saved roadmaps, skill progress, and saved quiz-result history.

## Run locally

The project expects Nexa.py and its Python dependencies to be installed in the selected virtual environment. For the current workstation:

```powershell
& 'D:\mine\.venv\Scripts\python.exe' -m pip install pymongo argon2-cffi PyJWT python-dotenv
& 'D:\mine\.venv\Scripts\python.exe' index.py
```

Open `http://127.0.0.1:3000`. Configure environment variables in the root `.env` file:

- `MONGO_URI` — MongoDB Atlas connection URI (required).
- `JWT_SECRET` — random secret of at least 32 characters (required).
- `APP_ENV` — set to `production` to enable Secure session cookies by default.
- `COOKIE_SECURE` — optional explicit `true`/`false` override; use `true` behind HTTPS.

`.env` is excluded by `.gitignore`. Do not commit credentials. When testing over local HTTP, leave `COOKIE_SECURE` unset or set it to `false`; enable it for HTTPS deployments.

## Authentication and storage

Passwords are hashed with Argon2. Successful signup/login set a 24-hour JWT in an `HttpOnly; SameSite=Lax` cookie; browser JavaScript does not receive or store the token. Protected browser pages require a valid session cookie, and APIs also accept an `Authorization: Bearer` token. Legacy API clients may still submit `{ "token": "..." }` for compatibility.

Logout expires the browser cookie. JWTs are not stored server-side, so a copied token remains valid until its 24-hour expiry. HTTPS and `COOKIE_SECURE=true` are required for production cookie transport.

## API

Responses are JSON. Errors have `success: false`, `error`, and `statusCDE`.

| Method | Path | Auth | Purpose |
|---|---|---|---|
| GET | `/api/v1/health` | No | Health check |
| GET | `/api/v1/careers` | No | Career names and existing IDs |
| GET | `/api/v1/career/<id>` | No | One career by ID |
| POST | `/api/v1/auth/sign-up` | No | Create Argon2-protected account and session cookie (`201`) |
| POST | `/api/v1/auth/login` | No | Validate credentials and create session cookie |
| POST | `/api/v1/auth/logout` | No | Expire session cookie |
| GET | `/api/v1/auth/me` | Yes | Current account details |
| DELETE | `/api/v1/auth/account` | Yes | Delete account; requires JSON `{"confirmation":"DELETE","password":"..."}` |
| POST | `/api/v1/discription` | Yes | Save onboarding profile (legacy route/spelling) |
| GET | `/api/v1/profile` | Yes | Retrieve profile; returns `completed: false` when none exists |
| PUT | `/api/v1/profile` | Yes | Update profile |
| GET or POST | `/api/v1/dash` | Yes | Dashboard data (POST retains legacy token-body support) |
| GET | `/api/v1/recommendations` | Yes | Rule-based career matches |
| GET | `/api/v1/explore/careers?search=<text>&category=<category>` | No | Search/filter the detailed 50-career catalog |
| GET | `/api/v1/career/<id>/roadmap` | No | Career detail, education, skills, staged roadmap, projects, and free resources |
| POST | `/api/v1/careers/compare` | No | Compare 2–4 careers using `{"career_ids":[1,2]}` |
| POST | `/api/v1/career-quiz` | No | Rule-based recommendations; expects `education`, and 1–12 values each for `subjects`, `interests`, `skills`, and `work_styles` |
| GET | `/api/v1/learning` | Yes | Retrieve favorites, saved roadmaps, completed skills, and quiz-result history |
| POST | `/api/v1/learning/favorites` | Yes | Add/remove favorite using `{"career_id":1,"favorite":true}` |
| POST | `/api/v1/learning/roadmaps` | Yes | Save/remove roadmap using `{"career_id":1,"saved":true}` |
| PUT | `/api/v1/learning/progress` | Yes | Set skill status using `{"career_id":1,"skill":"Python","completed":true}` |
| POST | `/api/v1/learning/quiz-results` | Yes | Save 1–5 recommended career IDs |

Public pages are `/explore`, `/career-quiz`, `/compare`, and `/career?id=<id>`. `/my-learning` requires a session. The quiz score is a transparent weighted match based on the submitted subjects, interests, skills, education, and work styles; it is not a prediction or a claim of career-fit accuracy.

Profile fields are `education` (string) and `subjects`, `interests`, `skills`, `preferred_careers` (non-empty arrays of at most 20 strings, each at most 80 characters). Profile updates are upserts keyed by the authenticated user ID.

## Recommendation scoring

Each career is defined using subject, interest, and skill signals. The score is a transparent weighted sum: subjects 25 points, interests 30, related skills 25, an explicitly preferred career 15, and education-level compatibility 5. A category awards its points when at least one configured signal matches. Results include reasons, profile-relevant skills, suggested skills, and next-step ideas; the percentage is only this rule score.

## MongoDB

The `users`, `career_profiles`, and `career_learning` collections are stored in the `icehacks` database. Startup ensures unique indexes on `users.email`, `career_profiles.user_id`, and `career_learning.user_id`. Learning state is one document per user; account removal also deletes that state using a MongoDB session transaction, as supported by MongoDB Atlas replica sets.

## Verify

Run the focused checks from the project root:

```powershell
& 'D:\mine\.venv\Scripts\python.exe' -m unittest discover -s tests -v
```
