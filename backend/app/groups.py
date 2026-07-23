"""Balanced group builder.

Splits classified respondents into 6 groups sized as evenly as possible
(remainder groups get one extra member), while spreading the five
FourSight buckets (A/B/C/D/Integrador) across groups instead of clustering
same-type people together.

Approach: visit people largest-bucket-first, and for each person greedily
place them in the still-open group that currently has the fewest members of
their bucket (ties broken by smallest current group). That directly
optimizes for "different profiles per group" instead of relying on a fixed
dealing pattern, which breaks down when one bucket dominates (e.g. many
people tied across several preferences and bucketed under the same
alphabetically-first type).
"""
from collections import defaultdict

NUM_GROUPS = 6


def _bucket_key(person: dict) -> str:
    return "I" if person["is_integrador"] else person["primary_types"][0]


def _composition(members: list[dict]) -> dict:
    counts = {"A": 0, "B": 0, "C": 0, "D": 0, "I": 0}
    for m in members:
        counts[_bucket_key(m)] += 1
    return counts


def build_groups(people: list[dict], num_groups: int = NUM_GROUPS) -> list[dict]:
    if not people:
        return []

    buckets: dict[str, list[dict]] = defaultdict(list)
    for p in people:
        buckets[_bucket_key(p)].append(p)
    for key in buckets:
        buckets[key].sort(key=lambda p: p["nombre"])

    # visit largest bucket first so the hardest-to-place people get first pick of slots
    visit_order: list[dict] = []
    for key in sorted(buckets, key=lambda k: -len(buckets[k])):
        visit_order.extend(buckets[key])

    total = len(people)
    base, remainder = divmod(total, num_groups)
    target_sizes = [base + 1] * remainder + [base] * (num_groups - remainder)

    groups: list[list[dict]] = [[] for _ in range(num_groups)]
    type_counts_by_group = [defaultdict(int) for _ in range(num_groups)]

    for person in visit_order:
        key = _bucket_key(person)
        open_groups = [g for g in range(num_groups) if len(groups[g]) < target_sizes[g]]
        best = min(open_groups, key=lambda g: (type_counts_by_group[g][key], len(groups[g])))
        groups[best].append(person)
        type_counts_by_group[best][key] += 1

    return [
        {
            "id": idx + 1,
            "nombre": f"Grupo {idx + 1}",
            "size": len(members),
            "members": members,
            "composition": _composition(members),
        }
        for idx, members in enumerate(groups)
    ]
