

from __future__ import annotations

import re
from collections.abc import Sequence

from django import forms
from django.core.exceptions import ValidationError
from django.core.validators import validate_email

from apps.documents.models import Document
from apps.documents.services import SignatureRecipientInput
from apps.projects.models import Project
from apps.users.models import User


class SignatureRequestCreateForm(forms.Form):
    """
    Création d'une demande de signature.

    Les signataires internes proviennent des membres actifs du projet.
    Les signataires externes sont saisis sous la forme :
    Nom Prénom <adresse@exemple.fr>
    """

    EXTERNAL_SIGNER_PATTERN = re.compile(
        r"^\s*(?P<name>.+?)\s*<(?P<email>[^<>]+)>\s*$"
    )

    title = forms.CharField(
        label="Titre de la demande",
        max_length=255,
        widget=forms.TextInput(
            attrs={
                "autocomplete": "off",
                "data-trim": True,
            }
        ),
    )

    documents = forms.ModelMultipleChoiceField(
        label="Documents PDF à signer",
        queryset=Document.objects.none(),
        widget=forms.CheckboxSelectMultiple(),
    )

    internal_signers = forms.ModelMultipleChoiceField(
        label="Signataires internes",
        queryset=User.objects.none(),
        required=False,
        widget=forms.SelectMultiple(
            attrs={
                "size": 6,
            }
        ),
        help_text=(
            "Utilisateurs actifs affectés au projet. "
            "Maintenez Ctrl pour plusieurs sélections."
        ),
    )

    external_signers = forms.CharField(
        label="Signataires externes",
        required=False,
        widget=forms.Textarea(
            attrs={
                "rows": 4,
                "placeholder": (
                    "Jean Dupont <jean.dupont@entreprise.fr>\n"
                    "Marie Martin <marie.martin@client.fr>"
                ),
            }
        ),
        help_text=(
            "Un signataire par ligne, au format "
            "Nom Prénom <adresse@exemple.fr>."
        ),
    )

    def __init__(
        self,
        *args,
        project: Project,
        initial_document_ids: Sequence[str] = (),
        **kwargs,
    ) -> None:
        super().__init__(*args, **kwargs)

        self.project = project

        documents = (
            Document.objects
            .filter(
                project=project,
                current_version__isnull=False,
                is_doe_generated=False,
            )
            .select_related(
                "current_version",
                "folder",
            )
            .order_by(
                "folder__name",
                "title",
            )
        )

        internal_signers = (
            User.objects
            .filter(
                is_active=True,
                project_memberships__project=project,
                project_memberships__is_active=True,
            )
            .distinct()
            .order_by(
                "last_name",
                "first_name",
            )
        )

        self.fields["documents"].queryset = documents
        self.fields["internal_signers"].queryset = (
            internal_signers
        )

        if not self.is_bound and initial_document_ids:
            self.initial["documents"] = list(
                initial_document_ids
            )

    def clean_documents(self):
        documents = self.cleaned_data["documents"]

        unsupported_documents = []

        for document in documents:
            version = document.current_version

            if not (
                version.mime_type.lower() == "application/pdf"
                or version.original_filename.lower().endswith(
                    ".pdf"
                )
            ):
                unsupported_documents.append(document.title)

        if unsupported_documents:
            raise ValidationError(
                "Seuls les documents PDF peuvent être envoyés "
                "en signature : "
                + ", ".join(unsupported_documents)
                + "."
            )

        return documents

    def clean(self):
        cleaned_data = super().clean()

        internal_signers = cleaned_data.get(
            "internal_signers"
        )

        external_signers = cleaned_data.get(
            "external_signers",
            "",
        )

        recipient_inputs: list[SignatureRecipientInput] = []

        if internal_signers:
            for user in internal_signers:
                recipient_inputs.append(
                    SignatureRecipientInput(
                        full_name=str(user),
                        email=user.email,
                        user=user,
                    )
                )

        for line_number, line in enumerate(
            external_signers.splitlines(),
            start=1,
        ):
            normalized_line = line.strip()

            if not normalized_line:
                continue

            match = self.EXTERNAL_SIGNER_PATTERN.match(
                normalized_line
            )

            if match is None:
                self.add_error(
                    "external_signers",
                    (
                        f"Ligne {line_number} : utilisez le format "
                        "Nom Prénom <adresse@exemple.fr>."
                    ),
                )
                continue

            full_name = match.group("name").strip()
            email = match.group("email").strip().lower()

            try:
                validate_email(email)
            except ValidationError:
                self.add_error(
                    "external_signers",
                    (
                        f"Ligne {line_number} : l'adresse e-mail "
                        "est invalide."
                    ),
                )
                continue

            recipient_inputs.append(
                SignatureRecipientInput(
                    full_name=full_name,
                    email=email,
                )
            )

        if not recipient_inputs:
            raise ValidationError(
                "Sélectionnez au moins un signataire interne "
                "ou ajoutez un signataire externe."
            )

        cleaned_data["recipient_inputs"] = tuple(
            recipient_inputs
        )

        return cleaned_data