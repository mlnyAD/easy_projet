

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True, slots=True)
class FormCollectionColumnDefinition:
    """
    Décrit une colonne d'une collection de formulaire.

    Une colonne peut représenter :
    - un champ éditable du formset ;
    - une valeur d'affichage ;
    - une donnée dérivée ou enrichie.

    Le composant ne contient aucune logique métier.
    """

    name: str

    label: str | None = None

    field_name: str | None = None
    
    source_name: str | None = None

    visible: bool = True

    align: str = "left"

    width: str = "auto"

    readonly: bool = False


@dataclass(frozen=True, slots=True)
class FormCollectionDefinition:
    """
    Décrit une collection répétable rattachée à un formulaire.

    Une collection correspond typiquement à un formset Django :
    participants, affectations, dépendances, destinataires, etc.
    """

    name: str

    title: str

    description: str | None = None

    columns: tuple[FormCollectionColumnDefinition, ...] = field(
        default_factory=tuple
    )

    allow_add: bool = True

    allow_delete: bool = True

    add_label: str = "Ajouter"

    delete_label: str = "Supprimer"

    visible: bool = True