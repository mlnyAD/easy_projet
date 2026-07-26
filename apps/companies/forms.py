

from django import forms

from common.forms.widgets import TelInput

from .models import Company


class CompanyForm(forms.ModelForm):
    class Meta:
        model = Company

        fields = (
            "name",
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
            "name": forms.TextInput(
                attrs={
                    "maxlength": 150,
                    "placeholder": "Nom utilisé dans l'application",
                    "autocomplete": "organization",
                    "data-uppercase": True,
                    "data-trim": True,
                }
            ),
            "email": forms.EmailInput(
                attrs={
                    "maxlength": 254,
                    "autocomplete": "email",
                    "placeholder": "contact@entreprise.fr",
                    "data-lowercase": True,
                    "data-trim": True,
                }
            ),
            "phone": TelInput(
                attrs={
                    "maxlength": 20,
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
                    "maxlength": 17,
                    "placeholder": "123 456 789 00012",
                    "autocomplete": "siret",
                    "data-uppercase": True,
                    "data-trim": True,
                }
            ),
            "vat_number": forms.TextInput(
                attrs={
                    "maxlength": 32,
                    "placeholder": "Ex. FR12345678901",
                    "autocomplete": "off",
                    "data-uppercase": True,
                    "inputmode": "numeric",
                    "data-trim": True,
                }
            ),
            
        }