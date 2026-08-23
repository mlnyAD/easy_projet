

# Architecture de la gestion documentaire

## 1. Objet

La gestion documentaire d'Easy Projet fournit les fonctions
documentaires nécessaires à la réalisation et au suivi des projets.

Easy Projet n'a pas vocation à devenir une GED généraliste ou un
produit GED autonome.

La gestion documentaire reste intégrée au fonctionnement métier
d'Easy Projet.

---

## 2. Principes d'architecture

### 2.1 Easy Projet reste propriétaire des documents

Les fichiers sont stockés dans l'infrastructure maîtrisée par
Easy Projet.

Un outil externe peut :

- visualiser un document ;
- modifier un document ;
- signer un document ;
- convertir un document.

Il ne devient jamais le stockage de référence du document.

Le fichier de référence reste sous le contrôle d'Easy Projet.

---

### 2.2 Séparation Document / fichier

Le document est un objet métier durable.

Le fichier correspond à une version physique du document.

Exemple :

Document
    Note technique ventilation

Versions
    V1 -> note_ventilation.docx
    V2 -> note_ventilation.docx
    V3 -> note_ventilation.docx

Un changement de version ne crée pas un nouveau Document.

---

### 2.3 Versionnement natif

Le versionnement fait partie du noyau documentaire dès la V1.

Chaque modification entraînant la conservation d'un nouvel état
du fichier crée une nouvelle DocumentVersion.

Une version existante n'est pas écrasée.

---

### 2.4 Indépendance vis-à-vis des outils externes

Un document n'est jamais associé durablement à un logiciel
d'édition ou de visualisation.

Easy Projet distingue :

- le format technique du fichier ;
- la capacité nécessaire ;
- l'outil configuré pour la société.

Exemples de capacités :

- OFFICE_EDIT ;
- OFFICE_VIEW ;
- CAD_VIEW ;
- PDF_VIEW ;
- IMAGE_VIEW ;
- MEDIA_PLAY ;
- SIGN.

Exemples de fournisseurs :

OFFICE_EDIT
    -> OnlyOffice
    -> Microsoft Office / autre fournisseur

CAD_VIEW
    -> CADViewer
    -> autre fournisseur futur

Le changement de fournisseur ne nécessite aucune modification
du document ou de ses versions.

---

## 3. Objets du noyau documentaire

Le noyau V1 repose principalement sur quatre objets :

- Document ;
- DocumentVersion ;
- DocumentFolder ;
- DocumentHistory.

Les liens vers d'autres objets métier pourront être ajoutés
ultérieurement lorsqu'un besoin fonctionnel réel le nécessite.

---

## 4. Document

Document représente l'objet documentaire métier.

Principales informations :

- identifiant ;
- société ;
- projet ;
- dossier documentaire ;
- nom / titre ;
- type documentaire ;
- statut métier ;
- état GED ;
- version courante ;
- sélection DOE ;
- créateur ;
- date de création ;
- date de modification.

Le Document ne contient pas directement le fichier physique.

---

## 5. DocumentVersion

DocumentVersion représente une version physique d'un Document.

Principales informations :

- identifiant ;
- document ;
- numéro de version ;
- nom original du fichier ;
- extension ;
- type MIME ;
- taille ;
- clé de stockage ;
- empreinte d'intégrité ;
- auteur ;
- date de création.

La clé de stockage est indépendante du nom présenté à
l'utilisateur.

Le renommage d'un Document ne nécessite donc pas le renommage
physique du fichier stocké.

---

## 6. Intégrité

Chaque version possède une empreinte numérique, par exemple
SHA-256.

Cette empreinte permet :

- de détecter une modification du fichier ;
- de contribuer à la traçabilité ;
- de vérifier l'intégrité d'une version archivée.

---

## 7. DocumentFolder

DocumentFolder représente l'arborescence logique visible par
l'utilisateur.

Principales informations :

- identifiant ;
- projet ;
- dossier parent ;
- nom ;
- ordre ;
- état actif.

L'arborescence utilisateur est indépendante de l'organisation
physique des fichiers dans le stockage.

Déplacer un document dans l'arborescence ne déplace donc pas
nécessairement son fichier physique.

---

## 8. Création future des arborescences

L'architecture doit permettre ultérieurement trois modes
d'initialisation :

1. arborescence vide ;
2. arborescence issue d'un modèle de société ;
3. copie de l'arborescence d'un autre projet sans copie des
   documents.

Cette fonction pourra également être réutilisée dans une future
fonction de duplication de projet.

Elle n'est pas nécessaire au noyau GED V1.

---

## 9. Statut métier et état GED

Deux dimensions distinctes sont conservées.

### 9.1 Statut métier

Catalogue `DOCUMENT_STATUS`.

Valeurs prévues :

- TO_BE_DRAFTED : A rédiger ;
- IN_PROGRESS : En cours ;
- PENDING_VALIDATION : A valider ;
- VALIDATED : Validé ;
- ABANDONED : Abandonné ;
- OBSOLETE : Obsolète.

Ce catalogue est fixe et non modifiable.

### 9.2 État GED

Catalogue `DOCUMENT_LIFECYCLE`.

Valeurs prévues :

- ACTIVE : Actif ;
- ARCHIVED : Archivé ;
- TRASHED : Corbeille.

L'état GED est indépendant du statut métier.

Exemple :

VALIDATED + ACTIVE
VALIDATED + ARCHIVED
IN_PROGRESS + TRASHED

Une restauration depuis la corbeille ne modifie pas le statut
métier du document.

La suppression définitive est une opération et non un statut.

---

## 10. Type documentaire

Catalogue `DOCUMENT_TYPE`.

