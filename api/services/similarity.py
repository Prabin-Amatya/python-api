from django.db import transaction

from api.models import AppUser, SimilarityScore


REASON_MAP = {
    "anger": 1,
    "ego": 2,
    "fear": 3,
    "pressure": 4,
    "genuine_interest": 5,
    "grind": 6,
    "fomo": 7,
    "self": 8,
}

STRUGGLE_MAP = {
    "last_minute_work_done": 1,
    "i_dont_get_things_done": 2,
    "i_am_very_consistent": 3,
    "i_get_most_things_done_but_struggle_sometimes": 4,
}

COMEBACK_MAP = {"yes": 1, "no": 2, "already_doing_good": 3}
RELATIONSHIP_MAP = {
    "loving": 1,
    "absent_but_in_life": 2,
    "abandoned": 3,
    "trouble_communicating": 4,
}


def _tokenize_hobbies(hobbies_csv):
    if not hobbies_csv:
        return []
    return [item.strip().lower() for item in hobbies_csv.split(",") if item.strip()]


def _jaccard_similarity(left_tokens, right_tokens):
    left = set(left_tokens)
    right = set(right_tokens)
    if not left and not right:
        return 1.0
    if not left or not right:
        return 0.0
    return len(left & right) / len(left | right)


def _normalized_difference(left, right, max_value):
    if max_value == 0:
        return 1.0
    return 1.0 - (abs(left - right) / max_value)


def _exact_or_none(left, right):
    return 1.0 if left == right else 0.0


def _build_similarity_score(source, target):
    scores = [
        _normalized_difference(source.age, target.age, 100),
        _normalized_difference(float(source.income), float(target.income), 1_000_000),
        _exact_or_none(source.job.lower(), target.job.lower()),
        _exact_or_none(source.marital_status.lower(), target.marital_status.lower()),
        _normalized_difference(source.children, target.children, 10),
        _exact_or_none(source.gender.lower(), target.gender.lower()),
        _jaccard_similarity(_tokenize_hobbies(source.hobbies_csv), _tokenize_hobbies(target.hobbies_csv)),
        _normalized_difference(source.autism_level, target.autism_level, 10),
        _normalized_difference(source.adhd_level, target.adhd_level, 10),
        _normalized_difference(source.ocd_level, target.ocd_level, 10),
        _exact_or_none(source.personality_type.lower(), target.personality_type.lower()),
        _exact_or_none(source.self_worth_tasks, target.self_worth_tasks),
        _exact_or_none(source.bullied, target.bullied),
        _exact_or_none(source.volatile_family, target.volatile_family),
        _exact_or_none(source.clinically_depressed, target.clinically_depressed),
        _exact_or_none(source.grief_impact, target.grief_impact),
        _exact_or_none(source.morning_person, target.morning_person),
        _normalized_difference(
            REASON_MAP.get(source.reason_productive, 0),
            REASON_MAP.get(target.reason_productive, 0),
            max(REASON_MAP.values()),
        ),
        _normalized_difference(
            STRUGGLE_MAP.get(source.productivity_struggle, 0),
            STRUGGLE_MAP.get(target.productivity_struggle, 0),
            max(STRUGGLE_MAP.values()),
        ),
        _normalized_difference(
            COMEBACK_MAP.get(source.comeback_plan, 0),
            COMEBACK_MAP.get(target.comeback_plan, 0),
            max(COMEBACK_MAP.values()),
        ),
        _normalized_difference(
            RELATIONSHIP_MAP.get(source.mother_relationship, 0),
            RELATIONSHIP_MAP.get(target.mother_relationship, 0),
            max(RELATIONSHIP_MAP.values()),
        ),
        _normalized_difference(
            RELATIONSHIP_MAP.get(source.father_relationship, 0),
            RELATIONSHIP_MAP.get(target.father_relationship, 0),
            max(RELATIONSHIP_MAP.values()),
        ),
    ]
    return round(sum(scores) / len(scores), 4)


@transaction.atomic
def recompute_similarity_matrix():
    users = list(AppUser.objects.all().prefetch_related("habits"))
    SimilarityScore.objects.all().delete()

    for source in users:
        ranked = []
        for target in users:
            if source.id == target.id:
                continue
            ranked.append((target, _build_similarity_score(source, target)))

        ranked.sort(key=lambda item: item[1], reverse=True)
        for index, (target, score) in enumerate(ranked, start=1):
            SimilarityScore.objects.create(
                source_user=source,
                target_user=target,
                score=score,
                rank=index,
            )


def get_similar_users_with_habits(user_id, limit=5):
    similarities = (
        SimilarityScore.objects.select_related("target_user")
        .filter(source_user_id=user_id)
        .order_by("rank")[:limit]
    )

    payload = []
    for similarity in similarities:
        target = similarity.target_user
        habits = target.habits.filter(success_rate__gte=0.6, is_active=True).order_by("-success_rate")
        payload.append(
            {
                "user_id": target.id,
                "display_name": target.display_name,
                "similarity_score": similarity.score,
                "success_rate": round(target.success_rate, 3),
                "habits": [
                    {
                        "name": habit.name,
                        "description": habit.description,
                        "success_rate": round(habit.success_rate, 3),
                    }
                    for habit in habits
                ],
            }
        )
    return payload
