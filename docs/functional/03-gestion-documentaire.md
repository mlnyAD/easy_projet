

### Gestion documentaire

1. Objet
   Définir les objectifs de la gestion documentaire.

2. Règles générales
   Quels documents sont concernés ?
      - Tout document pouvant être échangé au cours de la vie du projet
   Quel est leur cycle de vie ?
      - Les documents vivent avec le projet. Le document est créé au cours de la réalisation du projet puis suit les règles d’archivage qui régissent le projet

3. Fonctions offertes
   - éditer       -> Créer/Modifier/Enregistrer un document
   - consulter    -> Visualiser/Ecouter un document
   - naviguer     -> Permettre la navigation dans l'arborescence
   - diffuser     -> Transmettre un document à un ou n destinataires soit par mail, soit par messagerie instantanée
   - versionner   -> Stocker (ou savoir retrouver) les différentes éditions d’un document
   - archiver     -> Faire un archivage dans une zone donnée avec ou sans la possibilité de le modifier ultérieurement
   - supprimer    -> Détruire le document. Dépôt dans une corbeille. Puis suppression définitive 
   - signer       -> Apposer/ou demander une signature électronique au document	
   - notifier     -> Prévenir un contact que le document est disponible
   - dupliquer    -> Faire une copie du document (sous un nouveau non pour l’éditer par exemple)
   - partager     -> Permettre l’accès au document depuis une url ou un QR Code 
   - lier         -> Lier 2 documents ensemble ou un évènement et un document. Par exemple le plan d’un local et sa photo.
   - télécharger  -> Permettre de créer un document par l’import depuis un environnement externe. 
   - téléverser   -> Opération inverse
   - DOE          -> Sélectionner le document pour intégrer le DOE
   - imprimer     -> Assurer l’impression du document vers l’imprimante locale

4. Contraintes métier
   - conservation -> Assurer la conservation du document sur une période donnée 
   - traçabilité  -> Connaitre les intervenants sur un document
   - droits d'accès  -> Ne permettre l'accès au docuement qu'aux seules personnes autorisées
   - intégrité    -> Garantir qu'un document n' pas été modifié

5. Évolutions possibles
   - IA     -> Résumé d'un texte, traduction d'un texte, modification image, classement d'une liste de documents

6. Formats des documents (non exhaustif)
   - Texte  -> Formats : doc, docx, xls, xlsx, ppt, pptx, pdf, …
   - Image  -> Formats : jpg, jpeg, …
   - Vidéos -> Formats : mov, api, mp4, …
   - Sons   -> Formats : wav, ogg, mp3, …
   - Plans  ->	Formats : dwg

7. Outils externes
Sur ses autres produits Axcio-Data utilise des logiciels externes. L’idéal serait que chaque société puisse décider des outils externes qu'elle souhaite utiliser.

ONLY OFFICE
OnlyOffice est utilisé pour la création/modification des documents de type Word, Excel et Powerpoint.
Cet outil est utilisé par défaut. Voir si on peut utiliser Microsoft Office si celui-ci est installé sur le poste client.

CAD VIEWER
CAD Viewer est un outil de visualisation des fichier AutoCAD, extension DWG, …

8. Divers
Est-ce que la prise d'images, de vidéo est fréquente sur un chantier ?	Oui
Faut-il faire des impressions ?	Oui
Nombre d’utilisateurs simultanés?	30 utilisateurs simultanés
Nombre d’enregistrements « vivants »?	50 000 documents
Nombre de documents GED?	50 000 enregistrements métiers

9. Décisions retenues
- stockage documentaire interne obligatoire à Easy Projet ;
- héritage des droits applicatifs existants, sans ACL documentaire spécifique en V1 ;
- les fichiers sont pérennes, les outils externes sont interchangeables.
- La navigation documentaire propose au minimum deux modes d’affichage interchangeables : liste détaillée et grille d’icônes. Les fonctions de sélection, ouverture, menu contextuel et actions groupées restent disponibles dans les deux modes.
- Le titre du document est libre et indépendant du nom de fichier ;
- Le numéro de version est un simple entier 1, 2, 3 ;