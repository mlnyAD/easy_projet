

from __future__ import annotations

from enum import StrEnum


class TreeNodeKind(StrEnum):
    """
    Nature structurelle d'un nœud d'arborescence.

    BRANCH représente un nœud pouvant contenir des enfants.
    LEAF représente un nœud terminal.
    """

    BRANCH = "branch"
    LEAF = "leaf"