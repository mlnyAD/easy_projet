
    
from django import template
from django.template.loader import render_to_string

from framework.integrations.django.field_renderer import FieldRenderer


register = template.Library()

_field_renderer = FieldRenderer()


@register.simple_tag(takes_context=True)
def render_ep_field(context, field) -> str:
    """
    Rend un champ avec le template associé à son type.
    """
    template_name = _field_renderer.get_template_name(field)

    field_context = context.flatten()
    field_context["field"] = field

    request = context.get("request")

    return render_to_string(
        template_name=template_name,
        context=field_context,
        request=request,
    )