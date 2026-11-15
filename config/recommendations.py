from config.careers import careers

CAREER_SIGNALS = {
    "Doctor": (("biology", "chemistry"), ("health", "medicine", "helping people"), ("communication", "empathy", "biology"), ("clinical experience", "anatomy", "patient care"), "undergraduate"),
    "Engineer": (("math", "physics"), ("design", "building", "technology"), ("problem solving", "math", "design"), ("engineering fundamentals", "computer-aided design"), "undergraduate"),
    "Software Developer": (("computer science", "math"), ("programming", "technology", "building apps"), ("python", "programming", "problem solving"), ("data structures", "version control", "testing"), "school"),
    "Web Developer": (("computer science", "art", "design"), ("web", "technology", "design"), ("javascript", "html", "css"), ("accessibility", "responsive design", "web security"), "school"),
    "Data Scientist": (("math", "statistics", "computer science"), ("data", "research", "patterns"), ("python", "statistics", "analysis"), ("sql", "data visualization", "machine learning"), "undergraduate"),
    "AI Engineer": (("math", "computer science"), ("artificial intelligence", "technology", "research"), ("python", "math", "problem solving"), ("machine learning", "data engineering", "model evaluation"), "undergraduate"),
    "Machine Learning Engineer": (("math", "statistics", "computer science"), ("artificial intelligence", "data", "research"), ("python", "statistics", "programming"), ("machine learning", "model deployment", "data engineering"), "undergraduate"),
    "Cybersecurity Analyst": (("computer science", "math"), ("security", "technology", "investigation"), ("networking", "problem solving", "attention to detail"), ("network security", "incident response", "security fundamentals"), "school"),
    "Network Engineer": (("computer science", "physics"), ("networking", "technology", "infrastructure"), ("networking", "troubleshooting", "problem solving"), ("routing", "cloud networking", "network security"), "school"),
    "Database Administrator": (("computer science", "math"), ("data", "technology", "organization"), ("sql", "attention to detail", "problem solving"), ("database design", "backup and recovery", "cloud databases"), "school"),
    "Teacher": (("education", "english", "math"), ("teaching", "learning", "helping people"), ("communication", "organization", "empathy"), ("lesson planning", "classroom management", "assessment"), "undergraduate"),
    "Professor": (("research", "english", "science"), ("teaching", "research", "learning"), ("communication", "writing", "analysis"), ("academic research", "public speaking", "curriculum design"), "graduate"),
    "Scientist": (("biology", "chemistry", "physics"), ("science", "research", "discovery"), ("analysis", "curiosity", "problem solving"), ("experimental design", "statistics", "scientific writing"), "undergraduate"),
    "Researcher": (("science", "math", "english"), ("research", "discovery", "analysis"), ("writing", "analysis", "curiosity"), ("research methods", "statistics", "data management"), "undergraduate"),
    "Pharmacist": (("chemistry", "biology"), ("health", "medicine", "helping people"), ("attention to detail", "communication", "science"), ("pharmacology", "patient counseling", "medication safety"), "undergraduate"),
    "Nurse": (("biology", "health science"), ("health", "helping people", "medicine"), ("empathy", "communication", "teamwork"), ("patient care", "clinical skills", "first aid"), "undergraduate"),
    "Surgeon": (("biology", "chemistry"), ("medicine", "health", "problem solving"), ("precision", "focus", "teamwork"), ("anatomy", "clinical experience", "surgical fundamentals"), "graduate"),
    "Dentist": (("biology", "chemistry"), ("health", "medicine", "helping people"), ("precision", "communication", "empathy"), ("oral health", "anatomy", "patient care"), "graduate"),
    "Veterinarian": (("biology", "chemistry"), ("animals", "health", "science"), ("empathy", "problem solving", "communication"), ("animal care", "anatomy", "clinical experience"), "undergraduate"),
    "Psychologist": (("psychology", "biology", "statistics"), ("psychology", "mental health", "helping people"), ("empathy", "listening", "analysis"), ("research methods", "active listening", "psychological assessment"), "graduate"),
    "Architect": (("math", "art", "physics"), ("design", "buildings", "creativity"), ("drawing", "design", "problem solving"), ("computer-aided design", "spatial reasoning", "building codes"), "undergraduate"),
    "Civil Engineer": (("math", "physics"), ("building", "infrastructure", "environment"), ("problem solving", "math", "planning"), ("structural analysis", "computer-aided design", "project management"), "undergraduate"),
    "Mechanical Engineer": (("math", "physics"), ("design", "machines", "technology"), ("problem solving", "math", "design"), ("computer-aided design", "thermodynamics", "prototyping"), "undergraduate"),
    "Electrical Engineer": (("math", "physics"), ("electronics", "technology", "energy"), ("problem solving", "math", "attention to detail"), ("circuit design", "embedded systems", "testing"), "undergraduate"),
    "Robotics Engineer": (("math", "physics", "computer science"), ("robotics", "technology", "building"), ("programming", "problem solving", "design"), ("control systems", "robotics", "electronics"), "undergraduate"),
    "Accountant": (("math", "business"), ("finance", "organization", "business"), ("attention to detail", "organization", "math"), ("accounting software", "financial reporting", "tax fundamentals"), "undergraduate"),
    "Financial Analyst": (("math", "economics", "business"), ("finance", "data", "business"), ("analysis", "math", "communication"), ("financial modeling", "excel", "forecasting"), "undergraduate"),
    "Economist": (("math", "economics", "statistics"), ("economics", "policy", "research"), ("analysis", "writing", "math"), ("econometrics", "statistics", "policy analysis"), "undergraduate"),
    "Business Manager": (("business", "math", "economics"), ("leadership", "business", "planning"), ("communication", "organization", "leadership"), ("project management", "budgeting", "coaching"), "undergraduate"),
    "Entrepreneur": (("business", "math", "art"), ("business", "building", "innovation"), ("communication", "creativity", "problem solving"), ("market research", "financial planning", "sales"), "school"),
    "Lawyer": (("law", "history", "english"), ("justice", "debate", "advocacy"), ("writing", "research", "communication"), ("legal research", "argumentation", "public speaking"), "graduate"),
    "Judge": (("law", "history", "english"), ("justice", "law", "public service"), ("fairness", "analysis", "communication"), ("legal procedure", "judgment writing", "mediation"), "graduate"),
    "Police Officer": (("law", "physical education"), ("public service", "safety", "helping people"), ("communication", "teamwork", "calm under pressure"), ("conflict resolution", "first aid", "community engagement"), "school"),
    "Pilot": (("math", "physics", "geography"), ("aviation", "travel", "technology"), ("focus", "communication", "decision making"), ("flight training", "navigation", "weather interpretation"), "school"),
    "Astronaut": (("math", "physics", "science"), ("space", "science", "exploration"), ("teamwork", "problem solving", "fitness"), ("aerospace fundamentals", "robotics", "research"), "undergraduate"),
    "Journalist": (("english", "history", "politics"), ("writing", "news", "storytelling"), ("writing", "research", "communication"), ("fact checking", "interviewing", "multimedia reporting"), "school"),
    "Writer": (("english", "history", "art"), ("writing", "storytelling", "creativity"), ("writing", "creativity", "research"), ("editing", "story structure", "publishing"), "school"),
    "Graphic Designer": (("art", "design", "computer science"), ("design", "creativity", "visual art"), ("creativity", "drawing", "communication"), ("typography", "visual design", "design software"), "school"),
    "UI/UX Designer": (("design", "art", "computer science"), ("design", "technology", "user experience"), ("creativity", "empathy", "problem solving"), ("prototyping", "user research", "accessibility"), "school"),
    "Photographer": (("art", "design"), ("photography", "storytelling", "visual art"), ("creativity", "attention to detail", "communication"), ("lighting", "photo editing", "composition"), "school"),
    "Filmmaker": (("art", "english", "design"), ("film", "storytelling", "creativity"), ("communication", "creativity", "teamwork"), ("video editing", "screenwriting", "production planning"), "school"),
    "Animator": (("art", "design", "computer science"), ("animation", "storytelling", "creativity"), ("drawing", "creativity", "patience"), ("3d modeling", "animation software", "storyboarding"), "school"),
    "Game Developer": (("computer science", "math", "art"), ("games", "technology", "storytelling"), ("programming", "creativity", "problem solving"), ("game engines", "3d math", "game design"), "school"),
    "Digital Marketer": (("business", "english", "math"), ("marketing", "communication", "creativity"), ("writing", "analysis", "communication"), ("search optimization", "analytics", "campaign planning"), "school"),
    "Chef": (("food science", "business"), ("cooking", "food", "creativity"), ("organization", "creativity", "teamwork"), ("food safety", "menu planning", "kitchen operations"), "school"),
    "Electrician": (("physics", "math"), ("building", "electronics", "problem solving"), ("attention to detail", "troubleshooting", "safety"), ("electrical safety", "circuit fundamentals", "apprenticeship"), "school"),
    "Fashion Designer": (("art", "design"), ("fashion", "design", "creativity"), ("drawing", "creativity", "attention to detail"), ("textile knowledge", "pattern making", "fashion illustration"), "school"),
    "Environmental Scientist": (("biology", "chemistry", "geography"), ("environment", "science", "conservation"), ("research", "analysis", "problem solving"), ("field research", "environmental sampling", "gis"), "undergraduate"),
    "Marine Biologist": (("biology", "chemistry", "oceanography"), ("marine life", "animals", "conservation"), ("research", "observation", "analysis"), ("marine ecology", "field research", "data analysis"), "undergraduate"),
    "Sports Coach": (("physical education", "biology"), ("sports", "teaching", "fitness"), ("communication", "leadership", "motivation"), ("training plans", "sports science", "first aid"), "school"),
    "Cloud Architect": (("computer science", "math"), ("cloud computing", "technology", "infrastructure"), ("systems thinking", "problem solving", "communication"), ("cloud platforms", "distributed systems", "security architecture"), "undergraduate"),
    "DevOps Engineer": (("computer science", "math"), ("automation", "technology", "infrastructure"), ("programming", "problem solving", "teamwork"), ("continuous integration", "cloud platforms", "monitoring"), "school"),
    "Data Analyst": (("math", "statistics", "computer science"), ("data", "business", "patterns"), ("analysis", "statistics", "communication"), ("sql", "spreadsheets", "data visualization"), "school"),
    "Product Manager": (("business", "computer science", "english"), ("product design", "technology", "leadership"), ("communication", "research", "planning"), ("product strategy", "user research", "prioritization"), "school"),
    "UX Researcher": (("psychology", "design", "english"), ("user experience", "research", "helping people"), ("listening", "analysis", "communication"), ("interviewing", "usability testing", "research ethics"), "undergraduate"),
    "Social Worker": (("psychology", "sociology", "english"), ("community", "helping people", "social justice"), ("empathy", "communication", "organization"), ("case management", "advocacy", "community resources"), "undergraduate"),
    "Paramedic": (("biology", "health science"), ("health", "emergency response", "helping people"), ("calm under pressure", "teamwork", "communication"), ("first aid", "emergency care", "patient assessment"), "school"),
    "Public Health Analyst": (("biology", "statistics", "math"), ("health", "research", "community"), ("analysis", "communication", "problem solving"), ("epidemiology", "data analysis", "health policy"), "undergraduate"),
    "Geologist": (("geography", "chemistry", "physics"), ("earth science", "environment", "field work"), ("observation", "analysis", "problem solving"), ("field mapping", "mineral identification", "geospatial analysis"), "undergraduate"),
    "Renewable Energy Engineer": (("math", "physics", "environmental science"), ("renewable energy", "technology", "environment"), ("problem solving", "design", "analysis"), ("energy systems", "electrical fundamentals", "sustainability"), "undergraduate"),
    "Urban Planner": (("geography", "math", "art"), ("cities", "community", "environment"), ("planning", "communication", "research"), ("land-use planning", "gis", "community engagement"), "undergraduate"),
    "Human Resources Manager": (("business", "psychology", "english"), ("people", "leadership", "workplace culture"), ("communication", "empathy", "organization"), ("recruitment", "employment practices", "conflict resolution"), "undergraduate"),
    "Supply Chain Analyst": (("math", "business", "economics"), ("logistics", "data", "planning"), ("analysis", "organization", "problem solving"), ("inventory planning", "spreadsheet analysis", "logistics systems"), "undergraduate"),
    "Content Creator": (("art", "english", "computer science"), ("storytelling", "video", "social media"), ("creativity", "communication", "planning"), ("content strategy", "video editing", "audience analytics"), "school"),
    "Forensic Scientist": (("biology", "chemistry", "math"), ("science", "investigation", "justice"), ("attention to detail", "analysis", "writing"), ("evidence handling", "laboratory methods", "scientific reporting"), "undergraduate"),
}

