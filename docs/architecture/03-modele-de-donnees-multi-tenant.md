

# Modèle de données multi-tenant

## 1. Objet du document

Ce document décrit l’implémentation technique de l’architecture multi-client d’Easy Projet.

Il traduit les règles fonctionnelles définies dans :

```text
08-environnement-client-et-isolation-des-donnees.md
```

Il décrit notamment :

* les entités principales ;
* leurs responsabilités ;
* leurs relations ;
* les cardinalités ;
* les contraintes d’intégrité ;
* le rattachement des données aux environnements ;
* les mécanismes de filtrage ;
* les règles de requêtage ;
* les contrôles d’accès ;
* les conséquences sur le framework générique ;
* les tests d’isolation.

Ce document décrit le **COMMENT**.

---

## 2. Principe technique fondamental

L’environnement client est représenté par une entité et une table dédiées.

Le couple société–licence provoque sa création, mais ne remplace pas cette entité.

```text
Company contractante
        +
Première License
        ↓
ClientEnvironment
```

L’identifiant de `ClientEnvironment` constitue la clé stable d’isolation des données métier.

Toute donnée métier doit être rattachée :

* directement à un environnement ;
* ou indirectement par une relation dont l’intégrité garantit l’appartenance à cet environnement.

---

## 3. Entités principales

Le modèle repose sur les entités structurantes suivantes :

```text
Company
ClientEnvironment
License
Operator
EnvironmentCompany
EnvironmentMembership
Project
ProjectMembership
```

Les noms définitifs pourront être adaptés aux conventions du projet, mais leurs responsabilités doivent rester distinctes.

---

## 4. Company

### 4.1 Responsabilité

`Company` représente l’identité globale, neutre et juridique d’une société.

Elle appartient au niveau plateforme.

Elle ne contient pas de données propres à un client.

### 4.2 Données indicatives

```text
Company
- id
- legal_name
- trading_name éventuel
- legal_identifier
- secondary_legal_identifier éventuel
- legal_form
- registered_address
- postal_code
- city
- country
- official_status
- created_at
- updated_at
```

### 4.3 Contraintes

* L’identifiant principal est stable.
* L’identifiant légal doit être unique lorsqu’il est renseigné et fiable.
* Les doublons doivent être évités.
* Les données confidentielles ou relationnelles sont interdites dans cette entité.
* La suppression physique doit être fortement limitée.

### 4.4 Société contractante

Une société est contractante lorsqu’elle est associée à un `ClientEnvironment`.

La notion de société contractante ne nécessite pas nécessairement un booléen global dans `Company`.

Elle peut être déduite de l’existence de la relation avec `ClientEnvironment`.

---

## 5. ClientEnvironment

### 5.1 Responsabilité

`ClientEnvironment` représente l’espace privé d’un client.

Il constitue :

* une entité métier ;
* une table physique ;
* une frontière de sécurité ;
* le point de rattachement des licences ;
* le contexte d’appartenance des données métier.

### 5.2 Données indicatives

```text
ClientEnvironment
- id
- contracting_company_id
- code
- name
- status
- created_at
- activated_at
- suspended_at
- archived_at
- closed_at
- created_by_id
- updated_at
```

### 5.3 Contraintes

```text
UNIQUE(contracting_company_id)
UNIQUE(code)
```

Une société contractante possède au maximum un environnement.

La suppression physique d’un environnement est interdite en exploitation normale.

### 5.4 Cycle de vie

Le statut peut être représenté par un catalogue ou une énumération contrôlée.

Exemples :

```text
PREPARATION
ACTIVE
SUSPENDED
NO_ACTIVE_LICENSE
ARCHIVED
CLOSED
```

Le statut d’un environnement ne doit pas être déduit uniquement de l’état de ses licences.

---

## 6. License

### 6.1 Responsabilité

`License` représente un droit commercial accordé par AXCIO-DATA.

Elle appartient au niveau plateforme mais est rattachée à un environnement client.

### 6.2 Données indicatives

