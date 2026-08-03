

import os
import unittest
from django import forms

os.environ.setdefault(
    "DJANGO_SETTINGS_MODULE",
    "config.settings",
)

import django

django.setup()

from django.template import Context, Template, engines

from framework.form import FieldDefinition, FieldKind
from framework.integrations.django.templatetags.ep_form_fields import register


engines["django"].engine.template_libraries["ep_form_fields"] = register

class DjangoCompanyForm(forms.Form):
    company = forms.CharField(
        label="Société",
        max_length=150,
        help_text="Raison sociale de l'entreprise.",
    )
    
class EPFormFieldsTemplateTagTests(unittest.TestCase):

    def test_render_ep_field_uses_text_template(self) -> None:
        field = FieldDefinition(
            name="company",
            label="Société",
            kind=FieldKind.TEXT,
        )

        template = Template(
            """
            {% load ep_form_fields %}
            {% render_ep_field field %}
            """
        )

        html = template.render(
            Context(
                {
                    "field": field,
                }
            )
        )

        self.assertIn(
            'name="company"',
            html,
        )

        self.assertIn(
            "Société",
            html,
        )

    def test_render_ep_field_accepts_django_bound_field(self) -> None:
        form = DjangoCompanyForm()

        template = Template(
            """
            {% load ep_form_fields %}
            {% render_ep_field field %}
            """
        )

        html = template.render(
            Context(
                {
                    "field": form["company"],
                }
            )
        )

        self.assertIn(
            'name="company"',
            html,
        )

        self.assertIn(
            "Société",
            html,
        )

    def test_render_ep_field_preserves_django_widget_properties(self) -> None:
        form = DjangoCompanyForm(
            initial={
                "company": "Entreprise Exemple",
            }
        )

        template = Template(
            """
            {% load ep_form_fields %}
            {% render_ep_field field %}
            """
        )

        html = template.render(
            Context(
                {
                    "field": form["company"],
                }
            )
        )

        self.assertIn(
            'id="id_company"',
            html,
        )
        self.assertIn(
            'value="Entreprise Exemple"',
            html,
        )
        self.assertIn(
            'maxlength="150"',
            html,
        )
        self.assertIn(
            "required",
            html,
        )
        self.assertIn(
            "Raison sociale de l&#x27;entreprise.",
            html,
        )

    def test_render_ep_field_adds_easy_project_css_class(self) -> None:
        form = DjangoCompanyForm()

        template = Template(
            """
            {% load ep_form_fields %}
            {% render_ep_field field %}
            """
        )

        html = template.render(
            Context(
                {
                    "field": form["company"],
                }
            )
        )

        self.assertIn(
            "edf-form-input",
            html,
        )
    
if __name__ == "__main__":
    unittest.main()