

# Environnement client et isolation des données

## 1. Objet du document

Ce document définit les règles fonctionnelles et les invariants d’architecture relatifs :

* aux clients Easy Projet ;
* aux environnements clients ;
* aux sociétés ;
* aux opérateurs ;
* aux licences ;
* aux projets ;
* à la propriété des données ;
* à l’isolation des données entre clients ;
* aux droits d’accès.

Il décrit le **QUOI**, indépendamment des choix techniques d’implémentation.

Les modèles de données, les tables, les contraintes techniques et les mécanismes de filtrage sont décrits dans le document :

```text
09-modele-de-donnees-multi-tenant.md
```

---

## 2. Principe fondamental

Easy Projet est une plateforme SaaS multi-client.

Chaque client dispose d’un environnement de travail propre appelé :

```text
Environnement client
```

L’environnement client constitue la frontière principale d’isolation et de sécurité des données.

Toute donnée métier appartient directement ou indirectement à un et un seul environnement client.

Les permissions des utilisateurs sont évaluées uniquement après la validation de cette frontière.

> Un utilisateur ne peut jamais accéder à une donnée appartenant à un environnement auquel il n’est pas autorisé à accéder, quel que soit son rôle dans un autre environnement.

---

## 3. Niveaux fonctionnels

L’architecture fonctionnelle distingue trois niveaux.

### 3.1 Niveau plateforme

Le niveau plateforme est administré par AXCIO-DATA.

Il contient notamment :

* les identités globales des sociétés ;
* les identités globales des opérateurs ;
* les comptes d’authentification ;
* les licences ;
* les catalogues globaux ;
* les paramètres de la plateforme ;
* les informations de version ;
* les éléments nécessaires à l’administration d’Easy Projet.

### 3.2 Niveau environnement client

Le niveau environnement contient toutes les données propres à un client :

* les sociétés présentes dans l’environnement ;
* les opérateurs présents dans l’environnement ;
* les projets ;
* les paramètres propres au client ;
* les données communes aux projets ;
* les données administratives locales ;
* les données métier.

### 3.3 Niveau projet

Le niveau projet contient les données opérationnelles d’un projet :

* les rôles des opérateurs ;
* les sociétés intervenantes ;
* les lots de travaux ;
* les tâches ;
* le planning ;
* les documents ;
* les réunions ;
* les risques ;
* les réserves ;
* les données financières ;
* les reportings ;
* les relevés d’heures ;
* les autres données d’exploitation.

```text
Plateforme AXCIO-DATA
        ↓
Environnement client
        ↓
Projet
```

---

## 4. Définition du client

Un client Easy Projet est une société ayant acquis au moins une licence.

```text
Société contractante
        +
Au moins une licence
        =
Client Easy Projet
```

La société contractante est la société ayant conclu la relation commerciale avec AXCIO-DATA.

Elle ne doit pas être confondue avec les autres sociétés pouvant intervenir dans ses projets.

---

## 5. Définition de l’environnement client

L’environnement client est l’espace de travail privé associé à une société contractante.

Il est créé lors de l’association de la première licence à cette société.

```text
Société contractante
        +
Première licence créée par AXCIO-DATA
        ↓
Création de l’environnement client
```

Une société contractante possède au maximum un environnement client.

Les licences ultérieures sont rattachées au même environnement.

L’environnement client :

* possède une identité propre ;
* constitue une frontière de sécurité ;
* contient les données du client ;
* est indépendant du cycle de vie de chaque licence ;
* continue d’exister après l’échéance des licences ;
* ne doit pas être supprimé automatiquement lorsqu’aucune licence n’est active.

L’association société–licence provoque la création de l’environnement, mais ne constitue pas techniquement ou fonctionnellement l’environnement lui-même.

---

## 6. Cycle de vie de l’environnement client

L’environnement client peut connaître plusieurs états fonctionnels.

Exemples :

* actif ;
* suspendu ;
* sans licence active ;
* archivé ;
* fermé.

L’échéance d’une licence ne provoque pas :

