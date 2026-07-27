

"""
EPContext

Contexte d'exécution du framework.

Une instance d'EPContext représente le contexte de travail actif
d'un opérateur pendant une opération.

Elle est transmise à l'ensemble des composants du framework
(EPList, EPForm, EPDetail, Providers, Workflows, ...).

EPContext est immuable.
Un changement de contexte de travail implique la création
d'une nouvelle instance.
"""

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True, slots=True)
class EPContext:
    """Contexte d'exécution du framework."""

    operator: Any
    client_environment: Any
    company: Any | None = None
    project: Any | None = None