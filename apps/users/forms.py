

from __future__ import annotations

from django import forms

from apps.catalogs.models import CatalogValue
from apps.companies.models import Company
from common.constants.user import (
    USER_EMAIL_LENGTH,
    USER_FIRST_NAME_LENGTH,
    USER_LAST_NAME_LENGTH,
    USER_MOBILE_LENGTH,
    USER_PHONE_LENGTH,
)
from common.forms.fields import CatalogModelChoiceField
from common.forms.widgets import (
    FileUploadInput,
    TelInput,
)

from .models import User

from django.contrib.auth.password_validation import (
    password_validators_help_text_html,
    validate_password,
)
from django.core.exceptions import ValidationError


class UserForm(forms.ModelForm):
    """
    Formulaire de création et de modification d'un utilisateur.

    Le mot de passe et les préférences personnelles ne sont jamais
    saisis dans ce formulaire d'administration.

    Un nouvel utilisateur est créé avec un mot de passe inutilisable,
    dans l'attente de la validation de son invitation.
    """

    employment_type = CatalogModelChoiceField(
        queryset=CatalogValue.objects.none(),
        catalog_code="USER_EMPLOYMENT_TYPE",
        required=False,
        label="Type d'emploi",
    )

    job = CatalogModelChoiceField(
        queryset=CatalogValue.objects.none(),
        catalog_code="USER_JOB",
        required=False,
        label="Métier",
    )

    global_role = CatalogModelChoiceField(
        queryset=CatalogValue.objects.none(),
        catalog_code="USER_GLOBAL_ROLE",
        required=True,
        label="Rôle global",
    )

    access_level = CatalogModelChoiceField(
        queryset=CatalogValue.objects.none(),
        catalog_code="USER_LEVEL_ACCESS",
        required=True,
        label="Niveau d'accès",
    )

    class Meta:
        model = User

        fields = (
            "last_name",
            "first_name",
            "email",
            "phone",
            "mobile",
            "company",
            "employment_type",
            "job",
            "global_role",
            "access_level",
            "is_active",
        )

        labels = {
            "is_active": "Utilisateur actif",
        }

        widgets = {
            "last_name": forms.TextInput(
                attrs={
                    "maxlength": USER_LAST_NAME_LENGTH,
                    "autocomplete": "family-name",
                    "data-uppercase": True,
                    "data-trim": True,
                }
            ),
            "first_name": forms.TextInput(
                attrs={
                    "maxlength": USER_FIRST_NAME_LENGTH,
                    "autocomplete": "given-name",
                    "data-trim": True,
                }
            ),
            "email": forms.EmailInput(
                attrs={
                    "maxlength": USER_EMAIL_LENGTH,
                    "autocomplete": "email",
                    "placeholder": "prenom.nom@entreprise.fr",
                    "data-lowercase": True,
                    "data-trim": True,
                }
            ),
            "phone": TelInput(
                attrs={
                    "maxlength": USER_PHONE_LENGTH,
                    "autocomplete": "tel",
                    "inputmode": "tel",
                    "placeholder": "01 23 45 67 89",
                    "data-phone": True,
                    "data-trim": True,
                }
            ),
            "mobile": TelInput(
                attrs={
                    "maxlength": USER_MOBILE_LENGTH,
                    "autocomplete": "tel",
                    "inputmode": "tel",
                    "placeholder": "06 12 34 56 78",
                    "data-phone": True,
                    "data-trim": True,
                }
            ),
        }

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

        self.fields["company"].queryset = (
            Company.objects
            .filter(is_active=True)
            .order_by("name")
        )

        self._configure_catalog_field(
            field_name="employment_type",
            catalog_code="USER_EMPLOYMENT_TYPE",
        )
        self._configure_catalog_field(
            field_name="job",
            catalog_code="USER_JOB",
        )
        self._configure_catalog_field(
            field_name="global_role",
            catalog_code="USER_GLOBAL_ROLE",
        )
        self._configure_catalog_field(
            field_name="access_level",
            catalog_code="USER_LEVEL_ACCESS",
        )

        if not self.is_bound and not self.instance.pk:
            self._apply_catalog_default("employment_type")
            self._apply_catalog_default("job")
            self._apply_catalog_default("global_role")
            self._apply_catalog_default("access_level")

    def save(self, commit: bool = True) -> User:
        user = super().save(commit=False)

        if user._state.adding:
            user.set_unusable_password()

        if commit:
            user.save()
            self.save_m2m()

        return user

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
            
