# Consigne OpenClassrooms — Concevez et déployez un système RAG

> Retranscription intégrale de l'énoncé OpenClassrooms.
> Parcours 1039 — Projet 1836 — Data Engineer. Durée : 50 heures.
> Source : https://openclassrooms.com/fr/paths/1039/projects/1836
> Relevé le 17/09/2026.

---

## 1. Présentation du projet

### Qu'allez-vous apprendre dans ce projet ?

Vous avez appris la structuration de l'architecture des données, la modélisation des flux de données et les processus de traitement.

Dans ce projet, vous allez consolider vos compétences et réaliser un système Retrieval-Augmented Generation (RAG) fonctionnel basé sur LangChain et le modèle Mistral, soutenu par une base vectorielle Faiss.

Vous allez découvrir l'intégration de modèles NLP dans un système de type RAG. Vous utiliserez le framework LangChain pour gérer les interactions entre la base de données vectorielle et les modèles NLP.

Les intégrations permettront de réaliser un chatbot capable de fournir des réponses augmentées par la recherche dans une base de données vectorielle, améliorant ainsi l'expérience utilisateur en fournissant des informations précises et adaptées.

Vous plongerez ainsi dans les processus d'automatisation des flux de données via des scripts Python et la mise en place de tests continus pour suivre les performances du modèle et la qualité des données.

### En quoi ces compétences sont-elles importantes pour votre carrière ?

Ces compétences sont utiles pour le domaine de la science des données et de l'ingénierie des données, où la gestion efficace des flux de données et des modèles IA est essentielle.

Elles permettent de concevoir et de déployer des systèmes d'extraction et de génération augmentée performants. Ces pratiques sont recherchées par les recruteurs en data engineering, machine learning et intelligence artificielle, notamment pour la gestion de pipelines de données, l'intégration de modèles NLP, et l'automatisation des processus de traitement des données.

### Comment allez-vous procéder ?

Ce projet est découpé en 3 activités.

1. **Cours** : Vous suivrez le cours *Mettez en place un RAG pour un LLM* pour comprendre les enjeux de l'extraction augmentée et de l'intégration des modèles NLP avec les bases de données vectorielles.
2. **Ressources pédagogiques** : Vous pourrez les consulter pour une bonne réalisation de votre projet.
3. **Mission** : Vous réaliserez la conception et le déploiement d'un système RAG complet, intégrant des modèles Mistral avec LangChain.

### Objectifs pédagogiques

- Mettre en place un processus de nettoyage afin d'améliorer la qualité des données
- Configurer l'environnement de travail nécessaire à l'exploitation des données
- Identifier ou créer un modèle d'apprentissage adapté aux contraintes et besoins métiers

---

## 2. Organisez-vous pour ce projet

### Durée estimée de ce projet

50 heures de travail supervisé et 50 heures de travail personnel sont prévues sur ce projet.

- **Si vous suivez votre formation à temps plein** : vous devriez consacrer à ce projet moins de 3 semaines. Idéalement, vous devriez donc effectuer 2 séances de mentorat avec votre mentor avant de présenter votre projet en soutenance la semaine suivante.
- **Si vous suivez votre formation en alternance** : vous devriez consacrer à ce projet moins de 6 semaines. Idéalement, vous devriez donc effectuer 5 séances de mentorat avec votre mentor avant de présenter votre projet en soutenance la semaine suivante.

Respecter ces durées vous permet de réaliser votre formation dans les temps. Rassurez-vous, un retard éventuel pourra être rattrapé sur un projet suivant.

---

## 3. Mission — Développez un assistant pour la recommandation d'évènements culturels

### Comment allez-vous procéder ?

Cette mission suit un scénario de projet professionnel.

Vous pouvez suivre les étapes pour vous aider à réaliser vos livrables.

Avant de démarrer, nous vous conseillons de :

- lire toute la mission et ses documents liés ;
- prendre des notes sur ce que vous avez compris ;
- consulter les étapes pour vous guider ;
- préparer une liste de questions pour votre première session de mentorat.

### Prêt à mener la mission ?

Vous êtes ingénieur data freelance spécialisé en intégration de modèles NLP et gestion de bases de données vectorielles. Vous travaillez pour l'entreprise **Puls-Events**, une société innovante dans le domaine de la gestion d'événements culturels.

L'entreprise Puls-Events propose une plateforme web permettant aux utilisateurs de découvrir et de suivre des événements culturels en temps réel. Elle collecte des informations à partir de diverses sources, comme Open Agenda, pour proposer des événements adaptés aux préférences de ses utilisateurs, filtrables par lieu et par période.

Elle souhaite tester l'intégration d'un chatbot intelligent, capable de fournir des recommandations personnalisées et augmentées par des réponses précises issues de données d'événements.

