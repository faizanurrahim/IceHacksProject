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
}


def _normalise(value: str) -> str:
    normalized = " ".join(value.casefold().replace("&", " ").split())
    return ALIASES.get(normalized, normalized)


def _matches(profile_values: list[str], signals: tuple[str, ...]) -> list[str]:
    values = [_normalise(value) for value in profile_values]
    return [
        signal
        for signal in signals
        if any(signal in value or value in signal for value in values)
    ]


def recommend_careers(description: dict, limit: int = 5) -> list[dict]:
    education = description.get("education", "")
    education_level = EDUCATION_LEVELS.get(_normalise(education), 0)
    preferred = description.get("preferred_careers", [])
    subjects = description.get("subjects", [])
    interests = description.get("interests", [])
    skills = description.get("skills", [])

    results = []
    for career in careers:
        subject_signals, interest_signals, skill_signals, learn, level = CAREER_SIGNALS[career]
        matched_subjects = _matches(subjects, subject_signals)
        matched_interests = _matches(interests, interest_signals)
        matched_skills = _matches(skills, skill_signals)
        preferred_match = any(
            _normalise(career) == _normalise(value) or
            _normalise(career) in _normalise(value)
            for value in preferred
        )
        required_level = {"school": 0, "undergraduate": 1, "graduate": 2}[level]
        education_match = education_level >= required_level

        score = (
            25 * bool(matched_subjects)
            + 30 * bool(matched_interests)
            + 25 * bool(matched_skills)
            + 15 * preferred_match
            + 5 * education_match
        )
        reasons = []
        if matched_subjects:
            reasons.append("Your favourite subjects connect to " + ", ".join(matched_subjects))
        if matched_interests:
            reasons.append("This aligns with your interests in " + ", ".join(matched_interests))
        if matched_skills:
            reasons.append("You already listed related skills: " + ", ".join(matched_skills))
        if preferred_match:
            reasons.append("You included this career in your preferences")
        if education_match:
            reasons.append("Your current education level fits this early exploration path")
        if not reasons:
            reasons.append("Explore this path to see whether its day-to-day work interests you")

        results.append({
            "career": career,
            "name": career,
            "id": careers[career],
            "score": score,
            "match_percentage": score,
            "reasons": reasons,
            "relevant_skills": matched_skills,
            "suggested_skills": list(learn),
            "next_steps": [
                f"Explore introductory resources in {career.lower()}",
                "Try a beginner project, course, or volunteer experience",
                "Talk with someone working in this field",
            ],
        })

    results.sort(key=lambda result: (-result["score"], result["career"]))
    return results[:limit]
