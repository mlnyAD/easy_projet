

from __future__ import annotations

from django import forms
from django.forms import (
    BaseInlineFormSet,
    inlineformset_factory,
)

from apps.catalogs.models import CatalogValue
from apps.projects.models import Project
from apps.users.models import User
from common.constants.meeting import (
    MEETING_COMMENTS_LENGTH,
    MEETING_DURATION_MAX_HOURS,
    MEETING_LOCATION_LENGTH,
    MEETING_PARTICIPANT_EXTERNAL_EMAIL_LENGTH,
    MEETING_REFERENCE_LENGTH,
    MEETING_SUBJECT_LENGTH,
)
from common.forms.fields import CatalogModelChoiceField

from .models import Meeting, MeetingParticipant


class MeetingForm(forms.ModelForm):
    """
    Formulaire de création et de modification d'une réunion.
    """

    status = CatalogModelChoiceField(
        queryset=CatalogValue.objects.none(),
        catalog_code="MEETING_STATUS",
        required=True,
        label="État",
    )

    class Meta:
        model = Meeting

        fields = (
            "project",
            "organizer",
            "status",
            "reference",
            "subject",
            "scheduled_at",
            "duration_hours",
            "location",
            "agenda",
            "notes",
            "comments",
            "is_active",
        )

        labels = {
            "agenda": "Ordre du jour",
            "notes": "Notes de convocation",
            "comments": "Commentaires internes",
            "is_active": "Réunion active",
        }

        help_texts = {
            "notes": (
                "Ces informations pourront être transmises "
                "aux participants avec l'invitation."
            ),
            "comments": (
                "Ces informations restent réservées "
                "à un usage interne."
            ),
        }

        widgets = {
            "reference": forms.TextInput(
                attrs={
                    "maxlength": MEETING_REFERENCE_LENGTH,
                    "autocomplete": "off",
                    "placeholder": (
                        "Générée automatiquement si vide"
                    ),
                    "data-uppercase": True,
                    "data-trim": True,
                }
            ),
            "subject": forms.TextInput(
                attrs={
                    "maxlength": MEETING_SUBJECT_LENGTH,
                    "autocomplete": "off",
                    "placeholder": "Objet de la réunion",
                    "data-trim": True,
                }
            ),
            "scheduled_at": forms.DateTimeInput(
                attrs={
                    "type": "datetime-local",
                },
                format="%Y-%m-%dT%H:%M",
            ),
            "duration_hours": forms.NumberInput(
                attrs={
                    "min": "0.25",
                    "max": str(
                        MEETING_DURATION_MAX_HOURS
                    ),
                    "step": "0.25",
                    "inputmode": "decimal",
                    "placeholder": "Ex. 1,50",
                }
            ),
            "location": forms.TextInput(
                attrs={
                    "maxlength": MEETING_LOCATION_LENGTH,
                    "autocomplete": "off",
                    "placeholder": (
                        "Salle, adresse ou lien de visioconférence"
                    ),
                    "data-trim": True,
                }
            ),
            "agenda": forms.Textarea(
                attrs={
                    "maxlength": MEETING_COMMENTS_LENGTH,
                    "rows": 5,
                    "placeholder": (
                        "Points prévus à l'ordre du jour"
                    ),
                    "data-trim": True,
                }
            ),
            "notes": forms.Textarea(
                attrs={
                    "maxlength": MEETING_COMMENTS_LENGTH,
                    "rows": 4,
                    "placeholder": (
                        "Informations pratiques ou consignes "
                        "destinées aux participants"
                    ),
                    "data-trim": True,
                }
            ),
            "comments": forms.Textarea(
                attrs={
                    "maxlength": MEETING_COMMENTS_LENGTH,
                    "rows": 4,
                    "placeholder": (
                        "Commentaires réservés "
                        "à l'organisation interne"
                    ),
                    "data-trim": True,
                }
            ),
        }

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

        self.fields["reference"].required = False

        self.fields["scheduled_at"].input_formats = (
            "%Y-%m-%dT%H:%M",
            "%Y-%m-%d %H:%M:%S",
            "%Y-%m-%d %H:%M",
        )

        self.fields["project"].queryset = (
            Project.objects
            .filter(is_active=True)
            .select_related(
                "owner_company",
                "project_manager",
            )
            .order_by(
                "reference",
                "name",
            )
        )

        self.fields["organizer"].queryset = (
            User.objects
            .filter(is_active=True)
            .select_related("company")
            .order_by(
                "last_name",
                "first_name",
            )
        )

        self._configure_catalog_field(
            field_name="status",
            catalog_code="MEETING_STATUS",
        )

        if not self.is_bound and not self.instance.pk:
            self._apply_catalog_default(
                "status"
            )

    def _configure_catalog_field(
        self,
        *,
        field_name: str,
        catalog_code: str,
    ) -> None:
        catalog = (
            CatalogValue.objects
            .filter(
                catalog_type__code=catalog_code,
                catalog_type__is_active=True,
            )
            .values(
                "catalog_type__is_editable",
                "catalog_type__is_incremental",
            )
            .first()
        )

        field = self.fields[field_name]

        field.queryset = (
            CatalogValue.objects
            .filter(
                catalog_type__code=catalog_code,
                catalog_type__is_active=True,
                is_active=True,
            )
            .select_related(
                "catalog_type"
            )
            .order_by(
                "level",
                "sort_order",
                "label",
            )
        )

        if catalog is None:
            field.catalog_is_editable = False
            field.catalog_is_incremental = False
            return

        field.catalog_is_editable = (
            catalog[
                "catalog_type__is_editable"
            ]
        )

        field.catalog_is_incremental = (
            catalog[
                "catalog_type__is_incremental"
            ]
        )

    def _apply_catalog_default(
        self,
        field_name: str,
    ) -> None:
        default_value = (
            self.fields[field_name]
            .queryset
            .filter(
                is_default=True
            )
            .first()
        )

        if default_value is not None:
            self.initial[field_name] = (
                default_value.pk
            )


