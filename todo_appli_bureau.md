### #############################
###     Application bureau
###        Environnement
### #############################

### Transaction Accueil
*A définir*

### Transaction Sociétés
Liste : RAS
Transaction : RAS

### Transaction Contacts
Liste : RAS
Transaction : Tester un utilisateur avec plusieurs environnements client

### Transaction Licences
Liste : Ras
Transaction : RAS

### Transaction client
Crééer une arborescence type
Créer un projet type
Fonction de recherche des orphelins 
Fonction de recherche des fichiers bloqués en édition
Développer la transaction cliet avec les objets déjà définis

### Transaction Localisation des projets
RAS

### Transaction Risques
Liste : RAS
Transaction : RAS

### Transaction Intégrations externes
Liste : Distinguer une intégration externe globale (proposée par Axcio-Data) d'une intégration privée
Transaction : Ajouter un flag : Globale ou Privée

### Transaction Dashboard
A faire :
- dashboard Société ;
- dashboard multi-projets / CP ;
- choix des agrégats et navigation entre niveaux.


### #############################
###     Application bureau
###         Mes projets
### #############################

### Transaction Projets
Liste : RAS
Transaction : RAS

### Transaction Favoris
Liste : Offir les mêmes actions sur le fichier que dans l'arborescence

### Transaction Lots de travaux
Liste : RAS
Transaction : RAS

### Transaction Tâches
Liste : RAS
Transaction : RAS

### Transaction Planning
Global : Ajouter des commandes : Tout déplier, tout replier, déplier/replier lot
Gantt : RAS
Plan de charge : Aligner les colonnes Semaines 
Ressources : Pour chaque ressource indiquer son activité pour la semaine
Calendrier : Prévoir qu'une tâche peut durer seulement 1 jour
             Si une tâche sur plusieurs jours, afficher cette tâche pour chaque jour

### Transaction Réunions
Liste : RAS
Transaction : RAS