EDUCATION_LEVELS = {
    "middle school": 0,
    "grade 9": 0,
    "grade 10": 0,
    "grade 11": 0,
    "grade 12": 1,
    "intermediate": 1,
    "bachelor's degree": 2,
    "master's degree": 3,
    "doctorate": 3,
}

ALIASES = {
    "mathematics": "math",
    "coding": "programming",
    "computer programming": "programming",
    "computing": "computer science",
    "technology and programming": "technology programming",
    "art and design": "art design",
    "healthcare": "health",
    "space exploration": "space",
}


def _normalise(value: str) -> str:
    normalized = " ".join(value.strip().casefold().replace("&", " ").split())
    return ALIASES.get(normalized, normalized)


def _normalise_values(values) -> list[str]:
    if not isinstance(values, (list, tuple)):
        return []
    normalized = []
    for value in values:
        if isinstance(value, str) and value.strip() and len(value.strip()) <= 80:
            item = _normalise(value)
            if item and item not in normalized:
                normalized.append(item)
    return normalized


def _matches(profile_values: list[str], signals: tuple[str, ...]) -> list[str]:
    values = _normalise_values(profile_values)
    return [
        signal
        for signal in signals
        if any(
            _normalise(signal) in value or value in _normalise(signal)
            for value in values
        )
    ]


