

# 1. Objet

Le présent document décrit l'organisation des applications métier constituant Easy Projet.

Chaque application métier regroupe un ensemble cohérent de fonctionnalités répondant à un domaine fonctionnel identifié.

Cette organisation favorise la modularité, la maintenabilité et l'évolution du produit.

Les domaines fonctionnels regroupent les applications proposées par Easy Projet selon leur finalité. Ils sont organisés en deux familles : les domaines métier, qui permettent la gestion des projets, et les domaines support, qui accompagnent les utilisateurs dans l'utilisation de la plateforme.

Les applications métier s'exécutent dans le contexte d'un environnement client actif et s'appuient exclusivement sur les composants du framework ainsi que sur les services transverses. Elles constituent la couche fonctionnelle du produit et implémentent les règles métier propres à chaque domaine.

# 2. Rôle des applications métier

Les applications métier mettent en œuvre les fonctionnalités attendues par les utilisateurs.

Elles appliquent les règles de gestion propres à chaque domaine fonctionnel et s'appuient sur les composants génériques ainsi que sur les services transverses pour offrir une expérience utilisateur homogène.
Elles ne gèrent ni l'authentification, ni les autorisations, ni la résolution de l'environnement actif. Ces mécanismes sont assurés par les services transverses et le framework.

Chaque application métier est responsable de son domaine fonctionnel sans empiéter sur les responsabilités des autres applications.

# 3. Principes de conception

Les applications métier respectent les principes suivants :

- une responsabilité fonctionnelle clairement identifiée ;
- un faible couplage avec les autres applications ;
- une forte cohésion interne ;
- l'utilisation systématique des composants génériques et des services transverses ;
- une évolution indépendante des autres domaines fonctionnels lorsque cela est possible,
- aucune logique technique transverse ;
- fonctionnement dans le contexte de l'environnement actif ;
- utilisation exclusive des interfaces publiques du framework ;
- absence de duplication des règles métier entre applications.

# 4. Familles d'applications métier

| Domaine                 | Application     | Finalité                                                  |
| ----------------------- | --------------- | --------------------------------------------------------- |
| **Gestion métier**      | Sociétés        | Gérer les entreprises intervenant sur les projets         |
|                         | Opérateurs      | Gérer les utilisateurs et leurs affectations              |
|                         | Projets         | Gérer les projets                                         |
|                         | Lots de travaux | Structurer les projets                                    |
|                         | Tâches          | Planifier et suivre les travaux                           |
|                         | Documents       | Gérer la documentation                                    |
|                         | Réunions        | Organiser et suivre les réunions                          |
|                         | Finances        | Gérer les budgets et les dépenses                         |
|                         | Reporting       | Produire les tableaux de bord et indicateurs              |
|                         | Catalogues      | Gérer les référentiels                                    |
|                         | Localisation    | Visualiser les informations sur une carte                 |
|                         | Messagerie      | Faciliter les échanges entre utilisateurs                 |
|                         | Todo            | Centraliser les actions à réaliser                        |
| **Support utilisateur** | Aide en ligne   | Assister les utilisateurs dans l'utilisation du produit   |
|                         | About           | Présenter les informations de version et de configuration |
|                         | Licence         | Gérer les licences d'utilisation                          |
|                         | Paramétrage     | Configurer le fonctionnement général du produit           |
|                         | Environnements  | Administration des environnements clients (*)             |
|                         | Affectations    | Gestion des appartenances aux environnements et aux projets|
|                         | Audits          | Consultation des journaux et de la traçabilité            |

(*)(réservé administration système)

                   Easy Projet
                       │
              Environnement actif
                       │
        ┌──────────────┴──────────────┐
        │                             │
 Applications métier          Applications support

# 5. Règles d'utilisation

Chaque fonctionnalité métier doit être rattachée à une application clairement identifiée.

Les échanges entre applications doivent rester limités aux informations nécessaires à leur fonctionnement.

Les fonctionnalités communes doivent être prises en charge par les services transverses ou les composants génériques et ne doivent pas être dupliquées dans les applications métier.

Toute évolution fonctionnelle doit respecter le découpage fonctionnel défini par l'architecture.

Les applications métier ne doivent jamais accéder directement aux mécanismes techniques du framework lorsqu'un service dédié existe.

Les applications métier ne doivent jamais contourner les mécanismes d'autorisation.

Toute donnée manipulée appartient à l'environnement courant.

Les applications métier doivent préserver la traçabilité des opérations.

# 6. Évolutions

De nouvelles applications métier pourront être ajoutées afin d'accompagner l'évolution du produit.

Toute nouvelle application devra correspondre à un domaine fonctionnel clairement identifié et respecter les principes d'architecture définis par Easy Projet.

Toute nouvelle application métier devra :

- correspondre à un domaine fonctionnel clairement identifié ;
- respecter les principes du framework ;
- utiliser les services transverses ;
- fonctionner dans le contexte de l'environnement actif ;
- préserver les invariants définis dans le document 00-principes-architecture.md.