### Transaction Mon rapport d'activité (RA)
Traiter le cas où l'utilisateur ne peut pas créer son propre RA. A saisir par le CP.
Offrir la possibilité de visualiser les RA déjà émis pour utilisateur (par exemple depuis le popup menu à gauche en bas d'écran)

### Transaction Validation des RA
Liste : Adopter le même look que les autres listes 
        Ajoputer un bouton Quitter
Transaction : Quand un RA est à traiter par le CP, il faudrait le notifier avec le compteur des notifications.


### #############################
###     Application bureau
###    Gestion documentaire
### #############################

### Documents
Mettre les fichiers supprimés dans une corbeille lors de la suppression initiale
Implémenter Partager et Permissions

### Affichage des répertoires

### Import photos
??? Pour la suite, je garderais en tête deux évolutions seulement : preview_fit différencié entre photo utilisateur (cover) et logo société (contain), puis plus tard une vraie sélection de société active si le modèle multi-société évolue. Pour l’instant, ce n’est pas bloquant. ???

### DOE
Je la formaliserais ainsi :
1. Générer le DOE : sélection des documents marqués « Intégrer au DOE ».
2. L’application transmet à l’IA les métadonnées utiles : nom, type, lot, description, version, statut, auteur, éventuellement contenu textuel exploitable. La seule liste de noms de fichiers sera souvent insuffisante.
3. L’IA reçoit également le modèle d’arborescence DOE vierge.
4. L’IA retourne une proposition structurée :
   document → dossier cible, avec éventuels documents non classés et raisons.
5. Easy Projet génère un DOE brouillon : arborescence, copies des fichiers et index.
6. Le CP ou son adjoint ajuste le classement, ajoute ou exclut des documents, puis valide.
7. La validation fige une version du DOE et produit le ZIP ainsi que l’index PDF.

### Signature électronique
Oui : par un webhook Documenso.
À chaque signature ou fin de signature, Documenso appelle une URL d’Easy Projet. L’application pourra alors :
- mettre à jour le statut des signataires et de la demande ;
- enregistrer la date de fin ;
- récupérer le PDF signé final ;
- créer une notification Easy Projet pour les utilisateurs concernés.
Ce n’est pas encore câblé dans le code : l’adaptateur sait déjà vérifier le secret webhook, mais il faut ajouter la vue de réception et le traitement des événements.
Comme Easy Projet est actuellement sur localhost, Documenso Cloud ne peut pas l’appeler directement. Pour les essais, il faudra exposer temporairement le serveur Django via un tunnel HTTPS Cloudflare ; en production, l’URL publique du serveur sera utilisée. Documenso prévoit explicitement les webhooks pour suivre ces événements. docs.documenso.com

### #############################
###     Application bureau
###     Fonctions communes
### #############################
Listes : Impossible de sortir de la liste des colonnes si on ne fait pas appliquer
Si on sélectionne un article en page 2, après rafraichissement, on revient en page 1
Rester sur la page en cours

### Ergonomie
Fonction disponible → affichage normal et action active.
Fonction prévue mais non implémentée → grisée + italique + désactivée + infobulle « Fonction à venir ».

### Login
Donner la possibilité de visualiser le mot de passe lors de la saisie

### Formulaires
Revoir la hauteur des sections
Revoir le nombre de champs de saisie par ligne

### CSS

### Boites de dialogue


### #############################
###     Application bureau
###     Travaux d'ensemble
### #############################

### Fin recherche sécurité niveau 1
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

### Homogénéiser les arborescences de déveoppement
dans apps certains ont des fichiers test dans la racine, d'autres les tests sont dans un répertoire dédieé.
A harmoniser

--------------------------------------------------------------------------
### Feuille de route
1 - Achever le cœur fonctionnel Easy Projet. 
Nous terminons les attributions métier des utilisateurs, les rôles, périmètres et autorisations Level 2, puis les éventuels points fonctionnels indispensables pour disposer d'une V1 réellement exploitable. Ensuite, tu constitues un jeu de données/test représentatif du fonctionnement réel d'une entreprise, nous faisons une campagne de tests fonctionnels et de non-régression, puis une passe d'ergonomie sur l'ensemble. Le résultat attendu est une première version opérationnelle et cohérente, indépendamment des enrichissements futurs.

2 - Consolider la documentation. 
Nous faisons l'inventaire de ce qui existe et de ce qui est devenu obsolète. À partir de cette matière et du logiciel réellement construit, nous reconstituons une chaîne documentaire cohérente : CdCF → conception générale → conception détaillée → framework → manuel utilisateur. Pour la conception générale, des figures PowerPoint sont effectivement adaptées : architecture fonctionnelle, silos ClientEnvironment, acteurs et périmètres, architecture applicative, flux documentaires, intégrations, etc. C'est également dans ce bloc que nous consoliderons toutes les règles métier décidées au fil du développement. Il faudra distinguer ce qui relève de la spécification de ce qui relève du manuel utilisateur.

3 - Reprendre les intégrations externes et l'IA. 
Une fois le noyau stabilisé et documenté, nous réévaluons les intégrations déjà expérimentées ou envisagées — GED, ONLYOFFICE, CADViewer, signature électronique, messagerie/Teams, workflows, etc. — avec une architecture d'orchestration homogène. Puis nous abordons l'IA sur une base métier stable : aide au découpage des tâches, ressources, rappels, comptes rendus, DOE, recherche documentaire, etc.

Un point me paraît particulièrement important dans ton séquencement : ne pas chercher maintenant à produire le manuel utilisateur définitif. Nous devons bien enregistrer les règles métier au fur et à mesure, mais la rédaction structurée du manuel gagnera à intervenir après la stabilisation fonctionnelle et la passe ergonomique. Sinon nous documenterions des écrans et des parcours qui vont encore évoluer.

### Messagerie interne , Notifications , ToDo
Élément              Rôle
Messagerie interne	Échanges humains, par projet, avec contenu, réponses et pièces jointes.
Notifications	      Alerte système personnelle, courte, avec un lien vers l’objet concerné.
Mes ToDO	            Travail que l’utilisateur doit effectuer ou suivre.
Les notifications devraient couvrir uniquement les événements qui demandent une attention :
- invitation, modification ou annulation de réunion ;
- tâche affectée ou retirée ;
- nouveau rapport d’activité à saisir ;
- rapport d’activité à valider ou à reprendre ;
- document à relire ou à valider ;
- risque, réserve ou action assignée ;
- nouveau message interne : la notification ouvre alors le message, mais ne le remplace pas ;
- échéance proche ou dépassée.


### Ecrans à reprendre pour normalisation framework
Le premier relevé donne 23 templates contenant une balise <form>, mais ce ne sont pas 23 écrans à reprendre.
Catégorie	                        Éléments	                                       Conclusion
Composants techniques ou fragments	Sidebar, actions utilisateurs, panneau messages, 
                                    filtre planning, dialogues dossiers, template 
                                    edf/form/view.html	                                À exclure du décompte des écrans
Déjà normalisés ou hybrides	      Formulaire réunion, import documentaire	           Pas une priorité ; à examiner au 
                                                                                        cas par cas
Écrans spécifiques métier	        Connexion, changement de mot de passe, messagerie, 
                                    Todo, reporting, photo projet, configuration client	Rendu spécifique souvent justifié
Écran clairement hors framework	    apps/documents/templates/documents/                 Candidat immédiat à la migration
                                    document_form.html	                                


Le résultat le plus significatif est le troisième :
apps/documents/templates/documents/document_form.html
apps/documents/templates/documents/document_import.html

- document_form.html est bien un formulaire à reprendre plus tard.
- document_import.html utilise déjà render_ep_field, mais possède aussi un rendu direct ponctuel. Il est donc hybride, pas forcément à réécrire entièrement.
À ce stade, je ne vois pas une dette massive : il y a surtout un écran documentaire manifestement non aligné, puis plusieurs écrans métier spécialisés dont la normalisation devra être décidée selon leur intérêt.
Je propose, quand le fonctionnel documentaire sera stabilisé, de faire un inventaire priorisé de ces écrans :
1. Création de document ;
2. Import documentaire ;
3. Formulaires de configuration client ;
4. Formulaires de reporting ;
5. Dialogues et formulaires spécialisés, seulement si leur ergonomie reste insuffisante.