def _coverage_score(weight: int, matched: list[str], signals: tuple[str, ...]) -> float:
    unique_signals = {_normalise(signal) for signal in signals}
    if not unique_signals:
        return 0
    unique_matches = {_normalise(signal) for signal in matched}
    return weight * len(unique_matches) / len(unique_signals)


def _has_answer_evidence(result: dict) -> bool:
    return bool(result["matched_subjects"] or result["matched_interests"] or result["matched_skills"])


def recommend_careers(description: dict, limit: int = 5) -> list[dict]:
    if not isinstance(description, dict):
        return []
    try:
        requested_limit = int(limit)
    except (TypeError, ValueError):
        requested_limit = 5
    if isinstance(limit, bool):
        requested_limit = 5
    requested_limit = min(max(requested_limit, 1), len(careers))

    education = description.get("education", "")
    education = education.strip() if isinstance(education, str) and len(education) <= 80 else ""
    education_level = EDUCATION_LEVELS.get(_normalise(education), -1) if education else -1
    preferred = _normalise_values(description.get("preferred_careers", []))
    subjects = description.get("subjects", [])
    interests = description.get("interests", [])
    skills = description.get("skills", [])

    results = []
    for career in careers:
        subject_signals, interest_signals, skill_signals, learn, level = CAREER_SIGNALS[career]
        matched_subjects = _matches(subjects, subject_signals)
        matched_interests = _matches(interests, interest_signals)
        matched_skills = _matches(skills, skill_signals)
        preferred_match = _normalise(career) in preferred
        required_level = {"school": 0, "undergraduate": 1, "graduate": 2}[level]
        education_match = education_level >= required_level if education_level >= 0 else False
        subject_score = _coverage_score(25, matched_subjects, subject_signals)
        interest_score = _coverage_score(30, matched_interests, interest_signals)
        skill_score = _coverage_score(25, matched_skills, skill_signals)
        preference_score = 15 if preferred_match else 0
        education_score = 5 if education_match else 0
        score = round(
            subject_score + interest_score + skill_score
            + preference_score + education_score
        )
        skill_gaps = [
            skill for skill in learn
            if _normalise(skill) not in _normalise_values(skills)
        ]
        reasons = []
        if matched_subjects:
            reasons.append("Matched subjects: " + ", ".join(matched_subjects))
        if matched_interests:
            reasons.append("Matched interests: " + ", ".join(matched_interests))
        if matched_skills:
            reasons.append("Matched skills: " + ", ".join(matched_skills))
        if preferred_match:
            reasons.append("Your selected dream career added a 15-point preference boost.")
        if education_match:
            reasons.append("Your education level is broadly compatible with exploring this training path.")
        if preferred_match and not (matched_subjects or matched_interests or matched_skills):
            reasons.append(
                "Your current subject, interest, and skill answers do not overlap with this career's configured signals."
            )
        if skill_gaps:
            reasons.append("Skills to build: " + ", ".join(skill_gaps))

        results.append({
            "career": career,
            "name": career,
            "id": careers[career],
            "score": score,
            "match_percentage": score,
            "reasons": reasons,
            "matched_subjects": matched_subjects,
            "matched_interests": matched_interests,
            "relevant_skills": matched_skills,
            "matched_skills": matched_skills,
            "skill_gaps": skill_gaps,
            "preferred_career": preferred_match,
            "component_scores": {
                "subjects": round(subject_score, 1),
                "interests": round(interest_score, 1),
                "skills": round(skill_score, 1),
                "preferred_career": preference_score,
                "education": education_score,
            },
            "suggested_skills": skill_gaps,
            "next_steps": [
                f"Explore introductory resources in {career.lower()}",
                "Try a beginner project, course, or volunteer experience",
                "Talk with someone working in this field",
            ],
        })

    relevant = [
        result for result in results
        if _has_answer_evidence(result) or result["preferred_career"]
    ]
    relevant.sort(key=lambda result: (-result["score"], result["career"]))
    selected = relevant[:requested_limit]
    selected_ids = {result["id"] for result in selected}
    for preferred_career in preferred:
        preferred_result = next(
            (
                result for result in relevant
                if _normalise(result["career"]) == preferred_career
            ),
            None,
        )
        if preferred_result and preferred_result["id"] not in selected_ids:
            selected.append(preferred_result)
            selected_ids.add(preferred_result["id"])
    selected.sort(key=lambda result: (-result["score"], result["career"]))

    evidence_sets = {
        result["id"]: {
            "subjects": set(result["matched_subjects"]),
            "interests": set(result["matched_interests"]),
            "skills": set(result["matched_skills"]),
        }
        for result in relevant
    }
    for result in selected:
        if not result["preferred_career"]:
            continue
        own_evidence = evidence_sets[result["id"]]
        alternatives = []
        for candidate in relevant:
            if candidate["id"] == result["id"]:
                continue
            candidate_evidence = evidence_sets[candidate["id"]]
            overlap = sum(
                len(own_evidence[field] & candidate_evidence[field])
                for field in ("subjects", "interests", "skills")
            )
            alternatives.append((overlap, candidate["score"], candidate["career"]))
        alternatives.sort(key=lambda item: (-item[0], -item[1], item[2]))
        result["related_alternatives"] = [
            name for overlap, _, name in alternatives if overlap > 0
        ][:3]
        if not result["related_alternatives"]:
            result["related_alternatives"] = [
                candidate["career"]
                for candidate in relevant
                if candidate["id"] != result["id"]
            ][:3]
    return selected
