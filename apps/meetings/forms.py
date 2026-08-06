

from __future__ import annotations

from django import forms

from apps.catalogs.models import CatalogValue
from apps.projects.models import Project
from apps.users.models import User
from common.constants.meeting import (
    MEETING_COMMENTS_LENGTH,
    MEETING_DURATION_MAX_HOURS,
    MEETING_LOCATION_LENGTH,
    MEETING_PARTICIPANT_EXTERNAL_EMAIL_LENGTH,
    MEETING_PARTICIPANT_EXTERNAL_NAME_LENGTH,
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
            # Rattachement
            "project",
            "organizer",
            "status",

            # Identification
            "reference",
            "subject",

            # Organisation
            "scheduled_at",
            "duration_hours",
            "location",

            # Informations
            "notes",
            "comments",

            # État
            "is_active",
        )

        labels = {
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
                "Ces informations restent réservées à un usage interne."
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
                    "max": str(MEETING_DURATION_MAX_HOURS),
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
                        "Commentaires réservés à l'organisation interne"
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
            self._apply_catalog_default("status")

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
            .select_related("catalog_type")
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
            catalog["catalog_type__is_editable"]
        )
        field.catalog_is_incremental = (
            catalog["catalog_type__is_incremental"]
        )

    def _apply_catalog_default(
        self,
        field_name: str,
    ) -> None:
        default_value = (
            self.fields[field_name]
            .queryset
            .filter(is_default=True)
            .first()
        )

        if default_value is not None:
            self.initial[field_name] = default_value.pk


class MeetingParticipantForm(forms.ModelForm):
    """
    Formulaire de gestion d'un participant interne ou externe.
    """

    invitation_response = CatalogModelChoiceField(
        queryset=CatalogValue.objects.none(),
        catalog_code="MEETING_INVITATION_RESPONSE",
        required=False,
        label="Réponse à l'invitation",
    )

    class Meta:
        model = MeetingParticipant

        fields = (
            "meeting",
            "participant",
            "external_name",
            "external_email",
            "invitation_response",
            "is_active",
        )

        labels = {
            "participant": "Participant interne",
            "external_name": "Nom du participant externe",
            "external_email": "Email du participant externe",
            "is_active": "Participation active",
        }

        help_texts = {
            "participant": (
                "Sélectionnez un utilisateur Easy Projet, "
                "ou renseignez un participant externe."
            ),
            "external_name": (
                "Obligatoire lorsqu'aucun participant interne "
                "n'est sélectionné."
            ),
        }

        widgets = {
            "external_name": forms.TextInput(
                attrs={
                    "maxlength": (
                        MEETING_PARTICIPANT_EXTERNAL_NAME_LENGTH
                    ),
                    "autocomplete": "name",
                    "placeholder": "Nom du participant externe",
                    "data-trim": True,
                }
            ),
            "external_email": forms.EmailInput(
                attrs={
                    "maxlength": (
                        MEETING_PARTICIPANT_EXTERNAL_EMAIL_LENGTH
                    ),
                    "autocomplete": "email",
                    "inputmode": "email",
                    "placeholder": "adresse@exemple.fr",
                    "data-trim": True,
                }
            ),
        }

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

        self.fields["participant"].queryset = (
            User.objects
            .filter(is_active=True)
            .select_related("company")
            .order_by(
                "last_name",
                "first_name",
            )
        )

        self._configure_catalog_field(
            field_name="invitation_response",
            catalog_code="MEETING_INVITATION_RESPONSE",
        )

        if not self.is_bound and not self.instance.pk:
            self._apply_catalog_default(
                "invitation_response"
            )

    def clean(self):
        cleaned_data = super().clean()

        participant = cleaned_data.get("participant")
        external_name = (
            cleaned_data.get("external_name") or ""
        ).strip()
        external_email = (
            cleaned_data.get("external_email") or ""
        ).strip()

        if participant is not None and (
            external_name or external_email
        ):
            message = (
                "Un participant ne peut pas être à la fois "
                "interne et externe."
            )

            self.add_error(
                "participant",
                message,
            )
            self.add_error(
                "external_name",
                (
                    "Laissez ce champ vide pour un "
                    "participant interne."
                ),
            )
            self.add_error(
                "external_email",
                (
                    "Laissez ce champ vide pour un "
                    "participant interne."
                ),
            )

        if participant is None and not external_name:
            self.add_error(
                "external_name",
                (
                    "Le nom du participant externe "
                    "est obligatoire."
                ),
            )

        cleaned_data["external_name"] = external_name
        cleaned_data["external_email"] = (
            external_email.lower()
        )

        return cleaned_data

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
            .select_related("catalog_type")
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
            catalog["catalog_type__is_editable"]
        )
        field.catalog_is_incremental = (
            catalog["catalog_type__is_incremental"]
        )

    def _apply_catalog_default(
        self,
        field_name: str,
    ) -> None:
        default_value = (
            self.fields[field_name]
            .queryset
            .filter(is_default=True)
            .first()
        )

        if default_value is not None:
            self.initial[field_name] = default_value.pk