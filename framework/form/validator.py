

from framework.form.definition import FormDefinition
from framework.form.field import FieldDefinition
from framework.form.kinds import FieldKind
from framework.form.section import SectionDefinition
from framework.types.field_width import FieldWidth
from framework.providers import ChoiceProviderDefinition


class FormValidationError(ValueError):
    """
    Erreur levée lorsqu'une définition de formulaire est invalide.
    """


class FormValidator:
    """
    Valide la cohérence d'une définition de formulaire.
    """

    def validate(self, definition: FormDefinition) -> None:
        if not isinstance(definition, FormDefinition):
            raise FormValidationError(
                "La définition doit être une instance de FormDefinition."
            )

        self._validate_name(definition.name)
        self._validate_title(definition.title)
        self._validate_sections(definition.sections)

    def _validate_name(self, name: str) -> None:
        if not isinstance(name, str):
            raise FormValidationError(
                "Le nom du formulaire doit être une chaîne de caractères."
            )

        if not name.strip():
            raise FormValidationError(
                "Le nom du formulaire est obligatoire."
            )

    def _validate_title(self, title: str) -> None:
        if not isinstance(title, str):
            raise FormValidationError(
                "Le titre du formulaire doit être une chaîne de caractères."
            )

        if not title.strip():
            raise FormValidationError(
                "Le titre du formulaire est obligatoire."
            )

    def _validate_sections(
        self,
        sections: list[SectionDefinition],
    ) -> None:
        if not isinstance(sections, list):
            raise FormValidationError(
                "Les sections du formulaire doivent être fournies sous forme de liste."
            )

        if not sections:
            raise FormValidationError(
                "Le formulaire doit contenir au moins une section."
            )

        field_names: set[str] = set()

        for section in sections:
            self._validate_section(section)

            for field in section.fields:
                if field.name in field_names:
                    raise FormValidationError(
                        f"Le champ '{field.name}' est défini plusieurs fois."
                    )

                field_names.add(field.name)

    def _validate_section(
        self,
        section: SectionDefinition,
    ) -> None:
        if not isinstance(section, SectionDefinition):
            raise FormValidationError(
                "Chaque section doit être une instance de SectionDefinition."
            )

        if not isinstance(section.title, str):
            raise FormValidationError(
                "Le titre d'une section doit être une chaîne de caractères."
            )

        if not section.title.strip():
            raise FormValidationError(
                "Le titre d'une section est obligatoire."
            )

        if not isinstance(section.fields, list):
            raise FormValidationError(
                "Les champs d'une section doivent être fournis sous forme de liste."
            )

        if not section.fields:
            raise FormValidationError(
                f"La section '{section.title}' doit contenir au moins un champ."
            )

        for field in section.fields:
            self._validate_field(field)

    def _validate_field(
        self,
        field: FieldDefinition,
    ) -> None:
        if not isinstance(field, FieldDefinition):
            raise FormValidationError(
                "Chaque champ doit être une instance de FieldDefinition."
            )

        if not isinstance(field.name, str):
            raise FormValidationError(
                "Le nom d'un champ doit être une chaîne de caractères."
            )

        if not field.name.strip():
            raise FormValidationError(
                "Le nom d'un champ est obligatoire."
            )

        if field.label is not None and not isinstance(field.label, str):
            raise FormValidationError(
                f"Le libellé du champ '{field.name}' doit être une chaîne de caractères."
            )

        if not isinstance(field.kind, FieldKind):
            raise FormValidationError(
                f"Le type du champ '{field.name}' est invalide."
            )

        if field.help_text is not None and not isinstance(
            field.help_text,
            str,
        ):
            raise FormValidationError(
                f"L'aide du champ '{field.name}' doit être une chaîne de caractères."
            )

        if field.readonly and field.disabled:
            raise FormValidationError(
                f"Le champ '{field.name}' ne peut pas être à la fois readonly et disabled."
            )
            
        if (
            field.provider is not None
            and not isinstance(field.provider, ChoiceProviderDefinition)
        ):
            raise FormValidationError(
                f"Le provider du champ '{field.name}' est invalide."
        )

        if not isinstance(field.width, FieldWidth):
            raise FormValidationError(
                f"La largeur du champ '{field.name}' est invalide."
            )

        if field.placeholder is not None and not isinstance(field.placeholder, str):
            raise FormValidationError(
                f"Le placeholder du champ '{field.name}' est invalide."
            )

        if field.icon is not None and not isinstance(field.icon, str):
            raise FormValidationError(
                f"L'icône du champ '{field.name}' est invalide."
            )

        if not isinstance(field.visible, bool):
            raise FormValidationError(
                f"La propriété visible du champ '{field.name}' est invalide."
            )

        if not isinstance(field.autofocus, bool):
            raise FormValidationError(
                f"La propriété autofocus du champ '{field.name}' est invalide."
            )

        if (
            field.tab_index is not None
            and not isinstance(field.tab_index, int)
        ):
            raise FormValidationError(
                f"Le tab_index du champ '{field.name}' est invalide."
            )