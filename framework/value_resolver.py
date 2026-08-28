

from __future__ import annotations

from collections.abc import Mapping
from typing import Any


class ValueResolutionError(ValueError):
    """
    Erreur produite lors de la résolution d'une valeur.
    """


def resolve_value(
    source: Any,
    name: str,
) -> Any:
    """
    Résout une valeur depuis un mapping ou un objet.

    Le nom peut représenter un chemin d'attributs,
    par exemple :

    - "name"
    - "user.company"
    - "user.company.name"
    """
    if not isinstance(name, str):
        raise TypeError(
            "Le nom de la valeur doit être une chaîne."
        )

    if not name.strip():
        raise ValueError(
            "Le nom de la valeur ne peut pas être vide."
        )

    current = source

    for part in name.split("."):
        if isinstance(current, Mapping):
            if part not in current:
                raise ValueResolutionError(
                    f"La source ne contient pas "
                    f"la valeur {part!r}."
                )

            current = current[part]
            continue

        if not hasattr(current, part):
            raise ValueResolutionError(
                f"L'objet de type "
                f"{type(current).__name__!r} "
                f"ne possède pas l'attribut "
                f"{part!r}."
            )

        current = getattr(
            current,
            part,
        )

    return current