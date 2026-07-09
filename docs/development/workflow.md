

# Méthode de développement Easy Projet

Chaque sujet de développement suit le cycle suivant :

1. Analyse
2. Conception
3. Validation
4. Développement
5. Tests
6. Documentation
7. Clôture du sujet

## Definition of Done

Un sujet est considéré comme terminé uniquement si les points suivants sont validés :

* conception validée ;
* développement terminé ;
* absence de duplication inutile ;
* `python manage.py check` sans erreur ;
* migrations créées et relues si concerné ;
* migrations appliquées si nécessaire ;
* documentation mise à jour ;
* `CHANGELOG.md` mis à jour ;
* ADR créée ou mise à jour si la décision est structurante ;
* commit Git réalisé.

## Règles sur les migrations

Une migration Django n'est pas considérée comme un simple fichier généré automatiquement.

Avant exécution, elle doit être relue pour vérifier :

* les noms de tables ;
* les types de champs ;
* les contraintes ;
* les clés étrangères ;
* les règles `on_delete` ;
* les index ;
* les contraintes d'unicité.

## Niveaux de décision

Lorsqu'une question se pose, il faut identifier son niveau :

1. Métier
2. Modèle
3. Implémentation

La correction doit être apportée au bon niveau.
