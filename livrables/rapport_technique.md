# Rapport technique — POC RAG Puls-Events

**Assistant de recommandation d'évènements culturels en Seine-Saint-Denis**

Mathieu Zinzen — Data Engineer freelance pour Puls-Events — POC de septembre 2026, V2 de novembre 2026

---

## 1. Contexte et objectif

Puls-Events propose une plateforme web de découverte d'évènements culturels, alimentée entre autres
par OpenAgenda. L'entreprise veut savoir si un **chatbot** peut recommander des évènements en langage
naturel (« un spectacle de marionnettes pour mon fils ? », « que faire le 21 juin ? ») en
s'appuyant uniquement sur des données réelles, sans inventer d'évènements.

Ce document présente le **Proof of Concept** réalisé pour répondre à cette question : un système
**RAG** (*Retrieval-Augmented Generation*) qui retrouve les évènements pertinents dans une base
vectorielle **Faiss**, puis fait rédiger la réponse par un modèle **Mistral**, le tout orchestré par
**LangChain**. Le POC doit être présenté aux équipes produit et marketing avant une décision de
déploiement à plus grande échelle.

Le cahier des charges impose :

- des données OpenAgenda limitées à un périmètre géographique et à des évènements de **moins d'un an** ;
- une base vectorielle **reconstructible sur demande** par des scripts de pré-processing et de
  vectorisation ;
- des tests unitaires vérifiant la fraîcheur et le périmètre des données indexées, intégrés à un pipeline ;
- un jeu de test annoté de questions / réponses pour mesurer la qualité du système ;
- pas d'historique de conversation : chaque question est traitée seule.

Le code est versionné sur GitHub (`Matz-ai/concevoir-et-deployer-un-systeme-rag`) et se reproduit en
suivant le README.

---

## 2. Architecture du système

Le système se découpe en deux temps : un pipeline **hors ligne** qui construit la base vectorielle, et
une chaîne **en ligne** qui répond aux questions.

```
 HORS LIGNE — reconstruction de la base (à la demande)

  API OpenAgenda ──► extract.py ──► data/raw/        4 569 évènements bruts (JSON)
  (open data)                           │
                                        ▼
                     preprocess.py ──► data/processed/ 2 295 évènements propres (CSV)
                                        │               ▲
                                        │               └── pytest (tests/) + GitHub Actions
                                        ▼
                     build_index.py ──► chunks (1 000 car.) ──► mistral-embed ──► Faiss
                                                                  (OpenRouter)     3 860 vecteurs
                                                                                   + métadonnées

 EN LIGNE — une question

  question ──► mistral-embed ──► Faiss : 10 chunks les plus proches, parmi les évènements à venir
                                   │
                                   ▼
               prompt (consigne + date du jour + chunks + question) ──► Mistral Large ──► réponse
                                                                                          + sources
```

| Script | Rôle |
| --- | --- |
| `src/extract.py` | interroge l'API open data OpenAgenda, pagine et écrit les évènements bruts |
| `src/preprocess.py` | nettoie et structure les évènements, journalise chaque règle d'écart |
| `src/build_index.py` | compose le texte, le découpe en chunks, le vectorise et construit l'index Faiss |
| `src/rag.py` | la chaîne LangChain : recherche Faiss + génération Mistral, renvoie réponse et sources |
| `src/chat.py` | la démo en ligne de commande |
| `src/evaluate.py` | passe le jeu de test annoté dans la chaîne et mesure la qualité |
| `tests/test_data_quality.py` | contrôles de qualité des données indexées, exécutés en CI |

Les trois scripts du pipeline hors ligne se relancent dans l'ordre et reconstruisent l'index de bout
en bout en quelques minutes, pour environ 0,10 $ d'appels d'embeddings. Aucune donnée n'est versionnée :
seul le code l'est.

---

## 3. Les données

### 3.1 Source et périmètre

Les évènements viennent du jeu open data **« evenements-publics-openagenda »**, exposé par l'API
Opendatasoft. Il ne demande pas de clé, et permet de filtrer côté serveur :

