

from __future__ import annotations

from django import forms
from django.db.models import Q
from django.forms import (
    BaseInlineFormSet,
    inlineformset_factory,
)

from apps.catalogs.models import CatalogValue
from apps.projects.models import Project, ProjectMembership
from apps.projects.services.authorization import (
    ProjectAuthorizationService,
)
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
    def __init__(
        self,
        *args,
        user=None,
        **kwargs,
    ) -> None:
        super().__init__(*args, **kwargs)

        self.fields["reference"].required = False

        self.fields["scheduled_at"].input_formats = (
            "%Y-%m-%dT%H:%M",
            "%Y-%m-%d %H:%M:%S",
            "%Y-%m-%d %H:%M",
        )

        if user is None:
            self.fields["project"].queryset = (
                self.fields["project"]
                .queryset
                .none()
            )
        else:
            workable_projects = (
                ProjectAuthorizationService
                .get_workable_projects(user)
            )

            project_filter = Q(
                pk__in=workable_projects,
            )

            if self.instance.pk:
                project_filter |= Q(
                    pk=self.instance.project_id,
                )

            self.fields["project"].queryset = (
                Project.objects
                .filter(project_filter)
                .select_related(
                    "owner_company",
                )
                .order_by(
                    "reference",
                    "name",
                )
            )

        selected_project = self._get_selected_project()

        if selected_project is None:
            self.fields["organizer"].queryset = User.objects.none()
        else:
            self.fields["organizer"].queryset = (
                User.objects
                .filter(
                    is_active=True,
                    company_id=selected_project.company_id,
                )
                .select_related("company")
                .order_by("last_name", "first_name")
            )

        self._configure_catalog_field(
            field_name="status",
            catalog_code="MEETING_STATUS",
        )

        if not self.is_bound and self.instance._state.adding:
            self._apply_catalog_default(
                "status"
            )

    def _get_selected_project(self):
        project_id = None

        if self.is_bound:
            project_id = self.data.get(
                self.add_prefix("project")
            )
        elif self.instance.project_id:
            project_id = self.instance.project_id
        else:
            project_id = self.initial.get("project")

        if not project_id:
            return None

        return self.fields["project"].queryset.filter(
            pk=project_id,
        ).first()

    def clean(self):
        cleaned_data = super().clean()

        project = cleaned_data.get("project")
        organizer = cleaned_data.get("organizer")

        if (
            project is not None
            and organizer is not None
            and organizer.company_id != project.company_id
        ):
            self.add_error(
                "organizer",
                "L'organisateur doit appartenir à la société du projet.",
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
        project=None,
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

        if project is None:
            self.fields["participant"].queryset = User.objects.none()
            return

        member_ids = (
            ProjectMembership.objects
            .filter(
                project=project,
                is_active=True,
                user__is_active=True,
            )
            .values_list("user_id", flat=True)
        )

        self.fields["participant"].queryset = (
            User.objects
            .filter(pk__in=member_ids)
            .select_related("company")
            .order_by("last_name", "first_name")
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

    def __init__(self, *args, project=None, **kwargs):
        self.project = project
        super().__init__(*args, **kwargs)

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

        if self.project is None:
            raise forms.ValidationError(
                "Le projet de la réunion doit être renseigné."
            )

        valid_participant_ids = set(
            ProjectMembership.objects
            .filter(
                project=self.project,
                is_active=True,
                user__is_active=True,
                user_id__in=participant_ids,
            )
            .values_list("user_id", flat=True)
        )

        if participant_ids != valid_participant_ids:
            raise forms.ValidationError(
                "Les participants internes doivent être "
                "des utilisateurs actifs rattachés au projet."
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
