# Easy Projet

## 2026-07-08

- Création du projet Django
- Configuration PostgreSQL
- Validation de la connexion
- Début de la phase 2 (développement)

## [0.1.1-dev] - 2026-07-10

### Ajouté
- Modèle `Company`
- Migration initiale de l’app `companies`
- Administration Django des sociétés
- Validation de la création d’une société dans PostgreSQL

### Corrigé
- Reconstruction propre de la base PostgreSQL
- Rétablissement du modèle utilisateur standard Django
- Utilisation du rôle PostgreSQL `easy_projet_user`

## [0.2.0-dev] - 2026-07-11

### Ajouté
- Architecture du Design System
- Component Library
- Première version de Company
- Documentation de développement

### Modifié
- Dictionnaire de données enrichi avec la colonne Widget
- Principes de développement

## [0.1.0-dev] - 2026-07-18

### Ajout
- Composants TextInput, EmailInput, PhoneInput et Checkbox stabilisés.
- Intégration de TelInput.
- Centralisation des comportements JavaScript des formulaires.
- Uniformisation des attributs data-*.

### Technique
- Refactorisation de ep_forms.py.
- Simplification de ep_form_field.html.

## Version 0.2.0 – Première transaction métier

### Ajouts

- Création de la première liste métier : Sociétés.
- Mise en place du flux complet :
  - Liste des sociétés
  - Création d'une société
  - Retour automatique vers la liste
  - Message de confirmation.
- Première pagination de la liste.
- Première table responsive.
- Validation de l'architecture des vues CRUD.

### Architecture

- Validation de l'approche "développer un cas concret avant de généraliser".
- La liste Société devient la référence pour la conception du futur composant EPList.