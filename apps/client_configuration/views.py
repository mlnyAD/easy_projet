

from __future__ import annotations

from collections import defaultdict

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import transaction
from django.utils import timezone
from django.http import HttpResponseBadRequest
from django.shortcuts import (
    get_object_or_404,
    redirect,
)
from django.urls import reverse
from django.views import View
from django.views.generic import FormView, TemplateView

from apps.core.models import ClientEnvironment

from .forms import (
    DocumentFolderTemplateFolderForm,
    DocumentFolderTemplateForm,
)
from .models import (
    DocumentFolderTemplate,
    DocumentFolderTemplateFolder,
)
from .services.access import (
    ClientConfigurationAccessService,
)
from apps.documents.models import DocumentEditLock
from apps.documents.services import DocumentEditLockService


class ClientConfigurationHomeView(
    LoginRequiredMixin,
    TemplateView,
):
    """
    Affiche les environnements clients administrables
    par l'utilisateur connecté.
    """

    template_name = (
        "client_configuration/home.html"
    )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context["client_environments"] = (
            ClientConfigurationAccessService
            .get_manageable_client_environments(
                self.request.user
            )
        )

        return context


class ClientEnvironmentConfigurationMixin(
    LoginRequiredMixin,
):
    """
    Charge un environnement client uniquement lorsqu'il est
    administrable par l'utilisateur connecté.
    """

    client_environment_url_kwarg = (
        "client_environment_pk"
    )

    def get_client_environment(self) -> ClientEnvironment:
        if not hasattr(
            self,
            "_client_environment",
        ):
            self._client_environment = get_object_or_404(
                ClientConfigurationAccessService
                .get_manageable_client_environments(
                    self.request.user
                ),
                pk=self.kwargs[
                    self.client_environment_url_kwarg
                ],
            )

        return self._client_environment


class ClientEnvironmentMaintenanceMixin(
    ClientEnvironmentConfigurationMixin,
):
    """
    Fournit le périmètre documentaire sur lequel l'utilisateur
    peut exécuter des commandes de maintenance.
    """

    def get_maintainable_projects(self):
        if not hasattr(
            self,
            "_maintainable_projects",
        ):
            self._maintainable_projects = (
                ClientConfigurationAccessService
                .get_maintainable_projects(
                    self.request.user,
                    client_environment=(
                        self.get_client_environment()
                    ),
                )
            )

        return self._maintainable_projects

    def get_maintainable_edit_locks(self):
        return (
            DocumentEditLock.objects
            .filter(
                document__project__in=(
                    self.get_maintainable_projects()
                ),
            )
            .select_related(
                "document",
                "document__project",
                "user",
                "version",
            )
        )


class ClientEnvironmentCommandsView(
    ClientEnvironmentMaintenanceMixin,
    TemplateView,
):
    """
    Affiche les commandes de maintenance accessibles dans
    l'environnement client courant.
    """

    template_name = (
        "client_configuration/"
        "client_environment_commands.html"
    )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        client_environment = (
            self.get_client_environment()
        )
        now = timezone.now()

        edit_locks = list(
            self.get_maintainable_edit_locks()
            .order_by(
                "expires_at",
                "document__project__reference",
                "document__title",
            )
        )

        expired_lock_count = 0

        for edit_lock in edit_locks:
            edit_lock.is_expired = (
                edit_lock.expires_at <= now
            )

            if edit_lock.is_expired:
                expired_lock_count += 1

        context.update(
            {
                "client_environment": client_environment,
                "active_tab": "commands",
                "tabs": (
                    {
                        "label": "Commandes",
                        "url": reverse(
                            "client_configuration:"
                            "client-environment",
                            kwargs={
                                "client_environment_pk": (
                                    client_environment.pk
                                ),
                            },
                        ),
                        "is_active": True,
                    },
                    {
                        "label": "Arborescences",
                        "url": reverse(
                            "client_configuration:"
                            "document-folder-template-list",
                            kwargs={
                                "client_environment_pk": (
                                    client_environment.pk
                                ),
                            },
                        ),
                        "is_active": False,
                    },
                    {
                        "label": "DOE",
                        "url": "",
                        "is_active": False,
                        "disabled": True,
                    },
                ),
                "edit_locks": edit_locks,
                "expired_lock_count": expired_lock_count,
            }
        )

        return context