- **périmètre géographique** : la **Seine-Saint-Denis (93)** (`location_department`). Un département
  dense en offre culturelle, assez volumineux pour que la recherche sémantique ait du sens, assez petit
  pour reconstruire l'index pendant une démo ;
- **fenêtre temporelle** : évènements dont la première date est postérieure à « maintenant moins un an »,
  ce qui couvre un an d'historique et tous les évènements à venir.

L'API refuse un décalage de pagination supérieur à 10 000 : les filtres sont donc appliqués côté serveur
avant de paginer, par pages de 100. L'extraction ramène **4 569 évènements**.

### 3.2 Nettoyage

`preprocess.py` réduit les 56 champs de la source à 12 (identifiant, titre, description, mots-clés,
dates de début et de fin, dates en texte, lieu, adresse, ville, département, lien), puis applique six
règles dans l'ordre. Chacune note combien de lignes elle écarte :

| Règle | Écartés | Pourquoi |
| --- | --: | --- |
| Hors Seine-Saint-Denis | 0 | contrôle de sécurité : le filtre serveur a déjà fait le travail |
| Agenda France Travail | 2 146 | ateliers emploi (CV, entretiens) publiés sur OpenAgenda, hors sujet pour Puls-Events |
| Commencé il y a plus d'un an | 0 | double contrôle du filtre temporel |
| Annulé par l'organisateur | 2 | ne doit pas être recommandé |
| Doublon (même titre, date et lieu) | 43 | un même évènement publié dans plusieurs agendas |
| Description inexploitable (< 30 caractères) | 83 | la description ne fait que répéter le titre |
| **Sortie** | **2 295** | |

Deux traitements portent aussi sur le texte :

- **choix de la description** : `description_fr` est un résumé tronqué à 200 caractères,
  `longdescription_fr` le texte intégral mais absent pour un évènement sur quinze. On garde la plus
  longue des deux ;
- **suppression du HTML** : les longues descriptions arrivent balisées ; balises, entités et espaces
  multiples sont retirés, car ils n'apportent rien au modèle d'embeddings.

La découverte la plus importante est venue de l'exploration des données, pas du code : **près de la
moitié du volume brut était constituée d'ateliers France Travail**. Sans cette règle, une question sur
« un atelier pour les enfants » aurait remonté des ateliers de rédaction de CV.

Le dataset final compte 2 295 évènements, avec des descriptions de 500 caractères en médiane. Saint-Denis
(421), Saint-Ouen (300) et Montreuil (201) sont les trois villes les plus représentées. **276 d'entre eux
seulement sont encore d'actualité** au 25 septembre 2026 : le reste est de l'historique.

### 3.3 Qualité des données dans le pipeline

`tests/test_data_quality.py` vérifie, avec pytest, ce qui partira dans la base vectorielle :

- tous les évènements sont en Seine-Saint-Denis ;
- tous ont commencé il y a moins d'un an ;
- aucun doublon ;
- les champs indispensables à l'indexation sont renseignés.

Chaque contrôle tourne sur deux jeux : un **échantillon de sept évènements** construit dans le fichier de
test (deux valides, et une violation de chacune des règles), et le **dataset réel** s'il a été généré.
L'échantillon rend les tests exécutables dans la CI GitHub Actions, qui n'a ni clé API ni données ; le
dataset réel est le seul à prouver que les évènements réellement indexés respectent les règles. Quand il
est absent, ces tests sont marqués *skipped* plutôt que faussement verts. Le workflow installe
`requirements.txt` et lance `pytest` à chaque push : il vérifie aussi que l'environnement se réinstalle
sur une machine neuve.

---

## 4. Choix techniques

### 4.1 Ce qui est vectorisé

Le texte vectorisé n'est pas la description seule, mais la concaténation **titre + mots-clés + lieu +
ville + dates + description**. Sans le lieu dans le vecteur, le même spectacle joué à Montreuil et à
Bobigny aurait un vecteur identique, et une question « que faire à Montreuil ? » ne pourrait pas les
départager. Les mêmes champs sont conservés en **métadonnées** à côté de chaque vecteur (dates, lieux,
descriptions, identifiant, lien), pour l'affichage des sources et le filtrage.

