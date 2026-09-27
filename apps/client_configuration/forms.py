

from __future__ import annotations

from django import forms

from .models import (
    DocumentFolderTemplate,
    DocumentFolderTemplateFolder,
)


class DocumentFolderTemplateForm(forms.ModelForm):
    """
    Formulaire de création et modification d'un modèle
    d'arborescence documentaire.
    """

    class Meta:
        model = DocumentFolderTemplate
        fields = [
            "name",
            "description",
            "is_active",
        ]
        widgets = {
            "name": forms.TextInput(
                attrs={
                    "autocomplete": "off",
                    "data-trim": True,
                }
            ),
            "description": forms.Textarea(
                attrs={
                    "rows": 4,
                    "data-trim": True,
                }
            ),
        }

    def __init__(
        self,
        *args,
        client_environment,
        **kwargs,
    ):
        self.client_environment = client_environment

        super().__init__(
            *args,
            **kwargs,
        )

        self.instance.client_environment = client_environment

    def clean_name(self):
        name = (
            self.cleaned_data["name"]
            .strip()
        )

        if not name:
            raise forms.ValidationError(
                "Le nom du modèle est obligatoire."
            )

        duplicate_exists = (
            DocumentFolderTemplate.objects
            .filter(
                client_environment=(
                    self.client_environment
                ),
                name=name,
            )
            .exclude(
                pk=self.instance.pk,
            )
            .exists()
        )

        if duplicate_exists:
            raise forms.ValidationError(
                "Un modèle d'arborescence portant ce nom existe déjà."
            )

        return name


class DocumentFolderTemplateFolderForm(forms.ModelForm):
    """
    Formulaire d'un dossier appartenant à un modèle
    d'arborescence documentaire.
    """

    class Meta:
        model = DocumentFolderTemplateFolder
        fields = [
            "name",
            "parent",
            "sort_order",
            "is_active",
        ]
        widgets = {
            "name": forms.TextInput(
                attrs={
                    "autocomplete": "off",
                    "data-trim": True,
                }
            ),
        }

    def __init__(
        self,
        *args,
        template,
        **kwargs,
    ):
        self.template = template

        super().__init__(
            *args,
            **kwargs,
        )

        self.instance.template = template

        parents = (
            DocumentFolderTemplateFolder.objects
            .filter(
                template=template,
            )
            .order_by(
                "parent__sort_order",
                "parent__name",
                "sort_order",
                "name",
            )
        )

        if self.instance.pk:
            parents = parents.exclude(
                pk=self.instance.pk,
            )

        self.fields["parent"].queryset = parents
        self.fields["parent"].required = False
        self.fields["parent"].empty_label = (
            "Racine de l'arborescence"
        )

    def clean_name(self):
        name = (
            self.cleaned_data["name"]
            .strip()
        )

        if not name:
            raise forms.ValidationError(
                "Le nom du dossier est obligatoire."
            )

        return name

    def clean(self):
        cleaned_data = super().clean()

        parent = cleaned_data.get("parent")
        name = cleaned_data.get("name")

        if parent is None or not name:
            return cleaned_data

        duplicate_exists = (
            DocumentFolderTemplateFolder.objects
            .filter(
                template=self.template,
                parent=parent,
                name=name,
            )
            .exclude(
                pk=self.instance.pk,
            )
            .exists()
        )

        if duplicate_exists:
            self.add_error(
                "name",
                (
                    "Un dossier portant ce nom existe déjà "
                    "à cet emplacement."
                ),
            )

        return cleaned_data
    