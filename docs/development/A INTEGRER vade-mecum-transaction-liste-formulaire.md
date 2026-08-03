

Vade-mecum — Ajouter une transaction Liste + Formulaire
1. Objectif

Ce document décrit la procédure standard pour ajouter une transaction métier dans Easy Projet comprenant :

une liste construite avec EPList ;
un formulaire de création et de modification construit avec EPForm ;
les routes Django associées ;
les vues ;
les contrôles ;
les tests.

Une transaction doit être construite à partir du dictionnaire métier. Elle ne doit pas redéfinir localement une information déjà décrite dans ce dictionnaire.

2. Principe général

Le flux de construction est le suivant :

Dictionnaire métier
        │
        ├── modèle Django
        │
        ├── définition EPList
        │
        └── définition EPForm
                │
                ▼
          vues Django
                │
                ▼
      intégration du framework
                │
                ▼
          templates génériques

Les responsabilités sont séparées :

Élément	Responsabilité
Dictionnaire	Décrit les données métier
Modèle Django	Assure la persistance
EPList	Décrit la présentation de la liste
EPForm	Décrit la composition du formulaire
Vues Django	Orchestrent les traitements
Templates	Assurent le rendu
URLs	Exposent les transactions
Tests	Vérifient le contrat et le comportement
3. Arborescence cible

Pour une application nommée companies :

apps/
└── companies/
    ├── migrations/
    ├── templates/
    │   └── companies/
    │       └── company_actions.html
    ├── __init__.py
    ├── admin.py
    ├── apps.py
    ├── columns.py
    ├── form_definition.py
    ├── forms.py
    ├── models.py
    ├── tests.py
    ├── urls.py
    └── views.py

Selon l'organisation future du projet, les tests pourront être répartis dans un répertoire dédié :

apps/
└── companies/
    └── tests/
        ├── test_forms.py
        ├── test_list.py
        ├── test_models.py
        ├── test_urls.py
        └── test_views.py
4. Étapes de réalisation
Étape 1 — Vérifier le dictionnaire métier

Avant toute implémentation, vérifier que l'entité et ses champs sont décrits dans le dictionnaire.

Chaque champ utilisé par la liste ou le formulaire doit être défini dans le schéma du dictionnaire.

Exemple conceptuel :

{
    "name": {
        "label": "Nom",
        "data_type": "string",
        "required": True,
        "max_length": 150,
        "visible": True,
        "width": "lg",
    },
    "email": {
        "label": "Adresse électronique",
        "data_type": "email",
        "required": True,
        "autocomplete": "email",
        "width": "md",
    },
}
Règle

Toute donnée déclarative consommée par le framework doit être définie dans le schéma du dictionnaire. Lorsqu'elle est facultative, le framework doit être capable de la restituer grâce à une valeur par défaut.

Les valeurs facultatives non renseignées sont obtenues depuis :

framework/defaults/
Étape 2 — Créer ou vérifier le modèle Django
Fichier à créer ou modifier
apps/<application>/models.py

Exemple :

from django.db import models


class Company(models.Model):
    name = models.CharField(
        max_length=150,
        verbose_name="Nom",
    )
    email = models.EmailField(
        max_length=254,
        verbose_name="Adresse électronique",
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name="Actif",
    )

    def __str__(self) -> str:
        return self.name

Le modèle doit respecter le dictionnaire :

type de donnée ;
longueur maximale ;
caractère obligatoire ;
unicité ;
valeur métier par défaut ;
relations ;
contraintes.
Contrôles
python manage.py check

Puis :

python manage.py makemigrations <application>

Vérifier la migration générée avant de l'appliquer :

python manage.py migrate
Étape 3 — Définir les colonnes EPList
Fichier à créer
apps/<application>/columns.py

Exemple :

from framework.list.column_definition import ColumnDefinition

from .dictionary import COMPANY_ENTITY_DEFINITION


COMPANY_COLUMNS = (
    ColumnDefinition(
        field=COMPANY_ENTITY_DEFINITION.fields["name"],
    ),
    ColumnDefinition(
        field=COMPANY_ENTITY_DEFINITION.fields["email"],
    ),
    ColumnDefinition(
        field=COMPANY_ENTITY_DEFINITION.fields["phone"],
    ),
    ColumnDefinition(
        field=COMPANY_ENTITY_DEFINITION.fields["city"],
    ),
    ColumnDefinition(
        field=COMPANY_ENTITY_DEFINITION.fields["is_active"],
    ),
)

L'API exacte d'accès aux champs doit suivre celle exposée par EntityDefinition.

Selon cette API, l'accès pourra être de la forme :

COMPANY_ENTITY_DEFINITION.fields["name"]

ou :

COMPANY_ENTITY_DEFINITION.get_field("name")
Surcharges autorisées

Une colonne peut surcharger une propriété de présentation lorsqu'une différence avec le champ métier est nécessaire :

ColumnDefinition(
    field=field,
    label="Société",
    width="lg",
    sortable=True,
    truncate=True,
)