```text
License
- id
- environment_id
- license_number
- license_type
- starts_at
- expires_at
- status
- created_at
- created_by_id
- suspended_at
- renewed_from_id éventuel
```

### 6.3 Contraintes

* Une licence appartient à un seul environnement.
* Une licence ne peut pas changer d’environnement.
* Un environnement peut posséder plusieurs licences.
* L’échéance d’une licence ne supprime pas l’environnement.
* La suppression physique d’une licence utilisée doit être interdite.

### 6.4 Relation avec les projets

La règle commerciale actuelle doit être traduite explicitement.

Si le principe est :

```text
Un projet = une licence
```

alors la relation devra garantir :

* un projet est rattaché à une licence ;
* une licence projet n’autorise qu’un projet ;
* le projet et la licence appartiennent au même environnement.

Une contrainte d’unicité pourra être appliquée sur la relation projet–licence.

La cardinalité définitive devra être validée dans le domaine de gestion des licences.

---

## 7. Operator

### 7.1 Responsabilité

`Operator` représente l’identité globale d’une personne utilisant Easy Projet.

Il appartient au niveau plateforme.

Il est associé au mécanisme d’authentification Django.

### 7.2 Données indicatives

Selon la stratégie retenue, `Operator` peut être :

* le modèle utilisateur Django personnalisé ;
* ou une entité métier liée en un-à-un au modèle d’authentification.

Exemple conceptuel :

```text
Operator
- id
- email
- first_name
- last_name
- global_status
- is_active
- invitation_status
- invited_at
- activated_at
- last_login
- created_at
- updated_at
```

### 7.3 Contraintes

* L’adresse électronique de connexion doit être unique selon la politique d’authentification retenue.
* Un opérateur peut appartenir à plusieurs environnements.
* La désactivation globale bloque toute connexion.
* La désactivation locale ne modifie pas l’état global.
* Les historiques ne doivent pas être supprimés lors d’une désactivation.

---

## 8. EnvironmentCompany

### 8.1 Responsabilité

`EnvironmentCompany` représente la présence d’une société globale dans un environnement.

Elle contient les données locales propres à la relation entre le client et cette société.

### 8.2 Données indicatives

```text
EnvironmentCompany
- id
- environment_id
- company_id
- display_name
- relationship_type
- local_email
- local_phone
- local_address
- contact_information
- qualification_information
- internal_notes
- is_active
- starts_at
- ends_at
- created_at
- updated_at
```

### 8.3 Contraintes

```text
UNIQUE(environment_id, company_id)
```

Une société globale ne doit être présente qu’une fois dans un même environnement, sauf justification métier explicite.

`environment_id` est immuable après création.

Les données de `EnvironmentCompany` ne doivent jamais être utilisées dans un autre environnement.

### 8.4 Société contractante dans son propre environnement

La société contractante peut également posséder une ligne `EnvironmentCompany` dans son environnement.

Cette ligne représente ses données locales et opérationnelles.

Elle ne remplace pas la relation structurante :

```text
ClientEnvironment.contracting_company_id
```

---

## 9. EnvironmentMembership

### 9.1 Responsabilité

`EnvironmentMembership` représente la présence d’un opérateur dans un environnement.

Elle porte les droits et informations ayant une portée sur l’environnement.

### 9.2 Données indicatives

```text
EnvironmentMembership
- id
- environment_id
- operator_id
- environment_company_id éventuel
- environment_role
- is_active
- starts_at
- ends_at
- can_manage_environment_members
- can_manage_environment_companies
- created_at
- updated_at
```

### 9.3 Contraintes

```text
UNIQUE(environment_id, operator_id)
```

* Une appartenance concerne un seul environnement.
* Une appartenance peut être désactivée sans désactiver l’opérateur global.
* `environment_id` est immuable.
* La société de rattachement doit appartenir au même environnement.
* Les capacités d’administration doivent être explicites.

### 9.4 Rôles et capacités

Le rôle ne doit pas être le seul mécanisme de permission.

Des capacités peuvent compléter les rôles :