Ce chatbot, soutenu par un système de génération de réponses augmentées (RAG), doit être capable d'extraire et d'analyser des informations à partir d'une base de données vectorielle.

Vous êtes chargé de réaliser un premier **Proof of Concept (POC)** pour démontrer la faisabilité de ce concept.

### Message du responsable technique

> **De :** Jérémy
> **À :** moi
> **Objet :** version fonctionnelle du POC RAG
>
> Salut,
>
> Nous avons besoin que tu termines une version fonctionnelle du POC RAG. Il sera présenté en réunion avec les équipes produit et marketing pour vérifier l'intérêt du projet et envisager son déploiement à plus grande échelle.
>
> Comme discuté ensemble, nous allons nous appuyer sur la source de données des événements publics Open Agenda. Tu pourras te limiter au périmètre géographique de ton choix. Veille cependant à ce qu'il y ait uniquement des événements récents de moins d'un an.
>
> Ce qui est attendu :
>
> - **Environnement virtuel** : Pour que le projet soit facilement reproductible, dépendances et documentation sous forme d'un readme.
> - **Système RAG fonctionnel** : Code complet du système RAG versionné dans un repo git, avec intégration de LangChain, Mistral et Faiss. Le système doit être en mesure de reconstruire la base vectorielle sur demande (scripts de pré-processing et de vectorisation des données).
> - **Rapport technique (PDF ou Word)** : Document entre 5 et 10 pages, expliquant l'architecture du système, tes choix techniques, les modèles sélectionnés, les résultats obtenus pour le POC et les recommandations pour la version finale.
> - **Tests unitaires (Python)** : Prévois un fichier .py pour tester que les données intégrées dans la base vectorielle correspondent bien à des évènements de moins d'un an dans la région géographique que tu auras sélectionnée.
> - **Présentation (PowerPoint)** : Entre 10 et 15 slides pour exposer le concept du projet, les résultats du POC.
> - **Démo live du système** : Prépare une démo live pour illustrer les capacités du POC.
>
> N'hésite pas si tu as besoin de précisions sur le périmètre ou les attentes. On compte sur toi pour que tout soit prêt dans les délais !
>
> Ah oui, j'oubliais.. Pour évaluer le système, nous aurons besoin de créer un **jeu de données test annoté de questions / réponses**. Ce jeu test sera utilisé pour mesurer la qualité des réponses par rapport aux réponses annotées.
>
> Merci et bon courage !
>
> Jérémy

---

## 4. Les étapes de la mission

Cette mission est entièrement guidée. Vous pouvez suivre les étapes ci-dessous.

### Étape 1 — Préparez l'environnement de travail

> Ce projet situé vers la fin du parcours ne contient pas de fiche d'autoévaluation.

**Description**

Configurer l'environnement de développement nécessaire pour implémenter le système RAG. Installer les bibliothèques requises, et s'assurer que tout fonctionne correctement.

**Prérequis**

- Avoir installé les bibliothèques LangChain et Faiss.

**Résultat attendu**

Un environnement de développement fonctionnel avec tous les outils installés et prêts à être utilisés.

**Recommandations**

- Commencez par créer un environnement virtuel.
- Installez les packages requis : `pip install langchain faiss-cpu mistral`.
- Testez que toutes les installations sont correctes en exécutant un simple script Python pour importer les bibliothèques requises.

**Points de vigilance**

- Vérifier que toutes les versions des packages sont compatibles.
- S'assurer que Faiss est bien installé avec le backend CPU pour éviter des erreurs.

**Outils**

- Python 3
- LangChain, Faiss, Mistral API
- Environnement virtuel (e.g., virtualenv ou conda)

**Ressources**

- Documentation Faiss
- LangChain API Reference

---

### Étape 2 — Effectuez le pré-processing des données Open Agenda

**Description**

Récupérer les données d'événements à partir de la plateforme Open Agenda, les filtrer par localisation et période, et structurer ces données pour une utilisation future dans la base de données vectorielle.

**Prérequis**