* la suppression de l’environnement ;
* la suppression des projets ;
* la suppression des documents ;
* la suppression des historiques ;
* la perte des données du client.

Les conséquences fonctionnelles de l’absence de licence active seront définies dans les règles de gestion des licences.

---

## 7. Gestion des sociétés

### 7.1 Identité globale d’une société

La plateforme contient une identité globale et neutre des sociétés.

Cette identité représente la personne morale réelle.

Elle contient uniquement des informations :

* publiques ;
* juridiques ;
* objectives ;
* non confidentielles ;
* indépendantes de la relation avec un client donné.

Exemples :

* raison sociale ;
* nom légal ;
* SIREN ou identifiant équivalent ;
* SIRET éventuel ;
* adresse officielle ;
* pays ;
* forme juridique ;
* statut d’activité officiel.

Cette identité globale peut être commune à plusieurs environnements.

Elle ne doit contenir aucune donnée métier ou commerciale propre à un client.

### 7.2 Présence d’une société dans un environnement

Une même société peut être présente dans plusieurs environnements clients.

Exemples :

* sous-traitant ;
* bureau de contrôle ;
* maître d’œuvre ;
* fournisseur ;
* partenaire ;
* entreprise intervenante.

Sa présence dans un environnement constitue une information distincte de son identité globale.

Chaque environnement peut définir ses propres informations concernant cette société :

* nom d’usage ;
* coordonnées locales ;
* contacts ;
* type de relation ;
* qualifications ;
* commentaires ;
* statut actif ou inactif ;
* dates de collaboration ;
* informations administratives internes ;
* informations utiles aux projets.

Ces informations sont strictement propres à l’environnement.

Elles ne sont jamais partagées automatiquement avec un autre environnement.

```text
Société globale X
├── présence dans l’environnement A
├── présence dans l’environnement B
└── présence dans l’environnement C
```

La désactivation d’une société dans un environnement n’a aucun effet sur sa présence dans les autres environnements.

---

## 8. Gestion des opérateurs

### 8.1 Identité globale de l’opérateur

L’opérateur possède une identité globale liée à son compte d’authentification.

Cette identité contient notamment :

* son identité ;
* son adresse électronique de connexion ;
* les informations nécessaires à l’authentification ;
* le statut global du compte ;
* les informations liées à l’invitation et à l’activation du compte.

Un opérateur peut appartenir à plusieurs environnements avec un seul compte de connexion.

### 8.2 Présence de l’opérateur dans un environnement

La présence d’un opérateur dans un environnement est distincte de son identité globale.

Elle peut contenir :

* l’environnement concerné ;
* sa société de rattachement dans cet environnement ;
* son statut local ;
* ses responsabilités au niveau de l’environnement ;
* ses dates de présence ;
* ses informations administratives locales.

Une désactivation locale :

* retire l’accès à l’environnement concerné ;
* ne désactive pas le compte global ;
* n’affecte pas les autres environnements ;
* conserve les historiques et les traces d’activité.

### 8.3 Opérateur sans projet

Lorsqu’un opérateur est retiré de son dernier projet :

* son compte global reste actif ;
* il peut encore s’authentifier ;
* il ne peut accéder à aucune donnée métier ;
* il peut être affecté ultérieurement à un autre projet ;
* il peut conserver des accès dans un autre environnement.

Après connexion, le système lui indique qu’aucun projet actif ne lui est actuellement affecté.

### 8.4 Désactivation globale

L’opérateur doit pouvoir demander ou déclencher la désactivation de son propre compte global.

Selon les règles de conservation applicables et la présence de données historiques associées, il doit également pouvoir demander la suppression de son compte.

La suppression d’un compte ne doit cependant pas entraîner la disparition des données métier, des journaux ou des historiques nécessaires au fonctionnement, à la traçabilité ou à la conservation des projets.

Lorsque la suppression physique complète n’est pas possible, les données personnelles de l’opérateur doivent être supprimées, rendues anonymes ou réduites au strict nécessaire, tandis que les références historiques indispensables sont conservées.

La désactivation ou la suppression du compte global :

