

# 1. Objet

Le présent document décrit les services transverses mis à disposition de l'ensemble des applications métier d'Easy Projet.

Ces services fournissent des fonctionnalités communes qui ne relèvent d'aucun domaine métier particulier. Ils garantissent un comportement homogène de l'application et évitent la duplication des mécanismes communs.

# 2. Rôle des services transverses

Les services transverses assurent des fonctions communes nécessaires au fonctionnement global d'Easy Projet.

Ils sont partagés par toutes les applications métier et interviennent indépendamment des fonctionnalités propres à chaque domaine.

Leur objectif est de centraliser les mécanismes communs afin d'améliorer la cohérence, la maintenance et l'évolutivité du produit.

Les services transverses sont exécutés dans le contexte de l'environnement actif. Ils appliquent les principes d'isolation des données, de sécurité et de traçabilité définis par l'architecture du produit.

# 3. Principes de conception

Les services transverses respectent les principes suivants :

- indépendance vis-à-vis des applications métier ;
- mutualisation des fonctionnalités communes ;
- configuration privilégiée au développement spécifique ;
- simplicité d'utilisation ;
- évolutivité sans impact sur les applications utilisatricesfonctionnement dans le contexte de l'environnement actif ;
- absence de logique métier spécifique ;
- interfaces publiques stables ;
- traçabilité systématique des opérations lorsque nécessaire.

# 4. Familles de services

| Famille                          | Rôle                                                                     |
| -------------------------------- | ------------------------------------------------------------------------ |
| Gestion des environnements	     | Déterminer le contexte de travail et assurer l'isolation des données.    |
| Authentification	           | Vérifier l'identité des opérateurs.                                      |
| Autorisations	                 | Déterminer les droits dans l'environnement courant.                      |
| Notifications                    | Informer les utilisateurs des événements importants                      |
| Journalisation et traçabilité    | Conserver l'historique des actions                                       |
| Recherche globale                | Retrouver rapidement les informations                                    |
| Gestion des documents            | Fournir les mécanismes communs de stockage et de consultation            |
| Import / Export                  | Échanger des données avec d'autres systèmes                              |
| Génération de documents          | Produire PDF, Excel ou autres restitutions                               |
| Configuration                    | Gérer les paramètres généraux du produit                                 |
| Intégration                      | Communiquer avec les services externes (OnlyOffice, CADViewer, IA, etc.) |
| Audit	                       | Produire les informations nécessaires aux contrôles et à la conformité.  |
| Cache (éventuel)	           | Optimiser les performances sans modifier le comportement fonctionnel.    |


# 5. Règles d'utilisation

Les applications métier doivent s'appuyer sur les services transverses pour toute fonctionnalité commune au produit.

Aucune application métier ne doit réimplémenter un service déjà fourni par l'architecture.

Lorsqu'un nouveau besoin commun apparaît dans plusieurs domaines fonctionnels, celui-ci doit être étudié afin d'être intégré comme service transverse plutôt que développé de manière spécifique dans chaque application.

Les services transverses doivent rester indépendants des règles métier propres aux applications qui les utilisent.

Les services transverses constituent des briques mutualisées. Ils ne doivent dépendre d'aucune application métier afin de pouvoir être utilisés de manière identique dans l'ensemble du produit.

Les services transverses ne doivent jamais contourner les mécanismes d'autorisation.

Les services transverses ne doivent jamais accéder directement aux données d'un environnement autre que celui résolu pour la requête courante.

Toute opération ayant un impact sur les données métier doit pouvoir être tracée lorsque les exigences de sécurité ou de conformité l'imposent.

Les services transverses ne doivent jamais porter de règles métier propres à une application.
             Environnement actif
                     │
                     ▼
          +------------------------+
          | Services transverses   |
          +------------------------+
             ▲        ▲        ▲
             │        │        │
      +------+   +----+----+   +------+
      │             │               │
+-------------+ +-------------+ +--------------+
| Projets     | | Documents   | | Réunions     |
+-------------+ +-------------+ +--------------+

# 6. Évolutions

Les services transverses sont appelés à évoluer en fonction des besoins du produit.

Tout nouveau service devra répondre à un besoin partagé par plusieurs applications métier et respecter les principes de mutualisation, d'indépendance et de réutilisation définis dans le présent document.

L'évolution des services transverses ne devra pas remettre en cause les interfaces publiques utilisées par les applications métier.

Les évolutions des services transverses devront préserver :

- leur indépendance vis-à-vis des applications métier ;
- l'isolation des environnements ;
- la stabilité de leurs interfaces publiques ;
- la traçabilité des traitements ;
- les principes d'architecture définis dans le document 00-principes-architecture.md.