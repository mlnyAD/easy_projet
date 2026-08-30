

from django import forms

from common.constants.company import (
    COMPANY_EMAIL_LENGTH,
    COMPANY_NAME_LENGTH,
    COMPANY_PHONE_LENGTH,
    COMPANY_SIRET_LENGTH,
    COMPANY_VAT_NUMBER_LENGTH,
)
from common.forms.widgets import (
    FileUploadInput,
    TelInput,
)

from .models import Company


class CompanyForm(forms.ModelForm):
    class Meta:
        model = Company

        fields = (
            "name",
            "logo",
            "siret",
            "vat_number",
            "email",
            "phone",
            "address_1",
            "address_2",
            "address_3",
            "postal_code",
            "city",
            "country",
            "is_active",
        )

        labels = {
            "is_active": "Société active",
        }

        help_texts = {
            "name": "Nom utilisé dans l'application.",
        }

        widgets = {
            "logo": FileUploadInput(),
            "name": forms.TextInput(
                attrs={
                    "maxlength": COMPANY_NAME_LENGTH,
                    "placeholder": "Nom utilisé dans l'application",
                    "autocomplete": "organization",
                    "data-uppercase": True,
                    "data-trim": True,
                }
            ),
            "email": forms.EmailInput(
                attrs={
                    "maxlength": COMPANY_EMAIL_LENGTH,
                    "autocomplete": "email",
                    "placeholder": "contact@entreprise.fr",
                    "data-lowercase": True,
                    "data-trim": True,
                }
            ),
            "phone": TelInput(
                attrs={
                    "maxlength": COMPANY_PHONE_LENGTH,
                    "autocomplete": "tel",
                    "inputmode": "tel",
                    "placeholder": "01 23 45 67 89",
                    "data-phone": True,
                    "data-trim": True,
                }
            ),
            "postal_code": forms.TextInput(
                attrs={
                    "autocomplete": "postal-code",
                    "inputmode": "numeric",
                }
            ),
            "city": forms.TextInput(
                attrs={
                    "autocomplete": "address-level2",
                    "data-uppercase": True,
                    "data-trim": True,
                }
            ),
            "country": forms.TextInput(
                attrs={
                    "autocomplete": "country-name",
                    "data-uppercase": True,
                    "data-trim": True,
                }
            ),
            "siret": forms.TextInput(
                attrs={
                    "maxlength": COMPANY_SIRET_LENGTH,
                    "placeholder": "123 456 789 00012",
                    "autocomplete": "off",
                    "data-trim": True,
                }
            ),
            "vat_number": forms.TextInput(
                attrs={
                    "maxlength": COMPANY_VAT_NUMBER_LENGTH,
                    "placeholder": "Ex. FR12345678901",
                    "autocomplete": "off",
                    "data-uppercase": True,
                    "data-trim": True,
                }
            ),
        }