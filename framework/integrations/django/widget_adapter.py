

from __future__ import annotations

from collections.abc import Iterable

from django.forms import (
    CheckboxInput,
    FileInput,
    HiddenInput,
    PasswordInput,
    RadioSelect,
    Select,
    SelectMultiple,
    Textarea,
)
from django.forms.widgets import (
    Input,
    Widget,
)


# ---------------------------------------------------------------------------
# Classes sémantiques du Design System Easy Projet.
#
# Le WidgetAdapter identifie la nature UI du widget Django.
# La présentation effective de ces composants est définie dans :
#
#     static/src/edf/forms.css
#
# Le framework Python ne doit donc pas contenir de règles de présentation
# Tailwind ou CSS.
# ---------------------------------------------------------------------------

_INPUT_CLASSES = (
    "ep-input",
)

_TEXTAREA_CLASSES = (
    "ep-textarea",
)

_SELECT_CLASSES = (
    "ep-select",
)

_CHECKBOX_CLASSES = (
    "ep-checkbox",
)

_RADIO_CLASSES = (
    "ep-radio",
)

_FILE_CLASSES = (
    "ep-file",
)

_INVALID_CLASSES = (
    "ep-field-invalid",
)


class WidgetAdapter:
    """
    Adapte les widgets Django au Design System Easy Projet.

    L'adaptateur associe une classe sémantique EDF au widget Django
    correspondant.

    Il complète les attributs existants sans supprimer les
    personnalisations éventuellement définies par le formulaire métier.

    La présentation des composants est entièrement déléguée aux fichiers
    CSS EDF.
    """

    def adapt(
        self,
        widget: Widget,
        *,
        has_errors: bool = False,
        described_by: str | None = None,
    ) -> Widget:
        """
        Adapte un widget Django et retourne la même instance.

        Les widgets invisibles ne nécessitent aucune adaptation visuelle.
        """

        if not isinstance(widget, Widget):
            raise TypeError(
                "widget doit être une instance de django.forms.Widget."
            )

        if isinstance(widget, HiddenInput):
            return widget

        if isinstance(widget, CheckboxInput):
            self._adapt_checkbox(widget)

        elif isinstance(widget, RadioSelect):
            self._adapt_radio(widget)

        elif isinstance(widget, FileInput):
            self._adapt_file(widget)

        elif isinstance(widget, Textarea):
            self._adapt_textarea(widget)

        elif isinstance(widget, (Select, SelectMultiple)):
            self._adapt_select(widget)

        elif isinstance(widget, Input):
            self._adapt_input(widget)

        self._adapt_accessibility(
            widget,
            has_errors=has_errors,
            described_by=described_by,
        )

        return widget

    def _adapt_input(
        self,
        widget: Input,
    ) -> None:
        """
        Adapte un champ de saisie standard.
        """

        self._merge_classes(
            widget,
            _INPUT_CLASSES,
        )

        if isinstance(widget, PasswordInput):
            self._set_default_attr(
                widget,
                "autocomplete",
                "current-password",
            )

    def _adapt_textarea(
        self,
        widget: Textarea,
    ) -> None:
        """
        Adapte une zone de texte multiligne.

        Django utilise 10 lignes par défaut pour Textarea.
        EDF ramène cette valeur à 4 afin de conserver des formulaires
        compacts. Une valeur explicitement définie par le formulaire
        métier reste inchangée.
        """

        self._merge_classes(
            widget,
            _TEXTAREA_CLASSES,
        )

        current_rows = widget.attrs.get("rows")

        if current_rows in (None, 10, "10"):
            widget.attrs["rows"] = 4

    def _adapt_select(
        self,
        widget: Select | SelectMultiple,
    ) -> None:
        """
        Adapte une liste de sélection.
        """

        self._merge_classes(
            widget,
            _SELECT_CLASSES,
        )

    def _adapt_checkbox(
        self,
        widget: CheckboxInput,
    ) -> None:
        """
        Adapte une case à cocher.
        """

        self._merge_classes(
            widget,
            _CHECKBOX_CLASSES,
        )

    def _adapt_radio(
        self,
        widget: RadioSelect,
    ) -> None:
        """
        Adapte un groupe de boutons radio.
        """

        self._merge_classes(
            widget,
            _RADIO_CLASSES,
        )

    def _adapt_file(
        self,
        widget: FileInput,
    ) -> None:
        """
        Adapte un champ de sélection de fichier.
        """

        self._merge_classes(
            widget,
            _FILE_CLASSES,
        )

    def _adapt_accessibility(
        self,
        widget: Widget,
        *,
        has_errors: bool,
        described_by: str | None,
    ) -> None:
        """
        Complète les attributs d'accessibilité du widget.

        En cas d'erreur :
        - aria-invalid indique l'état invalide ;
        - ep-field-invalid fournit l'état visuel associé.

        aria-describedby relie le widget aux textes d'aide et aux
        messages d'erreur lorsqu'ils existent.
        """

        if has_errors:
            widget.attrs["aria-invalid"] = "true"

            self._merge_classes(
                widget,
                _INVALID_CLASSES,
            )

        if described_by:
            self._merge_attribute_values(
                widget,
                attribute="aria-describedby",
                values=(described_by,),
            )

    @staticmethod
    def _set_default_attr(
        widget: Widget,
        name: str,
        value: object,
    ) -> None:
        """
        Définit un attribut uniquement s'il n'existe pas déjà.
        """

        widget.attrs.setdefault(
            name,
            value,
        )

    @classmethod
    def _merge_classes(
        cls,
        widget: Widget,
        classes: Iterable[str],
    ) -> None:
        """
        Ajoute des classes CSS sans supprimer les classes existantes.
        """

        cls._merge_attribute_values(
            widget,
            attribute="class",
            values=classes,
        )

    @staticmethod
    def _merge_attribute_values(
        widget: Widget,
        *,
        attribute: str,
        values: Iterable[str],
    ) -> None:
        """
        Fusionne les valeurs d'un attribut HTML sans doublon.

        Cette méthode permet notamment de préserver les attributs ajoutés
        par les formulaires métier avant le passage dans l'adaptateur EDF.
        """

        existing_values = str(
            widget.attrs.get(
                attribute,
                "",
            )
        ).split()

        merged_values = list(existing_values)

        for value in values:
            for item in str(value).split():
                if item and item not in merged_values:
                    merged_values.append(item)

        if merged_values:
            widget.attrs[attribute] = " ".join(
                merged_values
            )