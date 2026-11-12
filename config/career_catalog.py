from config.careers import careers
from config.recommendations import CAREER_SIGNALS, recommend_careers

CAREER_CATEGORIES = {
    "Healthcare & Life Science": (
        "Doctor", "Pharmacist", "Nurse", "Surgeon", "Dentist",
        "Veterinarian", "Psychologist", "Paramedic", "Public Health Analyst",
        "Forensic Scientist",
    ),
    "Technology": (
        "Software Developer", "Web Developer", "Data Scientist",
        "AI Engineer", "Machine Learning Engineer", "Cybersecurity Analyst",
        "Network Engineer", "Database Administrator", "Robotics Engineer",
        "Game Developer", "Cloud Architect", "DevOps Engineer", "Data Analyst",
        "Product Manager", "UX Researcher",
    ),
    "Engineering & Built Environment": (
        "Engineer", "Architect", "Civil Engineer", "Mechanical Engineer",
        "Electrical Engineer", "Pilot", "Astronaut",
    ),
    "Education & Research": ("Teacher", "Professor", "Scientist", "Researcher"),
    "Business & Finance": (
        "Accountant", "Financial Analyst", "Economist", "Business Manager",
        "Entrepreneur", "Digital Marketer", "Human Resources Manager",
        "Supply Chain Analyst",
    ),
    "Law & Public Service": ("Lawyer", "Judge", "Police Officer", "Social Worker"),
    "Creative & Media": (
        "Journalist", "Writer", "Graphic Designer", "UI/UX Designer",
        "Photographer", "Filmmaker", "Animator", "Fashion Designer",
        "Content Creator",
    ),
    "Environment & Outdoors": (
        "Environmental Scientist", "Marine Biologist", "Sports Coach",
        "Geologist", "Renewable Energy Engineer", "Urban Planner",
    ),
    "Skilled Trades & Hospitality": ("Chef", "Electrician"),
}

