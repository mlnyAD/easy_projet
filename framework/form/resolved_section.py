

"""
Section de formulaire prête à être affichée.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from framework.form.resolved_field import ResolvedField


@dataclass(frozen=True, slots=True)
class ResolvedSection:
    """
    Représente une section dont les champs sont prêts à être affichés.
    """

    title: str

    description: str | None = None

    fields: list[ResolvedField] = field(default_factory=list)