### 4.2 Découpage en chunks

`RecursiveCharacterTextSplitter` de LangChain, **1 000 caractères avec 100 de recouvrement**. Ce choix
respecte l'étape de chunking demandée sans morceler inutilement : **74 % des évènements tiennent en un
seul chunk**, seules les longues programmations (festivals, saisons) sont coupées. Le recouvrement évite
qu'une phrase à cheval sur deux chunks perde son sens. Chaque chunk garde l'identifiant de son évènement.

Résultat : **2 295 évènements → 3 860 chunks → 3 860 vecteurs**.

### 4.3 Modèles Mistral et accès via OpenRouter

| Usage | Modèle | Justification |
| --- | --- | --- |
| Embeddings | `mistral-embed` (version 2312), 1 024 dimensions | imposé ; vecteurs normés, envoyés par lots de 50 |
| Génération | `mistral-large-2512`, `temperature=0` | environ 0,002 $ par question ; `mistral-small`, moins cher, renvoyait des erreurs 429 en série au moment des tests |

Les modèles sont ceux de Mistral, comme l'impose le cahier des charges, mais ils sont appelés via
**OpenRouter**, une passerelle compatible avec l'API OpenAI, pour laquelle une clé existait déjà. Le code
utilise donc `ChatOpenAI` et `OpenAIEmbeddings` de `langchain-openai` avec une URL de base personnalisée.
Un piège a dû être contourné : `OpenAIEmbeddings` compte par défaut les tokens avec `tiktoken` et envoie
des identifiants de tokens OpenAI au lieu du texte, ce que l'endpoint Mistral refuse
(`check_embedding_ctx_length=False`).

Repasser sur l'API Mistral native ne demande que de changer l'URL de base et le nom des modèles.

### 4.4 Index Faiss

L'index est un **`IndexFlatL2`**, le défaut de LangChain : une recherche **exacte** qui compare la
question à chacun des 3 860 vecteurs. À ce volume, une requête prend quelques millisecondes et l'index
pèse 16 Mo (plus 4,5 Mo de métadonnées). Faiss optimise ce calcul brut par des opérations vectorisées
(BLAS, instructions SIMD du processeur), sans aucun paramètre à régler.

Les index approximatifs (`IVF`, qui ne parcourt que les partitions les plus proches ; `HNSW`, un graphe
de voisinage) échangent un peu de rappel contre de la vitesse. Ce compromis n'a d'intérêt qu'à partir de
centaines de milliers de vecteurs.

Les vecteurs Mistral sont **normés** : la distance L2 classe alors exactement comme la similarité
cosinus, et `IndexFlatL2` n'introduit aucun biais par rapport à `IndexFlatIP`.

### 4.5 La chaîne LangChain

`rag.py` tient en une cinquantaine de lignes. La chaîne prend une question, et renvoie la réponse
**avec les évènements qui l'ont fondée** :

1. **Recherche** : `index.as_retriever(...)` renvoie les **10 chunks** les plus proches, **filtrés sur
   `date_fin ≥ aujourd'hui`**. L'index conserve un an d'historique comme l'exige l'énoncé, mais seuls les
   évènements à venir sont recommandables. Demander au modèle d'ignorer les dates passées ne marchait
   pas : filtrer avant lui est déterministe.
2. **Contexte** : chaque chunk est préfixé de sa date de début complète, car les dates affichées par
   OpenAgenda (« Samedi 3 octobre ») n'ont pas d'année. La date du jour est aussi donnée au modèle.
3. **Génération** : une consigne système demande de répondre **uniquement** à partir des évènements
   fournis, de citer titre, date et lieu, et de **dire franchement** quand aucun ne convient.