Valeurs initiales :

- CR de réunion ;
- Note technique ;
- Photo ;
- Plan ;
- Devis ;
- Facture ;
- Bon de commande ;
- Rapport de visite ;
- Courrier ;
- Contrat ;
- Rapport d'expertise.

Le catalogue est incrémental.

Le type documentaire est une information métier.

Il ne doit pas être confondu avec le format technique du fichier.

Exemple :

document_type = Note technique
extension = .docx
mime_type = application/vnd.openxmlformats-officedocument.wordprocessingml.document

---

## 11. Création des documents

### 11.1 Création native

Easy Projet permet au minimum de créer :

- un document Word ;
- un document Excel ;
- un document PowerPoint.

La première version est créée dans le stockage Easy Projet puis
ouverte avec l'éditeur configuré pour la société.

OnlyOffice constitue le fournisseur par défaut envisagé.

### 11.2 Import

Les autres formats sont créés dans la GED par import d'un fichier
existant.

Cela concerne notamment :

- PDF ;
- images ;
- vidéos ;
- sons ;
- DWG ;
- autres formats autorisés.

---

## 12. Résolution des outils

Le choix de l'outil externe est effectué au moment de l'action.

Exemple :

Utilisateur demande Ouvrir
        |
        v
Easy Projet identifie le format
        |
        v
Easy Projet détermine la capacité nécessaire
        |
        v
Easy Projet consulte la configuration de la société
        |
        v
Adaptateur approprié
        |
        +-- OnlyOffice
        +-- CADViewer
        +-- navigateur
        +-- autre fournisseur

Aucune référence permanente à OnlyOffice, CADViewer ou un autre
produit ne doit être stockée dans Document ou DocumentVersion.

---

## 13. Stockage

PostgreSQL contient les informations métier et les métadonnées.

Les fichiers sont stockés dans un stockage documentaire propre à
Easy Projet.

Exemple :

PostgreSQL
    Document
    DocumentVersion
    DocumentFolder
    DocumentHistory

Stockage
    fichiers DOCX
    fichiers XLSX
    fichiers PPTX
    fichiers PDF
    fichiers DWG
    images
    vidéos
    sons

Le mécanisme de stockage doit pouvoir évoluer vers un stockage
objet compatible S3 sans remise en cause du modèle métier.

---

## 14. Droits d'accès

La GED ne possède pas de système d'autorisation documentaire
spécifique en V1.

Les droits sont ceux déjà définis dans Easy Projet pour
l'utilisateur et son contexte métier.

Principe :

accès au document
    =
accès de l'utilisateur au projet / contexte concerné

Aucune ACL documentaire supplémentaire n'est introduite en V1.

---

## 15. Historique

DocumentHistory assure la traçabilité des opérations.

Actions susceptibles d'être journalisées :

- création ;
- import ;
- ouverture ;
- modification ;
- création d'une version ;
- renommage ;
- déplacement ;
- copie ;
- téléchargement ;
- partage ;
- archivage ;
- restauration ;
- mise en corbeille ;
- signature ;
- sélection DOE.

L'historique ne remplace pas le journal technique général de
l'application.

Il représente l'historique métier du document.

---

## 16. Services documentaires

Les opérations sont portées par des services et non directement
par les modèles.

Exemples :

DocumentCreationService
DocumentImportService
DocumentVersionService
DocumentStorageService
DocumentOpenService
DocumentMoveService
DocumentCopyService
DocumentArchiveService
DocumentTrashService
DocumentDownloadService
DocumentShareService

Les intégrations externes sont isolées derrière des adaptateurs.

Exemples :

OnlyOfficeAdapter
CadViewerAdapter
SignatureProviderAdapter

---

## 17. Interface utilisateur

La navigation documentaire repose sur une représentation de type
explorateur.

Fonctions prévues :

- navigation dans l'arborescence ;
- fil d'Ariane ;
- création de dossier ;
- création Word / Excel / PowerPoint ;
- import ;
- sélection simple ou multiple ;
- menu d'actions ;
- actions groupées.

Deux modes d'affichage doivent être proposés :

- mode liste ;
- mode grille / icônes.

La préférence d'affichage peut être mémorisée par utilisateur.

Les deux modes utilisent exactement les mêmes données et les
mêmes droits.

---

## 18. Actions unitaires

Le menu associé à un document propose notamment :

- Ouvrir ;
- Renommer ;
- Télécharger ;
- Copier ;
- Déplacer ;
- Partager ;
- Favoris ;
- Détails ;
- Supprimer.

Supprimer correspond en premier lieu à une mise en corbeille.

---

## 19. Actions groupées

Une sélection multiple peut permettre notamment :

- télécharger ;
- déplacer ;
- copier ;
- ajouter aux favoris ;
- archiver ;
- supprimer ;
- sélectionner pour le DOE.

Les actions disponibles dépendent de leur pertinence pour
l'ensemble de la sélection.

---

## 20. DOE

Un document peut être sélectionné pour participer au DOE.

Cette sélection ne provoque pas immédiatement une copie physique
du fichier.

Le DOE pourra être constitué ultérieurement à partir des versions
documentaires retenues.

---

## 21. Évolutions

L'architecture doit permettre ultérieurement :

- OCR ;
- indexation documentaire ;
- recherche plein texte ;
- indexation sémantique ;
- classement assisté par IA ;
- résumé ;
- traduction ;
- analyse d'images ;
- tableaux de bord documentaires ;
- génération assistée du DOE ;
- nouveaux éditeurs ;
- nouveaux viewers ;
- nouveaux fournisseurs de signature.

Ces fonctions doivent rester des extensions du noyau documentaire
et non modifier sa structure fondamentale.