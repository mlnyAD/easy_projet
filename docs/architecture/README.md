

# Architecture Easy Projet

## Objet

Ce répertoire rassemble l'ensemble de la documentation d'architecture d'Easy Projet.

Il constitue la référence de conception du produit et décrit les principes, les choix structurants et les règles qui guident le développement de la plateforme.

L'architecture est organisée selon une progression logique permettant de comprendre progressivement le fonctionnement du système, depuis les principes fondateurs jusqu'au langage de description des applications métier.

---

# Organisation

La documentation est structurée en quatre grandes parties.

## I – Fondations

Ces documents présentent les principes structurants de l'architecture.

| Document | Objet |
|----------|-------|
| 00-principes-architecture.md | Principes fondateurs et invariants de l'architecture |
| 01-architecture-generale.md | Vue d'ensemble de l'architecture |
| 02-environnement-client-et-isolation-des-donnees.md | Isolation des environnements clients |
| 03-modele-de-donnees-multi-tenant.md | Implémentation du modèle multi-environnement |

---

## II – Cœur de la plateforme

Cette partie décrit les composants constituant le socle technique d'Easy Projet.

| Document | Objet |
|----------|-------|
| 04-framework-generique.md | Principes du framework Easy Projet |
| 05-services-transverses.md | Services communs utilisés par toutes les applications |
| 06-domaines-fonctionnels.md | Organisation des applications métier |

---

## III – Infrastructure

Cette partie décrit les mécanismes assurant la conservation et l'ouverture du système.

| Document | Objet |
|----------|-------|
| 07-persistance-des-donnees.md | Principes de persistance des données |
| 08-connecteurs.md | Architecture des connecteurs externes |

---

## IV – Langage métier

Cette partie décrit le langage utilisé par le framework pour représenter les entités métier.

| Document | Objet |
|----------|-------|
| 09-dictionnaire-metier.md | Structure du dictionnaire métier |
| 10-reference-proprietes.md | Référence complète des propriétés du dictionnaire |

---

## Présentation

| Document | Objet |
|----------|-------|
| 11-architecture-presentation.md | Présentation synthétique de l'architecture Easy Projet |

---

# Ordre de lecture recommandé

Pour une première découverte de l'architecture, il est recommandé de suivre l'ordre numérique des documents.

Chaque document s'appuie sur les concepts introduits dans les précédents.

---

# Principes

L'architecture d'Easy Projet repose sur plusieurs principes majeurs :

- séparation des responsabilités ;
- généricité maîtrisée ;
- indépendance des domaines métier ;
- isolation des environnements clients ;
- réutilisation maximale des composants ;
- pérennité des interfaces publiques ;
- évolutivité sans remise en cause des fondations.

---

# Évolution de la documentation

Cette documentation est un document vivant.

Toute évolution de l'architecture doit être répercutée dans les documents concernés afin de maintenir une description fidèle du fonctionnement réel de la plateforme.

Les principes d'architecture constituent la référence prioritaire pour toute évolution future.