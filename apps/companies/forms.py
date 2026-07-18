

from django import forms

from common.forms.widgets import TelInput

from .models import Company


class CompanyForm(forms.ModelForm):
    class Meta:
        model = Company

        fields = (
            "code",
            "name",
            "legal_name",
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

        help_texts = {
            "code": "Code interne unique de la société.",
            "name": "Nom utilisé dans l'application.",
            "legal_name": "Raison sociale officielle.",
        }

        widgets = {
            "code": forms.TextInput(
                attrs={
                    "maxlength": 10,
                    "placeholder": "Ex. AXCIO",
                    "autocomplete": "off",
                    "data_uppercase": True,
                    "data_trim": True,
                }
            ),
            "name": forms.TextInput(
                attrs={
                    "maxlength": 150,
                    "placeholder": "Nom utilisé dans l'application",
                    "autocomplete": "organization",
                    "data_trim": True,
                }
            ),
            "email": forms.EmailInput(
                attrs={
                    "maxlength": 254,
                    "autocomplete": "email",
                    "placeholder": "contact@entreprise.fr",
                    "data_lowercase": True,
                    "data_trim": True,
                }
            ),            
            "phone": TelInput(
                attrs={
                    "maxlength": 20,
                    "autocomplete": "tel",
                    "inputmode": "tel",
                    "placeholder": "01 23 45 67 89",
                    "data_trim": True,
                }
            ),
            "postal_code": forms.TextInput(
                attrs={
                    "autocomplete": "postal-code",
                    "inputmode": "numeric",
                }
            ),
            "city": forms.TextInput(
                attrs={"autocomplete": "address-level2"}
            ),
            "country": forms.TextInput(
                attrs={"autocomplete": "country-name"}
            ),
        }