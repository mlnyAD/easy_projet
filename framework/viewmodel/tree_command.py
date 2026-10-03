

from __future__ import annotations

from dataclasses import dataclass

from framework.tree import TreeCommandTarget


@dataclass(frozen=True, slots=True)
class TreeCommandViewModel:
    """
    Représentation de présentation d'une commande d'arborescence.
    """

    identifier: str
    label: str
    icon: str
    target: TreeCommandTarget
    url: str | None
    method: str
    is_enabled: bool