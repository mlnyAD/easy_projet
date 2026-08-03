


On n'y parlerait pas de Tailwind ni de CSS, mais des principes ergonomiques d'Easy Projet.

voir s'il peut aussi servir de charte graphique  --> homogénéité de l'IHM

Quelques chapitres pourraient être :

1. Principes généraux
2. Couleurs
3. Typographie
4. Listes
5. Formulaires
6. Notifications
7. Dialogues
8. Icônes
9. Accessibilité
10. Ergonomie passive
11. À étudier

La dernière rubrique, "À étudier", me paraît importante. Elle permettra de noter les idées sans décider immédiatement de leur mise en œuvre. Par exemple :

barre de progression des Toasts ;
empilage en cascade des Toasts ;
alternance légère de couleur des lignes de listes ;
animation très discrète lors de l'apparition des notifications ;
homogénéisation des couleurs d'état.

Ainsi, rien ne se perd et nous gardons une vision de ce qui reste à affin

Ce document deviendrait la référence pour les futurs développements. Ainsi, lorsque nous créerons les modules Planning, Documents, Réunions ou Risques, nous n'aurons plus à rediscuter ces choix : ils seront déjà définis et l'application conservera une identité visuelle et ergonomique homogène.


Toute évolution ergonomique doit apporter une aide implicite, sans interrompre le travail de l'utilisateur.

Une bonne IHM ne demande pas à l'utilisateur de réfléchir à son fonctionnement. Elle l'accompagne discrètement. Chaque détail pris isolément semble anodin, mais leur accumulation produit une différence très sensible après plusieurs heures d'utilisation.

Jusqu'à présent, nous avons déjà construit plusieurs de ces "micro-aides" :

dates au format français ;
Oui / Non au lieu de True / False ;
libellés des catalogues au lieu des codes ;
tooltips au survol ;
formulaires plus compacts ;
sections mieux structurées ;
champs éditables légèrement colorés ;
toasts non bloquants.

Aucune de ces améliorations n'est spectaculaire, mais ensemble elles rendent l'application plus naturelle.

Je proposerais d'ajouter un principe dans notre Design System

Toute évolution ergonomique doit apporter une aide implicite, sans interrompre le travail de l'utilisateur.

Cela deviendrait un critère de conception.

Par exemple :

un toast informe sans imposer un clic ;
un fond coloré indique où l'on peut agir ;
une ligne survolée aide à suivre la lecture ;
un tooltip apparaît uniquement lorsqu'on en a besoin.

À l'inverse, nous éviterons autant que possible :

les boîtes de dialogue inutiles ;
les confirmations systématiques ;
les messages qui masquent l'écran ;
les couleurs agressives.