```text
can_manage_environment_members
can_manage_environment_companies
can_view_all_projects
can_create_projects
```

Cela permet à une petite structure de cumuler plusieurs responsabilités sans fusionner artificiellement les rôles.

---

## 10. Project

### 10.1 Responsabilité

`Project` représente un projet métier appartenant à un environnement.

### 10.2 Données indicatives

```text
Project
- id
- environment_id
- license_id éventuel
- code
- name
- description
- status
- starts_at
- ends_at
- created_at
- updated_at
```

### 10.3 Contraintes

* Un projet appartient à un seul environnement.
* `environment_id` est obligatoire.
* `environment_id` est immuable.
* Le code du projet doit être unique dans l’environnement.

```text
UNIQUE(environment_id, code)
```

* Si une licence est associée au projet, elle doit appartenir au même environnement.
* La suppression physique doit être limitée ou interdite dès qu’il existe des données liées.

---

## 11. ProjectMembership

### 11.1 Responsabilité

`ProjectMembership` représente l’affectation et le rôle d’un opérateur dans un projet.

### 11.2 Données indicatives

```text
ProjectMembership
- id
- project_id
- environment_membership_id
- project_role
- is_responsible
- is_active
- starts_at
- ends_at
- created_at
- updated_at
```

### 11.3 Contraintes

```text
UNIQUE(project_id, environment_membership_id)
```

L’environnement de l’appartenance doit être identique à celui du projet.

```text
project.environment_id
=
environment_membership.environment_id
```

Cette cohérence doit être vérifiée :

* dans le domaine ;
* dans les services ;
* dans les validations ;
* et, lorsque possible, par les contraintes de persistance.

### 11.4 Chef de projet responsable

Le chef de projet possède un accès en lecture-écriture lorsqu’il est nommément responsable du projet.

Cette responsabilité peut être portée par :

```text
project_role = PROJECT_MANAGER
is_responsible = true
```

ou par une relation dédiée si plusieurs responsables doivent être gérés.

### 11.5 Lecture des autres projets

Un chef de projet actif dans l’environnement peut lire les autres projets du même environnement.

Cette permission ne nécessite pas une affectation à chaque projet.

Elle est déduite :

* de son appartenance active à l’environnement ;
* de sa qualité de chef de projet ;
* de la présence du projet dans le même environnement.

L’écriture reste conditionnée à sa responsabilité explicite sur le projet.

---

## 12. Données directement rattachées à l’environnement

Les entités communes à plusieurs projets doivent porter directement `environment_id`.

Exemples :

```text
EnvironmentCompany
EnvironmentMembership
EnvironmentSetting
EnvironmentTemplate
EnvironmentDocumentModel
EnvironmentSequence
```

Cette liste n’est pas exhaustive.

---

## 13. Données rattachées au projet

Les entités strictement propres à un projet peuvent être rattachées indirectement à l’environnement par le projet.

Exemples :

```text
Task
WorkPackage
Meeting
Risk
ProjectDocument
FinancialLot
FinancialItem
ProjectReport
TimeEntry
```

Exemple :

```text
Task
- id
- project_id
- ...
```

L’environnement est alors déterminé par :

```text
task.project.environment_id
```

### 13.1 Rattachement direct redondant

Dans certains cas, une entité projet peut également porter `environment_id` pour :

* optimiser les recherches ;
* simplifier les politiques de sécurité ;
* faciliter le partitionnement ;
* renforcer certaines contraintes.

Cette duplication ne doit être utilisée que si elle est contrôlée.

La cohérence suivante devient obligatoire :

```text
entity.environment_id
=
entity.project.environment_id
```

Aucune valeur divergente ne peut être acceptée.

---

## 14. Immutabilité de l’environnement

L’environnement d’une donnée métier est fixé lors de sa création.

Il est interdit de modifier directement :

```text
environment_id
```

après création.

Cette règle doit être appliquée à plusieurs niveaux :

* modèle de domaine ;
* formulaire ;
* service applicatif ;
* API ;
* import ;
* interface d’administration ;
* tests.

