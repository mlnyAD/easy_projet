

from __future__ import annotations

from django import forms

from apps.catalogs.models import CatalogValue
from apps.core.models import ClientEnvironmentMembership
from apps.users.models import User
from apps.users.services.access import UserAccessService
from common.forms.fields import CatalogModelChoiceField


class ClientEnvironmentMembershipForm(
    forms.ModelForm,
):
    """
    Formulaire de rattachement d'un utilisateur à un
    environnement client.
    """

    employment_type = CatalogModelChoiceField(
        queryset=CatalogValue.objects.none(),
        catalog_code="USER_EMPLOYMENT_TYPE",
        required=False,
        label="Type d'emploi",
    )

    is_client_admin_delegate = forms.BooleanField(
        required=False,
        label="Administrateur client délégué",
    )

    class Meta:
        model = ClientEnvironmentMembership

        fields = (
            "client_environment",
            "employment_type",
            "is_active",
            "is_client_admin_responsible",
        )

        labels = {
            "client_environment": (
                "Environnement client"
            ),
            "is_active": "Rattachement actif",
            "is_client_admin_responsible": (
                "Administrateur client titulaire"
            ),
        }

        help_texts = {
            "client_environment": (
                "Seules les sociétés disposant d'une "
                "licence sont proposées."
            ),
        }

    def __init__(
        self,
        *args,
        actor: User,
        target_user: User | None = None,
        **kwargs,
    ) -> None:
        super().__init__(
            *args,
            **kwargs,
        )

        self.actor = actor
        self.target_user = target_user

        self.fields[
            "client_environment"
        ].queryset = (
            UserAccessService
            .get_assignable_client_environments(
                actor
            )
        )

        self._configure_catalog_field(
            field_name="employment_type",
            catalog_code="USER_EMPLOYMENT_TYPE",
        )

        if (
            not self.is_bound
            and not self.instance.pk
        ):
            self.fields["is_active"].initial = True

        if not self.is_bound:
            self.fields[
                "is_client_admin_delegate"
            ].initial = (
                self.instance.is_client_admin
                and not self.instance
                .is_client_admin_responsible
            )

    def clean(self):
        cleaned_data = super().clean()

        is_responsible = bool(
            cleaned_data.get(
                "is_client_admin_responsible",
                False,
            )
        )

        is_delegate = bool(
            cleaned_data.get(
                "is_client_admin_delegate",
                False,
            )
        )

        if is_responsible and is_delegate:
            message = (
                "Un administrateur client ne peut pas être "
                "simultanément titulaire et délégué."
            )

            self.add_error(
                "is_client_admin_responsible",
                message,
            )

            self.add_error(
                "is_client_admin_delegate",
                message,
            )

        """
        Le modèle vérifie qu'un titulaire est aussi
        administrateur client. Cette valeur technique doit
        donc être préparée avant la validation du modèle.
        """
        self.instance.is_client_admin = (
            is_responsible
            or is_delegate
        )

        self.instance.is_client_admin_responsible = (
            is_responsible
        )

        return cleaned_data
    
    def save(
        self,
        commit: bool = True,
    ) -> ClientEnvironmentMembership:
        membership = super().save(
            commit=False,
        )

        is_responsible = bool(
            self.cleaned_data.get(
                "is_client_admin_responsible",
                False,
            )
        )

        is_delegate = bool(
            self.cleaned_data.get(
                "is_client_admin_delegate",
                False,
            )
        )

        membership.is_client_admin_responsible = (
            is_responsible
        )

        membership.is_client_admin = (
            is_responsible
            or is_delegate
        )

        """
        Dans l'écran dédié, target_user est déjà enregistré.

        Dans la collection du formulaire Utilisateur lors
        d'une création, le parent n'est pas encore enregistré :
        BaseInlineFormSet positionnera alors lui-même la
        relation user juste avant la sauvegarde.
        """
        if (
            self.target_user is not None
            and not self.target_user._state.adding
        ):
            membership.user = self.target_user

        if commit:
            membership.full_clean()
            membership.save()
            self.save_m2m()

        return membership

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


class BaseClientEnvironmentMembershipFormSet(
    forms.BaseInlineFormSet,
):
    """
    Collection des rattachements clients d'un utilisateur.

    Le queryset est limité au périmètre administrable par
    l'acteur connecté.
    """

    def __init__(
        self,
        *args,
        actor: User,
        **kwargs,
    ) -> None:
        self.actor = actor

        super().__init__(
            *args,
            **kwargs,
        )

    def get_queryset(self):
        if self.instance._state.adding:
            return ClientEnvironmentMembership.objects.none()

        return (
            UserAccessService
            .get_administrable_client_environment_memberships(
                self.actor,
                self.instance,
            )
        )

    def get_form_kwargs(
        self,
        index,
    ):
        kwargs = super().get_form_kwargs(
            index
        )

        kwargs["actor"] = self.actor
        kwargs["target_user"] = self.instance

        return kwargs


ClientEnvironmentMembershipFormSet = (
    forms.inlineformset_factory(
        User,
        ClientEnvironmentMembership,
        form=ClientEnvironmentMembershipForm,
        formset=BaseClientEnvironmentMembershipFormSet,
        fields=(
            "client_environment",
            "employment_type",
            "is_active",
            "is_client_admin_responsible",
        ),
        extra=0,
        can_delete=True,
    )
)