`k = 10` a été choisi après essai : à 5, des concerts de jazz présents dans l'index n'étaient pas
remontés ; 10 chunks restent courts (environ 3 000 tokens) et le modèle écarte ceux qui ne répondent pas.

**Pourquoi LangChain.** Le framework fournit, derrière une interface commune, tous les maillons du
pipeline : découpeur de texte, client d'embeddings, magasin vectoriel Faiss, gabarit de prompt, modèle de
chat. Chaque maillon est interchangeable — passer de Faiss à une autre base, ou d'OpenRouter à l'API
Mistral native, ne touche qu'une ligne. La syntaxe de composition (`|`, `RunnableParallel`) rend la
chaîne lisible, et donne gratuitement les mécanismes de nouvelle tentative (`with_retry`) utilisés contre
les erreurs 429.

### 4.6 La démo

`chat.py` est une boucle en ligne de commande : l'utilisateur tape une question, le système affiche la
réponse puis la liste des évènements récupérés (titre, dates, lieu, ville). L'affichage des sources n'est
pas cosmétique : il prouve que la réponse vient de l'index et non de la mémoire du modèle.

---

## 5. Évaluation

### 5.1 Protocole

**Le jeu de test** (`data/qa_test.json`) compte **20 questions annotées à la main** à partir
d'évènements réellement présents dans l'index : 8 par thème, 5 par lieu, 4 par date, et 3 **hors
corpus** (un match du PSG, un concert de Beyoncé, la météo) pour vérifier que le système n'invente rien.
Chaque entrée donne la réponse attendue et les identifiants des évènements qui doivent être retrouvés.

**Le critère** est celui du cahier des charges : une réponse est correcte si elle a *le même sens et
contient les mêmes informations* que la réponse annotée. Il est appliqué par un **juge Mistral**
(*LLM-as-a-judge*, `temperature=0`) qui rend CORRECT ou INCORRECT avec une justification. Les
alternatives ont été écartées :

| Méthode | Pourquoi elle ne convient pas |
| --- | --- |
| Comparaison exacte | ne tolère aucune reformulation |
| Recouvrement de mots-clés | ne sait pas lire un « non », ni distinguer une date juste d'une date fausse |
| Similarité d'embeddings | mesure la proximité du sujet, pas l'exactitude d'une date ou d'un lieu |

**En parallèle, sans LLM**, `evaluate.py` mesure le **rappel de la recherche** : la part des évènements
attendus présents dans les 10 chunks récupérés. C'est ce qui permet de savoir si une erreur vient de la
recherche ou de la génération.

### 5.2 Résultats

| Type de question | Réponses correctes |
| --- | :-: |
| Thème | 4 / 8 |
| Lieu | 2 / 5 |
| Date | 1 / 4 |
| Hors corpus | 2 / 3 |
| **Total** | **9 / 20 (45 %)** |

**Rappel moyen de la recherche : 52 %** sur les 17 questions qui attendent des évènements.