class AccountForm(forms.ModelForm):
    """
    Formulaire personnel de l'utilisateur connecté.

    Les données administratives sont affichées en lecture seule.
    L'utilisateur peut modifier sa photo et son mot de passe.
    """

    company_display = forms.CharField(
        label="Société",
        required=False,
        disabled=True,
    )

    global_role_display = forms.CharField(
        label="Rôle",
        required=False,
        disabled=True,
    )

    current_password = forms.CharField(
        label="Mot de passe actuel",
        required=False,
        strip=False,
        widget=forms.PasswordInput(
            attrs={
                "autocomplete": "current-password",
            }
        ),
    )

    new_password = forms.CharField(
        label="Nouveau mot de passe",
        required=False,
        strip=False,
        help_text=password_validators_help_text_html(),
        widget=forms.PasswordInput(
            attrs={
                "autocomplete": "new-password",
            }
        ),
    )

    new_password_confirmation = forms.CharField(
        label="Confirmation du nouveau mot de passe",
        required=False,
        strip=False,
        widget=forms.PasswordInput(
            attrs={
                "autocomplete": "new-password",
            }
        ),
    )

    class Meta:
        model = User

        fields = (
            "photo",
            "first_name",
            "last_name",
            "email",
        )

        widgets = {
            "photo": FileUploadInput(),
            "first_name": forms.TextInput(
                attrs={
                    "autocomplete": "given-name",
                }
            ),
            "last_name": forms.TextInput(
                attrs={
                    "autocomplete": "family-name",
                }
            ),
            "email": forms.EmailInput(
                attrs={
                    "autocomplete": "email",
                }
            ),
        }
        
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        
        if not self.instance.has_usable_password():
            self.fields["current_password"].required = False
            self.fields["current_password"].disabled = True
            self.fields["current_password"].help_text = (
                "Aucun mot de passe n'est encore défini pour ce compte."
            )

        # Données administrées depuis Contacts.
        self.fields["first_name"].disabled = True
        self.fields["last_name"].disabled = True
        self.fields["email"].disabled = True

        self.fields["company_display"].initial = (
            self.instance.company.name
            if self.instance.company_id
            else ""
        )

        self.fields["global_role_display"].initial = (
            self.instance.global_role.label
            if self.instance.global_role_id
            else ""
        )

    def clean(self):
        cleaned_data = super().clean()

        current_password = cleaned_data.get(
            "current_password"
        )
        new_password = cleaned_data.get(
            "new_password"
        )
        confirmation = cleaned_data.get(
            "new_password_confirmation"
        )

        password_change_requested = any(
            (
                current_password,
                new_password,
                confirmation,
            )
        )

        if not password_change_requested:
            return cleaned_data

        if self.instance.has_usable_password():
            if not current_password:
                self.add_error(
                    "current_password",
                    "Saisissez votre mot de passe actuel.",
                )
            elif not self.instance.check_password(current_password):
                self.add_error(
                    "current_password",
                    "Le mot de passe actuel est incorrect.",
                )
                
        if not new_password:
            self.add_error(
                "new_password",
                "Saisissez le nouveau mot de passe.",
            )

        if not confirmation:
            self.add_error(
                "new_password_confirmation",
                "Confirmez le nouveau mot de passe.",
            )

        if (
            new_password
            and confirmation
            and new_password != confirmation
        ):
            self.add_error(
                "new_password_confirmation",
                "Les deux mots de passe ne correspondent pas.",
            )

        if new_password:
            try:
                validate_password(
                    new_password,
                    user=self.instance,
                )
            except ValidationError as error:
                self.add_error(
                    "new_password",
                    error,
                )

        return cleaned_data

    def save(self, commit: bool = True) -> User:
        user = super().save(commit=False)

        new_password = self.cleaned_data.get(
            "new_password"
        )

        if new_password:
            user.set_password(new_password)

        if commit:
            user.save()
            self.save_m2m()

        return user