class DocumentEditLockExpiredCleanupView(
    ClientEnvironmentMaintenanceMixin,
    View,
):
    """
    Supprime les verrous expirés dans le périmètre autorisé.
    """

    def post(self, request, *args, **kwargs):
        deleted_count = (
            DocumentEditLockService.release_expired(
                locks=self.get_maintainable_edit_locks(),
                user=request.user,
            )
        )

        if deleted_count:
            messages.success(
                request,
                (
                    f"{deleted_count} verrou(s) expiré(s) "
                    "ont été supprimés."
                ),
            )
        else:
            messages.info(
                request,
                "Aucun verrou expiré à supprimer.",
            )

        return redirect(
            "client_configuration:client-environment",
            client_environment_pk=(
                self.get_client_environment().pk
            ),
        )


class DocumentEditLockForceReleaseView(
    ClientEnvironmentMaintenanceMixin,
    View,
):
    """
    Libère un verrou sélectionné dans le périmètre autorisé.
    """

    lock_url_kwarg = "lock_pk"

    def post(self, request, *args, **kwargs):
        edit_lock = get_object_or_404(
            self.get_maintainable_edit_locks(),
            pk=self.kwargs[
                self.lock_url_kwarg
            ],
        )

        released = (
            DocumentEditLockService.force_release(
                lock=edit_lock,
                user=request.user,
            )
        )

        if released:
            messages.success(
                request,
                (
                    "Le verrou d'édition a été "
                    "libéré."
                ),
            )
        else:
            messages.info(
                request,
                (
                    "Le verrou avait déjà été supprimé "
                    "ou remplacé."
                ),
            )

        return redirect(
            "client_configuration:client-environment",
            client_environment_pk=(
                self.get_client_environment().pk
            ),
        )
        

class DocumentFolderTemplateListView(
    ClientEnvironmentConfigurationMixin,
    TemplateView,
):
    """
    Liste les modèles documentaires d'un environnement client.
    """

    template_name = (
        "client_configuration/"
        "document_folder_template_list.html"
    )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        client_environment = (
            self.get_client_environment()
        )

        context.update(
            {
                "client_environment": client_environment,
                "document_folder_templates": (
                    DocumentFolderTemplate.objects
                    .filter(
                        client_environment=(
                            client_environment
                        ),
                    )
                    .order_by(
                        "name",
                    )
                ),
            }
        )

        return context


class DocumentFolderTemplateMixin(
    ClientEnvironmentConfigurationMixin,
):
    """
    Charge un modèle documentaire appartenant à l'environnement
    client administrable courant.
    """

    template_url_kwarg = "template_pk"

    def get_document_folder_template(
        self,
    ) -> DocumentFolderTemplate:
        if not hasattr(
            self,
            "_document_folder_template",
        ):
            self._document_folder_template = (
                get_object_or_404(
                    DocumentFolderTemplate.objects
                    .filter(
                        client_environment=(
                            self.get_client_environment()
                        ),
                    ),
                    pk=self.kwargs[
                        self.template_url_kwarg
                    ],
                )
            )

        return self._document_folder_template