Un changement d’environnement doit être réalisé par une fonction explicite de copie.

---

## 15. Filtrage des requêtes

### 15.1 Règle générale

Toute requête portant sur une donnée métier doit intégrer l’environnement courant.

Exemple interdit :

```python
Project.objects.get(pk=project_id)
```

Exemple acceptable :

```python
Project.objects.get(
    pk=project_id,
    environment=current_environment,
)
```

Exemple recommandé :

```python
Project.objects.for_environment(
    current_environment
).get(pk=project_id)
```

### 15.2 Interdiction du filtrage a posteriori

Il est interdit de récupérer d’abord une donnée puis de vérifier ensuite si elle appartient à l’environnement.

Exemple interdit :

```python
project = Project.objects.get(pk=project_id)

if project.environment_id != current_environment.id:
    raise PermissionDenied
```

La donnée d’un autre environnement ne doit pas être chargée dans le flux métier courant.

Le filtrage doit être effectué dans la requête elle-même.

---

## 16. Managers et QuerySets

Les modèles multi-tenant doivent exposer des méthodes explicites.

Exemple conceptuel :

```python
class EnvironmentQuerySet(models.QuerySet):
    def for_environment(self, environment):
        return self.filter(environment=environment)
```

Pour une donnée rattachée au projet :

```python
class ProjectScopedQuerySet(models.QuerySet):
    def for_environment(self, environment):
        return self.filter(project__environment=environment)
```

Des méthodes complémentaires peuvent être définies :

```text
for_environment(environment)
visible_to(operator, environment)
editable_by(operator, environment)
for_project(project)
active()
```

Les méthodes doivent éviter la duplication des règles de sécurité dans les vues.

---

## 17. Contexte courant

Le système doit disposer d’un contexte explicite contenant au minimum :

```text
CurrentContext
- operator
- environment
- project éventuel
- environment_membership
- project_membership éventuel
- permissions calculées
```

Le contexte ne doit jamais être construit à partir d’un identifiant d’environnement fourni librement par le navigateur sans validation.

Il doit être résolu à partir :

* de l’utilisateur authentifié ;
* de ses appartenances actives ;
* du projet demandé ;
* des relations autorisées.

---

## 18. Résolution du projet courant

Lorsqu’un utilisateur sélectionne un projet :

1. le système recherche le projet dans les projets qu’il est autorisé à consulter ;
2. le système détermine l’environnement du projet ;
3. il vérifie l’appartenance de l’utilisateur à cet environnement ;
4. il détermine son rôle ;
5. il calcule les permissions applicables ;
6. il construit le contexte courant.

Le client ne doit pas pouvoir imposer indépendamment :

```text
environment_id
project_id
```

Le contexte d’environnement doit être déduit du projet autorisé.

---

## 19. Matrice d’accès aux projets

### 19.1 Administrateur client

```text
Environnement courant
└── tous les projets
    └── droits selon ses capacités
```

### 19.2 Chef de projet responsable

```text
Projet dont il est responsable
└── lecture et écriture
```

### 19.3 Chef de projet non responsable

```text
Autre projet du même environnement
└── lecture seule
```

### 19.4 Opérateur de projet

```text
Projet auquel il est affecté
└── droits définis par son rôle
```

### 19.5 Utilisateur d’un autre environnement

```text
Projet
└── aucun accès
```

---

## 20. Services applicatifs

Les actions métier sensibles doivent être encapsulées dans des services.

Exemples :

```text
CreateClientEnvironment
AttachLicenseToEnvironment
AddCompanyToEnvironment
AddOperatorToEnvironment
AssignOperatorToProject
DeactivateEnvironmentMembership
CopyProjectDataBetweenEnvironments
SendDocumentOutsideEnvironment
```

Les services doivent :

* recevoir un contexte autorisé ;
* vérifier l’environnement ;
* appliquer les règles métier ;
* exécuter l’action dans une transaction ;
* journaliser les opérations sensibles.

