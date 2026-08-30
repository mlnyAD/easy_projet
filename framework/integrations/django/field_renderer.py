

"""
Rendu des champs du framework Easy Projet.
"""

from django.forms.boundfield import BoundField
from django.forms.widgets import (
    CheckboxInput,
    Select,
)

from framework.form import (
    FieldDefinition,
    FieldKind,
)
from framework.form.resolved_field import ResolvedField


class FieldRenderer:
    """
    Résout le template associé à un champ.

    Les widgets Django ordinaires utilisent leur nature
    de widget pour déterminer le template.

    Les composants explicitement spécialisés par le
    framework peuvent imposer leur propre template.
    """

    DEFAULT_TEMPLATE = "edf/form/field.html"

    TEMPLATE_BY_KIND = {
        FieldKind.TEXT: "edf/form/fields/text.html",
        FieldKind.FILE_UPLOAD: (
            "edf/form/fields/file_upload.html"
        ),
    }

    WIDGET_TEMPLATE = {
        Select: "edf/form/fields/select.html",
        CheckboxInput: "edf/form/fields/checkbox.html",
    }

    def get_template_name(self, field) -> str:
        """
        Retourne le template correspondant au champ fourni.
        """

        if isinstance(field, ResolvedField):
            return self._get_resolved_field_template(
                field
            )

        if isinstance(field, FieldDefinition):
            return self.TEMPLATE_BY_KIND.get(
                field.kind,
                self.DEFAULT_TEMPLATE,
            )

        if isinstance(field, BoundField):
            return self._get_bound_field_template(
                field
            )

        return self.DEFAULT_TEMPLATE

    def _get_resolved_field_template(
        self,
        field: ResolvedField,
    ) -> str:
        """
        Résout le template d'un champ Easy Projet lié
        à un BoundField Django.

        FILE_UPLOAD est une sémantique explicite du framework
        et prend donc priorité.

        Pour les autres champs, le widget Django reste
        la référence afin de préserver les comportements
        existants, notamment Select et CheckboxInput.
        """

        if field.kind == FieldKind.FILE_UPLOAD:
            return self.TEMPLATE_BY_KIND[
                FieldKind.FILE_UPLOAD
            ]

        return self._get_bound_field_template(
            field.bound_field
        )

    def _get_bound_field_template(
        self,
        field: BoundField,
    ) -> str:
        """
        Résout le template à partir du widget Django.
        """

        widget = field.field.widget

        for widget_type, template_name in (
            self.WIDGET_TEMPLATE.items()
        ):
            if isinstance(
                widget,
                widget_type,
            ):
                return template_name

        return self.DEFAULT_TEMPLATE