

# 12 — Conventions de modélisation

## 1. Objet du document

Ce document définit les conventions utilisées pour modéliser les entités métier d’Easy Projet.

Ces conventions ont pour objectifs :

- de maintenir une structure homogène entre les différents domaines fonctionnels ;
- de limiter les duplications ;
- de faciliter la compréhension du code ;
- de garantir la cohérence entre les dictionnaires métier, les modèles Django, les formulaires et les vues ;
- de simplifier les évolutions futures du framework.

Elles s’appliquent à l’ensemble des entités métier d’Easy Projet.

---

## 2. Principe général

Chaque entité métier est décrite à partir d’une source de référence unique : son dictionnaire métier.

Exemples :

```text
common/dictionaries/company.py
common/dictionaries/user.py
common/dictionaries/project.py
common/dictionaries/document.py

Le dictionnaire décrit la signification métier des champs.

Il ne décrit pas directement :

la présentation HTML ;
les classes CSS ;
les composants Tailwind ou Preline ;
les widgets Django ;
la structure physique des tables PostgreSQL.

Les couches techniques interprètent le dictionnaire sans y introduire de préoccupations de présentation.

3. Un dictionnaire unique par entité

Une entité ne doit posséder qu’un seul dictionnaire métier.

Exemple :

COMPANY_DICTIONARY = {
    ...
}

Les listes, formulaires, vues de détail, exports et autres composants doivent importer ce dictionnaire au lieu d’en créer une copie locale.

Il est interdit de dupliquer tout ou partie d’un dictionnaire dans :

un fichier de définition de liste ;
un formulaire ;
une vue ;
un template ;
un export ;
un test fonctionnel.

Cette règle garantit que les libellés, types, contraintes et propriétés métier restent cohérents dans toute l’application.

4. Identité des champs

Le nom d’un champ doit rester identique dans toutes les couches lorsque cela est techniquement possible.

Exemple :

Dictionnaire : first_name
Modèle       : first_name
Formulaire   : first_name
Template     : first_name
Liste        : first_name

Les traductions ou adaptations de noms doivent rester exceptionnelles et être documentées.

Les noms de champs sont écrits :

en anglais ;
en minuscules ;
en snake_case ;
sans abréviation ambiguë.

Exemples corrects :

first_name
preferred_name
postal_code
created_at

Exemples à éviter :

prenom
prefName
cp
creationDate
5. Ordre des champs

Dans le modèle Django, les champs doivent suivre autant que possible l’ordre du dictionnaire métier.

Les champs sont regroupés par blocs fonctionnels cohérents.

Exemple :

# Identity

# Contact information

# Company relationship

# Permissions

# Preferences

# Audit fields

Cette organisation facilite la comparaison entre :

le dictionnaire ;
le modèle ;
le formulaire ;
la documentation.
6. Identifiants

Les principales entités métier utilisent des UUID comme clés primaires.

Exemple :

id = models.UUIDField(
    primary_key=True,
    default=uuid.uuid4,
    editable=False,
)

Les UUID permettent notamment :

d’éviter les identifiants séquentiels exposés ;
de faciliter les échanges entre systèmes ;
de limiter les risques de collision lors d’imports ;
de préparer les architectures distribuées ;
de produire des clés de stockage opaques pour les documents.

Un UUID ne remplace toutefois pas un contrôle d’autorisation.

La connaissance d’un identifiant ne doit jamais suffire pour accéder à une ressource.

7. Relations entre entités

Une relation entre deux entités doit être représentée par une relation Django réelle.

Exemple correct :

company = models.ForeignKey(
    Company,
    on_delete=models.PROTECT,
    related_name="users",
)

Exemple à éviter :

company_id = models.UUIDField()

L’utilisation de ForeignKey, OneToOneField ou ManyToManyField permet de bénéficier :

de l’intégrité référentielle ;
des jointures ORM ;
des contraintes de suppression ;
des relations inverses ;
d’une meilleure lisibilité du modèle.

Dans le dictionnaire métier, une relation vers une entité est décrite par une référence explicite :

"company": {
    "label": "Société",
    "data_type": "uuid",
    "required": True,
    "reference": "company",
}

La propriété reference désigne l’entité métier cible.

8. Relations vers les catalogues

Les valeurs issues d’un catalogue sont stockées comme des relations vers CatalogValue.

Exemple conceptuel :

job = models.ForeignKey(
    CatalogValue,
    on_delete=models.PROTECT,
    related_name="+",
    blank=True,
    null=True,
)

Le dictionnaire précise le catalogue attendu :

"job": {
    "label": "Métier",
    "data_type": "uuid",
    "required": False,
    "catalog": "USER_JOB",
}

Une validation doit garantir que la valeur sélectionnée appartient bien au catalogue déclaré.

Par exemple, le champ job ne doit accepter qu’une valeur du catalogue :

USER_JOB

Les catalogues ne doivent pas être représentés par des chaînes libres dans les modèles métier.

9. Propriétés reference et catalog

Les propriétés reference et catalog sont mutuellement exclusives.

Un champ ne doit pas déclarer simultanément :

"reference": "company"

et :

"catalog": "USER_JOB"

La propriété reference est utilisée pour une relation vers une entité métier.

La propriété catalog est utilisée pour une relation vers une valeur de catalogue.

Ces propriétés ne doivent être utilisées que sur un champ dont le type métier est compatible avec un identifiant de référence, actuellement :

uuid
10. Types métier et types techniques

Le dictionnaire utilise des types métier indépendants de Django.

Exemples :

string
text
boolean
integer
decimal
date
datetime
email
phone
uuid
image

Le modèle Django traduit ensuite ces types en types techniques.

Exemples :

string   → models.CharField
text     → models.TextField
boolean  → models.BooleanField
date     → models.DateField
datetime → models.DateTimeField
email    → models.EmailField
image    → models.ImageField

Cette séparation permet au dictionnaire d’être utilisé par d’autres couches que Django :

exports ;
API ;
documentation ;
validation ;
génération de formulaires ;
outils d’administration.
11. Présentation et widgets

Le dictionnaire métier ne doit pas contenir de dépendance directe à une technologie de présentation.

Il ne doit donc pas déclarer des éléments tels que :

TextInput
Select
CheckboxInput
Tailwind
Preline
classe CSS
template HTML

Le composant de présentation déduit le comportement attendu à partir des propriétés métier.

Exemples :

catalog présent   → liste de valeurs du catalogue
reference présent → sélecteur d’entité
image             → dépôt et aperçu d’image
boolean           → contrôle booléen
text              → zone de texte

Une propriété de présentation ne doit être ajoutée au dictionnaire que lorsqu’un besoin concret ne peut pas être déduit du métier.

12. Champs obligatoires et facultatifs

Le dictionnaire utilise la propriété :

"required": True

ou :

"required": False

Cette propriété doit rester cohérente avec le modèle Django.

Exemple obligatoire :

first_name = models.CharField(
    max_length=100,
)

Exemple facultatif :

phone = models.CharField(
    max_length=20,
    blank=True,
)

Pour les relations facultatives :

job = models.ForeignKey(
    CatalogValue,
    on_delete=models.PROTECT,
    blank=True,
    null=True,
    related_name="+",
)

L’utilisation de null=True sur les champs textuels doit être évitée sauf justification particulière.

Pour les chaînes facultatives, la valeur vide est normalement représentée par une chaîne vide.

13. Unicité

Une contrainte d’unicité métier est déclarée dans le dictionnaire :

"unique": True

Elle doit également être appliquée au niveau du modèle et de la base de données.

Exemple :

email = models.EmailField(
    max_length=254,
    unique=True,
)

La validation applicative améliore le retour utilisateur, mais elle ne remplace pas la contrainte en base.

14. Valeurs générées

Les champs produits automatiquement par l’application sont déclarés avec :

"generated": True

Exemples :

id
initials
created_at
updated_at

Un champ généré ne doit normalement pas être demandé directement à l’utilisateur dans un formulaire standard.

Une modification manuelle peut être autorisée uniquement lorsqu’elle correspond à un besoin métier explicite.

15. Normalisation des données

Les données doivent être normalisées avant leur enregistrement lorsque cela évite des incohérences.

Exemples :

suppression des espaces inutiles ;
normalisation des adresses électroniques ;
passage en majuscules d’un numéro de TVA ;
suppression des espaces dans un SIRET ;
calcul des initiales ;
normalisation des numéros de téléphone lorsque la règle est définie.

La normalisation doit être placée dans une couche adaptée :

méthode du modèle ;
formulaire ;
validateur métier ;
service métier.

Une même règle ne doit pas être recopiée dans plusieurs couches sans nécessité.

Les contraintes critiques doivent rester protégées par le modèle ou la base de données.

16. Gestion des suppressions

Le comportement on_delete doit être choisi en fonction de la règle métier.

Valeurs couramment utilisées :

PROTECT

À utiliser lorsqu’une suppression rendrait les données existantes incohérentes.

Exemple :

company = models.ForeignKey(
    Company,
    on_delete=models.PROTECT,
)
CASCADE

À utiliser lorsque l’objet dépend entièrement de son parent et n’a aucun sens sans lui.

SET_NULL

À utiliser uniquement lorsqu’une relation peut légitimement disparaître sans supprimer l’objet.

Le choix de on_delete doit être intentionnel. Il ne doit pas être utilisé par défaut sans analyse du besoin métier.

Pour les principales entités, l’inactivation fonctionnelle est généralement préférée à la suppression physique.

17. Activation et archivage

Les entités durables utilisent généralement un champ :

is_active = models.BooleanField(default=True)

L’inactivation permet de préserver :

l’historique ;
les références existantes ;
les journaux d’activité ;
les documents liés ;
les affectations passées.

Une entité inactive ne doit plus être proposée pour de nouvelles affectations, mais elle reste consultable lorsque cela est nécessaire à l’historique.

Le champ is_active ne constitue pas automatiquement une suppression logique complète.

Une stratégie d’archivage ou de suppression logique plus avancée ne doit être introduite que lorsqu’un besoin concret le justifie.

18. Traçabilité

Les principales entités possèdent au minimum :

created_at
updated_at

Exemple :

created_at = models.DateTimeField(auto_now_add=True)
updated_at = models.DateTimeField(auto_now=True)

Les champs created_by et updated_by peuvent être ajoutés lorsque leur gestion est prise en charge de manière homogène par le framework.

La traçabilité ne doit pas être implémentée différemment dans chaque application métier.

Les besoins plus complets de journalisation relèvent du service transversal d’audit.

19. Modèle utilisateur

Le modèle utilisateur d’Easy Projet utilise l’adresse électronique comme identifiant de connexion.

Il n’utilise pas de champ username.

Le modèle doit s’appuyer sur les mécanismes standards de Django :

AbstractBaseUser
PermissionsMixin

Il dispose d’un manager dédié chargé notamment de :

créer un utilisateur ;
créer un superutilisateur ;
normaliser l’adresse électronique ;
vérifier les propriétés nécessaires à l’administration Django.

Les rôles dépendant d’un contexte ne doivent pas être placés directement sur l’utilisateur.

Exemples :

rôle sur un projet
rôle dans une équipe
profil de coût sur un projet

Ces informations appartiennent aux entités d’affectation correspondantes.

20. Organisation des modèles

Une application simple peut commencer avec un fichier :

apps/<domain>/models.py

Lorsque le nombre de modèles ou la complexité augmente, un package models peut être utilisé :

apps/users/
    models/
        __init__.py
        user.py
        managers.py
        querysets.py

La création de plusieurs fichiers ne doit pas être anticipée sans besoin réel.

Le découpage est justifié lorsque :

plusieurs modèles existent ;
un manager possède une logique significative ;
les fichiers deviennent difficiles à lire ;
des composants ont une responsabilité clairement distincte.

L’objectif est la lisibilité, pas la multiplication systématique des fichiers.

21. Managers et QuerySets

Un manager personnalisé doit être créé lorsqu’il apporte une responsabilité réelle.

Pour le modèle utilisateur, un manager est nécessaire pour gérer l’authentification par adresse électronique.

Pour les autres modèles, les managers ou QuerySets personnalisés ne doivent être introduits que pour centraliser des requêtes récurrentes.

Exemple :

Company.objects.active()

Une méthode utilisée une seule fois ne justifie pas nécessairement un QuerySet personnalisé.

22. Contraintes de base de données

Les règles structurelles importantes doivent être protégées par la base de données lorsque cela est possible.

Exemples :

unicité d’une adresse électronique ;
unicité d’un code métier ;
interdiction de certaines combinaisons ;
cohérence entre dates ;
index sur les champs fréquemment recherchés.

Les validations Python améliorent l’expérience utilisateur, mais elles ne suffisent pas à protéger l’intégrité des données contre :

les imports ;
les scripts ;
les traitements asynchrones ;
les accès concurrents ;
les erreurs de programmation.
23. Index

Un index doit répondre à un besoin de recherche, de tri ou de jointure identifié.

Les index sont généralement pertinents sur :

les clés étrangères ;
les champs utilisés dans les filtres fréquents ;
les champs utilisés pour les recherches ;
certaines combinaisons propres à l’isolation par environnement.

Les index inutiles doivent être évités, car ils augmentent :

l’espace de stockage ;
le coût des insertions ;
le coût des mises à jour ;
la complexité des migrations.

L’optimisation doit être fondée sur les usages réels et, à terme, sur les mesures de performance.

24. Isolation par environnement client

Toute entité appartenant à un client doit être rattachée directement ou indirectement à un ClientEnvironment.

L’isolation ne doit pas reposer uniquement sur les vues ou les formulaires.

Elle doit être appliquée de manière cohérente dans :

les requêtes ;
les services métier ;
les contrôles d’autorisation ;
les imports et exports ;
les accès aux documents ;
les tâches asynchrones.

Un identifiant transmis par l’utilisateur ne doit jamais être utilisé sans vérifier que l’objet appartient à son environnement autorisé.

25. Modèles métier et périmètre fonctionnel

Les modèles doivent rester centrés sur la gestion de projet.

Easy Projet n’a pas vocation à reproduire :

un logiciel de ressources humaines ;
un logiciel de paie ;
un logiciel de comptabilité générale ;
un ERP complet.

Les informations stockées sur une entité doivent répondre à un besoin direct de gestion de projet.

Lorsqu’une information relève d’un autre métier, Easy Projet doit privilégier, si nécessaire :

un import ;
un export ;
une API ;
un connecteur.
26. Migrations

Toute modification de modèle doit être suivie de la création et de l’examen de la migration correspondante.

Commandes habituelles :

python manage.py makemigrations
python manage.py migrate
python manage.py check

Une migration doit être relue avant son application, notamment lorsqu’elle :

supprime un champ ;
modifie une relation ;
ajoute une contrainte ;
transforme des données ;
modifie une clé primaire ;
rend obligatoire un champ auparavant facultatif.

Les migrations constituent l’historique de la structure de la base et ne doivent pas être modifiées arbitrairement après leur diffusion.

27. Tests

Chaque modèle doit être couvert au minimum sur les règles métier significatives.

Exemples :

création avec les données minimales ;
refus d’une valeur invalide ;
normalisation d’un champ ;
contrainte d’unicité ;
valeur par défaut ;
calcul d’un champ généré ;
relation vers un catalogue valide ;
refus d’une valeur provenant d’un mauvais catalogue ;
comportement d’inactivation ;
représentation textuelle.

Les tests doivent vérifier le comportement attendu, pas uniquement l’existence des champs.

28. Règle de simplicité

Une abstraction ne doit être créée que lorsqu’elle répond à un besoin concret déjà identifié.

Il faut éviter :

les modèles génériques trop abstraits ;
les mixins créés pour un seul champ ;
les services sans logique réelle ;
les managers pour une requête unique ;
les propriétés de dictionnaire inutilisées ;
les architectures prévues pour des scénarios hypothétiques.

La règle retenue est :

Commencer par une implémentation simple et cohérente, puis généraliser lorsqu’au moins plusieurs besoins réels partagent le même comportement.

29. Synthèse

Les conventions principales sont les suivantes :

Une entité possède un dictionnaire métier unique.
Les noms de champs restent cohérents entre les couches.
Les modèles suivent l’organisation du dictionnaire.
Les entités principales utilisent des UUID.
Les relations utilisent les champs relationnels Django.
Les catalogues sont référencés par CatalogValue.
Le dictionnaire décrit le métier, pas la présentation.
Les contraintes importantes sont également protégées en base.
L’inactivation est préférée à la suppression des entités durables.
L’isolation par environnement client est systématique.
Les modèles restent dans le périmètre de la gestion de projet.
Toute généralisation doit répondre à un besoin concret.

Ce document peut être considéré comme validé pour la version actuelle du socle. La prochaine étape est la cré