Une surcharge ne doit pas dupliquer inutilement la valeur déjà fournie par le dictionnaire ou par les conventions du framework.

Étape 4 — Définir le formulaire EPForm
Fichier à créer
apps/<application>/form_definition.py

Exemple :

from framework.form.definition import FormDefinition
from framework.form.field import FieldDefinition
from framework.form.section import SectionDefinition


COMPANY_FORM_DEFINITION = FormDefinition(
    identifier="company",
    sections=(
        SectionDefinition(
            identifier="identity",
            label="Identification",
            fields=(
                FieldDefinition(name="name"),
                FieldDefinition(name="siret"),
                FieldDefinition(name="vat_number"),
                FieldDefinition(name="is_active"),
            ),
        ),
        SectionDefinition(
            identifier="contact",
            label="Coordonnées",
            fields=(
                FieldDefinition(name="email"),
                FieldDefinition(name="phone"),
            ),
        ),
        SectionDefinition(
            identifier="address",
            label="Adresse",
            fields=(
                FieldDefinition(name="address_1"),
                FieldDefinition(name="address_2"),
                FieldDefinition(name="address_3"),
                FieldDefinition(name="postal_code"),
                FieldDefinition(name="city"),
                FieldDefinition(name="country"),
            ),
        ),
    ),
)
Important

Le FieldDefinition d'EPForm :

framework/form/field.py

décrit l'utilisation d'un champ dans le formulaire.

Il ne doit pas être confondu avec le FieldDefinition du dictionnaire :

framework/dictionary/field.py

Ce dernier représente la définition métier complète issue du dictionnaire.

Étape 5 — Créer le formulaire Django
Fichier à créer ou modifier
apps/<application>/forms.py

Exemple :

from django import forms

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

Le formulaire Django assure notamment :

la liaison avec le modèle ;
la validation Django ;
la conversion des valeurs ;
la gestion des erreurs ;
la création des BoundField.

EPForm assure la composition et la présentation déclarative du formulaire.

Étape 6 — Créer les vues
Fichier à créer ou modifier
apps/<application>/views.py

La transaction comprend généralement trois vues :

liste
création
modification

Exemple conceptuel :

from django.shortcuts import get_object_or_404, redirect, render

from framework.form.form import EPForm

from .columns import COMPANY_COLUMNS
from .form_definition import COMPANY_FORM_DEFINITION
from .forms import CompanyForm
from .models import Company
Vue liste

La vue liste doit :

construire le queryset ;
appliquer les règles de visibilité ;
appliquer les filtres ;
appliquer le tri ;
appliquer la pagination ;
transmettre les colonnes et les lignes au moteur EPList.

Exemple simplifié :

def company_list(request):
    queryset = Company.objects.order_by("name")

    context = {
        "title": "Sociétés",
        "queryset": queryset,
        "columns": COMPANY_COLUMNS,
    }

    return render(
        request,
        "edf/list/list.html",
        context,
    )

Dans l'implémentation réelle, utiliser le renderer, le ViewModel et les services EPList existants plutôt que de reconstruire leur comportement dans la vue.

Vue création
def company_create(request):
    django_form = CompanyForm(
        request.POST or None,
    )

    if request.method == "POST" and django_form.is_valid():
        company = django_form.save()
        return redirect(
            "companies:update",
            pk=company.pk,
        )

    ep_form = EPForm(
        definition=COMPANY_FORM_DEFINITION,
        form=django_form,
    )

    return render(
        request,
        "edf/form/view.html",
        {
            "title": "Créer une société",
            "ep_form": ep_form,
        },
    )
Vue modification
def company_update(request, pk):
    company = get_object_or_404(
        Company,
        pk=pk,
    )

    django_form = CompanyForm(
        request.POST or None,
        instance=company,
    )

    if request.method == "POST" and django_form.is_valid():
        django_form.save()
        return redirect(
            "companies:update",
            pk=company.pk,
        )

    ep_form = EPForm(
        definition=COMPANY_FORM_DEFINITION,
        form=django_form,
    )

    return render(
        request,
        "edf/form/view.html",
        {
            "title": "Modifier une société",
            "ep_form": ep_form,
            "object": company,
        },
    )

Les signatures exactes doivent être adaptées aux classes actuellement exposées par EPList et EPForm.

Étape 7 — Déclarer les routes
Fichier à créer ou modifier
apps/<application>/urls.py

Exemple :

from django.urls import path

from .views import (
    company_create,
    company_list,
    company_update,
)


app_name = "companies"

urlpatterns = [
    path(
        "",
        company_list,
        name="list",
    ),
    path(
        "new/",
        company_create,
        name="create",
    ),
    path(
        "<uuid:pk>/edit/",
        company_update,
        name="update",
    ),
]
Vérifier l'inclusion globale

Dans :

config/urls.py

Exemple :

from django.urls import include, path


urlpatterns = [
    path(
        "companies/",
        include("apps.companies.urls"),
    ),
]
Étape 8 — Ajouter les actions propres à la transaction
Fichier à créer si nécessaire
apps/<application>/templates/<application>/<entity>_actions.html

Exemple :

