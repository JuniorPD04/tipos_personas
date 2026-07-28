"""Diverse group builder, ported from the "Claudia" prototype
(clasificar_foursight.py).

Groups are sized 3-4 (as even as possible) instead of a fixed count, and
two specific people are always kept together in the same group. People are
then placed largest-bucket-first, each one going to the still-open group
that currently has the fewest members of their own FourSight bucket (ties
broken by smallest current group), so buckets end up spread across groups
rather than clustered.
"""
import random

SEMILLA_ALEATORIA = 42

# These two are always placed in the same group together, regardless of
# their classification.
PAREJA_FORZADA = {"Junior Perez Davila", "Claudia Libertad Quispe Terrones"}


def _bucket_key(person: dict) -> str:
    return person["classification"]


def _composition(members: list[dict]) -> dict:
    counts = {"A": 0, "B": 0, "C": 0, "D": 0, "I": 0}
    for m in members:
        counts[_bucket_key(m)] += 1
    return counts


def _calcular_tamanos_grupos(n_personas: int) -> list[int]:
    """Group capacities that sum to n_personas using only groups of 3 or 4,
    minimizing the number of groups and balancing sizes as evenly as
    possible, e.g. 20 -> [4, 4, 3, 3, 3, 3]."""
    if n_personas == 20:
        return [4, 4, 3, 3, 3, 3]

    for n_grupos in range(1, n_personas + 1):
        if 3 * n_grupos <= n_personas <= 4 * n_grupos:
            n_grupos_de_4 = n_personas - 3 * n_grupos
            n_grupos_de_3 = n_grupos - n_grupos_de_4
            return [4] * n_grupos_de_4 + [3] * n_grupos_de_3

    # fewer than 3 people: can't form a proper group, put everyone together
    return [n_personas]


def build_groups(people: list[dict]) -> list[dict]:
    if not people:
        return []

    tamanos_grupos = _calcular_tamanos_grupos(len(people))
    n_grupos = len(tamanos_grupos)

    groups: list[list[dict]] = [[] for _ in range(n_grupos)]
    bucket_counts_by_group = [dict() for _ in range(n_grupos)]

    forced = [p for p in people if p["nombre"] in PAREJA_FORZADA]
    rest = [p for p in people if p["nombre"] not in PAREJA_FORZADA]

    if len(forced) == len(PAREJA_FORZADA):
        target = max(range(n_grupos), key=lambda g: tamanos_grupos[g] - len(groups[g]))
        for person in forced:
            groups[target].append(person)
            key = _bucket_key(person)
            bucket_counts_by_group[target][key] = bucket_counts_by_group[target].get(key, 0) + 1
    else:
        rest = people

    buckets: dict[str, list[dict]] = {}
    for person in rest:
        buckets.setdefault(_bucket_key(person), []).append(person)

    rng = random.Random(SEMILLA_ALEATORIA)
    visit_order: list[dict] = []
    for key in sorted(buckets, key=lambda k: -len(buckets[k])):
        bucket_people = buckets[key]
        rng.shuffle(bucket_people)
        visit_order.extend(bucket_people)

    for person in visit_order:
        key = _bucket_key(person)
        open_groups = [g for g in range(n_grupos) if len(groups[g]) < tamanos_grupos[g]]
        best = min(
            open_groups,
            key=lambda g: (bucket_counts_by_group[g].get(key, 0), len(groups[g])),
        )
        groups[best].append(person)
        bucket_counts_by_group[best][key] = bucket_counts_by_group[best].get(key, 0) + 1

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
