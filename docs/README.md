

# Easy Projet - Documentation

Bienvenue dans la documentation du projet **Easy Projet**.

Cette documentation est versionnée avec le code source et constitue la référence officielle du projet. Elle décrit les aspects fonctionnels, techniques et architecturaux de l'application.

Les objectifs sont de :

- documenter les choix d'architecture ;
- conserver l'historique des décisions importantes ;
- faciliter la maintenance et l'évolution du produit ;
- permettre à un nouveau développeur de comprendre rapidement l'organisation du projet.

L'ensemble de la documentation est organisé par domaine afin de séparer les préoccupations fonctionnelles, techniques et architecturales.

## Organisation de la documentation

La documentation est organisée par domaine afin de faciliter son utilisation et sa maintenance.

Chaque répertoire possède un objectif précis et constitue la référence sur son domaine de responsabilité.

| Répertoire | Contenu |
|------------|---------|
| `architecture/` | Architecture générale du produit, principes de conception et composants génériques. |
| `functional/` | Expression des besoins, règles métier, cas d'utilisation et dictionnaire des données. |
| `development/` | Environnement de développement, conventions, procédures et outils. |
| `technical/` | Documentation technique, déploiement, exploitation et maintenance. |
| `ui/` | Interface utilisateur, composants graphiques, ergonomie et charte visuelle. |
| `vision/` | Vision du produit, objectifs et feuille de route. |
| `adr/` | Architecture Decision Records (historique des décisions d'architecture). |

Chaque information doit être documentée dans un seul endroit afin d'éviter les incohérences et les duplications.

## Principes de documentation

La documentation fait partie intégrante du projet Easy Projet.

Elle est conservée dans le dépôt Git et évolue en même temps que le code source.

Les principes suivants s'appliquent à l'ensemble des documents :

1. La documentation est la référence officielle du projet.
2. Toute évolution importante de l'architecture doit être documentée.
3. Une information ne doit exister qu'à un seul endroit.
4. Les décisions d'architecture sont conservées dans des ADR.
5. Les documents doivent être mis à jour dans le même commit que les développements concernés.
6. La documentation doit rester simple, claire et concise.
7. Les documents obsolètes sont conservés lorsqu'ils présentent un intérêt historique, mais leur statut doit être explicitement indiqué.
8. La documentation doit pouvoir être comprise par une personne découvrant le projet.

L'objectif est de garantir la cohérence entre le produit, son architecture et sa documentation tout au long de son cycle de vie.

## Cycle de développement

Les évolutions importantes du projet suivent un processus commun afin de garantir la qualité, la cohérence et la maintenabilité du produit.

Chaque chantier est traité selon les étapes suivantes :

1. Analyse du besoin.
2. Étude des solutions envisageables.
3. Validation de l'architecture retenue.
4. Mise à jour de la documentation.
5. Développement.
6. Tests et validation.
7. Mise à jour de la documentation si nécessaire.
8. Commit Git.

Ce processus permet de garantir que la documentation, l'architecture et le code restent cohérents tout au long du développement.

Les décisions d'architecture importantes font l'objet d'une Architecture Decision Record (ADR).

