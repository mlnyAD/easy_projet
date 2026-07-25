

# Principes du Framework Easy Projet

## Objet

Ce document définit les principes de conception du framework Easy Projet.

Contrairement aux Architecture Decision Records (ADR), ces principes ne décrivent pas une décision ponctuelle. Ils constituent des règles permanentes qui s'imposent à l'ensemble des composants du framework.

Tout nouveau composant générique doit respecter ces principes.

---

# Principes du framework

## PF-001 — Les templates ne contiennent pas de logique métier

Les templates sont exclusivement responsables de la présentation.

Toute logique métier ou technique est réalisée en dehors de la couche de présentation.

---

## PF-002 — Le framework ne contient aucun vocabulaire métier

Le framework fournit uniquement des mécanismes génériques.

Les notions propres aux domaines fonctionnels (projet, société, réunion, document, etc.) sont portées exclusivement par les applications métier.

---

## PF-003 — Les ViewModels préparent les données d'affichage

Les composants d'interface manipulent des ViewModels plutôt que directement les modèles métier.

Les ViewModels constituent l'interface entre la logique métier et la présentation.

---

## PF-004 — Le fonctionnel pilote l'évolution du framework

Le framework n'évolue que pour répondre à un besoin identifié dans une ou plusieurs applications métier.

Le développement du framework n'est jamais réalisé de manière spéculative.

---

## PF-005 — Les paramètres visuels sont centralisés

Les paramètres graphiques (styles, composants, comportements visuels) sont centralisés afin de garantir une interface homogène dans l'ensemble du produit.

---

## PF-006 — Les composants génériques ne portent aucune règle métier

Les composants du framework implémentent exclusivement des comportements techniques ou fonctionnels communs.

Les règles métier restent sous la responsabilité des applications métier.

---

## PF-007 — Le contexte d'environnement est résolu avant toute logique métier

Les composants du framework travaillent toujours dans le contexte d'un environnement actif.

Ils ne déterminent jamais eux-mêmes les droits d'accès ni le contexte d'exécution.

---

## PF-008 — Les composants manipulent des ViewModels plutôt que les modèles métier

Le framework privilégie une séparation claire entre les modèles de persistance et les modèles destinés à la présentation.

Cette séparation facilite les évolutions de l'interface utilisateur et limite le couplage avec les données.

---

## PF-009 — Le framework est la méthode privilégiée de développement

Toute nouvelle application métier doit utiliser les composants du framework avant d'envisager un développement spécifique.

La création d'un composant spécifique constitue une exception qui doit être justifiée.

---

## PF-010 — Le framework est indépendant des domaines fonctionnels

Tout composant générique doit pouvoir être utilisé par plusieurs applications métier sans adaptation spécifique.

Cette indépendance garantit la pérennité et la réutilisation du framework.

---

# Évolution

Les principes du framework sont destinés à évoluer avec Easy Projet.

Toute évolution doit préserver les principes d'architecture du projet, notamment :

* la simplicité ;
* la généricité maîtrisée ;
* la séparation des responsabilités ;
* l'isolation des environnements ;
* la réutilisation maximale des composants.
