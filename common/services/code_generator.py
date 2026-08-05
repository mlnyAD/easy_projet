

"""
Génération des codes techniques séquentiels.
"""

from __future__ import annotations

import re
import unicodedata

from django.db import models


def normalize_code_part(value: str) -> str:
    """
    Normalise une valeur destinée à faire partie d'un code.
    """
    normalized = unicodedata.normalize(
        "NFKD",
        value,
    )
    ascii_value = normalized.encode(
        "ascii",
        "ignore",
    ).decode("ascii")

    return re.sub(
        r"[^A-Z0-9]+",
        "_",
        ascii_value.upper(),
    ).strip("_")


def generate_scoped_code(
    *,
    model: type[models.Model],
    parent: models.Model,
    parent_field_name: str,
    prefix: str,
    max_length: int,
    digits: int = 3,
) -> str:
    """
    Génère un code séquentiel unique dans le périmètre d'un parent.

    Le parent doit être verrouillé par l'appelant avec select_for_update().
    """
    if parent.pk is None:
        raise ValueError(
            "Le parent doit être enregistré avant la génération du code."
        )

    normalized_prefix = normalize_code_part(prefix)

    if not normalized_prefix:
        raise ValueError(
            "Le préfixe du code ne peut pas être vide."
        )

    expression = re.compile(
        rf"^{re.escape(normalized_prefix)}_(\d+)$"
    )

    existing_codes = (
        model.objects
        .filter(
            **{
                parent_field_name: parent,
                "code__startswith": f"{normalized_prefix}_",
            }
        )
        .values_list(
            "code",
            flat=True,
        )
    )

    highest_number = 0

    for existing_code in existing_codes:
        match = expression.match(existing_code)

        if match is not None:
            highest_number = max(
                highest_number,
                int(match.group(1)),
            )

    next_number = highest_number + 1

    code = (
        f"{normalized_prefix}_"
        f"{next_number:0{digits}d}"
    )

    if len(code) > max_length:
        raise ValueError(
            f"Le code généré dépasse la longueur maximale "
            f"de {max_length} caractères."
        )

    return code