CAREER_SUMMARIES = {
    "Doctor": "Assess health concerns, explain treatment options, and coordinate patient care.",
    "Engineer": "Apply science and mathematics to design, test, and improve practical systems.",
    "Software Developer": "Plan, build, test, and maintain software that solves user problems.",
    "Web Developer": "Create accessible websites and web applications for real users.",
    "Data Scientist": "Use statistics, code, and domain knowledge to find patterns in data.",
    "AI Engineer": "Build and evaluate software systems that use machine-learning models.",
    "Machine Learning Engineer": "Prepare data and deploy reliable machine-learning systems.",
    "Cybersecurity Analyst": "Monitor systems, investigate risks, and help protect digital assets.",
    "Network Engineer": "Design and maintain the networks that connect devices and services.",
    "Database Administrator": "Keep databases reliable, secure, backed up, and performant.",
    "Teacher": "Plan learning experiences, support students, and assess their progress.",
    "Professor": "Teach advanced subjects and contribute original research in a field.",
    "Scientist": "Ask testable questions and use evidence to expand scientific understanding.",
    "Researcher": "Find and assess evidence, analyze information, and communicate findings.",
    "Pharmacist": "Help people use medicines safely and accurately.",
    "Nurse": "Provide hands-on care, monitor health, and support patients and families.",
    "Surgeon": "Use specialized clinical training to perform procedures and guide recovery.",
    "Dentist": "Prevent, diagnose, and treat conditions affecting teeth and oral health.",
    "Veterinarian": "Care for animal health and advise the people responsible for animals.",
    "Psychologist": "Study behavior and support wellbeing through evidence-based practice.",
    "Architect": "Shape buildings and spaces around people, function, safety, and place.",
    "Civil Engineer": "Plan and maintain infrastructure such as roads, bridges, and water systems.",
    "Mechanical Engineer": "Design and improve machines, products, and mechanical systems.",
    "Electrical Engineer": "Design and test electrical, electronic, and power systems.",
    "Robotics Engineer": "Combine mechanics, electronics, and software to build robotic systems.",
    "Accountant": "Organize financial records and prepare accurate reports for decisions.",
    "Financial Analyst": "Evaluate financial information to help organizations make decisions.",
    "Economist": "Study how people and institutions allocate resources and respond to policy.",
    "Business Manager": "Coordinate people, goals, budgets, and operations in an organization.",
    "Entrepreneur": "Find a problem worth solving and build a sustainable product or service.",
    "Lawyer": "Research laws and represent or advise clients within a legal system.",
    "Judge": "Evaluate legal arguments and evidence, then apply the law impartially.",
    "Police Officer": "Support public safety, respond to incidents, and work with communities.",
    "Pilot": "Operate aircraft using technical procedures, training, and sound judgment.",
    "Astronaut": "Train for demanding crewed missions involving science and space operations.",
    "Journalist": "Verify information and report clear, fair stories to the public.",
    "Writer": "Develop and edit written work for readers, organizations, or publications.",
    "Graphic Designer": "Communicate ideas visually through typography, layout, and imagery.",
    "UI/UX Designer": "Research user needs and design clear, usable digital experiences.",
    "Photographer": "Tell stories or document subjects through images and visual choices.",
    "Filmmaker": "Develop and produce moving-image stories with a creative team.",
    "Animator": "Create the movement and visual sequences used in films, games, and media.",
    "Game Developer": "Build interactive games by combining software, design, and creative collaboration.",
    "Digital Marketer": "Reach audiences online, communicate value, and measure campaign outcomes.",
    "Chef": "Prepare food safely while planning menus, timing, and kitchen workflows.",
    "Electrician": "Install, inspect, and troubleshoot electrical systems safely.",
    "Fashion Designer": "Develop clothing concepts and turn them into wearable designs.",
    "Environmental Scientist": "Study environmental conditions and help assess human impacts.",
    "Marine Biologist": "Study ocean life and ecosystems using field and laboratory methods.",
    "Sports Coach": "Help athletes practice skills, work as a team, and develop safely.",
    "Cloud Architect": "Design secure, scalable cloud systems that meet an organization's technical needs.",
    "DevOps Engineer": "Automate software delivery and help teams operate reliable services.",
    "Data Analyst": "Turn datasets into clear findings that help people make informed decisions.",
    "Product Manager": "Coordinate user needs, product goals, and delivery with a cross-functional team.",
    "UX Researcher": "Study user needs and behavior to help teams make more usable products.",
    "Social Worker": "Support people and communities in accessing services and navigating challenges.",
    "Paramedic": "Provide urgent pre-hospital care and coordinate safe transfer to medical services.",
    "Public Health Analyst": "Analyze population health information to support community health decisions.",
    "Geologist": "Study Earth's materials and processes through fieldwork, samples, and analysis.",
    "Renewable Energy Engineer": "Design and evaluate systems that generate or store energy from renewable sources.",
    "Urban Planner": "Help communities plan land use, transport, housing, and public spaces.",
    "Human Resources Manager": "Support hiring, employee development, workplace policies, and people operations.",
    "Supply Chain Analyst": "Use data to improve how goods are sourced, moved, stored, and delivered.",
    "Content Creator": "Plan and produce useful or entertaining media for a defined audience.",
    "Forensic Scientist": "Examine evidence using validated scientific methods and document findings carefully.",
}

CATEGORY_RESPONSIBILITIES = {
    "Healthcare & Life Science": [
        "Listen to people and gather accurate information.",
        "Use evidence and professional standards to guide decisions.",
        "Communicate plans clearly and work with other specialists.",
    ],
    "Technology": [
        "Understand user or organization needs before choosing a solution.",
        "Build, configure, test, or analyze technical systems.",
        "Document work and improve reliability, accessibility, or security.",
    ],
    "Engineering & Built Environment": [
        "Translate requirements into safe, practical designs or operations.",
        "Use models, measurements, and technical tools to evaluate options.",
        "Collaborate with specialists and refine work against constraints.",
    ],
    "Education & Research": [
        "Plan a clear question, lesson, or investigation.",
        "Gather evidence and interpret it carefully.",
        "Explain findings or concepts to learners and colleagues.",
    ],
    "Business & Finance": [
        "Understand customer, organizational, or financial needs.",
        "Analyze information and plan resources or campaigns.",
        "Communicate recommendations and review results.",
    ],
    "Law & Public Service": [
        "Gather facts and understand relevant rules and context.",
        "Communicate clearly, fairly, and respectfully.",
        "Make careful decisions while following ethical procedures.",
    ],
    "Creative & Media": [
        "Research an audience, subject, or communication goal.",
        "Develop ideas and produce thoughtful creative work.",
        "Revise from feedback and prepare work for its intended medium.",
    ],
    "Environment & Outdoors": [
        "Observe people, environments, or performance in context.",
        "Collect information safely and interpret it responsibly.",
        "Share practical findings and support ongoing improvement.",
    ],
    "Skilled Trades & Hospitality": [
        "Plan work, tools, materials, and safety requirements.",
        "Deliver a reliable service or product with care and precision.",
        "Check quality, solve problems, and improve the process.",
    ],
}

