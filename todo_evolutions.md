
### Formulaires


### Transaction Tâches
- Concaténer les sections Rattachement et Identification
- Afficher dans la liste des tâches le nombre de ressources affectées

comme fonction transversale de workflow / file d’actions

Je recommande donc :
- ne rien supprimer immédiatement du modèle ;
- ne pas verrouiller les dates « initiales » dès la première sauvegarde ;
- considérer les dates actuelles start_date / end_date comme le planning courant, pas comme le réel ;
- conserver les dates initiales comme une première référence, mais les renommer ultérieurement Début/fin de référence ;
- à terme, remplacer ces champs par une vraie transaction « Valider le planning de référence », qui crée un instantané complet du projet, de ses lots et de ses tâches.

Ainsi, une erreur de saisie se corrige normalement sans devoir supprimer la tâche, et le décalage reste mesurable entre planning de référence et planning courant.

### Planning

### Transaction client
Crééer une arborescence type
Créer un projet type
Fonction de recherche des orphelins 
Fonction de recherche des fichiers bloqués en édition

### Documents
Pourquoi télécharger le document l'ouvre automatiquement sur le poste client?
Mettre les fichiers supprimés dans une corbeille lors de la suppression initiale
Implémenter Partager et Permissions

Traiter dans un second temps le renouvellement/expiration en session
Future page de maintenance des verrous.
Sans l'implémenter maintenant on pourrait aussi mettre un batch qui au démarrage du serveur débloque les verrous.

### CSS

### Réunions

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

### Rapports d'activité
Traiter le cas où l'utilisateur ne peut pas créer son propre RA. A saisir par le CP.
Quand un RA est à traiter par le CP, il faudrait le notifier avec le compteur des notifications.

### Sociétés

### Risques
Concaténer les sections Rattachement et Identification et la mettre en tête du formulaire

### Contacts
Liste : réduire la hauteur des lignes pour avoir une page entière à l'écran

### Formulaires
Revoir la hauteur des sections
Revoir le nombre de champs de saisie par ligne

## Lots de travaux

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
Projet inactif. On ne peut pas voir les éléments du projet. 

### Transaction licences
Liste des licences : n'afficher que les licences de la société de l'utilisateur

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

### Homogénéiser les arborescence
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
Élément             Rôle
Messagerie interne	Échanges humains, par projet, avec contenu, réponses et pièces jointes.
Notifications	    Alerte système personnelle, courte, avec un lien vers l’objet concerné.
Mes ToDO	        Travail que l’utilisateur doit effectuer ou suivre.
Les notifications devraient couvrir uniquement les événements qui demandent une attention :
- invitation, modification ou annulation de réunion ;
- tâche affectée ou retirée ;
- nouveau rapport d’activité à saisir ;
- rapport d’activité à valider ou à reprendre ;
- document à relire ou à valider ;
- risque, réserve ou action assignée ;
- nouveau message interne : la notification ouvre alors le message, mais ne le remplace pas ;
- échéance proche ou dépassée.

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


### Ecrans à reprendre pour normalisation framework
Le premier relevé donne 23 templates contenant une balise <form>, mais ce ne sont pas 23 écrans à reprendre.
Catégorie	                        Éléments	                                       Conclusion
Composants techniques ou fragments	Sidebar, actions utilisateurs, panneau messages, 
                                    filtre planning, dialogues dossiers, template 
                                    edf/form/view.html	                                À exclure du décompte des écrans
Déjà normalisés ou hybrides	        Formulaire réunion, import documentaire	            Pas une priorité ; à examiner au 
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

Le bon choix est une application web responsive unique, avec un mode « terrain » plutôt qu’une application mobile distincte.
Même URL, mêmes comptes, mêmes droits et mêmes services métier ; seule l’interface s’adapte au téléphone et au rôle. Cela évite de dupliquer les règles de gestion et garantit que les données sont immédiatement partagées avec le bureau.
Le mode terrain pourrait proposer un menu très réduit :
- Mes tâches : à faire, en cours, terminées ;
- Mes projets : accès au projet courant et à ses informations essentielles ;
- Documents et plans : consultation rapide ;
- Photos : prise de photo, classement dans un album, annotation ultérieurement ;
- Réunions / consignes : convocations, comptes rendus, actions ;
- Signalements : risque, réserve ou remarque avec photo ;
- Notifications.
L’écran d’accueil ne doit pas être une reproduction du tableau de bord bureau : il doit répondre à « que dois-je faire maintenant ? » et « que puis-je consulter ou signaler sur ce chantier ? ».
Techniquement, il faudra privilégier :
- gros boutons et zones tactiles ;
- peu de colonnes, plutôt des cartes ;
- actions en un ou deux gestes ;
- appareil photo et partage de fichiers du navigateur ;
- chargements légers ;
- droits déjà existants, appliqués sans exception.
Une PWA installable pourra être ajoutée plus tard, sans changer l’application : raccourci sur l’écran d’accueil, cache des écrans essentiels et, éventuellement, synchronisation différée pour les zones sans réseau.

Priorités ergonomiques :
- une action principale par écran ;
- vocabulaire chantier, sans termes techniques ;
- boutons visibles, libellés explicites et icônes en complément ;
- accès direct aux tâches, photos, documents et signalements ;
- pas de tableaux larges ni de formulaires longs ;
- conservation automatique des brouillons quand elle sera nécessaire.
L’objectif : un utilisateur doit pouvoir consulter une consigne, prendre une photo ou signaler un problème sans formation.