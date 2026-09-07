
### Formulaires
Voir si on peut afficher les champs sur 1, 2, 4 champs par ligne


### Transaction Tâches
- Étudier une fiche tâche unifiée présentant sur une même page :
  - les informations de la tâche ;
  - les ressources affectées.
- Afficher dans la liste des tâches l'état de l'affectation :
  - nombre de ressources affectées ;
  - indicateur explicite lorsqu'aucune ressource n'est affectée.
- Conserver la possibilité de créer volontairement une tâche sans
  ressource : l'absence d'affectation doit être visible, mais ne doit
  pas nécessairement être bloquante.
Réduire les oublis d'affectation sans rigidifier le processus de
planification.


comme fonction transversale de workflow / file d’actions


### Planning
Faire du Master/détail quand c'est possible
tous les projets
  tous les lots
    toutes les âches
Rendre les barres de tâche sélectionnables

### Documents
Fonction de recherche des orphelins 
Fonction de recherche des fichiers bloqués en édition
Pourquoi télécharger le document l'ouvre automatiquement sur le poste client?
Mettre les fichiers supprimés dans une corbeille lors de la suppression initiale
Implémenter Partager et Permissions

Traiter dans un second temps le renouvellement/expiration en session
Future page de maintenance des verrous.
Sans l'implémenter maintenant on pourrait aussi mettre un batch qui au démarrage du serveur débloque les verrous.


### CSS
Revoir les définition de bg-axcio-dark et bg-axcio-light
Nettoyage des couleurs en dur dans le code
Faut-il conserver tailwind?

### Ergonomie
Fonction disponible → affichage normal et action active.
Fonction prévue mais non implémentée → grisée + italique + désactivée + infobulle « Fonction à venir ».

### Boites de dialogue
Adopter une position géographique commune pour toutes les modales.
En haut au milieu me parait bien

### Intégrations externes
Libellés trop proche Gestion docuementaire et Suite bureautique

### Affichage des répertoires
Faut-il fermer automatiquement un répertoire ouvert lorsqu'on en sélectionne un autre?

### Dashboard
A faire :
- dashboard Société ;
- dashboard multi-projets / CP ;
- choix des agrégats et navigation entre niveaux.

### Sociétés
SIRET : Placeholder affiche un format qui n'est pas repris après la saisie
PAYS : Mettre par défaut la France en présaisie
Liste des sociétés : mettre un badge sur les sociétés ayant au moins un licence

### Contacts
1er caractère du prénom en MAJ
Liste : réduire la hauteur des lignes pour avoir une page entière à l'écran

### Formulaires
Revoir la hauteur des sections
Revoir le nombre de champs de saisie par ligne

## Lots de travaux
Liste : Revoir les critères de filtres

### Import photos
Pour la suite, je garderais en tête deux évolutions seulement : preview_fit différencié entre photo utilisateur (cover) et logo société (contain), puis plus tard une vraie sélection de société active si le modèle multi-société évolue. Pour l’instant, ce n’est pas bloquant.

### Login
Donner la possibilité de visualiser le mot de passe lors de la saisie
Dans la liste des utilisateurs, ne pas mettre les icônes superposées mais en ligne

### Affichage des listes
Si on sélectionne un article en page 2, après rafraichissement, on revient en page 1
Rester sur la page en cours

### Transaction projet
Rubrique Chef de projet : ne proposer que des utilisateurs de sociétés l'environnement client
Rubrique utilisateurs : ne proposer que des utilisateurs de sociétés l'environnement client

### Transaction licences
Liste des licences : n'afficher que les licences de la société de l'utilisateur


### Fin recherche sécurité niveau 1
Reste à faire
Sujet restant	Nature	Priorité / moment
OnlyOffice callback : endpoint volontairement sans validation JWT ; UUID de version + URL fournie au callback	Sécurité	À traiter en durcissement sécurité
Téléchargement OnlyOffice depuis une URL fournie par le callback : risque potentiel de SSRF si origine/schéma non contrôlés	Sécurité	Important, avant production
Locks d'édition : nettoyage des verrous expirés au démarrage	Maintenance	Plus tard
Locks d'édition : outil admin pour débloquer un verrou coincé	Exploitation	Plus tard
Documents : contrôle des fichiers orphelins / cohérence stockage-base	Maintenance	Plus tard
Documents : contrôles complémentaires de cohérence des versions	Maintenance	Plus tard
OnlyOffice JWT : remplacer le secret actuel par un secret ≥ 32 octets	Configuration sécurité	Avant production
Licences / intégrations : masquer dans l'IHM les actions création/modification pour les rôles en lecture seule	Ergonomie / Niveau 2	Avec les droits/IHM
Mot de passe : œil afficher/masquer	Ergonomie	TODO évolution
Email catch-all Axcio Data : délais irréguliers	Infrastructure externe	À surveiller, pas bloquant
ProjectCompany et visibilité des salariés des sociétés participantes	Autorisations métier	Niveau 2
CLIENT_ADMIN pouvant potentiellement attribuer SYSTEM_ADMIN	Sécurité des autorisations	À traiter au début du Niveau 2

### Homogénéiser les arborescence
dans apps certains ont des fichiers test dans la racine, d'autres les tests sont dans un répertoire dédieé.
A harmoniser