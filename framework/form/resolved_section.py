

"""
Section de formulaire prête à être affichée.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from django.forms.boundfield import BoundField


@dataclass(frozen=True, slots=True)
class ResolvedSection:
    """
    Représente une section de formulaire dont les champs
    sont résolus en BoundField Django.
    """

    title: str
    
    description: str | None = None

    fields: list[BoundField] = field(default_factory=list)