**Fiabilité de la mesure.** Les 20 verdicts du juge ont été relus à la main : accord sur **18 / 20**.
Le juge est trop sévère sur la question météo (l'assistant refuse bien, puis suggère un évènement) et trop
indulgent sur les expositions du musée Paul-Éluard (un titre manque). Les deux erreurs se compensent : le
score humain est aussi de **9 / 20**. Un modèle Mistral qui juge un modèle Mistral est un biais connu ; la
relecture humaine est ce qui le contrôle.

### 5.3 Analyse

**La recherche est le maillon faible, pas la génération.** Sur les 11 réponses incorrectes, 10 ont une
recherche qui n'a pas remonté tous les évènements attendus. Quand la recherche les trouve tous
(7 questions), la réponse est correcte 6 fois sur 7. Le modèle de génération fait donc bien son travail
quand on lui donne les bons documents — et quand il ne les a pas, il dit le plus souvent qu'il n'y a rien,
ce qui est le comportement souhaité.

Trois causes ressortent :

- **Un mot-clé précis est mal capté par la recherche sémantique.** Les deux concerts de jazz attendus
  arrivent aux rangs 114 et 388 pour « Quels concerts de jazz sont prévus en Seine-Saint-Denis ? », et
  encore 100 et 181 pour « Où écouter du jazz ? ». Le mot « jazz » n'est que dans leurs mots-clés, pas
  dans leur description : leur vecteur parle d'autre chose. À l'inverse, les évènements dont le texte
  contient « Seine-Saint-Denis » passent devant.
- **Un vecteur ne sait pas ce qu'est une date.** « Quel concert le 13 décembre 2026 ? » ne ressemble
  sémantiquement à aucun évènement en particulier : 1 question par date sur 4 seulement réussit.
- **Une hallucination** (question 17, « week-end du 28-29 novembre ») : le modèle propose une tournée
  « potentiellement en Seine-Saint-Denis » à partir d'un fragment de description. La consigne système ne
  suffit pas à l'empêcher quand le contexte récupéré est hors sujet.

Les questions hors corpus, elles, sont bien traitées : aucun match du PSG ni concert de Beyoncé n'est
inventé.

### 5.4 Limite du jeu de test

La chaîne ne recommande que les évènements à venir : le jeu de test, construit le 25 septembre 2026, ne
cite que des évènements à partir du 31 octobre 2026 et **reste valable jusqu'au 30 octobre**. Au-delà,
les réponses attendues deviendront fausses. Dans un corpus qui se renouvelle, un jeu de test doit être
ré-annoté régulièrement.

---

## 6. Limites et recommandations pour la version finale

Le POC montre que l'architecture fonctionne de bout en bout : les données sont propres et testées, la
base se reconstruit sur demande, la réponse cite ses sources et le système refuse les questions hors
sujet. Avec 45 % de réponses correctes, il n'est pas prêt pour la production, mais l'évaluation désigne
précisément ce qu'il faut corriger.

### 6.1 Améliorer la recherche (priorité 1)

- **Recherche hybride.** Combiner la recherche vectorielle avec une recherche lexicale BM25, qui retrouve
  les mots-clés exacts (« jazz », « marionnettes », un nom de salle). LangChain le permet directement
  (`BM25Retriever` + `EnsembleRetriever`). C'est la réponse directe aux échecs sur les thèmes et les lieux.
- **Filtre par date extrait de la question.** Le filtre sur `date_fin` fonctionne déjà pour écarter le
  passé. Il suffit de faire extraire par le modèle la période demandée (« le 13 décembre », « ce
  week-end ») et de l'appliquer de la même façon sur les métadonnées, avant la recherche.
- **Filtre par ville.** Même principe pour les questions par lieu : la ville est déjà en métadonnée.
- **Un seuil de pertinence** sur la distance, pour ne pas donner au modèle des chunks hors sujet — ce qui
  limiterait aussi l'hallucination observée.

### 6.2 Passage à l'échelle de Faiss

À l'échelle d'un département, `IndexFlatL2` est idéal. À l'échelle nationale (plusieurs centaines de
milliers d'évènements), trois limites apparaissent :

- **Mémoire et temps.** Un index plat stocke chaque vecteur en entier (1 024 × 4 octets) et les parcourt
  tous : 1 million de vecteurs, c'est 4 Go de RAM et une recherche linéaire. Il faudra passer à un index
  approximatif (`HNSW`, ou `IVF` avec quantification `PQ` pour compresser les vecteurs), en mesurant la
  perte de rappel.
- **Filtrage.** Faiss ne gère pas les métadonnées : le POC classe tout l'index puis filtre les évènements
  passés en Python (`fetch_k = ntotal`). Ce contournement ne tient pas à grande échelle.
- **Mise à jour.** Faiss est une bibliothèque, pas une base de données : pas de mise à jour concurrente,
  pas de suppression simple par identifiant, pas de réplication. Pour la production, une base vectorielle
  (Qdrant, Weaviate, ou pgvector si Puls-Events a déjà PostgreSQL) apporte filtrage natif, mises à jour et
  haute disponibilité, souvent avec Faiss ou HNSW sous le capot.

### 6.3 Fraîcheur des données

Les évènements changent tous les jours. La version finale doit :

- relancer extraction et pré-processing **quotidiennement** (tâche planifiée), les tests de qualité
  servant de garde-fou avant tout ré-indexage ;
- passer à une mise à jour **incrémentale** : ne vectoriser que les évènements nouveaux ou modifiés
  (l'identifiant `uid` est déjà dans les métadonnées), et retirer les évènements terminés.

### 6.4 Coûts et fiabilité des appels API

- Le coût est faible : environ **0,10 $** pour vectoriser tout le corpus et **0,002 $** par question.
  À 10 000 questions par jour, la génération coûterait de l'ordre de 20 $ par jour avec Mistral Large ;
  un modèle plus petit serait à réévaluer avec le jeu de test.
- Le point faible réel est la **disponibilité** : le pool partagé d'OpenRouter a renvoyé de nombreuses
  erreurs 429 pendant le projet. Pour la production, recommandation d'**appeler l'API Mistral
  directement** avec un quota dédié — une seule ligne à changer dans le code.

### 6.5 Suivi en production et détection des dérives

Indicateurs à suivre :

| Indicateur | Ce qu'il détecte |
| --- | --- |
| Score sur le jeu de test annoté, rejoué chaque semaine | dérive de qualité après un changement de modèle, de prompt ou de données |
| Rappel de la recherche sur ce même jeu | si une baisse vient de la recherche ou de la génération |
| Part des réponses « aucun évènement ne correspond » | un index vide ou périmé, ou des questions nouvelles que le corpus ne couvre pas |
| Distance moyenne entre la question et le meilleur chunk | des questions qui s'éloignent du corpus (dérive des usages) |
| Latence, taux d'erreurs 429, coût par question | santé technique du service |
| Retour utilisateur (pouce haut / bas) | la satisfaction réelle, que le jeu de test ne capte pas |
| Volume et fraîcheur des évènements indexés | une extraction qui échoue silencieusement |

Le jeu de test lui-même doit être **enrichi et ré-annoté** régulièrement, à partir de vraies questions
d'utilisateurs, puisque ses réponses attendues vieillissent avec le corpus.

### 6.6 Synthèse

| Priorité | Recommandation | Effet attendu |
| :-: | --- | --- |
| 1 | Recherche hybride BM25 + vecteurs | questions par thème et par lieu |
| 1 | Filtres de date et de ville extraits de la question | questions par date et par lieu |
| 2 | API Mistral directe avec quota dédié | disponibilité |
| 2 | Mise à jour quotidienne et incrémentale de l'index | fraîcheur |
| 3 | Base vectorielle managée si passage à l'échelle nationale | volume, filtrage, mises à jour |
| 3 | Rejeu hebdomadaire du jeu de test + tableau de bord | détection des dérives |

Les deux premières recommandations s'appuient sur des métadonnées déjà présentes dans l'index : elles
ne demandent pas de refaire le pipeline, et le jeu de test permettra de mesurer leur effet.

---

## 7. Au-delà du POC : la V2

Les sections précédentes décrivent le POC déposé le 25 septembre 2026, figé sous le tag
`depot-openclassrooms-2026-09-25`. La V2 applique ensuite les recommandations de priorité 1 et une partie
du suivi proposé en 6.5. La chaîne imposée ne change pas (LangChain, Faiss, Mistral, OpenAgenda) ; deux
briques s'y ajoutent, hors énoncé : une API FastAPI (`api/`) et une interface Next.js (`web/`).
`src/chat.py` reste la démo de secours.

### 7.1 Une application web

`POST /api/chat` diffuse la réponse en flux SSE : les filtres lus, les sources dès que la recherche a
répondu, le texte au fil de l'eau, puis les citations vérifiées et le coût. L'interface affiche des
citations cliquables qui mènent à la carte de chaque évènement, une carte OpenStreetMap (Leaflet) des lieux
cités, et s'utilise aussi sur téléphone. Pas d'historique envoyé au modèle, comme dans le POC.

### 7.2 De meilleures réponses

| Ajout | Effet recherché |
| --- | --- |
| Recherche hybride : BM25 + Faiss, fusionnés par l'`EnsembleRetriever` de LangChain | retrouver un mot exact comme « jazz », qu'un vecteur noie |
| Filtres lus par Mistral en sortie structurée : commune, période, âge, thème | transformer « en décembre » en dates, appliquées aux métadonnées |
| Puces de filtres que l'utilisateur corrige | rendre visible une mauvaise lecture de la question |
| Demande de précision si aucun filtre n'est lu | ne pas répondre au hasard à « un truc sympa ? » |

Le jeu de test passe à 22 questions avec deux questions vagues. Pour comparer à conditions égales, les deux
versions sont rejouées à la date du 25 septembre (`DATE_REFERENCE`). La V1 est la chaîne sans recherche
hybride ni filtres :

| Type | Correctes, V1 | V2 | Rappel, V1 | V2 |
| --- | :-: | :-: | :-: | :-: |
| Thème | 5 / 8 | 6 / 8 | 8 / 15 | 15 / 15 |
| Lieu | 1 / 5 | 4 / 5 | 3 / 6 | 6 / 6 |
| Date | 1 / 4 | 4 / 4 | 1 / 5 | 5 / 5 |
| Hors corpus | 3 / 3 | 2 / 3 | — | — |
| Précision | 0 / 2 | 2 / 2 | — | — |
| **Total** | **10 / 22** | **18 / 22** | **12 / 26** | **26 / 26** |

Le diagnostic de la section 5 est confirmé : réparer la recherche fait presque doubler le score. Ces
chiffres appellent trois réserves :

- **Le maillon faible a changé.** Le rappel est à 100 %, mais la génération reste imparfaite : sur le jazz,
  les deux concerts sont dans le contexte et le modèle n'en cite qu'un.
- **Le score varie d'une exécution à l'autre.** La relecture humaine donne 19 / 22 (la météo est un refus
  correct, jugé trop court). Un rejeu du 6 novembre sur l'index reconstruit redonne 18 / 22 et 26 / 26, mais
  quatre verdicts basculent, deux dans chaque sens : il faut comparer des tendances, pas un point isolé.
- **Risque de surapprentissage.** Donner le thème à BM25 plutôt que la question entière a été choisi sur ce
  jeu (rappel de 22 à 26 sur 26). Il faudra le contrôler sur de nouvelles questions annotées.

Le coût : chaque question fait désormais deux appels Mistral, lecture des filtres puis réponse.

### 7.3 Suivre la qualité en production

L'application mesure maintenant une partie des indicateurs de la section 6.5, réunis sur une page `/qualite` :

| Indicateur | Source | Valeur observée |
| --- | --- | --- |
| Score et rappel, par type de question, V1 contre V2 | `data/evaluation_v1.csv`, `evaluation_v2.csv` | 18 / 22, 26 / 26 |
| Détail : attendu, obtenu, verdict du juge | jeu de test et évaluation | 22 questions |
| Avis 👍 / 👎 et commentaires | `data/avis.jsonl` | à collecter auprès d'utilisateurs |
| Jetons et coût par question | usage renvoyé par OpenRouter, `data/journal.jsonl` | 0,0009 € en moyenne |
| Temps de recherche et de génération | `data/journal.jsonl` | 2,2 s et 1,3 s en moyenne |

Le coût et les temps portent sur 11 questions de test, le 6 novembre : un ordre de grandeur, pas une mesure
de production. La détection de dérive reste à automatiser : rejouer le jeu de test chaque semaine, comparer
au score de référence et alerter en cas de baisse, regarder la part d'avis négatifs et surveiller la
fraîcheur de l'index. Les tests de qualité l'ont montré pendant la V2 : 61 évènements ont dépassé un an en
deux semaines, et le contrôle a échoué tant que le dataset n'a pas été régénéré, puis l'index reconstruit
(2 066 évènements, 3 481 vecteurs).