interdit toute nouvelle connexion ;
n’efface pas les actions réalisées antérieurement ;
n’altère pas les données appartenant aux environnements ;
n’affecte pas les autres opérateurs ;
doit être journalisée.

AXCIO-DATA conserve également la possibilité de désactiver globalement un compte, notamment :

en cas de problème de sécurité ;
en cas de compte frauduleux ;
à la suite d’une demande réglementaire ;
lorsqu’une personne ne doit plus pouvoir se connecter à la plateforme.

En conclusion:
Lorsqu’un opérateur quitte une société, son appartenance à l’environnement de cette société ainsi que ses affectations actives aux projets sont clôturées. Il perd immédiatement tout accès aux données de cet environnement, y compris aux données qu’il a lui-même créées ou auxquelles il a contribué. Ses travaux, ses contributions et son identité historique restent néanmoins conservés dans l’environnement au bénéfice des utilisateurs toujours autorisés. Si l’opérateur rejoint une autre société, la même identité globale peut être associée à un nouvel environnement sans créer aucun droit sur ses anciens environnements.

La qualité d’auteur, de participant ou d’ancien membre d’un projet ne constitue jamais un droit d’accès. Seules les appartenances actives et les permissions courantes autorisent la consultation ou la modification d’une donnée.

---

## 9. Gestion des licences

AXCIO-DATA est responsable :

* de la création des licences ;
* de leur association à une société contractante ;
* de leur activation ;
* de leur renouvellement ;
* de leur suspension ;
* de leur échéance.

La première licence associée à une société contractante provoque la création de l’environnement client.

Les licences suivantes sont rattachées au même environnement.

Une licence ne constitue pas l’environnement client.

L’environnement client persiste indépendamment de l’état de ses licences.

La relation exacte entre une licence et un projet est définie dans les règles commerciales et dans le modèle technique.

---

## 10. Gestion des projets

Un projet appartient à un seul environnement client.

Un projet ne peut pas changer d’environnement.

Toutes les données d’un projet appartiennent indirectement à l’environnement de ce projet.

```text
Environnement client
        └── Projet
              ├── lots
              ├── tâches
              ├── documents
              ├── réunions
              ├── finances
              └── reporting
```

Les rôles opérationnels des utilisateurs sont définis au niveau du projet.

Un même opérateur peut avoir des rôles différents dans plusieurs projets.

---

## 11. Responsabilités des acteurs

### 11.1 Administrateur système AXCIO-DATA

L’administrateur système peut notamment :

* créer une société contractante si elle n’existe pas ;
* créer une licence ;
* associer une licence à une société ;
* provoquer la création de l’environnement client ;
* administrer les données globales ;
* désactiver globalement un compte ;
* intervenir sur la gestion technique de la plateforme.

### 11.2 Administrateur client

L’administrateur client dispose d’une vision sur l’ensemble de son environnement.

Il peut notamment :

* gérer les sociétés présentes dans l’environnement ;
* gérer les opérateurs de l’environnement ;
* créer les données communes ;
* consulter les projets ;
* administrer les rattachements ;
* gérer les droits locaux ;
* désactiver un opérateur dans l’environnement.

Dans une petite structure, l’administrateur client peut également être chef de projet.

### 11.3 Chef de projet

Le chef de projet dispose :

* d’un accès en lecture et en écriture sur les projets dont il est nommément responsable ;
* d’un accès en lecture seule sur les autres projets du même environnement.

Sur ses propres projets, il peut créer et gérer les données relevant de sa responsabilité.

Sur les autres projets de l’environnement, il peut :

* consulter les informations ;
* s’inspirer des organisations existantes ;
* identifier les méthodes utilisées ;
* préparer de nouveaux projets ;
* réutiliser des principes ou structures autorisés.

Il ne peut pas modifier un projet dont il n’est pas responsable.

Selon les responsabilités qui lui sont accordées, un chef de projet peut également gérer ou désactiver des opérateurs dans l’environnement.

Cette capacité doit être explicitement autorisée et ne doit pas être déduite automatiquement du seul rôle de chef de projet.

### 11.4 Opérateur de projet

Un opérateur dispose d’un accès aux seuls projets auxquels il est affecté.

