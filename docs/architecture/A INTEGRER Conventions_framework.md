

Le document 02-conventions.md serait la référence des comportements implicites du framework.

Exemple :

Propriété	Valeur par défaut	Justification
visible	True	Un champ est visible sauf indication contraire
required	False	La validation est explicite
width	auto	Le Design System gère l'espace disponible
truncate	True	Les listes restent lisibles
readonly	False	Le formulaire est modifiable par défaut


docs/architecture/
    03-conventions-framework.md

Il contiendrait :

le rôle des conventions ;
leur emplacement (framework/defaults) ;
les règles d'utilisation ;
les valeurs par défaut existantes ;
les règles pour en ajouter de nouvelles.

Ce document deviendrait la référence. Ainsi, dans six mois, nous n'aurons pas à rediscuter de la question « où doit vivre une valeur par défaut ? ».