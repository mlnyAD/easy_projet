

from django import forms
from django.template import Context, Template
from django.test import SimpleTestCase

from common.forms.widgets import TelInput


class TestForm(forms.Form):
    name = forms.CharField(
        label="Nom",
        help_text="Nom utilisé dans l'application.",
        widget=forms.TextInput(
            attrs={
                "placeholder": "Nom de la société",
                "data-trim": True,
            }
        ),
    )

    email = forms.EmailField(
        label="Adresse électronique",
        widget=forms.EmailInput(),
    )

    phone = forms.CharField(
        label="Téléphone",
        widget=TelInput(),
    )

    is_active = forms.BooleanField(
        label="Société active",
        required=False,
        widget=forms.CheckboxInput(),
    )
    
    notes = forms.CharField(
    label="Observations",
    required=False,
    widget=forms.Textarea(
        attrs={
            "rows": 4,
            "placeholder": "Observations complémentaires",
			}
		),
	)

    country = forms.ChoiceField(
		label="Pays",
		choices=(
			("", "Sélectionner un pays"),
			("FR", "France"),
			("BE", "Belgique"),
		),
		widget=forms.Select(),
	)


class EPFormFieldTagTests(SimpleTestCase):
    def render_field(self, field):
        template = Template(
            "{% load ep_forms %}"
            "{% ep_form_field field %}"
        )

        return template.render(
            Context(
                {
                    "field": field,
                }
            )
        )

    def test_text_field_is_rendered(self):
        form = TestForm()

        html = self.render_field(form["name"])

        self.assertIn('type="text"', html)
        self.assertIn('name="name"', html)
        self.assertIn("Nom", html)
        self.assertIn(
            "Nom utilisé dans l&#x27;application.",
            html,
        )

    def test_existing_widget_attributes_are_preserved(self):
        form = TestForm()

        html = self.render_field(form["name"])

        self.assertIn(
			'placeholder="Nom de la société"',
			html,
		)
        self.assertIn(
			"data-trim",
			html,
		)

    def test_email_field_receives_email_attributes(self):
        form = TestForm()

        html = self.render_field(form["email"])

        self.assertIn('type="email"', html)
        self.assertIn('inputmode="email"', html)
        self.assertIn('autocomplete="email"', html)

    def test_phone_field_receives_phone_attributes(self):
        form = TestForm()

        html = self.render_field(form["phone"])

        self.assertIn('type="tel"', html)
        self.assertIn('inputmode="tel"', html)
        self.assertIn('autocomplete="tel"', html)
        self.assertIn("data-phone", html)

    def test_checkbox_is_rendered(self):
        form = TestForm()

        html = self.render_field(form["is_active"])

        self.assertIn('type="checkbox"', html)
        self.assertIn("Société active", html)

    def test_required_field_displays_required_indicator(self):
        form = TestForm()

        html = self.render_field(form["name"])

        self.assertIn("Champ obligatoire", html)

    def test_optional_checkbox_has_no_required_indicator(self):
        form = TestForm()

        html = self.render_field(form["is_active"])

        self.assertNotIn("Champ obligatoire", html)

    def test_field_errors_are_rendered(self):
        form = TestForm(
            data={
                "name": "",
                "email": "contact@example.com",
                "phone": "",
                "is_active": False,
            }
        )

        self.assertFalse(form.is_valid())

        html = self.render_field(form["name"])

        self.assertIn('role="alert"', html)
        self.assertIn('aria-invalid="true"', html)
        self.assertIn(
            f'id="{form["name"].auto_id}_errors"',
            html,
        )

    def test_help_text_is_linked_with_aria_describedby(self):
        form = TestForm()

        html = self.render_field(form["name"])

        self.assertIn(
            f'aria-describedby="{form["name"].auto_id}_help"',
            html,
        )
        
    def test_textarea_is_rendered(self):
        form = TestForm()

        html = self.render_field(form["notes"])

        self.assertIn("<textarea", html)
        self.assertIn('name="notes"', html)
        self.assertIn('rows="4"', html)
        self.assertIn(
			'placeholder="Observations complémentaires"',
			html,
		)
        self.assertIn("Observations", html)


    def test_select_is_rendered(self):
        form = TestForm()

        html = self.render_field(form["country"])

        self.assertIn("<select", html)
        self.assertIn('name="country"', html)
        self.assertIn(
			'<option value="FR">France</option>',
			html,
		)
        self.assertIn(
			'<option value="BE">Belgique</option>',
			html,
		)
        self.assertIn("Pays", html)