Il peut créer ou modifier les données d’exploitation autorisées par son rôle.

### 11.5 Sous-traitant

Le sous-traitant accède uniquement aux projets, données et fonctions pour lesquels il possède une affectation et des permissions explicites.

---

## 12. Flux de connexion

La connexion est réalisée à partir de l’identité globale de l’opérateur.

Après authentification, le système recherche :

1. les environnements auxquels l’opérateur appartient ;
2. les projets auxquels il est affecté ;
3. les projets qu’il peut consulter en raison de ses responsabilités ;
4. les rôles applicables.

Le système présente ensuite la liste des projets accessibles.

```text
Connexion
    ↓
Authentification globale
    ↓
Recherche des environnements autorisés
    ↓
Recherche des projets accessibles
    ↓
Présentation de la liste des projets
```

Chaque projet présenté doit préciser au minimum :

* son nom ;
* son environnement ou sa société cliente ;
* le rôle de l’utilisateur ;
* son statut.

Lorsqu’un projet est sélectionné, le système détermine automatiquement :

* l’environnement courant ;
* le projet courant ;
* le rôle courant ;
* les permissions applicables.

L’utilisateur n’a pas à sélectionner préalablement un environnement.

---

## 13. L’environnement comme coffre-fort

L’environnement client peut être assimilé à un coffre-fort.

Être authentifié sur la plateforme ne suffit pas pour accéder à son contenu.

Trois contrôles successifs sont appliqués :

```text
1. Qui êtes-vous ?
   → authentification globale

2. Avez-vous accès à cet environnement ?
   → appartenance ou autorisation valide

3. À quelles données pouvez-vous accéder ?
   → rôle, projet et permissions
```

L’environnement constitue la première frontière.

Les rôles et permissions déterminent ensuite les compartiments accessibles à l’intérieur de cet environnement.

---

## 14. Propriété des données

Les données métier appartiennent à l’environnement client.

Cette propriété est indépendante de l’identité de l’utilisateur qui a créé la donnée.

À l’intérieur de l’environnement, la visibilité dépend :

* du rôle ;
* des responsabilités ;
* de l’affectation au projet ;
* du type de donnée ;
* de l’action demandée.

Les données globales à la plateforme sont limitées à celles qui doivent réellement être partagées.

---

## 15. Données globales à la plateforme

Sont globales à la plateforme :

* les identités neutres des sociétés ;
* les identités des opérateurs ;
* les comptes d’authentification ;
* les catalogues globaux ;
* les licences ;
* les paramètres système ;
* les informations d’administration AXCIO-DATA ;
* les informations de version.

Une donnée globale ne doit contenir aucune information confidentielle propre à un environnement.

---

## 16. Données propres à l’environnement

Sont propres à un environnement client :

* les présences locales des sociétés ;
* les présences locales des opérateurs ;
* les projets ;
* les paramètres propres au client ;
* les informations administratives locales ;
* les contacts locaux ;
* les relations commerciales ;
* les lots de travaux ;
* les tâches ;
* les plannings ;
* les réunions ;
* les documents ;
* la GED ;
* les risques ;
* les réserves ;
* les finances ;
* les reportings ;
* les relevés d’heures ;
* les historiques métier ;
* toutes les données opérationnelles.

---

## 17. Données propres au projet

Sont notamment propres à un projet :

* les rôles des opérateurs ;
* les affectations ;
* les sociétés intervenantes ;
* les lots ;
* les tâches ;
* le planning ;
* les documents du projet ;
* les réunions ;
* les risques ;
* les réserves ;
* les éléments financiers ;
* les reportings ;
* les relevés d’heures ;
* les données d’exploitation.

Une donnée propre à un projet appartient également à l’environnement du projet.

---

## 18. Changement d’environnement interdit

Une donnée métier ne peut pas changer d’environnement.

L’environnement d’appartenance d’une donnée est fixé lors de sa création.

Si un besoin de transfert est démontré, il doit être traité par une opération explicite de copie.

```text
Environnement A
    └── donnée source
             ↓ copie contrôlée
Environnement B
    └── nouvelle donnée indépendante
```