WORK_STYLE_LABELS = {
    "people": "People-focused",
    "analytical": "Analytical",
    "hands_on": "Hands-on",
    "creative": "Creative",
    "structured": "Structured",
    "independent": "Independent",
}

CAREER_STYLES = {
    "Doctor": ("people", "analytical", "structured"),
    "Engineer": ("analytical", "hands_on", "structured"),
    "Software Developer": ("analytical", "creative", "independent"),
    "Web Developer": ("analytical", "creative", "hands_on"),
    "Data Scientist": ("analytical", "independent", "structured"),
    "AI Engineer": ("analytical", "creative", "independent"),
    "Machine Learning Engineer": ("analytical", "independent", "structured"),
    "Cybersecurity Analyst": ("analytical", "structured", "independent"),
    "Network Engineer": ("hands_on", "analytical", "structured"),
    "Database Administrator": ("analytical", "structured", "independent"),
    "Teacher": ("people", "creative", "structured"),
    "Professor": ("people", "analytical", "independent"),
    "Scientist": ("analytical", "independent", "structured"),
    "Researcher": ("analytical", "independent", "structured"),
    "Pharmacist": ("people", "analytical", "structured"),
    "Nurse": ("people", "hands_on", "structured"),
    "Surgeon": ("hands_on", "analytical", "structured"),
    "Dentist": ("people", "hands_on", "structured"),
    "Veterinarian": ("people", "hands_on", "analytical"),
    "Psychologist": ("people", "analytical", "independent"),
    "Architect": ("creative", "analytical", "hands_on"),
    "Civil Engineer": ("analytical", "hands_on", "structured"),
    "Mechanical Engineer": ("hands_on", "analytical", "creative"),
    "Electrical Engineer": ("hands_on", "analytical", "structured"),
    "Robotics Engineer": ("hands_on", "analytical", "creative"),
    "Accountant": ("structured", "analytical", "independent"),
    "Financial Analyst": ("analytical", "structured", "independent"),
    "Economist": ("analytical", "independent", "structured"),
    "Business Manager": ("people", "structured", "analytical"),
    "Entrepreneur": ("creative", "people", "independent"),
    "Lawyer": ("people", "analytical", "independent"),
    "Judge": ("analytical", "structured", "independent"),
    "Police Officer": ("people", "hands_on", "structured"),
    "Pilot": ("hands_on", "analytical", "structured"),
    "Astronaut": ("analytical", "hands_on", "people"),
    "Journalist": ("people", "creative", "independent"),
    "Writer": ("creative", "independent", "structured"),
    "Graphic Designer": ("creative", "independent", "hands_on"),
    "UI/UX Designer": ("creative", "people", "analytical"),
    "Photographer": ("creative", "hands_on", "independent"),
    "Filmmaker": ("creative", "people", "hands_on"),
    "Animator": ("creative", "hands_on", "independent"),
    "Game Developer": ("creative", "analytical", "people"),
    "Digital Marketer": ("creative", "analytical", "people"),
    "Chef": ("hands_on", "creative", "structured"),
    "Electrician": ("hands_on", "analytical", "structured"),
    "Fashion Designer": ("creative", "hands_on", "independent"),
    "Environmental Scientist": ("analytical", "hands_on", "independent"),
    "Marine Biologist": ("analytical", "hands_on", "independent"),
    "Sports Coach": ("people", "hands_on", "structured"),
    "Cloud Architect": ("analytical", "structured", "independent"),
    "DevOps Engineer": ("analytical", "hands_on", "structured"),
    "Data Analyst": ("analytical", "structured", "independent"),
    "Product Manager": ("people", "analytical", "creative"),
    "UX Researcher": ("people", "analytical", "creative"),
    "Social Worker": ("people", "structured", "independent"),
    "Paramedic": ("people", "hands_on", "structured"),
    "Public Health Analyst": ("analytical", "people", "structured"),
    "Geologist": ("analytical", "hands_on", "independent"),
    "Renewable Energy Engineer": ("analytical", "hands_on", "creative"),
    "Urban Planner": ("people", "analytical", "creative"),
    "Human Resources Manager": ("people", "structured", "analytical"),
    "Supply Chain Analyst": ("analytical", "structured", "independent"),
    "Content Creator": ("creative", "independent", "people"),
    "Forensic Scientist": ("analytical", "structured", "independent"),
}