class InternalMeetingParticipantForm(
    forms.ModelForm
):
    """
    Participant Easy Projet.
    """

    class Meta:
        model = MeetingParticipant

        fields = (
            "participant",
        )

    def __init__(
        self,
        *args,
        **kwargs,
    ) -> None:
        super().__init__(
            *args,
            **kwargs,
        )

        self.fields[
            "participant"
        ].required = True

        self.fields[
            "participant"
        ].label = "Participant"

        self.fields[
            "participant"
        ].queryset = (
            User.objects
            .filter(
                is_active=True
            )
            .select_related(
                "company"
            )
            .order_by(
                "last_name",
                "first_name",
            )
        )


class ExternalMeetingParticipantForm(
    forms.ModelForm
):
    """
    Participant externe identifié
    par son adresse email.
    """

    class Meta:
        model = MeetingParticipant

        fields = (
            "external_email",
        )

        widgets = {
            "external_email": (
                forms.EmailInput(
                    attrs={
                        "maxlength": (
                            MEETING_PARTICIPANT_EXTERNAL_EMAIL_LENGTH
                        ),
                        "autocomplete": "email",
                        "inputmode": "email",
                        "placeholder": "adresse@exemple.fr",
                        "data-trim": True,
                    }
                )
            ),
        }

    def __init__(
        self,
        *args,
        **kwargs,
    ) -> None:
        super().__init__(
            *args,
            **kwargs,
        )

        self.fields[
            "external_email"
        ].required = True

        self.fields[
            "external_email"
        ].label = "Adresse email"

    def clean_external_email(self):
        value = (
            self.cleaned_data[
                "external_email"
            ]
        )

        return value.strip().lower()


class InternalParticipantFormSet(
    BaseInlineFormSet
):
    """
    Formset des participants internes.
    """

    def get_queryset(self):
        return (
            super()
            .get_queryset()
            .filter(
                participant__isnull=False,
                is_active=True,
            )
            .select_related(
                "participant",
                "participant__company",
            )
        )

    def clean(self) -> None:
        super().clean()

        if any(self.errors):
            return

        participant_ids = set()

        for form in self.forms:
            if not form.cleaned_data:
                continue

            if form.cleaned_data.get(
                "DELETE"
            ):
                continue

            participant = (
                form.cleaned_data.get(
                    "participant"
                )
            )

            if participant is None:
                continue

            if participant.pk in participant_ids:
                raise forms.ValidationError(
                    "Un participant interne ne peut être "
                    "ajouté qu'une seule fois."
                )

            participant_ids.add(
                participant.pk
            )


class ExternalParticipantFormSet(
    BaseInlineFormSet
):
    """
    Formset des participants externes.
    """

    def get_queryset(self):
        return (
            super()
            .get_queryset()
            .filter(
                participant__isnull=True,
                is_active=True,
            )
        )

    def clean(self) -> None:
        super().clean()

        if any(self.errors):
            return

        emails = set()

        for form in self.forms:
            if not form.cleaned_data:
                continue

            if form.cleaned_data.get(
                "DELETE"
            ):
                continue

            email = (
                form.cleaned_data.get(
                    "external_email"
                )
                or ""
            ).strip().lower()

            if not email:
                continue

            if email in emails:
                raise forms.ValidationError(
                    "Une adresse email externe ne peut être "
                    "ajoutée qu'une seule fois."
                )

            emails.add(
                email
            )


InternalMeetingParticipantFormSet = (
    inlineformset_factory(
        Meeting,
        MeetingParticipant,
        form=InternalMeetingParticipantForm,
        formset=InternalParticipantFormSet,
        extra=0,
        can_delete=True,
    )
)


ExternalMeetingParticipantFormSet = (
    inlineformset_factory(
        Meeting,
        MeetingParticipant,
        form=ExternalMeetingParticipantForm,
        formset=ExternalParticipantFormSet,
        extra=0,
        can_delete=True,
    )
)