---

## 21. Création de l’environnement

La création de l’environnement doit être réalisée par un service transactionnel.

Exemple conceptuel :

```text
1. Rechercher ou créer la Company contractante
2. Vérifier qu’elle ne possède pas déjà un environnement
3. Créer la License
4. Créer le ClientEnvironment
5. Rattacher la License à l’environnement
6. Créer la présence locale de la société contractante
7. Créer les paramètres initiaux
8. Journaliser l’opération
```

L’ordre exact peut être adapté pour satisfaire les contraintes transactionnelles.

L’ensemble de l’opération doit réussir ou échouer intégralement.

---

## 22. Copie entre environnements

Une copie entre environnements ne doit jamais modifier l’environnement de la donnée source.

Le service de copie doit :

* vérifier les droits dans l’environnement source ;
* vérifier les droits dans l’environnement cible ;
* créer une nouvelle donnée ;
* attribuer un nouvel identifiant ;
* sélectionner explicitement les champs copiables ;
* exclure les données confidentielles non transférables ;
* recréer ou mapper les dépendances autorisées ;
* journaliser la source et la destination.

La copie ne doit jamais être une simple duplication brute de lignes SQL.

---

## 23. Diffusion externe d’un document

La diffusion externe doit être représentée comme une action métier.

Exemple d’entité de journalisation :

```text
DocumentDispatch
- id
- environment_id
- project_id
- document_id
- document_version_id
- sent_by_id
- recipient
- dispatch_type
- sent_at
- status
```

Les types peuvent inclure :

```text
EMAIL_ATTACHMENT
DOWNLOAD
EXPORT
EXTERNAL_SHARE
```

La copie diffusée ne donne aucun accès à l’environnement.

---

## 24. Journalisation

Les opérations suivantes doivent être journalisées :

* création d’un environnement ;
* association d’une licence ;
* activation ou suspension ;
* ajout d’une société à un environnement ;
* ajout d’un opérateur ;
* désactivation locale ;
* désactivation globale ;
* affectation à un projet ;
* retrait d’un projet ;
* copie entre environnements ;
* diffusion externe ;
* modification de droits ;
* tentative d’accès refusée significative.

La journalisation doit inclure, selon le cas :

* l’environnement ;
* le projet ;
* l’opérateur ;
* l’action ;
* la date ;
* la cible ;
* le résultat ;
* la source de l’opération.

---

## 25. Conséquences sur EPList

`EPList` ne doit jamais exécuter une liste métier sans contexte d’environnement.

Le contexte doit être injecté avant l’exécution de la requête.

Exemple conceptuel :

```python
queryset = definition.get_queryset(
    context=current_context,
)
```

Le framework doit permettre de distinguer :

* les entités globales ;
* les entités d’environnement ;
* les entités projet.

Une définition d’entité pourrait porter une portée :

```text
scope = GLOBAL
scope = ENVIRONMENT
scope = PROJECT
```

Pour une entité `ENVIRONMENT`, l’absence de contexte doit provoquer une erreur.

---

## 26. Conséquences sur EPDetail

`EPDetail` doit récupérer l’objet à partir d’une requête déjà limitée à l’environnement.

Exemple :

```python
queryset = Project.objects.for_environment(
    current_context.environment
)

project = get_object_or_404(queryset, pk=pk)
```

Une recherche globale suivie d’un contrôle est interdite.

---

## 27. Conséquences sur EPForm

`EPForm` doit :

* injecter automatiquement l’environnement à la création ;
* empêcher sa modification ;
* limiter les listes de choix à l’environnement courant ;
* valider les relations entre objets ;
* refuser toute référence à une donnée extérieure.

Exemple :

Un champ sélectionnant une société intervenante ne doit proposer que les `EnvironmentCompany` du même environnement.

---

## 28. Conséquences sur les imports

Tout import doit être exécuté dans un environnement explicite.

L’environnement ne doit pas être fourni ligne par ligne dans un fichier importé par un utilisateur standard.

