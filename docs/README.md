

# Easy Projet – Documentation

Bienvenue dans la documentation officielle du projet **Easy Projet**.

Cette documentation est versionnée avec le code source et constitue la référence officielle du projet. Elle décrit les aspects fonctionnels, techniques, architecturaux et organisationnels de l'application.

Elle a pour objectifs de :

* définir les principes de conception du produit ;
* documenter les choix d'architecture ;
* formaliser les règles métier et les conventions de développement ;
* conserver l'historique des décisions importantes ;
* faciliter la maintenance et l'évolution du produit ;
* permettre à tout nouvel intervenant de comprendre rapidement l'organisation du projet.

La documentation évolue en même temps que le code source et fait partie intégrante du projet.

---

# Philosophie de la documentation

La documentation constitue un référentiel unique.

Chaque information ne doit être décrite qu'à un seul endroit afin d'éviter les incohérences et les duplications.

Les différents documents sont organisés par domaine de responsabilité. Chaque domaine possède un objectif précis et constitue la référence sur son périmètre.

En cas de contradiction, les documents d'architecture font référence.

---

# Organisation de la documentation

| Répertoire      | Objet                                                                                               |
| --------------- | --------------------------------------------------------------------------------------------------- |
| `vision/`       | Vision du produit, objectifs, stratégie et feuille de route.                                        |
| `architecture/` | Principes fondateurs, architecture générale, modèle de données, sécurité et composants techniques.  |
| `functional/`   | Règles métier, acteurs, cas d'utilisation, dictionnaires métier et fonctionnement de l'application. |
| `framework/`    | Composants génériques du framework Easy Projet (EPList, EPForm, EPDetail, workflows, services...).  |
| `development/`  | Conventions de développement, environnement, qualité, tests et procédures.                          |
| `technical/`    | Déploiement, exploitation, maintenance, sauvegardes et administration technique.                    |
| `ui/`           | Interface utilisateur, composants graphiques, ergonomie et charte visuelle.                         |
| `adr/`          | Architecture Decision Records : historique des décisions importantes.                               |

---

# Ordre recommandé de lecture

Pour découvrir le projet, il est recommandé de suivre l'ordre suivant :

1. **Vision**

   * comprendre les objectifs du produit ;

2. **Architecture**

   * comprendre les principes fondateurs ;
   * comprendre les invariants techniques ;
   * comprendre l'isolation des données et le modèle multi-environnement ;

3. **Fonctionnel**

   * comprendre le métier ;
   * comprendre les besoins utilisateurs ;

4. **Framework**

   * comprendre les composants génériques utilisés par l'application ;

5. **Développement**

   * comprendre les règles de développement et de qualité ;

6. **Technique**

   * comprendre l'exploitation et le déploiement.

---

# Catégories de documents

Tous les documents n'ont pas la même vocation.

## Documents normatifs

Ils définissent les règles du projet.

Ils font référence en cas de doute ou de divergence.

Exemples :

* architecture ;
* règles métier ;
* conventions de développement.

---

## Documents descriptifs

Ils décrivent le fonctionnement actuel du produit ou de ses composants.

Exemples :

* framework ;
* interface utilisateur ;
* documentation technique.

---

## Documents historiques

Ils expliquent pourquoi certaines décisions ont été prises.

Ils permettent de comprendre l'évolution du projet sans remettre en cause les règles actuellement en vigueur.

Exemple :

* ADR (Architecture Decision Records).

---

# Principes de documentation

Les règles suivantes s'appliquent à l'ensemble de la documentation :

1. La documentation constitue la référence officielle du projet.
2. Toute évolution importante doit être documentée.
3. Une information ne doit exister qu'à un seul endroit.
4. Les décisions d'architecture importantes sont consignées dans des ADR.
5. Les documents sont mis à jour dans le même commit que les développements concernés.
6. Les documents doivent être simples, précis et sans ambiguïté.
7. Les documents obsolètes sont conservés lorsqu'ils présentent un intérêt historique et leur statut est explicitement indiqué.
8. La documentation doit rester compréhensible par une personne découvrant le projet.

---

# Cycle de développement

Les évolutions importantes suivent systématiquement le processus suivant :

1. Analyse du besoin.
2. Étude des solutions.
3. Validation de l'architecture.
4. Mise à jour de la documentation.
5. Développement.
6. Tests et validation.
7. Mise à jour éventuelle de la documentation.
8. Commit Git.

Ce processus garantit la cohérence permanente entre :

* les besoins ;
* l'architecture ;
* la documentation ;
* le code.

---

# Principes fondateurs d'Easy Projet

L'ensemble du projet repose sur quelques invariants architecturaux :

* une identité d'opérateur est unique et pérenne ;
* les autorisations dépendent exclusivement des appartenances et des responsabilités actives ;
* les données appartiennent à leur environnement et non à leurs auteurs ;
* l'historique est conservé afin d'assurer la traçabilité des projets ;
* les environnements sont totalement isolés les uns des autres ;
* le framework privilégie la généricité, la simplicité et la réutilisation des composants.

Ces principes constituent le socle de l'architecture d'Easy Projet et s'appliquent à l'ensemble des développements futurs.