class DocumentFolderTemplateCreateView(
    ClientEnvironmentConfigurationMixin,
    FormView,
):
    """
    Crée un modèle d'arborescence documentaire.
    """

    template_name = (
        "client_configuration/"
        "document_folder_template_form.html"
    )
    form_class = DocumentFolderTemplateForm

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()

        kwargs["client_environment"] = (
            self.get_client_environment()
        )

        return kwargs

    def form_valid(self, form):
        template = form.save()

        messages.success(
            self.request,
            (
                "Le modèle d'arborescence documentaire "
                "a été créé."
            ),
        )

        return redirect(
            "client_configuration:"
            "document-folder-template-folders",
            client_environment_pk=(
                template.client_environment_id
            ),
            template_pk=template.pk,
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context.update(
            {
                "client_environment": (
                    self.get_client_environment()
                ),
                "page_title": (
                    "Nouveau modèle d'arborescence"
                ),
                "submit_label": "Créer le modèle",
            }
        )

        return context


class DocumentFolderTemplateUpdateView(
    DocumentFolderTemplateMixin,
    FormView,
):
    """
    Modifie les informations générales d'un modèle
    d'arborescence documentaire.
    """

    template_name = (
        "client_configuration/"
        "document_folder_template_form.html"
    )
    form_class = DocumentFolderTemplateForm

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()

        kwargs.update(
            {
                "instance": (
                    self.get_document_folder_template()
                ),
                "client_environment": (
                    self.get_client_environment()
                ),
            }
        )

        return kwargs

    def form_valid(self, form):
        template = form.save()

        messages.success(
            self.request,
            (
                "Le modèle d'arborescence documentaire "
                "a été modifié."
            ),
        )

        return redirect(
            "client_configuration:"
            "document-folder-template-folders",
            client_environment_pk=(
                template.client_environment_id
            ),
            template_pk=template.pk,
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context.update(
            {
                "client_environment": (
                    self.get_client_environment()
                ),
                "document_folder_template": (
                    self.get_document_folder_template()
                ),
                "page_title": (
                    "Modifier le modèle d'arborescence"
                ),
                "submit_label": "Enregistrer",
            }
        )

        return context


class DocumentFolderTemplateFolderListView(
    DocumentFolderTemplateMixin,
    TemplateView,
):
    """
    Affiche l'arborescence et permet d'ajouter ou modifier
    un dossier depuis le même volet latéral.
    """

    template_name = (
        "client_configuration/"
        "document_folder_template_folder_list.html"
    )

    def get_context_data(self, **kwargs):
        folder_form = kwargs.pop(
            "folder_form",
            None,
        )
        selected_folder = kwargs.pop(
            "selected_folder",
            None,
        )

        context = super().get_context_data(**kwargs)

        template = self.get_document_folder_template()

        if selected_folder is None:
            selected_folder = self._get_selected_folder(
                folder_pk=self.request.GET.get(
                    "folder",
                    "",
                ),
            )

        if folder_form is None:
            folder_form = DocumentFolderTemplateFolderForm(
                instance=selected_folder,
                template=template,
            )

        folders = list(
            DocumentFolderTemplateFolder.objects
            .filter(
                template=template,
            )
            .order_by(
                "parent_id",
                "sort_order",
                "name",
            )
        )

        context.update(
            {
                "client_environment": (
                    self.get_client_environment()
                ),
                "document_folder_template": template,
                "folder_rows": self._build_folder_rows(
                    folders=folders,
                ),
                "folder_form": folder_form,
                "selected_folder": selected_folder,
                "parent_options": (
                    self._build_parent_options(
                        form=folder_form,
                    )
                ),
            }
        )

        return context

    def post(self, request, *args, **kwargs):
        template = self.get_document_folder_template()

        selected_folder = self._get_selected_folder(
            folder_pk=request.POST.get(
                "folder_pk",
                "",
            ),
        )

        folder_form = DocumentFolderTemplateFolderForm(
            request.POST,
            instance=selected_folder,
            template=template,
        )

        if folder_form.is_valid():
            folder_form.save()

            messages.success(
                request,
                (
                    "Le dossier a été modifié."
                    if selected_folder is not None
                    else "Le dossier a été ajouté."
                ),
            )

            return redirect(
                "client_configuration:"
                "document-folder-template-folders",
                client_environment_pk=(
                    template.client_environment_id
                ),
                template_pk=template.pk,
            )

        return self.render_to_response(
            self.get_context_data(
                folder_form=folder_form,
                selected_folder=selected_folder,
            )
        )

    def _get_selected_folder(
        self,
        *,
        folder_pk: str,
    ) -> DocumentFolderTemplateFolder | None:
        folder_pk = (folder_pk or "").strip()

        if not folder_pk:
            return None

        return get_object_or_404(
            DocumentFolderTemplateFolder.objects
            .filter(
                template=(
                    self.get_document_folder_template()
                ),
            ),
            pk=folder_pk,
        )

    @staticmethod
    def _build_parent_options(
        *,
        form: DocumentFolderTemplateFolderForm,
    ) -> tuple[dict, ...]:
        """
        Prépare les options du sélecteur parent, avec l'option
        effectivement sélectionnée par le formulaire.
        """

        selected_value = str(
            form["parent"].value() or ""
        )

        return tuple(
            {
                "value": str(value or ""),
                "label": label,
                "selected": (
                    str(value or "")
                    == selected_value
                ),
            }
            for value, label in (
                form.fields["parent"].choices
            )
        )

    @staticmethod
    def _build_folder_rows(
        *,
        folders: list[DocumentFolderTemplateFolder],
    ) -> list[dict]:
        """
        Transforme les dossiers en liste affichable sous la forme
        d'une arborescence textuelle.
        """

        folders_by_parent = defaultdict(list)

        for folder in folders:
            folders_by_parent[
                folder.parent_id
            ].append(folder)

        rows = []

        def append_children(
            *,
            parent_id,
            prefix: str,
        ) -> None:
            children = folders_by_parent[parent_id]

            for index, folder in enumerate(children):
                is_last = index == len(children) - 1

                if parent_id is None:
                    tree_prefix = ""
                    child_prefix = ""
                else:
                    tree_prefix = (
                        prefix
                        + (
                            "└── "
                            if is_last
                            else "├── "
                        )
                    )
                    child_prefix = (
                        prefix
                        + (
                            "    "
                            if is_last
                            else "│   "
                        )
                    )

                rows.append(
                    {
                        "folder": folder,
                        "tree_prefix": tree_prefix,
                    }
                )

                append_children(
                    parent_id=folder.pk,
                    prefix=child_prefix,
                )

        append_children(
            parent_id=None,
            prefix="",
        )

        return rows
    
    
class DocumentFolderTemplateFolderFormMixin(
    DocumentFolderTemplateMixin,
):
    """
    Fonctions communes aux formulaires de dossiers
    d'un modèle d'arborescence.
    """

    form_class = DocumentFolderTemplateFolderForm
    template_name = (
        "client_configuration/"
        "document_folder_template_folder_form.html"
    )

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()

        kwargs["template"] = (
            self.get_document_folder_template()
        )

        return kwargs

    def get_success_url(self) -> str:
        template = self.get_document_folder_template()

        return reverse(
            "client_configuration:"
            "document-folder-template-folders",
            kwargs={
                "client_environment_pk": (
                    template.client_environment_id
                ),
                "template_pk": template.pk,
            },
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context.update(
            {
                "client_environment": (
                    self.get_client_environment()
                ),
                "document_folder_template": (
                    self.get_document_folder_template()
                ),
            }
        )

        return context


class DocumentFolderTemplateFolderCreateView(
    DocumentFolderTemplateFolderFormMixin,
    FormView,
):
    """
    Crée un dossier dans un modèle d'arborescence.
    """

    def form_valid(self, form):
        form.save()

        messages.success(
            self.request,
            "Le dossier a été ajouté au modèle.",
        )

        return redirect(
            self.get_success_url()
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context.update(
            {
                "page_title": "Ajouter un dossier",
                "submit_label": "Ajouter le dossier",
            }
        )

        return context


class DocumentFolderTemplateFolderUpdateView(
    DocumentFolderTemplateFolderFormMixin,
    FormView,
):
    """
    Modifie un dossier d'un modèle d'arborescence.
    """

    folder_url_kwarg = "folder_pk"

    def get_folder(self) -> DocumentFolderTemplateFolder:
        if not hasattr(
            self,
            "_folder",
        ):
            self._folder = get_object_or_404(
                DocumentFolderTemplateFolder.objects
                .filter(
                    template=(
                        self.get_document_folder_template()
                    ),
                ),
                pk=self.kwargs[
                    self.folder_url_kwarg
                ],
            )

        return self._folder

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()

        kwargs["instance"] = self.get_folder()

        return kwargs

    def form_valid(self, form):
        form.save()

        messages.success(
            self.request,
            "Le dossier a été modifié.",
        )

        return redirect(
            self.get_success_url()
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context.update(
            {
                "folder": self.get_folder(),
                "page_title": "Modifier le dossier",
                "submit_label": "Enregistrer",
            }
        )

        return context


class DocumentFolderTemplateFolderDeleteView(
    DocumentFolderTemplateMixin,
    View,
):
    """
    Supprime un dossier vide d'un modèle d'arborescence.
    """

    folder_url_kwarg = "folder_pk"

    def post(self, request, *args, **kwargs):
        template = self.get_document_folder_template()

        folder = get_object_or_404(
            DocumentFolderTemplateFolder.objects
            .filter(
                template=template,
            ),
            pk=self.kwargs[
                self.folder_url_kwarg
            ],
        )

        if folder.children.exists():
            messages.error(
                request,
                (
                    "Le dossier contient des sous-dossiers. "
                    "Supprimez-les ou déplacez-les auparavant."
                ),
            )
        else:
            folder.delete()

            messages.success(
                request,
                "Le dossier a été supprimé.",
            )

        return redirect(
            "client_configuration:"
            "document-folder-template-folders",
            client_environment_pk=(
                template.client_environment_id
            ),
            template_pk=template.pk,
        )
        