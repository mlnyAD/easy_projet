

#-----------------------------------------------------------
#
# Organisation répertoire docs
#
#-----------------------------------------------------------

# Chaque dossier du répertoire docs a un rôle précis :
# adr/ : les décisions d'architecture.
# architecture/ : les schémas d'ensemble (apps, dépendances, architecture logicielle...).
# functional/ : les spécifications métier et les règles de gestion.
# technical/ : les conventions techniques, procédures d'installation, guides de développement.
# development/ : les notes utiles au développement (check-lists, guides de migration, procédures internes...).



## Comportement planning

- À partir de 1200 px : vue mixte Données + Chronologie ; le séparateur est
  déplaçable, au clavier avec les flèches et réinitialisable par double-clic.
- Sous 1200 px : choix exclusif entre les vues Données et Chronologie.
- Les barres représentent l'avancement déclaré (`progress_percent`) ; la date
  de situation reste une ligne verticale de référence.
- Les initiales des ressources sont regroupées près de l'élément et, pour les
  tâches, à l'intérieur de la barre lorsqu'il y a assez de place.
- Les noms et les barres sont des liens vers la transaction correspondante.

