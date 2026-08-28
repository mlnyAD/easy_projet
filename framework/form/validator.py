
            
from framework.form.collection import (
    FormCollectionColumnDefinition,
    FormCollectionDefinition,
)
from framework.form.definition import FormDefinition
from framework.form.field import FieldDefinition
from framework.form.kinds import FieldKind
from framework.form.section import SectionDefinition
from framework.providers import ChoiceProviderDefinition
from framework.types.field_width import FieldWidth


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
        self._validate_collections(definition.collections)

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
                "Les sections du formulaire doivent être fournies "
                "sous forme de liste."
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
                "Les champs d'une section doivent être fournis "
                "sous forme de liste."
            )

        if not section.fields:
            raise FormValidationError(
                f"La section '{section.title}' doit contenir "
                "au moins un champ."
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

        if (
            field.label is not None
            and not isinstance(field.label, str)
        ):
            raise FormValidationError(
                f"Le libellé du champ '{field.name}' doit être "
                "une chaîne de caractères."
            )

        if not isinstance(field.kind, FieldKind):
            raise FormValidationError(
                f"Le type du champ '{field.name}' est invalide."
            )

        if (
            field.help_text is not None
            and not isinstance(field.help_text, str)
        ):
            raise FormValidationError(
                f"L'aide du champ '{field.name}' doit être "
                "une chaîne de caractères."
            )

        if field.readonly and field.disabled:
            raise FormValidationError(
                f"Le champ '{field.name}' ne peut pas être "
                "à la fois readonly et disabled."
            )

        if (
            field.provider is not None
            and not isinstance(
                field.provider,
                ChoiceProviderDefinition,
            )
        ):
            raise FormValidationError(
                f"Le provider du champ '{field.name}' est invalide."
            )

        if not isinstance(field.width, FieldWidth):
            raise FormValidationError(
                f"La largeur du champ '{field.name}' est invalide."
            )

        if (
            field.placeholder is not None
            and not isinstance(field.placeholder, str)
        ):
            raise FormValidationError(
                f"Le placeholder du champ '{field.name}' est invalide."
            )

        if (
            field.icon is not None
            and not isinstance(field.icon, str)
        ):
            raise FormValidationError(
                f"L'icône du champ '{field.name}' est invalide."
            )

        if not isinstance(field.visible, bool):
            raise FormValidationError(
                f"La propriété visible du champ '{field.name}' "
                "est invalide."
            )

        if not isinstance(field.autofocus, bool):
            raise FormValidationError(
                f"La propriété autofocus du champ '{field.name}' "
                "est invalide."
            )

        if (
            field.tab_index is not None
            and not isinstance(field.tab_index, int)
        ):
            raise FormValidationError(
                f"Le tab_index du champ '{field.name}' est invalide."
            )

    def _validate_collections(
        self,
        collections: list[FormCollectionDefinition],
    ) -> None:
        if not isinstance(collections, list):
            raise FormValidationError(
                "Les collections du formulaire doivent être fournies "
                "sous forme de liste."
            )

        collection_names: set[str] = set()

        for collection in collections:
            self._validate_collection(collection)

            if collection.name in collection_names:
                raise FormValidationError(
                    f"La collection '{collection.name}' "
                    "est définie plusieurs fois."
                )

            collection_names.add(collection.name)

    def _validate_collection(
        self,
        collection: FormCollectionDefinition,
    ) -> None:
        if not isinstance(
            collection,
            FormCollectionDefinition,
        ):
            raise FormValidationError(
                "Chaque collection doit être une instance "
                "de FormCollectionDefinition."
            )

        if not isinstance(collection.name, str):
            raise FormValidationError(
                "Le nom d'une collection doit être "
                "une chaîne de caractères."
            )

        if not collection.name.strip():
            raise FormValidationError(
                "Le nom d'une collection est obligatoire."
            )

        if not isinstance(collection.title, str):
            raise FormValidationError(
                f"Le titre de la collection '{collection.name}' "
                "doit être une chaîne de caractères."
            )

        if not collection.title.strip():
            raise FormValidationError(
                f"Le titre de la collection '{collection.name}' "
                "est obligatoire."
            )

        if (
            collection.description is not None
            and not isinstance(collection.description, str)
        ):
            raise FormValidationError(
                f"La description de la collection "
                f"'{collection.name}' est invalide."
            )

        if not isinstance(collection.columns, tuple):
            raise FormValidationError(
                f"Les colonnes de la collection "
                f"'{collection.name}' doivent être fournies "
                "sous forme de tuple."
            )

        if not collection.columns:
            raise FormValidationError(
                f"La collection '{collection.name}' doit contenir "
                "au moins une colonne."
            )

        column_names: set[str] = set()

        for column in collection.columns:
            self._validate_collection_column(
                collection,
                column,
            )

            if column.name in column_names:
                raise FormValidationError(
                    f"La colonne '{column.name}' est définie "
                    f"plusieurs fois dans la collection "
                    f"'{collection.name}'."
                )

            column_names.add(column.name)

        if not isinstance(collection.allow_add, bool):
            raise FormValidationError(
                f"La propriété allow_add de la collection "
                f"'{collection.name}' est invalide."
            )

        if not isinstance(collection.allow_delete, bool):
            raise FormValidationError(
                f"La propriété allow_delete de la collection "
                f"'{collection.name}' est invalide."
            )

        if not isinstance(collection.add_label, str):
            raise FormValidationError(
                f"Le libellé d'ajout de la collection "
                f"'{collection.name}' est invalide."
            )

        if not collection.add_label.strip():
            raise FormValidationError(
                f"Le libellé d'ajout de la collection "
                f"'{collection.name}' est obligatoire."
            )

        if not isinstance(collection.delete_label, str):
            raise FormValidationError(
                f"Le libellé de suppression de la collection "
                f"'{collection.name}' est invalide."
            )

        if not collection.delete_label.strip():
            raise FormValidationError(
                f"Le libellé de suppression de la collection "
                f"'{collection.name}' est obligatoire."
            )

        if not isinstance(collection.visible, bool):
            raise FormValidationError(
                f"La propriété visible de la collection "
                f"'{collection.name}' est invalide."
            )

    def _validate_collection_column(
        self,
        collection: FormCollectionDefinition,
        column: FormCollectionColumnDefinition,
    ) -> None:
        if not isinstance(
            column,
            FormCollectionColumnDefinition,
        ):
            raise FormValidationError(
                f"Chaque colonne de la collection "
                f"'{collection.name}' doit être une instance "
                "de FormCollectionColumnDefinition."
            )

        if not isinstance(column.name, str):
            raise FormValidationError(
                f"Le nom d'une colonne de la collection "
                f"'{collection.name}' doit être une chaîne "
                "de caractères."
            )

        if not column.name.strip():
            raise FormValidationError(
                f"Le nom d'une colonne de la collection "
                f"'{collection.name}' est obligatoire."
            )

        if (
            column.label is not None
            and not isinstance(column.label, str)
        ):
            raise FormValidationError(
                f"Le libellé de la colonne '{column.name}' "
                f"de la collection '{collection.name}' est invalide."
            )

        if (
            column.field_name is not None
            and not isinstance(column.field_name, str)
        ):
            raise FormValidationError(
                f"Le field_name de la colonne '{column.name}' "
                f"de la collection '{collection.name}' est invalide."
            )

        if (
            column.source_name is not None
            and not isinstance(column.source_name, str)
        ):
            raise FormValidationError(
                f"Le source_name de la colonne '{column.name}' "
                f"de la collection '{collection.name}' est invalide."
            )

        if (
            column.field_name is not None
            and not column.field_name.strip()
        ):
            raise FormValidationError(
                f"Le field_name de la colonne '{column.name}' "
                "ne peut pas être vide."
            )

        if (
            column.source_name is not None
            and not column.source_name.strip()
        ):
            raise FormValidationError(
                f"Le source_name de la colonne '{column.name}' "
                "ne peut pas être vide."
            )

        if (
            column.field_name is None
            and column.source_name is None
        ):
            raise FormValidationError(
                f"La colonne '{column.name}' de la collection "
                f"'{collection.name}' doit définir field_name "
                "ou source_name."
            )

        if (
            column.field_name is not None
            and column.source_name is not None
        ):
            raise FormValidationError(
                f"La colonne '{column.name}' de la collection "
                f"'{collection.name}' ne peut pas définir "
                "simultanément field_name et source_name."
            )

        if not isinstance(column.visible, bool):
            raise FormValidationError(
                f"La propriété visible de la colonne "
                f"'{column.name}' est invalide."
            )

        if column.align not in {
            "left",
            "center",
            "right",
        }:
            raise FormValidationError(
                f"L'alignement de la colonne '{column.name}' "
                "doit être 'left', 'center' ou 'right'."
            )

        if not isinstance(column.width, str):
            raise FormValidationError(
                f"La largeur de la colonne '{column.name}' "
                "est invalide."
            )

        if not column.width.strip():
            raise FormValidationError(
                f"La largeur de la colonne '{column.name}' "
                "ne peut pas être vide."
            )

        if not isinstance(column.readonly, bool):
            raise FormValidationError(
                f"La propriété readonly de la colonne "
                f"'{column.name}' est invalide."
            )