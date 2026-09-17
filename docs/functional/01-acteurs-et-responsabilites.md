

1. Objet

Définir les 

2. Règles générales

3. Fonctions offertes

4. Contraintes métier

5. Évolutions possibles


Le système doit gérer différents intervenants avec chacun un métier, un niveau de responsabilité et des droits personnalisés.
Chaque intervenant intervient dans le système selon un rôle, des responsabilités et des droits qui lui sont propres.

Nous retenons donc cette règle comme cible Level 2 :

ClientEnvironment : 0..1 administrateur client titulaire + 0..N administrateurs délégués, avec les mêmes droits.
Project : 0..1 chef de projet titulaire + 0..N chefs de projet délégués, avec les mêmes droits.
Le statut titulaire/délégué est organisationnel, pas une différence de permissions.
La vacance du titulaire est autorisée.
Le périmètre reste exclusivement déterminé par ClientEnvironmentMembership et ProjectMembership : aucun changement au cloisonnement.
Nous évitons donc les rôles ADJOINT et, à ce stade, les tables de délégation supplémentaires.

Je propose de procéder par périmètre, en commençant par le plus central : les projets. Il faut maintenant formaliser et tester la matrice suivante :

Acteur	Voir projet	Modifier projet	Gérer participants	Gérer sociétés projet	Données financières
System Admin	Oui	Oui	Oui	Oui	Oui
Client Admin du CE	Oui	Oui	Oui	Oui	Oui
CP du projet, titulaire ou délégué	Oui	Oui	Oui	Oui	Oui
Utilisateur membre	Oui	Selon access_level	Selon access_level	Non	Non
Utilisateur hors projet	Non	Non	Non	Non	Non

| Action                                      | Admin système | Admin client | CP sur son projet | CP sur autre projet de la société | Standard affecté | Lecture seule affecté |
| ------------------------------------------- | :-----------: | :----------: | :---------------: | :-------------------------------: | :--------------: | :-------------------: |
| Voir le projet                              |       ✓       |       ✓      |         ✓         |                 ✓                 |         ✓        |           ✓           |
| Voir les participants                       |       ✓       |       ✓      |         ✓         |                 ✓                 |         ✓        |           ✓           |
| Voir tâches / planning / réunions / risques |       ✓       |       ✓      |         ✓         |                 ✓                 |         ✓        |           ✓           |
| Voir occupation / charge des ressources     |       ✓       |       ✓      |         ✓         |                 ✓                 |         ✓        |           ✓           |
| Créer/modifier les données opérationnelles  |       ✓       |       ✓      |         ✓         |                 —                 |         ✓        |           —           |
| Documents : déposer/versionner/éditer       |       ✓       |       ✓      |         ✓         |                 —                 |         ✓        |           —           |
| Affecter des ressources aux tâches          |       ✓       |       ✓      |         ✓         |                 —                 |         ✓        |           —           |
| Administrer les participants du projet      |       ✓       |       ✓      |         ✓         |                 —                 |         —        |           —           |
| Administrer les sociétés intervenantes      |       ✓       |       ✓      |         ✓         |                 —                 |         —        |           —           |
| Modifier les paramètres du projet           |       ✓       |       ✓      |         ✓         |                 —                 |         —        |           —           |
| Clôturer le projet                          |       ✓       |       ✓      |         ✓         |                 —                 |         —        |           —           |
| Voir les données financières                |       ✓       |       ✓      |         ✓         |                 —                 |         —        |           —           |
| Modifier les données financières            |       ✓       |       ✓      |         ✓         |                 —                 |         —        |           —           |


le 12/09/2026
Tableau de décision
Rôle	Voir les données du projet	Administrer projet / lots	Travailler sur tâches, réunions, risques	Finances	Valider les rapports
Administrateur système	Oui	Oui	Oui	Oui	Oui
Administrateur client	Oui, dans son environnement	Oui	Oui	Oui	Oui
Chef de projet du projet	Oui	Oui	Oui	Oui	Oui
Chef de projet transverse	Oui	Non	Non	Non	Non
Utilisateur STANDARD	Oui	Non	Oui	Non	Non
Utilisateur READ_ONLY	Oui	Non	Non	Non	Non
Hors périmètre	Non	Non	Non	Non	Non

Règles déjà appliquées :

Transaction	Lecture	Écriture
Projet	Tous les rôles ayant visibilité	Administration projet
Lot de travaux	Tous les rôles ayant visibilité	Administration projet
Tâche	Tous les rôles ayant visibilité	Droit de travail
Réunion	Tous les rôles ayant visibilité	Droit de travail
Risque	Tous les rôles ayant visibilité	Droit de travail
Rapport d’activité personnel	Son rédacteur	Son rédacteur, avant transmission
Validation des rapports	Administrateurs projet	Administrateurs projet
Finance	À implémenter	Administrateurs projet

Pour les documents, la règle de base à mettre en œuvre sera : consultation pour les rôles ayant visibilité ; dépôt, modification, versionnement et suppression avec droit de travail. Les documents financiers devront ensuite être soumis au droit Finance.


| Action                                                           | Accès                                                               |
| ---------------------------------------------------------------- | ------------------------------------------------------------------- |
| Explorer, aperçu, téléchargement, CAO, favoris                   | Visibilité projet                                                   |
| Créer, importer, renommer, déplacer, copier, supprimer, dossiers | Droit de travail                                                    |
| Éditer avec OnlyOffice / prendre un verrou                       | Droit de travail                                                    |
| Callback OnlyOffice                                              | Authentification technique du fournisseur, sans session utilisateur |



| Fonction GED                                        | Lecture seule | Lecture / écriture |
| --------------------------------------------------- | ------------: | -----------------: |
| Explorateur, ouverture, aperçu, téléchargement, CAO |           Oui |                Oui |
| Favoris personnels                                  |           Oui |                Oui |
| Créer / importer un document                        |           Non |                Oui |
| Renommer, déplacer, copier, supprimer un document   |           Non |                Oui |
| Créer, renommer, déplacer, supprimer un dossier     |           Non |                Oui |
| Édition OnlyOffice et renouvellement du verrou      |           Non |                Oui |
