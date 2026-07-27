

"""
Représentation d'un choix proposé par un ChoiceProvider.
"""

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class Choice:
    """
    Représente une valeur sélectionnable.

    Attributes:
        value: Valeur technique.
        label: Libellé affiché à l'utilisateur.
    """

    value: str
    label: str