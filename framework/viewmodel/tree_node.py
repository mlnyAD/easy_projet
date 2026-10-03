

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field

from framework.tree import TreeNodeKind


@dataclass(frozen=True, slots=True)
class TreeNodeViewModel:
    """
    Nœud prêt à être rendu dans une arborescence.
    """

    identifier: str
    label: str
    kind: TreeNodeKind
    icon: str | None
    url: str | None
    is_selected: bool
    is_expanded: bool
    is_disabled: bool
    data_attributes: Mapping[str, str] = field(
        default_factory=dict,
    )
    children: tuple["TreeNodeViewModel", ...] = ()
    source_object: object | None = None

    @property
    def has_children(self) -> bool:
        """
        Indique si le nœud possède au moins un enfant.
        """

        return bool(self.children)