RESOURCE_CATALOG = {
    "CS50x": {
        "title": "CS50's Introduction to Computer Science",
        "url": "https://cs50.harvard.edu/x/",
        "provider": "Harvard",
        "free": True,
        "skills": ["programming", "computer science", "problem solving"],
    },
    "freeCodeCamp": {
        "title": "Free coding and web-development courses",
        "url": "https://www.freecodecamp.org/learn/",
        "provider": "freeCodeCamp",
        "free": True,
        "skills": ["programming", "web development", "javascript", "data analysis"],
    },
    "MDN": {
        "title": "MDN Web Development Learning Area",
        "url": "https://developer.mozilla.org/en-US/docs/Learn",
        "provider": "MDN",
        "free": True,
        "skills": ["html", "css", "javascript", "accessibility", "web development"],
    },
    "Odin": {
        "title": "The Odin Project",
        "url": "https://www.theodinproject.com/",
        "provider": "The Odin Project",
        "free": True,
        "skills": ["web development", "javascript", "programming", "projects"],
    },
    "KhanMath": {
        "title": "Khan Academy: Math",
        "url": "https://www.khanacademy.org/math",
        "provider": "Khan Academy",
        "free": True,
        "skills": ["mathematics", "algebra", "statistics"],
    },
    "KhanScience": {
        "title": "Khan Academy: Science",
        "url": "https://www.khanacademy.org/science",
        "provider": "Khan Academy",
        "free": True,
        "skills": ["biology", "chemistry", "physics", "science"],
    },
    "OpenStax": {
        "title": "OpenStax free textbooks",
        "url": "https://openstax.org/subjects",
        "provider": "OpenStax",
        "free": True,
        "skills": ["biology", "chemistry", "physics", "economics", "statistics"],
    },
    "MITOCW": {
        "title": "MIT OpenCourseWare",
        "url": "https://ocw.mit.edu/",
        "provider": "MIT",
        "free": True,
        "skills": ["engineering", "mathematics", "science", "computer science"],
    },
    "OpenLearn": {
        "title": "OpenLearn free courses",
        "url": "https://www.open.edu/openlearn/",
        "provider": "The Open University",
        "free": True,
        "skills": ["business", "education", "health", "writing", "study skills"],
    },
    "GCF": {
        "title": "GCFGlobal free learning",
        "url": "https://edu.gcfglobal.org/en/",
        "provider": "GCFGlobal",
        "free": True,
        "skills": ["communication", "digital skills", "business", "career planning"],
    },
    "W3C": {
        "title": "W3C Web Accessibility Tutorials",
        "url": "https://www.w3.org/WAI/tutorials/",
        "provider": "W3C",
        "free": True,
        "skills": ["accessibility", "web design", "inclusive design"],
    },
}

CATEGORY_RESOURCES = {
    "Healthcare & Life Science": ("KhanScience", "OpenStax", "OpenLearn"),
    "Technology": ("CS50x", "freeCodeCamp", "KhanMath"),
    "Engineering & Built Environment": ("KhanMath", "KhanScience", "MITOCW"),
    "Education & Research": ("OpenLearn", "OpenStax", "GCF"),
    "Business & Finance": ("OpenLearn", "KhanMath", "GCF"),
    "Law & Public Service": ("OpenLearn", "GCF", "OpenStax"),
    "Creative & Media": ("GCF", "freeCodeCamp", "W3C"),
    "Environment & Outdoors": ("KhanScience", "OpenStax", "OpenLearn"),
    "Skilled Trades & Hospitality": ("OpenLearn", "KhanMath", "KhanScience"),
}

