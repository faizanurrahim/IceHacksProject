ALLOWED_FIELDS = {
    "education",
    "subjects",
    "interests",
    "skills",
    "preferred_careers",
}
LIST_FIELDS = ALLOWED_FIELDS - {"education"}


def validate_description(raw_description):
    if isinstance(raw_description, list):
        source = {}
        for item in raw_description:
            if not isinstance(item, dict):
                return None, "Invalid description format"
            field = item.get("field")
            if not isinstance(field, str) or field not in ALLOWED_FIELDS:
                return None, "Invalid description field"
            if field in source:
                return None, f"Duplicate field: {field}"
            source[field] = item.get("value")
    elif isinstance(raw_description, dict):
        source = raw_description
    else:
        return None, "Description must be an object or array"

    if set(source) != ALLOWED_FIELDS:
        missing = ALLOWED_FIELDS - set(source)
        unexpected = set(source) - ALLOWED_FIELDS
        if missing:
            return None, "Missing fields: " + ", ".join(sorted(missing))
        return None, "Invalid fields: " + ", ".join(sorted(unexpected))

    answers = {}
    education = source.get("education")
    if not isinstance(education, str) or not education.strip():
        return None, "Education is required"
    if len(education.strip()) > 80:
        return None, "Education must be 80 characters or fewer"
    answers["education"] = education.strip()

    for field in sorted(LIST_FIELDS):
        value = source.get(field)
        if not isinstance(value, list) or not value:
            return None, f"{field} must be a non-empty list"
        if len(value) > 20:
            return None, f"{field} may contain at most 20 items"
        if not all(
            isinstance(item, str) and item.strip() and len(item.strip()) <= 80
            for item in value
        ):
            return None, f"{field} must contain strings of 1 to 80 characters"
        answers[field] = list(dict.fromkeys(item.strip() for item in value))
    return answers, None
