

from django import template
from django.forms.boundfield import BoundField
from django.template.loader import render_to_string

from framework.integrations.django.field_renderer import FieldRenderer
from framework.integrations.django.widget_adapter import WidgetAdapter


register = template.Library()

_field_renderer = FieldRenderer()
_widget_adapter = WidgetAdapter()


@register.simple_tag(takes_context=True)
def render_ep_field(context, field) -> str:
    """
    Rend un champ avec le template associé à son type.
    """

    if isinstance(field, BoundField):
        described_by = []

        if field.help_text:
            described_by.append(f"{field.auto_id}_help")

        if field.errors:
            described_by.append(f"{field.auto_id}_errors")

        _widget_adapter.adapt(
            field.field.widget,
            has_errors=bool(field.errors),
            described_by=" ".join(described_by) or None,
        )

    template_name = _field_renderer.get_template_name(field)

    field_context = context.flatten()
    field_context["field"] = field

    request = context.get("request")

    return render_to_string(
        template_name=template_name,
        context=field_context,
        request=request,
    )