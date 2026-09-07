

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