CATEGORY_PROJECTS = {
    "Healthcare & Life Science": (
        "Create an evidence-based health topic explainer with sources and a glossary.",
        "Interview a qualified professional about their training and typical workday.",
    ),
    "Technology": (
        "Build a small, documented project that solves a problem you encounter.",
        "Publish a portfolio write-up with your approach, tests, and lessons learned.",
    ),
    "Engineering & Built Environment": (
        "Design a small solution to a local problem and document constraints and trade-offs.",
        "Build a safe scale model or simulation and compare the results with your design.",
    ),
    "Education & Research": (
        "Create a short lesson or research poster and ask a peer to review its clarity.",
        "Investigate a question using credible sources and explain your method and findings.",
    ),
    "Business & Finance": (
        "Analyze a familiar product or service and outline its audience, costs, and value.",
        "Create a simple budget or campaign plan using clearly stated assumptions.",
    ),
    "Law & Public Service": (
        "Summarize a public issue using primary sources and explain more than one perspective.",
        "Practice a structured debate or community-service project with reflection notes.",
    ),
    "Creative & Media": (
        "Create a small brief-based piece and document the audience and design choices.",
        "Build a portfolio case study showing drafts, feedback, and final work.",
    ),
    "Environment & Outdoors": (
        "Record a small local observation project and explain its limits and sources.",
        "Plan a safe community, conservation, or sports activity and evaluate its impact.",
    ),
    "Skilled Trades & Hospitality": (
        "Plan and safely complete a small practice project under appropriate supervision.",
        "Document a process checklist, quality checks, and what you would improve next time.",
    ),
}

CAREER_EDUCATION = {
    "Doctor": "Medical degree and supervised clinical training; requirements vary by country.",
    "Surgeon": "Medical degree followed by specialist surgical training and licensing.",
    "Dentist": "Dental degree and licensing; requirements vary by country.",
    "Pharmacist": "Accredited pharmacy education and licensing requirements vary by country.",
    "Nurse": "Nursing education and registration/licensing requirements vary by country.",
    "Veterinarian": "Accredited veterinary education and licensing requirements vary by country.",
    "Psychologist": "Psychology degree; independent clinical practice often requires postgraduate study and licensing.",
    "Professor": "Usually advanced study and research experience; requirements vary by institution.",
    "Lawyer": "Legal education and qualification/licensing depend on the jurisdiction.",
    "Judge": "Typically substantial legal experience and appointment or election under local law.",
    "Police Officer": "Local recruitment, training, and background requirements apply.",
    "Pilot": "Flight training, medical certification, and licenses depend on aircraft and country.",
    "Astronaut": "Highly competitive; agencies set advanced education, experience, and medical requirements.",
    "Teacher": "Education and certification requirements vary by school system and country.",
    "Electrician": "Apprenticeship or technical training and local licensing may be required.",
    "Chef": "Hospitality training or kitchen experience; food-safety rules apply locally.",
}

EDUCATION_BY_CATEGORY = {
    "Healthcare & Life Science": "Relevant science study is a useful start; clinical roles require accredited training and local licensing.",
    "Technology": "Build a foundation through school, self-study, projects, or a relevant degree; requirements differ by role.",
    "Engineering & Built Environment": "Math and science are useful foundations; regulated engineering titles may require accredited study and licensing.",
    "Education & Research": "Relevant subject study is useful; teaching credentials and research degrees depend on the role.",
    "Business & Finance": "Business, economics, mathematics, or practical project experience can provide a foundation.",
    "Law & Public Service": "Requirements depend strongly on the jurisdiction and public-service role; research local pathways.",
    "Creative & Media": "A portfolio, practice, and feedback are important; formal education is useful for some roles but not universal.",
    "Environment & Outdoors": "Science, field experience, and safety training are useful; requirements vary by specialty.",
    "Skilled Trades & Hospitality": "Practical training and supervised experience are useful; check local safety and licensing rules.",
}


def _category_for(career):
    for category, names in CAREER_CATEGORIES.items():
        if career in names:
            return category
    raise ValueError(f"Career {career!r} has no category")


