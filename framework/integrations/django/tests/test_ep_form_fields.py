

import os
import unittest

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


if __name__ == "__main__":
    unittest.main()