La copie doit :

* créer une nouvelle donnée ;
* attribuer un nouvel identifiant ;
* conserver la donnée source ;
* ne pas créer de dépendance implicite entre les environnements ;
* respecter les règles de confidentialité ;
* exclure les informations non transférables ;
* être journalisée.

---

## 19. Diffusion de données hors de l’environnement

L’isolation interdit tout accès direct non autorisé à une donnée depuis l’extérieur de l’environnement.

Elle n’interdit pas une sortie volontaire et contrôlée d’une copie.

Un utilisateur autorisé peut notamment :

* télécharger un document ;
* exporter une liste ;
* transmettre un document par courrier électronique ;
* joindre un document à un message destiné à une personne extérieure ;
* diffuser un document selon les règles de son projet.

Cette action doit être explicite.

Elle doit être encadrée par :

* une permission appropriée ;
* une sélection volontaire du document ;
* l’identification du destinataire ;
* la version du document ;
* la date de l’action ;
* l’identité de l’opérateur ;
* une journalisation suffisante.

> Une personne extérieure peut recevoir une copie diffusée par un utilisateur autorisé, mais elle ne bénéficie pas pour autant d’un accès à l’environnement.

---

## 20. Frontière de sécurité

L’environnement client constitue la frontière principale de sécurité.

La sécurité doit toujours être appliquée dans l’ordre suivant :

```text
1. Identification de l’environnement
2. Vérification de l’accès à l’environnement
3. Vérification du rôle
4. Vérification de l’affectation au projet
5. Vérification de l’action demandée
```

Les droits d’accès ne remplacent jamais l’isolation par environnement.

Un rôle élevé dans un environnement ne donne aucun droit dans un autre environnement.

---

## 21. Règles invariantes

Les règles suivantes sont obligatoires.

1. Un client est une société ayant acquis au moins une licence.
2. Une société contractante possède au maximum un environnement client.
3. L’environnement est créé lors de l’association de la première licence.
4. L’environnement est une entité distincte de la société et de la licence.
5. L’environnement persiste après l’échéance des licences.
6. Une identité globale de société peut être présente dans plusieurs environnements.
7. Une identité globale d’opérateur peut être présente dans plusieurs environnements.
8. Les données locales ne sont jamais partagées automatiquement entre environnements.
9. Une donnée métier appartient à un seul environnement.
10. Un projet appartient à un seul environnement.
11. Une donnée projet appartient à l’environnement de son projet.
12. Une donnée ne peut pas changer d’environnement.
13. Toute copie entre environnements est explicite, contrôlée et journalisée.
14. Toute consultation de données métier est limitée à un environnement autorisé.
15. Les permissions sont évaluées après le contrôle de l’environnement.
16. Une désactivation locale n’affecte pas les autres environnements.
17. La désactivation globale peut être déclenchée par l’opérateur pour son propre compte ou par AXCIO-DATA dans le cadre de l’administration et de la sécurité de la plateforme. Une demande de suppression doit préserver les données métier et les historiques qui ne peuvent pas être supprimés.
18. Un opérateur sans projet peut rester authentifiable sans accéder à des données métier.
19. Un chef de projet dispose d’un accès en lecture-écriture sur les projets dont il est responsable.
20. Un chef de projet dispose d’un accès en lecture seule sur les autres projets du même environnement.
21. Aucun rôle ne permet de franchir la frontière d’un autre environnement.
22. Une diffusion externe constitue une sortie volontaire d’une copie et non un accès à l’environnement.
23. Les données appartiennent toujours à l'environnement, jamais à l'utilisateur qui les a créées.
24. Aucune décision d'autorisation ne doit être prise à partir de l'identité seule d'un opérateur.

---

## 22. Règle directrice

Toute nouvelle fonctionnalité doit répondre à la question suivante :

> À quel environnement cette donnée appartient-elle et comment l’accès à cet environnement est-il garanti ?

Aucune fonctionnalité métier ne peut être considérée comme complète tant que cette question n’a pas reçu une réponse explicite.