Le contexte d’import détermine l’environnement cible.

Les références contenues dans le fichier doivent être résolues uniquement dans cet environnement.

---

## 29. Conséquences sur les exports

Tout export doit être construit à partir d’une requête déjà filtrée.

Le nom du fichier, les métadonnées ou le contenu peuvent indiquer :

* l’environnement ;
* le projet ;
* la date ;
* l’opérateur ;
* le périmètre exporté.

Les exports sensibles doivent être journalisés.

---

## 30. Conséquences sur l’administration Django

L’administration Django ne doit pas devenir un moyen de contourner l’isolation.

Deux approches sont possibles :

* réserver l’administration globale aux seuls administrateurs système AXCIO-DATA ;
* créer des interfaces métier spécifiques pour les administrateurs clients.

Les utilisateurs clients ne doivent pas utiliser une administration globale non filtrée.

Les champs `environment` doivent être :

* préremplis ;
* limités ;
* protégés ;
* ou non modifiables selon le contexte.

---

## 31. Contraintes de base de données

Les contraintes suivantes sont recommandées :

```text
ClientEnvironment
UNIQUE(contracting_company_id)

EnvironmentCompany
UNIQUE(environment_id, company_id)

EnvironmentMembership
UNIQUE(environment_id, operator_id)

Project
UNIQUE(environment_id, code)

ProjectMembership
UNIQUE(project_id, environment_membership_id)
```

Des index doivent être créés sur :

```text
environment_id
project_id
operator_id
company_id
status
is_active
```

Les index composites doivent suivre les requêtes réelles.

Exemples :

```text
(environment_id, status)
(environment_id, is_active)
(environment_id, code)
(project_id, is_active)
(operator_id, is_active)
```

---

## 32. Intégrité inter-environnement

Les relations suivantes doivent toujours rester dans un même environnement :

```text
Project ↔ License
ProjectMembership ↔ Project
ProjectMembership ↔ EnvironmentMembership
EnvironmentMembership ↔ EnvironmentCompany
Task ↔ Project
Document ↔ Project
Meeting ↔ Project
FinancialItem ↔ Project ou FinancialLot
```

Django ne permet pas toujours d’exprimer toutes ces contraintes directement par une clé étrangère simple.

Elles doivent alors être garanties par :

* les services ;
* les validateurs ;
* les contraintes personnalisées ;
* les tests ;
* éventuellement des déclencheurs de base de données si cela devient nécessaire.

---

## 33. Suppression logique

Les entités structurantes doivent privilégier la désactivation ou l’archivage.

Sont notamment concernées :

* `Company` ;
* `ClientEnvironment` ;
* `License` ;
* `Operator` ;
* `EnvironmentCompany` ;
* `EnvironmentMembership` ;
* `Project` ;
* `ProjectMembership`.

La suppression physique doit être limitée :

* aux erreurs de création sans dépendance ;
* aux données de test ;
* aux opérations techniques contrôlées.

Les historiques doivent rester exploitables.

---

## 34. Tests obligatoires d’isolation

Chaque fonctionnalité métier doit inclure des tests multi-environnements.

### 34.1 Tests de liste

* un utilisateur de A ne voit aucune donnée de B ;
* un chef de projet de A voit les projets autorisés de A ;
* aucun filtre transmis par le navigateur ne permet d’obtenir B.

### 34.2 Tests de détail

* l’identifiant d’une donnée de B retourne une absence de ressource ou un refus ;
* la donnée de B n’est jamais chargée par une requête globale.

### 34.3 Tests de formulaire

* les listes de choix ne contiennent que des objets de l’environnement courant ;
* une référence forgée vers B est refusée ;
* l’environnement ne peut pas être modifié.

### 34.4 Tests d’écriture

* une création utilise l’environnement courant ;
* une modification ne change pas l’environnement ;
* une relation inter-environnement est refusée.

### 34.5 Tests de rôle

* un chef de projet modifie ses propres projets ;
* il consulte les autres projets de l’environnement ;
* il ne modifie pas les projets dont il n’est pas responsable ;
* il n’accède à aucun projet d’un autre environnement.