- Avoir accès à l'API Open Agenda.
- Avoir compris les paramètres de filtrage souhaités (ville, période, type d'événement).

**Résultat attendu**

Un jeu de données d'événements propre et structuré, prêt à être indexé. Vous pourrez effectuer des tests unitaires pour vous assurer d'avoir récupéré les données attendues.

**Recommandations**

- Utiliser l'API Open Agenda pour récupérer les événements.
- Filtrer les événements par localisation et période (1 an d'historique et événements à venir).
- Convertir les descriptions des événements en format vectoriel avec un modèle de NLP comme Mistral.

**Points de vigilance**

- Attention aux données manquantes ou incorrectes.
- Vérifier la pertinence des filtres pour s'assurer que les événements sont bien ciblés.

**Outils**

- OpenAgenda API
- Pandas pour la manipulation des données
- Mistral pour la génération de vecteurs

**Ressources**

- OpenAgenda API Documentation
- Mistral Model Documentation

---

### Étape 3 — Implémentez la base de données vectorielle avec Faiss

**Description**

Indexer les descriptions des événements sous forme de vecteurs dans une base de données vectorielle avec Faiss, permettant une recherche rapide basée sur la similarité sémantique.

**Prérequis**

- Avoir nettoyé les données d'Open Agenda.
- Avoir découpé les textes en chunks avant la vectorisation des textes.
- Vectorisation de chaque chunk et indexation dans la base de données FAISS.

**Résultat attendu**

Une base de données Faiss contenant les événements indexés en fonction de leurs vecteurs sémantiques.

**Recommandations**

- Utilisez Faiss pour construire un index de recherche sémantique.
- Enregistrez les informations non seulement sur les vecteurs, mais aussi sur les métadonnées des événements (dates, lieux, descriptions).
- Faites des tests de recherche pour vérifier l'efficacité.

**Points de vigilance**

- S'assurer que l'index est optimisé pour des recherches rapides (utiliser les bons algorithmes dans Faiss).
- Vérifier que tous les événements ont bien été indexés.

**Outils**

- Faiss pour l'indexation vectorielle
- LangChain pour interagir avec Faiss

**Ressource**

- Faiss Index Guide

---

### Étape 4 — Intégrez LangChain pour le système RAG

**Description**

Développer le chatbot intelligent capable de fournir des recommandations personnalisées basées sur les événements indexés, et générer des réponses augmentées à partir des données présentes dans la base de données vectorielle.

**Prérequis**

- Les événements sont indexés dans Faiss.
- API Mistral pour générer des réponses naturelles à partir d'un LLM sélectionné sur la plateforme Mistral.

**Résultat attendu**

Un chatbot capable de fournir des recommandations d'événements et d'interagir avec l'utilisateur.

Une réponse IA est correcte si elle a le même sens et contient les mêmes informations que la réponse annotée par l'humain.

**Recommandations**

- Utilisez LangChain pour orchestrer les appels entre la base Faiss et le modèle Mistral.
- Configurez des chaînes de traitement pour que le chatbot puisse générer des réponses basées à la fois sur la recherche dans Faiss et sur le modèle de langage.

**Points de vigilance**

- S'assurer que les réponses générées sont à la fois pertinentes et bien formulées.
- Tester plusieurs scénarios d'interaction pour vérifier la robustesse du chatbot.
- L'historique de conversation entre le bot et l'humain n'est pas nécessaire dans le POC.

**Outils**

- LangChain pour la gestion des interactions
- Mistral pour la génération de réponses

**Ressources**

- LangChain Documentation
- Mistral Model

---

## 5. Livrables et soutenance

### Livrables

Voici un rappel des documents que vous devez déposer sur la plateforme.

| Compétences | Livrables |
| --- | --- |
| Configurer l'environnement de travail nécessaire à l'exploitation des données | Fichier Readme : présentation, objectifs, instructions pour la reproduction, description des fichiers/dossiers<br>Gestion des dépendances (conda ou pip) |
| Mettre en place un processus de nettoyage afin d'améliorer la qualité des données | Scripts de pré-processing et documentation intégrée sous forme de docstrings<br>Scripts de vectorisation et création/gestion d'index vectoriels<br>Tests unitaires intégrés sous forme de pipeline |
| Identifier ou créer un modèle d'apprentissage adapté aux contraintes et aux besoins métiers | Rapport technique<br>Code du système RAG |

Déposez sur la plateforme, dans un dossier zip nommé `Titre_du_projet_nom_prenom`, tous les livrables du projet comme suit : `Nom_Prenom_n° du livrable_nom du livrable_date de démarrage du projet`.

Cela donnera :

- `Nom_Prenom_1_readme_012025`
- `Nom_Prenom_2_gestion_012025`
- `Nom_Prenom_3_scripts_012025`

Par exemple, le premier livrable peut être : `Janek_Meriem_1_readme_012025`

### Soutenance

La soutenance ne porte que sur la mission.

Durant la présentation orale, l'évaluateur interprétera le rôle de Jérémy. La soutenance dure **30 minutes** et sera structurée de la manière suivante :

**Présentation des livrables (15 minutes)**
Présentation du système, justification technique des briques mises en place. Démonstration du système depuis l'environnement local.

**Discussion (10 minutes)**
L'évaluateur jouera le rôle de Jérémy. Il vous challengera sur les points suivants :

1. Peux-tu expliquer comment Faiss optimise les recherches dans une base vectorielle ?
2. Quelles seraient les limitations de Faiss pour une grande quantité de données ?
3. Pourquoi choisir LangChain pour intégrer des modèles NLP dans un pipeline ?
4. Quelles méthodes utilises-tu pour garantir la qualité des données dans un pipeline automatisé ?
5. Comment détecter les dérives de performance dans un modèle déployé ?
6. Quels indicateurs de performance sont les plus importants pour suivre un modèle en production ?

**Débrief (5 minutes)**
À la fin de la soutenance, l'évaluateur arrêtera de jouer le rôle de Jérémy pour vous permettre de débriefer ensemble.

Votre présentation doit durer **15 minutes (+/- 5 minutes)**. Puisque le respect des durées des présentations est important en milieu professionnel, les présentations en dessous de 10 minutes ou au-dessus de 20 minutes peuvent être refusées.

---

## 6. Ressources pédagogiques

### Pourquoi consulter ces ressources ?

Référez-vous régulièrement aux ressources ci-dessous. Elles vous accompagneront tout au long de l'élaboration de votre projet.

Il est cependant recommandé d'avoir assimilé les concepts du cours avant de vous lancer. En effet, une bonne compréhension des bases vous permettra de mieux appréhender les différentes étapes.

**Les fondamentaux**

- Étapes de traitement et de description du pipeline de données RAG — Azure Databricks
- Représentations vectorielles continues : traduction dans un espace de dimensions inférieures | Machine Learning

**Les documentations**

- Faiss
- Mistral AI
- LangChain

**Les tutoriels**

- Build a Retrieval Augmented Generation with LangChain
- Intégration de LangChain avec Faiss : Faiss | 🦜️🔗 LangChain

**Cours du parcours**

- Mettez en place un RAG pour un LLM

---

## 7. Synthèse — ce qui est imposé

Liste de contrôle extraite mot pour mot de l'énoncé. **Rien d'autre ne doit être ajouté au projet.**

| # | Attendu | Source |
| --- | --- | --- |
| 1 | Environnement virtuel + gestion des dépendances (pip ou conda) | Mail Jérémy / Livrables |
| 2 | README : présentation, objectifs, instructions de reproduction, description des fichiers et dossiers | Livrables |
| 3 | Données Open Agenda, périmètre géographique au choix, événements de moins d'un an | Mail Jérémy / Étape 2 |
| 4 | Scripts de pré-processing avec docstrings | Livrables / Étape 2 |
| 5 | Chunking puis vectorisation avec Mistral | Étape 2 / Étape 3 |
| 6 | Index Faiss avec métadonnées (dates, lieux, descriptions), reconstructible sur demande | Étape 3 / Mail Jérémy |
| 7 | Chaîne RAG LangChain + Mistral, sans historique de conversation | Étape 4 |
| 8 | Jeu de données test annoté questions / réponses + mesure de la qualité | Mail Jérémy |
| 9 | Tests unitaires Python : événements < 1 an et dans le périmètre géographique | Mail Jérémy |
| 10 | Tests unitaires intégrés sous forme de pipeline | Livrables |
| 11 | Code versionné dans un repo git | Mail Jérémy |
| 12 | Rapport technique 5 à 10 pages (PDF ou Word) | Mail Jérémy |
| 13 | Présentation PowerPoint 10 à 15 slides | Mail Jérémy |
| 14 | Démo live du système depuis l'environnement local | Mail Jérémy / Soutenance |
| 15 | Livrables zippés et nommés `Nom_Prenom_n_nom_MMAAAA` | Livrables |

**Technologies imposées :** Python 3, environnement virtuel, LangChain, Faiss (`faiss-cpu`), API Mistral, API OpenAgenda, Pandas.

**Non demandé par l'énoncé** — donc hors périmètre : API web (FastAPI/Flask), conteneurisation (Docker), interface web, base de données relationnelle, historique de conversation, déploiement cloud.

---

## 8. Au-delà du POC

La version déposée le 25/09/2026 est figée sous le tag `depot-openclassrooms-2026-09-25` et respecte
la liste ci-dessus. La V2 ajoute deux choses, et seulement deux, que l'énoncé place hors périmètre :

| Ajout | Ce que c'est | Pourquoi |
| --- | --- | --- |
| `api/` | une API FastAPI qui expose la chaîne de `src/rag.py` | le navigateur ne peut pas importer du Python : l'API diffuse la réponse au fil de l'eau (SSE), avec ses sources et ses citations |
| `web/` | une interface Next.js (chat, cartes d'évènements, citations cliquables) | montrer le POC à des utilisateurs de Puls-Events, y compris sur téléphone, plutôt qu'en ligne de commande |

La chaîne imposée ne change pas : LangChain, Faiss, embeddings et génération Mistral, pandas,
OpenAgenda. `src/chat.py` reste la démo live demandée par l'énoncé, et `src/evaluate.py` la mesure de
qualité.
