def generate_roadmap(missing_skills):
    if not missing_skills:
        return ["Your resume mentions all listed skills for this role. "
                "Build a project that demonstrates them."]

    roadmap = []

    for week, skill in enumerate(missing_skills[:4], start=1):
        roadmap.append(
            f"Week {week}: Learn {skill} basics and complete one small practice task."
        )

    if len(missing_skills) > 4:
        remaining = ", ".join(missing_skills[4:])
        roadmap.append(f"After Week 4: Continue with {remaining}.")

    return roadmap