<a href="{% url 'companies:create' %}">
    Nouvelle société
</a>

Ce template doit uniquement contenir les actions spécifiques à la transaction.

Le rendu général doit rester assuré par les templates génériques du Design System :

templates/edf/list/
templates/edf/form/
Règle

Une transaction métier ne doit pas recopier les templates génériques d'EPList ou d'EPForm.

Étape 9 — Ajouter la navigation

Modifier le composant de navigation concerné afin d'ajouter le lien vers la nouvelle liste.

Exemple conceptuel :

<a href="{% url 'companies:list' %}">
    Sociétés
</a>

Vérifier :

le libellé ;
l'icône ;
les droits d'accès ;
l'état actif ;
le positionnement dans le menu.
5. Tests à créer
5.1 Tests du modèle

Vérifier notamment :

création d'une instance valide ;
champs obligatoires ;
contraintes d'unicité ;
valeurs par défaut ;
représentation textuelle.
5.2 Tests du formulaire Django

Vérifier :

formulaire valide ;
formulaire invalide ;
champs obligatoires ;
erreurs de format ;
création ;
modification.
5.3 Tests de la définition EPList

Vérifier :

présence des colonnes attendues ;
ordre des colonnes ;
absence de doublon ;
propriétés de présentation ;
cohérence avec le dictionnaire.
5.4 Tests de la définition EPForm

Vérifier :

présence des sections ;
ordre des sections ;
présence des champs ;
absence de doublon ;
application des valeurs par défaut ;
surcharge explicite des propriétés.

Pour toute propriété facultative :

absence   → valeur par défaut
présence  → valeur déclarée
invalide  → erreur de validation
5.5 Tests des vues

Vérifier :

accès à la liste ;
accès au formulaire de création ;
accès au formulaire de modification ;
enregistrement valide ;
rejet des données invalides ;
redirection après sauvegarde ;
objet inexistant ;
contrôle des permissions.
5.6 Tests des URLs

Vérifier :

reverse("companies:list")
reverse("companies:create")
reverse(
    "companies:update",
    kwargs={"pk": company.pk},
)
6. Contrôles à exécuter
Contrôle Django
python manage.py check
Tests de l'application
python manage.py test apps.<application>

Exemple :

python manage.py test apps.companies
Tests du framework
python manage.py test framework
Tests complets
python manage.py test
Contrôle manuel

Vérifier dans l'application :

affichage de la liste ;
pagination ;
tri ;
création ;
affichage des erreurs ;
modification ;
retour à la liste ;
cohérence visuelle ;
navigation au clavier ;
contrôle des permissions.
7. Liste récapitulative des fichiers
Fichiers généralement ajoutés
apps/<application>/columns.py
apps/<application>/form_definition.py
apps/<application>/urls.py
apps/<application>/templates/<application>/<entity>_actions.html
Fichiers généralement modifiés
apps/<application>/models.py
apps/<application>/forms.py
apps/<application>/views.py
apps/<application>/tests.py
config/urls.py
Fichiers du framework à ne pas modifier pour une transaction standard
framework/defaults/
framework/dictionary/
framework/form/
framework/list/
framework/viewmodel/
framework/integrations/
templates/edf/

Une modification de ces fichiers indique normalement :

une évolution générale du framework ;
une nouvelle propriété déclarative ;
une nouvelle convention ;
un nouveau composant générique ;
ou la correction d'un défaut transversal.

Elle ne doit pas être réalisée uniquement pour satisfaire un cas métier local.

8. Critères de fin

La transaction est terminée lorsque :

le dictionnaire est complet ;
le modèle est cohérent avec le dictionnaire ;
les migrations sont appliquées ;
la liste s'affiche ;
le formulaire de création fonctionne ;
le formulaire de modification fonctionne ;
les validations sont affichées ;
les permissions sont appliquées ;
les tests de l'application passent ;
les tests du framework passent ;
le contrôle manuel est concluant ;
la documentation métier est mise à jour ;
une sauvegarde Git est réalisée.
9. Règles à retenir
Le dictionnaire est la source de vérité.
EPList et EPForm ne doivent pas réinventer les informations métier.
Les propriétés facultatives utilisent les conventions de framework/defaults.
Une surcharge locale doit répondre à un besoin explicite.
Une transaction métier ne doit pas modifier le framework sans nécessité transversale.
Les templates génériques ne doivent pas être recopiés dans les applications.
Les composants doivent être testés avant l'intégration fonctionnelle.
Le développement est terminé uniquement lorsque les tests automatiques et le contrôle manuel sont concluants.



------------------

Une seule localisation pour les templates

Éviter les doublons entre :

templates/...

et

apps/.../templates/...

Une transaction ne doit avoir qu'une seule implémentation.

2. Les composants du framework

Nous avons maintenant une vraie famille de composants :

framework
│
├── dictionary
├── list
├── form
├── button
└── defaults

Tous suivent exactement le même modèle :

Definition
        │
        ▼
Validator
        │
        ▼
EP<Component>
        │
        ▼
Intégration Django
        │
        ▼
Template