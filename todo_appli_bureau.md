### #############################
###     Application bureau
###        Environnement
### #############################

### Transaction Accueil
*A définir*

### Transaction Sociétés

### Transaction Contacts
Transaction : Tester un utilisateur avec plusieurs environnements client

### Transaction Licences

### Transaction client
Créer une arborescence type
Créer un projet type
Fonction de recherche des orphelins 
Fonction de recherche des fichiers bloqués en édition
Développer la transaction client avec les objets déjà définis

### Transaction Localisation des projets

### Transaction Risques

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

### Transaction Favoris

### Transaction Lots de travaux

### Transaction Tâches

### Transaction Planning
Global : Ajouter des commandes : Tout déplier, tout replier, déplier/replier lot
Gantt : RAS
Plan de charge : Aligner les colonnes Semaines 
Ressources : Pour chaque ressource indiquer son activité pour la semaine
Calendrier : Prévoir qu'une tâche peut durer seulement 1 jour
             Si une tâche sur plusieurs jours, afficher cette tâche pour chaque jour

### Transaction Réunions

### Transaction Mon rapport d'activité (RA)
Traiter le cas où l'utilisateur ne peut pas créer son propre RA. A saisir par le CP.
Offrir la possibilité de visualiser les RA déjà émis pour utilisateur (par exemple depuis le popup menu à gauche en bas d'écran)

### Transaction Validation des RA
Liste : Adopter le même look que les autres listes (Ultérieurement)
Transaction : Quand un RA est à traiter par le CP, il faudrait le notifier avec le compteur des notifications.


### #############################
###     Application bureau
###    Gestion documentaire
### #############################

### Documents
Implémenter Partager et Permissions
Il faudra ajouter l'administrateur système comme ayant droit de supprimer des fichiers (contenu illicite)

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

DOE à jour — recommandé
Le document source mis en corbeille n’est plus repris au prochain rafraîchissement. Sa copie DOE actuelle reste visible jusqu’à ce rafraîchissement.


### Signature électronique
Oui : par un webhook Documenso.
À chaque signature ou fin de signature, Documenso appelle une URL d’Easy Projet. L’application pourra alors :
- mettre à jour le statut des signataires et de la demande ;
- enregistrer la date de fin ;
- récupérer le PDF signé final ;
- créer une notification Easy Projet pour les utilisateurs concernés.
Ce n’est pas encore câblé dans le code : l’adaptateur sait déjà vérifier le secret webhook, mais il faut ajouter la vue de réception et le traitement des événements.
Comme Easy Projet est actuellement sur localhost, Documenso Cloud ne peut pas l’appeler directement. Pour les essais, il faudra exposer temporairement le serveur Django via un tunnel HTTPS Cloudflare ; en production, l’URL publique du serveur sera utilisée. Documenso prévoit explicitement les webhooks pour suivre ces événements. docs.documenso.com

A terme, l’utilisateur choisira n’importe quel document compatible, sans se soucier du PDF.


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


### IA
Pour le planning et le plan de charge, l’IA pourrait analyser :
- tâches, dépendances, jalons et dates ;
- charges prévues par métier et par personne ;
- disponibilités, surcharges et compétences ;
- retards ou incohérences de planification.
Elle retournerait par exemple :
- les surcharges détectées ;
- des scénarios de décalage ou de réaffectation ;
- les métiers manquants sur une période ;
- l’incidence de chaque proposition sur les dates et charges ;
- les hypothèses utilisées.
Point important : le calcul fiable des contraintes restera dans l’application — et éventuellement un solveur d’optimisation plus tard. L’IA sert surtout à interpréter la situation, comparer des scénarios et formuler des recommandations compréhensibles.
Pour la documentation, elle pourrait :
- résumer un document ou un dossier ;
- classer automatiquement les documents ;
- extraire les éléments importants d’un CCTP, d’un compte rendu ou d’un devis ;
- répondre à une question en citant précisément les documents source ;
- détecter les pièces manquantes dans un DOE.
Architecture cible simple :
- un module apps/ai ;
- une demande IA historisée : données transmises, utilisateur, date, objectif ;
- une réponse structurée et validée avant affichage ;
- des recommandations avec statut : proposée, acceptée, refusée, appliquée ;
- aucune donnée métier modifiée sans action explicite de l’utilisateur ;
- journalisation des décisions et des sources documentaires utilisées.
Je conseille de commencer par le planning en mode analyse seule : détection des surcharges, incohérences et risques de délai, sans optimisation automatique. C’est le cas le plus concret pour valider l’utilité et l’ergonomie avant d’étendre à la GED.


L’IA n’a aucun accès direct à votre serveur, à votre base de données ou à vos documents.
Le fonctionnement actuel est le suivant :
1. Easy Projet lit les données autorisées côté serveur.
2. Il prépare un extrait : tâches, dates, charges, ressources, besoins métiers, question et historique.
3. Cet extrait est envoyé à l’API OpenAI avec la clé stockée sur votre serveur.
4. OpenAI renvoie une réponse textuelle.
5. Easy Projet l’affiche, sans écriture automatique dans vos données.
Pour l’assistant de la topbar, seules la question et les quelques messages précédents sont transmis. Pour le Planning, les données calculées du projet sélectionné sont également transmises.
L’API ne reçoit donc que les informations que nous choisissons explicitement de lui envoyer ; elle ne peut ni parcourir la base, ni consulter les fichiers GED, ni agir dans l’application.

Je recommande cet ordre :
1. Conversion ciblée des écrans non conformes au standard
   Stabilise les composants, l’ergonomie et évite de dupliquer des écarts.
2. Transaction client / documentation
   Nous venons de travailler sur ce module ; recherche, fichiers bloqués et arborescences de types le rendront réellement exploitable.
3. OPR : photos, plans et modifications
   Le socle documentaire sera alors prêt pour ces pièces terrain.
4. Application terrain
   Elle pourra s’appuyer directement sur les flux OPR stabilisés.
5. Dashboards
   À traiter après consolidation des données opérationnelles, pour produire des indicateurs utiles et fiables.
Je commencerais par la conversion ciblée, puis la documentation.

-------------------------
Je retiens donc les règles suivantes :
- aucune arborescence « par défaut » ;
- le choix d’une arborescence est obligatoire lors de la création d’un projet ;
- seuls les modèles actifs, ayant au moins un dossier actif, sont proposés ;
- le modèle doit appartenir à l’environnement client correspondant à la société du projet ;
- le modèle est copié une seule fois ; une modification ultérieure du projet ne le réapplique jamais ;
- l’option is_default, son bouton et les routes associées seront supprimés de la configuration client.
Le futur choix DOE suivra le même principe.


Cas	Génération initiale	IA, ultérieurement
Modèle DOE choisi	Création de la structure du modèle, puis dépôt de tous les documents taggés dans un répertoire d’entrée du DOE, par exemple À classer.	Proposition de déplacement des documents vers les répertoires du modèle. Validation opérateur avant application.
Aucun modèle disponible	Génération du DOE en reproduisant l’arborescence et les noms des documents taggés.	Analyse de la structure produite et proposition de corrections de classement. Validation opérateur avant application.


Le dépôt temporaire À classer évite tout classement arbitraire avant décision de l’IA ou de l’opérateur. Les documents générés restent des copies DOE : les originaux ne sont jamais déplacés ni modifiés.

La première étape consiste donc à créer les modèles DOE dans la configuration client et à adapter la demande de génération pour proposer le choix lorsqu’au moins un modèle actif existe. L’assistance IA viendra ensuite comme une proposition réversible, jamais comme un déplacement automatique.
Oui. La règle devient :
- modèles DOE disponibles : l’opérateur peut en choisir un ou sélectionner « Sans modèle » ;
- modèle choisi : création de sa structure, avec les documents taggés déposés dans À classer ;
- aucun modèle choisi, volontairement ou faute de modèle disponible : génération classique par reproduction de l’arborescence source des documents taggés.
L’IA pourra ensuite proposer un classement ou des corrections dans les deux cas.