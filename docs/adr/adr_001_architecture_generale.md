

# ADR-001 - Architecture générale

## Statut

Accepté

## Date

2026-07-18

## Contexte

Easy Projet est une application de gestion de projets destinée aux PME du BTP.

Le projet est conçu pour évoluer pendant plusieurs années avec de nombreux modules fonctionnels.

L'objectif est de disposer d'une architecture simple, évolutive, facilement maintenable et limitant les duplications de code.

## Décision

L'application est organisée selon les principes suivants :

- une application Django par domaine métier ;
- un socle commun (`common`) pour les éléments partagés ;
- une séparation stricte entre logique métier et composants techniques ;
- une architecture orientée composants réutilisables ;
- PostgreSQL comme base de données ;
- Django Templates + Tailwind CSS + Preline pour l'interface utilisateur.

## Conséquences

Cette architecture permet :

- une forte modularité ;
- une bonne maintenabilité ;
- une montée en charge progressive des fonctionnalités ;
- la réutilisation des composants communs sans couplage avec le métier.

Les applications métier restent indépendantes les unes des autres.