

from django import template
from django.forms.boundfield import BoundField
from django.template.loader import render_to_string

from framework.form.kinds import FieldKind
from framework.form.resolved_field import ResolvedField
from framework.integrations.django.field_renderer import (
    FieldRenderer,
)
from framework.integrations.django.widget_adapter import (
    WidgetAdapter,
)


register = template.Library()

_field_renderer = FieldRenderer()
_widget_adapter = WidgetAdapter()


@register.simple_tag(takes_context=True)
def render_ep_field(context, field) -> str:
    """
    Rend un champ avec le template associé à son type.
    """

    bound_field = _resolve_bound_field(field)

    if bound_field is not None:
        described_by = []

        if bound_field.help_text:
            described_by.append(
                f"{bound_field.auto_id}_help"
            )

        if bound_field.errors:
            described_by.append(
                f"{bound_field.auto_id}_errors"
            )

        _widget_adapter.adapt(
            bound_field.field.widget,
            has_errors=bool(
                bound_field.errors
            ),
            described_by=(
                " ".join(described_by)
                or None
            ),
        )

    if isinstance(field, ResolvedField):
        _apply_file_upload_configuration(
            field
        )

    template_name = (
        _field_renderer.get_template_name(
            field
        )
    )

    field_context = context.flatten()

    field_context["field"] = field
    field_context["bound_field"] = bound_field

    request = context.get("request")

    return render_to_string(
        template_name=template_name,
        context=field_context,
        request=request,
    )


def _resolve_bound_field(
    field,
) -> BoundField | None:
    """
    Retourne le BoundField Django associé au champ.
    """

    if isinstance(
        field,
        ResolvedField,
    ):
        return field.bound_field

    if isinstance(
        field,
        BoundField,
    ):
        return field

    return None


def _apply_file_upload_configuration(
    field: ResolvedField,
) -> None:
    """
    Applique au widget Django la configuration
    déclarée par FileUploadDefinition.
    """

    if (
        field.kind
        != FieldKind.FILE_UPLOAD
    ):
        return

    upload = field.upload

    if upload is None:
        return

    widget = field.bound_field.field.widget

    if upload.multiple:
        widget.attrs["multiple"] = True
    else:
        widget.attrs.pop(
            "multiple",
            None,
        )

    accept_values = []

    accept_values.extend(
        upload.allowed_mime_types
    )

    accept_values.extend(
        upload.allowed_extensions
    )

    if accept_values:
        widget.attrs["accept"] = ",".join(
            accept_values
        )
    else:
        widget.attrs.pop(
            "accept",
            None,
        )