

import unittest

from django.forms import (
    CheckboxInput,
    FileInput,
    HiddenInput,
    PasswordInput,
    RadioSelect,
    Select,
    TextInput,
    Textarea,
)

from framework.integrations.django.widget_adapter import (
    WidgetAdapter,
)


class WidgetAdapterTests(unittest.TestCase):
    """
    Tests de l'adaptation des widgets Django au Design System EDF.

    Le WidgetAdapter attribue uniquement des classes sémantiques
    aux widgets Django.

    La présentation visuelle associée à ces classes est définie dans :

        static/src/edf/forms.css

    Les tests vérifient donc le contrat entre Django et EDF,
    et non les règles CSS ou les classes Tailwind utilisées pour
    construire visuellement les composants.
    """

    def setUp(self) -> None:
        self.adapter = WidgetAdapter()

    # ------------------------------------------------------------------
    # Contrat général
    # ------------------------------------------------------------------

    def test_adapt_returns_same_widget_instance(self) -> None:
        """
        L'adaptateur modifie le widget fourni sans le remplacer.
        """

        widget = TextInput()

        adapted_widget = self.adapter.adapt(widget)

        self.assertIs(
            adapted_widget,
            widget,
        )

    def test_adapt_rejects_non_widget_value(self) -> None:
        """
        Une valeur qui n'est pas un widget Django est refusée.
        """

        with self.assertRaises(TypeError):
            self.adapter.adapt(
                "not-a-widget"  # type: ignore[arg-type]
            )

    # ------------------------------------------------------------------
    # Classes sémantiques EDF
    # ------------------------------------------------------------------

    def test_text_input_receives_ep_input_class(
        self,
    ) -> None:
        """
        Un champ de saisie Django devient un composant ep-input.
        """

        widget = TextInput()

        self.adapter.adapt(widget)

        classes = widget.attrs["class"].split()

        self.assertIn(
            "ep-input",
            classes,
        )

    def test_textarea_receives_ep_textarea_class(
        self,
    ) -> None:
        """
        Une zone de texte Django devient un composant ep-textarea.
        """

        widget = Textarea()

        self.adapter.adapt(widget)

        classes = widget.attrs["class"].split()

        self.assertIn(
            "ep-textarea",
            classes,
        )

    def test_select_receives_ep_select_class(
        self,
    ) -> None:
        """
        Une liste Django devient un composant ep-select.
        """

        widget = Select()

        self.adapter.adapt(widget)

        classes = widget.attrs["class"].split()

        self.assertIn(
            "ep-select",
            classes,
        )

    def test_checkbox_receives_ep_checkbox_class(
        self,
    ) -> None:
        """
        Une case à cocher Django devient un composant ep-checkbox.
        """

        widget = CheckboxInput()

        self.adapter.adapt(widget)

        classes = widget.attrs["class"].split()

        self.assertIn(
            "ep-checkbox",
            classes,
        )

    def test_radio_receives_ep_radio_class(
        self,
    ) -> None:
        """
        Un groupe de boutons radio Django devient un composant ep-radio.
        """

        widget = RadioSelect()

        self.adapter.adapt(widget)

        classes = widget.attrs["class"].split()

        self.assertIn(
            "ep-radio",
            classes,
        )

    def test_file_input_receives_ep_file_class(
        self,
    ) -> None:
        """
        Un champ fichier Django devient un composant ep-file.
        """

        widget = FileInput()

        self.adapter.adapt(widget)

        classes = widget.attrs["class"].split()

        self.assertIn(
            "ep-file",
            classes,
        )

    # ------------------------------------------------------------------
    # Préservation des personnalisations métier
    # ------------------------------------------------------------------

    def test_existing_classes_are_preserved(self) -> None:
        """
        Les classes ajoutées par un formulaire métier sont conservées.
        """

        widget = TextInput(
            attrs={
                "class": (
                    "company-name-field custom-class"
                ),
            }
        )

        self.adapter.adapt(widget)

        classes = widget.attrs["class"].split()

        self.assertIn(
            "company-name-field",
            classes,
        )
        self.assertIn(
            "custom-class",
            classes,
        )
        self.assertIn(
            "ep-input",
            classes,
        )

    def test_classes_are_not_duplicated(self) -> None:
        """
        Plusieurs adaptations successives ne dupliquent pas les classes.
        """

        widget = TextInput(
            attrs={
                "class": "custom-class",
            }
        )

        self.adapter.adapt(widget)
        self.adapter.adapt(widget)

        classes = widget.attrs["class"].split()

        self.assertEqual(
            classes.count("custom-class"),
            1,
        )
        self.assertEqual(
            classes.count("ep-input"),
            1,
        )

    # ------------------------------------------------------------------
    # Textarea
    # ------------------------------------------------------------------

    def test_textarea_receives_rows_when_not_defined(
        self,
    ) -> None:
        """
        EDF utilise quatre lignes par défaut pour les zones de texte.
        """

        widget = Textarea()

        self.adapter.adapt(widget)

        self.assertEqual(
            widget.attrs["rows"],
            4,
        )

    def test_textarea_preserves_existing_rows(
        self,
    ) -> None:
        """
        Une hauteur explicitement définie par le métier est conservée.
        """

        widget = Textarea(
            attrs={
                "rows": 8,
            }
        )

        self.adapter.adapt(widget)

        self.assertEqual(
            widget.attrs["rows"],
            8,
        )

    # ------------------------------------------------------------------
    # Mot de passe
    # ------------------------------------------------------------------

    def test_password_input_receives_default_autocomplete(
        self,
    ) -> None:
        """
        Le comportement standard d'autocomplétion est ajouté
        aux champs mot de passe.
        """

        widget = PasswordInput()

        self.adapter.adapt(widget)

        self.assertEqual(
            widget.attrs["autocomplete"],
            "current-password",
        )

    def test_password_input_preserves_existing_autocomplete(
        self,
    ) -> None:
        """
        Une règle d'autocomplétion métier existante est prioritaire.
        """

        widget = PasswordInput(
            attrs={
                "autocomplete": "new-password",
            }
        )

        self.adapter.adapt(widget)

        self.assertEqual(
            widget.attrs["autocomplete"],
            "new-password",
        )

    # ------------------------------------------------------------------
    # Validation et accessibilité
    # ------------------------------------------------------------------

    def test_invalid_widget_receives_accessibility_attribute(
        self,
    ) -> None:
        """
        Un champ invalide expose son état aux technologies d'assistance
        et reçoit l'état visuel EDF correspondant.
        """

        widget = TextInput()

        self.adapter.adapt(
            widget,
            has_errors=True,
        )

        self.assertEqual(
            widget.attrs["aria-invalid"],
            "true",
        )

        classes = widget.attrs["class"].split()

        self.assertIn(
            "ep-input",
            classes,
        )
        self.assertIn(
            "ep-field-invalid",
            classes,
        )

    def test_widget_without_errors_has_no_aria_invalid(
        self,
    ) -> None:
        """
        Un champ valide ne reçoit pas aria-invalid.
        """

        widget = TextInput()

        self.adapter.adapt(
            widget,
            has_errors=False,
        )

        self.assertNotIn(
            "aria-invalid",
            widget.attrs,
        )

    def test_described_by_is_added(self) -> None:
        """
        aria-describedby est ajouté lorsqu'une description est fournie.
        """

        widget = TextInput()

        self.adapter.adapt(
            widget,
            described_by="id_name_help",
        )

        self.assertEqual(
            widget.attrs["aria-describedby"],
            "id_name_help",
        )

    def test_existing_described_by_is_preserved_and_completed(
        self,
    ) -> None:
        """
        Une description existante est conservée lors de l'adaptation.
        """

        widget = TextInput(
            attrs={
                "aria-describedby": (
                    "custom-description"
                ),
            }
        )

        self.adapter.adapt(
            widget,
            described_by="id_name_help",
        )

        described_by = widget.attrs[
            "aria-describedby"
        ].split()

        self.assertEqual(
            described_by,
            [
                "custom-description",
                "id_name_help",
            ],
        )

    # ------------------------------------------------------------------
    # Champs invisibles
    # ------------------------------------------------------------------

    def test_hidden_input_is_not_modified(
        self,
    ) -> None:
        """
        Un champ invisible ne reçoit aucune adaptation visuelle
        ou attribut d'accessibilité supplémentaire.
        """

        widget = HiddenInput(
            attrs={
                "class": "existing-hidden-class",
            }
        )

        self.adapter.adapt(
            widget,
            has_errors=True,
            described_by="hidden-help",
        )

        self.assertEqual(
            widget.attrs,
            {
                "class": "existing-hidden-class",
            },
        )


if __name__ == "__main__":
    unittest.main()