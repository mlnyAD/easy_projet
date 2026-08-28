

"""
Formulaire générique du framework Easy Projet.
"""

from dataclasses import dataclass, field

from django.forms.forms import BaseForm

from framework.context import EPContext
from framework.form.definition import FormDefinition
from framework.form.field import FieldDefinition
from framework.form.mode import FormMode
from framework.form.resolved_section import ResolvedSection
from framework.providers import Choice, ProviderRegistry
from framework.form.resolved_field import ResolvedField
from django.forms.formsets import BaseFormSet

from framework.form.resolved_collection import (
    ResolvedFormCollection,
)


@dataclass(frozen=True, slots=True)
class EPForm:
    """
    ViewModel générique d'un formulaire Easy Projet.

    Il associe une définition de formulaire à un formulaire Django
    afin d'exposer des sections directement exploitables par les
    templates.
    """

    definition: FormDefinition

    context: EPContext

    providers: ProviderRegistry

    mode: FormMode = FormMode.CREATE

    django_form: BaseForm = field(kw_only=True)
    
    formsets: dict[str, BaseFormSet] = field(
        default_factory=dict,
        kw_only=True,
    ) 

    @property
    def collections(
        self,
    ) -> list[ResolvedFormCollection]:
        """
        Retourne les collections dont les formsets
        Django ont été résolus.
        """
        resolved_collections: list[
            ResolvedFormCollection
        ] = []

        for collection_definition in (
            self.definition.collections
        ):
            collection_name = (
                collection_definition.name
            )

            try:
                formset = self.formsets[
                    collection_name
                ]
            except KeyError as error:
                raise ValueError(
                    f"La collection "
                    f"{collection_name!r} définie dans "
                    "EPForm ne possède aucun formset "
                    "Django correspondant."
                ) from error

            resolved_collections.append(
                ResolvedFormCollection(
                    definition=collection_definition,
                    formset=formset,
                )
            )

        return resolved_collections
    
    @property
    def title(self) -> str:
        """
        Retourne le titre du formulaire.
        """
        return self.definition.title

    @property
    def sections(self) -> list[ResolvedSection]:
        """
        Retourne les sections dont les champs ont été résolus
        en BoundField Django.
        """
        resolved_sections: list[ResolvedSection] = []

        for section in self.definition.sections:
            resolved_fields = [
                self._resolve_field(field_definition)
                for field_definition in section.fields
            ]

            resolved_sections.append(
                ResolvedSection(
                    title=section.title,
                    fields=resolved_fields,
                )
            )

        return resolved_sections

    def get_choices(
        self,
        field: FieldDefinition,
    ) -> list[Choice]:
        """
        Retourne les choix disponibles pour un champ.
        """
        if field.provider is None:
            return []

        provider = self.providers.get(
            field.provider.provider,
        )

        return provider.get_choices(
            field.provider,
            self.context,
        )

    @property
    def is_create(self) -> bool:
        return self.mode is FormMode.CREATE

    @property
    def is_edit(self) -> bool:
        return self.mode is FormMode.EDIT

    @property
    def is_readonly(self) -> bool:
        return self.mode is FormMode.READONLY

    def _resolve_field(
        self,
        field_definition: FieldDefinition,
    ) -> ResolvedField:
        """
        Associe un FieldDefinition à son BoundField Django.
        """
        field_name = field_definition.name

        try:
            bound_field = self.django_form[field_name]
        except KeyError as error:
            raise ValueError(
                f"Le champ {field_name!r} défini dans EPForm "
                "n'existe pas dans le formulaire Django."
            ) from error

        return ResolvedField(
            definition=field_definition,
            bound_field=bound_field,
        )