### 34.6 Tests d’export et de diffusion

* seuls les documents autorisés sont exportés ;
* l’action est journalisée ;
* aucune relation d’accès permanent n’est créée.

---

## 35. Tests de non-régression

Toute correction relative à une fuite de données doit ajouter un test de non-régression.

Les tests d’isolation sont considérés comme des tests de sécurité.

Ils doivent être exécutés :

* localement ;
* dans l’intégration continue ;
* avant toute mise en production.

---

## 36. Revue de code

Toute revue de code portant sur une donnée métier doit vérifier :

1. comment l’environnement est déterminé ;
2. où le filtrage est appliqué ;
3. si l’objet peut être obtenu par un identifiant forgé ;
4. si les relations sont limitées au même environnement ;
5. si les écritures conservent l’environnement ;
6. si les tests couvrent deux environnements distincts.

Une fonctionnalité sans test d’isolation ne doit pas être considérée comme terminée.

---

## 37. Règles techniques invariantes

1. `ClientEnvironment` est une table dédiée.
2. Son identifiant est la clé stable d’isolation.
3. Toute donnée métier possède un environnement direct ou indirect.
4. L’environnement est obligatoire.
5. L’environnement est immuable après création.
6. Toute requête métier est filtrée avant chargement des données.
7. Aucun contrôle a posteriori ne remplace le filtrage en base.
8. Les relations inter-environnements sont interdites.
9. Les rôles sont évalués après le contrôle de l’environnement.
10. Le projet détermine automatiquement l’environnement courant.
11. Le client ne peut pas imposer librement un environnement.
12. Les managers et services encapsulent les règles de filtrage.
13. Les composants génériques doivent recevoir un contexte d’environnement.
14. Les formulaires limitent toutes les relations à l’environnement courant.
15. Les imports et exports sont contextualisés.
16. Les copies entre environnements créent de nouvelles données.
17. Les opérations sensibles sont journalisées.
18. L’administration Django ne peut pas contourner l’isolation.
19. Les tests utilisent systématiquement au moins deux environnements.
20. Toute fonctionnalité métier doit démontrer son respect de l’isolation.

---

## 38. Ordre d’implémentation recommandé

L’implémentation devrait suivre cet ordre :

```text
1. Company
2. ClientEnvironment
3. License
4. Operator
5. EnvironmentCompany
6. EnvironmentMembership
7. Project
8. ProjectMembership
9. Résolution du contexte courant
10. Managers et QuerySets
11. Permissions
12. Adaptation EPList
13. Adaptation EPDetail
14. Adaptation EPForm
15. Tests d’isolation
16. Développement des domaines métier
```

Les domaines fonctionnels ne doivent être développés qu’après validation du socle d’isolation.

---

## 39. Décisions restant à préciser

Les points suivants devront être arbitrés avant ou pendant l’implémentation :

* relation exacte entre licence et projet ;
* nombre possible de responsables par projet ;
* modèle Django d’authentification retenu ;
* structure exacte des capacités d’administration ;
* stratégie de suppression et d’archivage ;
* éventuel rattachement direct de certaines données projet à l’environnement ;
* mécanisme de stockage du contexte courant ;
* comportement précis d’un environnement sans licence active ;
* politique de rétention et de restitution des données.

Ces décisions ne remettent pas en cause les invariants d’isolation définis dans ce document.

# 40. Contexte d'exécution du framework (EPContext)
# 40.1 Objectif
# 40.2 Construction du contexte
# 40.3 Contenu du contexte
# 40.4 Utilisation par les composants du framework
# 40.5 Utilisation par les ChoiceProviders
# 40.6 Principes d'architecture

Dans l'interface utilisateur, le terme "Contexte de travail" est utilisé. Il désigne l'environnement métier dans lequel l'utilisateur exerce son activité. Sur le plan technique, ce contexte est implémenté par un ClientEnvironment et matérialisé à l'exécution par un EPContext.