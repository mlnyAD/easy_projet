

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


_INPUT_CLASSES = (
    "edf-form-input",
    "block",
    "w-full",
    "rounded-lg",
    "border",
    "border-gray-300",
    "bg-[#F4FBFA]",
    "px-3",
    "py-2",
    "text-sm",
    "text-gray-900",
    "shadow-sm",
    "transition",
    "placeholder:text-gray-400",
    "focus:border-blue-500",
    "focus:outline-none",
    "focus:ring-2",
    "focus:ring-blue-500/20",
    "disabled:cursor-not-allowed",
    "disabled:bg-gray-100",
    "disabled:text-gray-700",
    "dark:border-neutral-700",
    "dark:bg-neutral-800/70",
    "dark:text-neutral-200",
    "dark:placeholder:text-neutral-500",
)

_TEXTAREA_CLASSES = (
    *_INPUT_CLASSES,
    "min-h-24",
    "resize-y",
)

_SELECT_CLASSES = (
    *_INPUT_CLASSES,
    "pe-9",
)

_CHECKBOX_CLASSES = (
    "size-4",
    "shrink-0",
    "rounded",
    "border-gray-300",
    "text-axcio-light",
    "accent-axcio-light",
    "focus:ring-axcio-light",
    "disabled:pointer-events-none",
    "disabled:opacity-50",
    "dark:border-neutral-700",
    "dark:bg-neutral-900",
)

_RADIO_CLASSES = (
    "size-4",
    "shrink-0",
    "border-gray-300",
    "text-blue-600",
    "focus:ring-blue-500",
    "disabled:pointer-events-none",
    "disabled:opacity-50",
    "dark:border-neutral-700",
    "dark:bg-neutral-900",
)

_FILE_CLASSES = (
    "block",
    "w-full",
    "rounded-lg",
    "border",
    "border-gray-300",
    "bg-[#F4FBFA]",
    "text-sm",
    "text-gray-900",
    "shadow-sm",
    "file:me-4",
    "file:border-0",
    "file:bg-gray-100",
    "file:px-4",
    "file:py-2",
    "file:text-sm",
    "file:font-medium",
    "hover:file:bg-gray-200",
    "focus:border-blue-500",
    "focus:outline-none",
    "focus:ring-2",
    "focus:ring-blue-500/20",
    "disabled:pointer-events-none",
    "disabled:opacity-50",
    "dark:border-neutral-700",
    "dark:bg-neutral-800/70",
    "dark:text-neutral-200",
    "dark:file:bg-neutral-800",
    "dark:file:text-neutral-200",
)

_INVALID_CLASSES = (
    "border-red-500",
    "focus:border-red-500",
    "focus:ring-red-500/20",
)


class WidgetAdapter:
    """Adapte les widgets Django au design system Easy Projet.

    L'adaptateur complète les attributs existants sans supprimer les
    personnalisations éventuellement définies par le formulaire métier.
    """

    def adapt(
        self,
        widget: Widget,
        *,
        has_errors: bool = False,
        described_by: str | None = None,
    ) -> Widget:
        """Adapte un widget et retourne la même instance.

        Args:
            widget:
                Widget Django à adapter.
            has_errors:
                Indique si le champ associé comporte des erreurs.
            described_by:
                Identifiant HTML de l'élément décrivant le champ, par exemple
                une aide ou un message d'erreur.
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

    def _adapt_input(self, widget: Input) -> None:
        self._merge_classes(widget, _INPUT_CLASSES)

        if isinstance(widget, PasswordInput):
            self._set_default_attr(widget, "autocomplete", "current-password")

    def _adapt_textarea(self, widget: Textarea) -> None:
        self._merge_classes(
            widget,
            _TEXTAREA_CLASSES,
        )

        current_rows = widget.attrs.get("rows")

        if current_rows in (None, 10, "10"):
            widget.attrs["rows"] = 4
        
    def _adapt_select(self, widget: Select | SelectMultiple) -> None:
        self._merge_classes(widget, _SELECT_CLASSES)

    def _adapt_checkbox(self, widget: CheckboxInput) -> None:
        self._merge_classes(widget, _CHECKBOX_CLASSES)

    def _adapt_radio(self, widget: RadioSelect) -> None:
        self._merge_classes(widget, _RADIO_CLASSES)

    def _adapt_file(self, widget: FileInput) -> None:
        self._merge_classes(widget, _FILE_CLASSES)

    def _adapt_accessibility(
        self,
        widget: Widget,
        *,
        has_errors: bool,
        described_by: str | None,
    ) -> None:
        if has_errors:
            widget.attrs["aria-invalid"] = "true"
            self._merge_classes(widget, _INVALID_CLASSES)

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
        widget.attrs.setdefault(name, value)

    @classmethod
    def _merge_classes(
        cls,
        widget: Widget,
        classes: Iterable[str],
    ) -> None:
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
        existing_values = str(widget.attrs.get(attribute, "")).split()

        merged_values = list(existing_values)

        for value in values:
            for item in str(value).split():
                if item and item not in merged_values:
                    merged_values.append(item)

        if merged_values:
            widget.attrs[attribute] = " ".join(merged_values)