

"""
Collection de formulaires prête à être affichée.
"""

from __future__ import annotations

from dataclasses import dataclass

from django.forms.forms import BaseForm
from django.forms.formsets import BaseFormSet

from framework.form.collection import (
    FormCollectionColumnDefinition,
    FormCollectionDefinition,
)
from framework.form.resolved_collection_cell import (
    ResolvedFormCollectionCell,
)
from framework.form.resolved_collection_row import (
    ResolvedFormCollectionRow,
)
from framework.value_resolver import resolve_value


@dataclass(frozen=True, slots=True)
class ResolvedFormCollection:
    """
    Associe une définition de collection Easy Projet
    à son formset Django.

    La collection résout également chaque formulaire du formset
    en une ligne constituée de cellules prêtes à être affichées.
    """

    definition: FormCollectionDefinition

    formset: BaseFormSet

    def __post_init__(self) -> None:
        if not isinstance(
            self.definition,
            FormCollectionDefinition,
        ):
            raise TypeError(
                "La propriété 'definition' doit être une instance "
                "de FormCollectionDefinition."
            )

        if not isinstance(
            self.formset,
            BaseFormSet,
        ):
            raise TypeError(
                "La propriété 'formset' doit être une instance "
                "de BaseFormSet."
            )

        if (
            self.definition.allow_delete
            and not self.formset.can_delete
        ):
            raise ValueError(
                f"La collection {self.definition.name!r} autorise "
                "la suppression, mais le formset Django "
                "ne définit pas can_delete=True."
            )

    @property
    def name(self) -> str:
        """Retourne le nom de la collection."""
        return self.definition.name

    @property
    def title(self) -> str:
        """Retourne le titre de la collection."""
        return self.definition.title

    @property
    def description(self) -> str | None:
        """Retourne la description de la collection."""
        return self.definition.description

    @property
    def columns(self) -> tuple[FormCollectionColumnDefinition, ...]:
        """Retourne les colonnes déclarées."""
        return self.definition.columns

    @property
    def allow_add(self) -> bool:
        """Indique si des lignes peuvent être ajoutées."""
        return self.definition.allow_add

    @property
    def allow_delete(self) -> bool:
        """Indique si des lignes peuvent être supprimées."""
        return self.definition.allow_delete

    @property
    def add_label(self) -> str:
        """Retourne le libellé de l'action d'ajout."""
        return self.definition.add_label

    @property
    def delete_label(self) -> str:
        """Retourne le libellé de l'action de suppression."""
        return self.definition.delete_label

    @property
    def visible(self) -> bool:
        """Indique si la collection est visible."""
        return self.definition.visible

    @property
    def management_form(self):
        """Retourne le formulaire de gestion Django."""
        return self.formset.management_form

    @property
    def forms(self):
        """Retourne les formulaires constituant la collection."""
        return self.formset.forms

    @property
    def empty_form(self):
        """
        Retourne le formulaire modèle utilisé
        pour les ajouts dynamiques.
        """
        return self.formset.empty_form

    @property
    def non_form_errors(self):
        """Retourne les erreurs globales du formset."""
        return self.formset.non_form_errors()

    @property
    def rows(self) -> list[ResolvedFormCollectionRow]:
        """
        Résout les formulaires du formset en lignes d'affichage.
        """
        return [
            self._resolve_row(django_form)
            for django_form in self.formset.forms
        ]

    @property
    def empty_row(self) -> ResolvedFormCollectionRow:
        """
        Résout le formulaire modèle utilisé pour les ajouts dynamiques.

        Les colonnes d'affichage ne sont pas résolues car l'empty_form
        ne représente pas encore une instance métier existante.
        """
        cells = [
            self._resolve_empty_cell(
                self.formset.empty_form,
                column,
            )
            for column in self.definition.columns
            if column.visible
        ]

        return ResolvedFormCollectionRow(
            django_form=self.formset.empty_form,
            cells=cells,
        )
        
    def _resolve_row(
        self,
        django_form: BaseForm,
    ) -> ResolvedFormCollectionRow:
        """
        Résout un formulaire Django en ligne de collection.
        """
        cells = [
            self._resolve_cell(
                django_form,
                column,
            )
            for column in self.definition.columns
            if column.visible
        ]

        return ResolvedFormCollectionRow(
            django_form=django_form,
            cells=cells,
        )

    def _resolve_cell(
        self,
        django_form: BaseForm,
        column: FormCollectionColumnDefinition,
    ) -> ResolvedFormCollectionCell:
        """
        Résout une colonne pour un formulaire donné.

        Une colonne déclarant field_name est associée
        à un BoundField Django.

        Une colonne déclarant source_name obtient sa valeur
        depuis l'instance portée par le formulaire.
        """
        if column.field_name is not None:
            try:
                bound_field = django_form[column.field_name]
            except KeyError as error:
                raise ValueError(
                    f"La colonne {column.name!r} référence "
                    f"le champ Django {column.field_name!r}, "
                    "absent du formulaire."
                ) from error

            return ResolvedFormCollectionCell(
                definition=column,
                bound_field=bound_field,
            )

        if column.source_name is not None:
            display_value = resolve_value(
                django_form.instance,
                column.source_name,
            )

            return ResolvedFormCollectionCell(
                definition=column,
                display_value=display_value,
            )

        raise ValueError(
            f"La colonne {column.name!r} doit définir "
            "'field_name' ou 'source_name'."
        )
        
    def _resolve_empty_cell(
        self,
        django_form: BaseForm,
        column: FormCollectionColumnDefinition,
    ) -> ResolvedFormCollectionCell:
        """
        Résout une cellule de la ligne modèle.

        Seuls les champs Django sont résolus.
        Les colonnes d'affichage restent vides.
        """
        if column.field_name is not None:
            try:
                bound_field = django_form[column.field_name]
            except KeyError as error:
                raise ValueError(
                    f"La colonne {column.name!r} référence "
                    f"le champ Django {column.field_name!r}, "
                    "absent du formulaire."
                ) from error

            return ResolvedFormCollectionCell(
                definition=column,
                bound_field=bound_field,
            )

        if column.source_name is not None:
            return ResolvedFormCollectionCell(
                definition=column,
                display_value=None,
            )

        raise ValueError(
            f"La colonne {column.name!r} doit définir "
            "'field_name' ou 'source_name'."
        )