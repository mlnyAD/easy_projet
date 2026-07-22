

# 1. Objet

Ce document décrit les composants génériques utilisés par Easy Projet.

Ces composants fournissent des comportements communs réutilisables par les différentes applications métier du produit.

Ils ont pour objectif d’assurer l’homogénéité de l’interface utilisateur, de limiter les duplications et de faciliter l’évolution du système.

Le présent document décrit leurs responsabilités et leurs règles générales d’utilisation, sans détailler leur implémentation technique.


# 2. Rôle des composants génériques

Les composants génériques ont pour objectif de mutualiser les fonctionnalités communes à l'ensemble des applications métier.

Ils permettent d'offrir une interface utilisateur homogène, de réduire les duplications de code et de simplifier les évolutions du produit.

Ils ne portent aucune règle métier propre à un domaine fonctionnel. Leur rôle est de fournir des mécanismes réutilisables pouvant être employés par toutes les applications du système.


# 3. Principes de conception

Les composants génériques respectent les principes suivants :

- indépendance vis-à-vis des applications métier ;
- réutilisation maximale ;
- paramétrage privilégié au développement spécifique ;
- comportement homogène dans l'ensemble du produit ;
- évolutions sans impact sur les applications utilisatrices.

# 4. Organisation des composants génériques

Les composants génériques sont organisés par famille selon leur responsabilité.

Chaque famille répond à un besoin commun rencontré dans les différentes applications métier.

Cette organisation favorise la réutilisation des composants et garantit une interface utilisateur cohérente dans l'ensemble du produit.

| Famille      | Rôle                                                    |
| ------------ | ------------------------------------------------------- |
| Présentation | Afficher les informations                               |
| Saisie       | Créer et modifier les données                           |
| Recherche    | Rechercher et filtrer les informations                  |
| Navigation   | Faciliter les déplacements dans l'application           |
| Restitution  | Présenter les tableaux de bord, rapports et impressions |


# 5. Composants de présentation

Les composants de présentation ont pour rôle d'afficher les informations manipulées par les applications métier.

Ils assurent une présentation homogène des données, quel que soit le domaine fonctionnel concerné.

Ils permettent notamment de présenter :

- des listes de données ;
- des fiches détaillées ;
- des arborescences ;
- des cartes ou tuiles ;
- des tableaux de bord.

Ces composants ne réalisent aucun traitement métier. Ils se limitent à présenter les informations fournies par les applications métier.


# 6. Composants de saisie

Les composants de saisie permettent la création, la consultation et la modification des informations.

Ils offrent un comportement homogène pour l'ensemble des formulaires du produit.

Ils prennent notamment en charge :

- la présentation des champs ;
- les contrôles de saisie ;
- les messages d'aide ;
- la validation des informations ;
- les actions d'enregistrement ou d'annulation.

Les règles métier restent sous la responsabilité des applications métier.


# 7. Composants de recherche

Les composants de recherche facilitent l'accès aux informations.

Ils permettent de rechercher, filtrer, trier et retrouver rapidement les données.

Ils assurent un comportement identique dans l'ensemble des applications métier afin de proposer une expérience utilisateur cohérente.


# 8. Composants de navigation

Les composants de navigation permettent aux utilisateurs de se déplacer simplement dans l'application.

Ils assurent une organisation cohérente des menus, des parcours et des accès aux différentes fonctionnalités.

Ils contribuent à limiter la profondeur de navigation et à faciliter l'utilisation quotidienne du produit.


# 9. Composants de restitution

Les composants de restitution permettent de présenter les informations synthétiques produites par le système.

Ils regroupent notamment :

- les tableaux de bord ;
- les indicateurs ;
- les états ;
- les impressions ;
- les exports.

Ils présentent les informations de manière homogène et adaptée aux différents profils d'utilisateurs.


# 10. Règles d'utilisation

Les applications métier doivent privilégier l'utilisation des composants génériques.

Le développement d'un composant spécifique ne doit être envisagé que lorsqu'aucun composant générique ne répond au besoin identifié.

Lorsqu'un nouveau composant générique est créé, celui-ci doit être conçu de manière à pouvoir être réutilisé par plusieurs applications métier.


# 11. Évolutions

La bibliothèque des composants génériques est appelée à évoluer au rythme des besoins fonctionnels du produit.

L'ajout de nouveaux composants devra respecter les principes définis dans le présent document afin de préserver l'homogénéité de l'interface utilisateur et la cohérence de l'architecture.