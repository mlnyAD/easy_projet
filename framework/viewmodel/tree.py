
    
from __future__ import annotations

from dataclasses import dataclass

from framework.viewmodel.tree_command import (
    TreeCommandViewModel,
)
from framework.viewmodel.tree_node import TreeNodeViewModel
from framework.viewmodel.tree_workspace import (
    TreeWorkspaceViewModel,
)


@dataclass(frozen=True, slots=True)
class TreeViewModel:
    """
    Vue complète d'une arborescence.
    """

    identifier: str
    workspaces: tuple[TreeWorkspaceViewModel, ...]
    active_workspace: TreeWorkspaceViewModel
    root_nodes: tuple[TreeNodeViewModel, ...]
    commands: tuple[TreeCommandViewModel, ...]
    selected_node_identifier: str | None