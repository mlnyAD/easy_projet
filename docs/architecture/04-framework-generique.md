

# 04 - Framework générique

# Objet

Ce document décrit l'architecture générale du Framework Easy Projet.

Le framework constitue la couche technique commune utilisée par l'ensemble des applications métier. Il fournit des composants génériques permettant de construire des interfaces homogènes, évolutives et indépendantes des domaines fonctionnels.

Contrairement aux Architecture Decision Records (ADR), ce document décrit des principes permanents d'architecture. Toute évolution du framework doit les respecter.

---

# Objectifs

Le framework poursuit plusieurs objectifs :

- séparer le métier de la présentation ;
- favoriser une architecture déclarative ;
- limiter les développements spécifiques ;
- garantir une interface utilisateur homogène ;
- faciliter les évolutions fonctionnelles ;
- maximiser la réutilisation des composants.

Le framework constitue la méthode privilégiée de développement des applications Easy Projet.

---

# Principes du Framework

## PF-001 — Les templates ne contiennent aucune logique métier

Les templates sont exclusivement responsables du rendu graphique.

Ils n'effectuent aucun traitement métier ni aucune décision fonctionnelle.

Toute logique est réalisée en amont.

---

## PF-002 — Le framework est indépendant des domaines fonctionnels

Le framework fournit uniquement des mécanismes génériques.

Il ne connaît aucune notion métier :

- projet ;
- société ;
- réunion ;
- document ;
- utilisateur ;
- etc.

Les applications métier portent exclusivement ces concepts.

---

## PF-003 — Le framework est déclaratif

Les applications décrivent ce qu'elles souhaitent obtenir.

Le framework décide comment produire le résultat.

Cette séparation garantit une grande stabilité des développements métier.

---

## PF-004 — Le fonctionnel pilote l'évolution du framework

Le framework n'évolue que pour répondre à un besoin identifié dans une ou plusieurs applications métier.

Aucun composant n'est développé de manière spéculative.

---

## PF-005 — Le Design System est centralisé

L'ensemble des choix graphiques est regroupé dans le Design System.

Il définit notamment :

- les composants graphiques ;
- les couleurs ;
- les espacements ;
- les comportements visuels ;
- les icônes ;
- les classes CSS.

Les applications métier ne manipulent jamais directement ces éléments.

---

## PF-006 — Les composants génériques ne portent aucune règle métier

Les composants implémentent uniquement des comportements communs.

Les validations fonctionnelles restent sous la responsabilité des applications métier.

---

## PF-007 — Le contexte est résolu avant le métier

Les composants du framework travaillent toujours dans un contexte déjà déterminé.

Ils ne calculent jamais :

- les droits ;
- le contexte d'exécution ;
- l'environnement actif.

---

## PF-008 — La présentation manipule des modèles dédiés

La présentation ne manipule pas directement les modèles de persistance.

Le framework construit des objets adaptés au rendu :

- ViewModels ;
- objets Resolved* ;
- composants EP*.

Cette séparation limite le couplage avec la base de données.

---

## PF-009 — Le framework est la méthode de développement par défaut

Toute nouvelle transaction doit être construite à l'aide des composants du framework.

Le développement spécifique constitue une exception qui doit être justifiée.

---

## PF-010 — Les composants sont réutilisables

Chaque composant doit pouvoir être utilisé par plusieurs domaines métier sans adaptation.

Cette indépendance garantit la pérennité du framework.

---

# Architecture générale

Tous les composants du framework suivent la même architecture.

```
Définition déclarative
        │
        ▼
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
ViewModel / Resolved*
        │
        ▼
Template Tags
        │
        ▼
Design System
        │
        ▼
Templates
```

Cette architecture est commune à l'ensemble des composants.

Aujourd'hui :

- EntityDefinition ;
- EPList ;
- EPForm ;
- EPButton.

Demain :

- EPDetail ;
- Dashboard ;
- Wizard ;
- tout nouveau composant générique.

---

# Philosophie déclarative

Le framework repose sur un principe fondamental.

Les applications métier décrivent une intention.

Le framework construit automatiquement la représentation technique.

Autrement dit :

Le métier décrit :

- les données ;
- les propriétés ;
- les comportements fonctionnels.

Le framework décide :

- du rendu ;
- des composants ;
- des classes CSS ;
- des widgets ;
- des templates.

Une évolution graphique ne nécessite donc aucune modification des applications métier.

---

# Responsabilités

## Applications métier

Les applications métier décrivent uniquement les informations fonctionnelles.

Elles définissent notamment :

- les dictionnaires ;
- les propriétés métier ;
- les règles métier ;
- les validations spécifiques.

Elles ne décrivent jamais :

- le HTML ;
- Tailwind ;
- les classes CSS ;
- les widgets ;
- les couleurs ;
- les composants graphiques.

---

## Framework

Le framework transforme une définition déclarative en composant exploitable.

Il construit notamment :

- EPList ;
- EPForm ;
- EPButton ;
- les ViewModels ;
- les objets Resolved*.

Le framework ne connaît jamais le domaine métier.

---

## Intégration Django

La couche d'intégration associe les composants génériques aux objets Django.

Exemple :

```
FieldDefinition
        +
BoundField Django
        │
        ▼
ResolvedField
```

Cette couche constitue l'adaptateur entre le framework et Django.

---

## Design System

Le Design System est responsable de la présentation.

Il définit :

- les couleurs ;
- les composants graphiques ;
- les boutons ;
- les listes ;
- les cartes ;
- les espacements ;
- les états visuels ;
- les icônes.

Il ne contient aucune logique métier.

---

## Templates

Les templates réalisent exclusivement le rendu.

Ils ne prennent aucune décision.

Ils affichent uniquement les objets préparés par le framework.

---

# Évolutivité

Le framework est conçu pour évoluer sans remettre en cause les applications métier.

L'ajout :

- d'un nouveau widget ;
- d'un nouveau composant ;
- d'un nouveau Design System ;

ne nécessite pas de modifier les dictionnaires métier.

Cette stabilité constitue l'un des objectifs principaux du framework.

---

# Composants actuels

Le framework est aujourd'hui constitué des composants suivants :

- Dictionary ;
- EPList ;
- EPForm ;
- EPButton.

Chaque composant respecte la même architecture et les mêmes conventions.

Cette homogénéité simplifie :

- le développement ;
- la maintenance ;
- les tests ;
- la documentation.

---

# Conclusion

Le Framework Easy Projet constitue la couche générique de l'application.

Les applications métier expriment leurs besoins sous une forme déclarative.

Le framework transforme ces descriptions en composants exécutables.

Cette architecture garantit :

- une séparation claire des responsabilités ;
- une forte réutilisation du code ;
- une maintenance simplifiée ;
- une évolution maîtrisée du produit.