def _learning_stages(career, category, skills):
    focus = skills[:]
    while len(focus) < 3:
        focus.append("communication and problem solving")
    beginner_skills = ", ".join(focus[:2])
    developing_skills = ", ".join(focus[2:4]) or focus[-1]
    applied_skills = ", ".join(focus[4:]) or focus[-1]
    resources = [RESOURCE_CATALOG[key] for key in CATEGORY_RESOURCES[category]]
    fundamentals = [resource for resource in resources if resource["free"]]
    return [
        {
            "level": "Beginner",
            "title": "Explore foundations",
            "learn": [
                f"Understand what {career} work involves and the problems it addresses.",
                f"Start with {beginner_skills}, alongside study, note-taking, and source-checking habits.",
            ],
            "resources": fundamentals[:2],
            "project": CATEGORY_PROJECTS[category][0],
        },
        {
            "level": "Developing",
            "title": "Build core skills",
            "learn": [
                f"Practice {developing_skills} through short, regular exercises.",
                "Learn the safety, ethics, and professional standards that apply to this field.",
            ],
            "resources": fundamentals[1:],
            "project": CATEGORY_PROJECTS[category][1],
        },
        {
            "level": "Applied",
            "title": "Apply what you learn",
            "learn": [
                f"Use {applied_skills} in a longer task with clear requirements.",
                "Ask for feedback, revise your work, and keep a record of what changed.",
            ],
            "resources": fundamentals[:2],
            "project": f"Create a {career.lower()} portfolio case study explaining your goal, process, evidence, and reflection.",
        },
        {
            "level": "Advanced",
            "title": "Prepare for next steps",
            "learn": [
                "Explore advanced training and entry requirements in your location.",
                "Connect with a mentor, teacher, club, supervised placement, or professional community.",
            ],
            "resources": fundamentals[-2:],
            "project": "Present your best work, identify your next learning goal, and update your plan from feedback.",
        },
    ]


def get_career_catalog():
    catalog = []
    for career, career_id in careers.items():
        category = _category_for(career)
        signals = CAREER_SIGNALS[career]
        skills = list(dict.fromkeys(
            [skill.title() for skill in signals[2]]
            + [skill.title() for skill in signals[3]]
        ))
        catalog.append({
            "id": career_id,
            "name": career,
            "category": category,
            "description": CAREER_SUMMARIES[career],
            "responsibilities": CATEGORY_RESPONSIBILITIES[category],
            "education": CAREER_EDUCATION.get(career, EDUCATION_BY_CATEGORY[category]),
            "required_skills": skills,
            "learning_difficulty": (
                "Advanced" if career in {
                    "Doctor", "Surgeon", "Dentist", "Pharmacist", "Veterinarian",
                    "Judge", "Astronaut", "Professor", "Psychologist",
                } else "Developing"
            ),
            "career_paths": [
                career,
                f"Senior {career}",
                f"{career} mentor, specialist, or team lead",
            ],
            "work_styles": [
                WORK_STYLE_LABELS[style]
                for style in CAREER_STYLES.get(career, ())
            ],
            "roadmap": _learning_stages(career, category, skills),
            "resources": [RESOURCE_CATALOG[key] for key in CATEGORY_RESOURCES[category]],
            "projects": list(CATEGORY_PROJECTS[category]),
            "next_steps": [
                f"Try one beginner {career.lower()} learning resource.",
                "Build a small project or supervised experience and ask for feedback.",
                "Check education, safety, and licensing requirements in your region.",
            ],
        })
    return catalog


def find_career(career_id):
    return next(
        (career for career in get_career_catalog() if career["id"] == career_id),
        None,
    )


def quiz_recommendations(answers, limit=5):
    profile = {
        "education": answers["education"],
        "subjects": answers["subjects"],
        "interests": answers["interests"],
        "skills": answers["skills"],
        "preferred_careers": [],
    }
    results = []
    for result in recommend_careers(profile, limit=len(careers)):
        career = find_career(result["id"])
        matched_styles = [
            style for style in answers["work_styles"]
            if style in CAREER_STYLES.get(career["name"], ())
        ]
        score = round(result["score"] * 0.85 + (
            15 * len(matched_styles) / max(len(answers["work_styles"]), 1)
        ))
        reasons = list(result["reasons"])
        if matched_styles:
            reasons.append(
                "This role can include your preferred work style: "
                + ", ".join(WORK_STYLE_LABELS[style] for style in matched_styles)
            )
        results.append({
            **result,
            "score": score,
            "match_percentage": score,
            "reasons": reasons,
            "category": career["category"],
        })
    results.sort(key=lambda result: (-result["score"], result["name"]))
    return results[:limit]
