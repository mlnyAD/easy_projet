

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class TreeWorkspaceViewModel:
    """
    Environnement de travail disponible dans une arborescence.
    """

    identifier: str
    label: str
    icon: str | None
    is_active: bool
    url: str | None = None