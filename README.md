# POC RAG — Assistant de recommandation d'évènements culturels

Proof of Concept d'un système **Retrieval-Augmented Generation** pour Puls-Events : un chatbot qui
recommande des évènements culturels en s'appuyant sur les données publiques **OpenAgenda**, une base
vectorielle **Faiss** et le modèle **Mistral**, orchestrés par **LangChain**.

Projet 11 du parcours Data Engineer OpenClassrooms — [énoncé complet](consigne.md).

---

## 📊 Où en est le projet ?

**Avancement : 6 / 12** ▓▓▓▓▓▓░░░░░░ 50 %

| # | Étape | Ce qui est produit | Statut |
| :-: | --- | --- | :-: |
| 0 | Cadrage & documentation | `consigne.md`, `README.md`, dépôt git | ✅ Fait |
| 1 | Environnement de travail | `requirements.txt`, `.venv`, `check_env.py` | ✅ Fait |
| 2 | Extraction OpenAgenda | `src/extract.py`, données brutes | ✅ Fait |
| 3 | Pré-processing & nettoyage | `src/preprocess.py`, dataset propre | ✅ Fait |
| 4 | Tests unitaires + pipeline CI | `tests/`, GitHub Actions | ✅ Fait |
| 5 | Chunking, embeddings & index Faiss | `src/build_index.py`, index Faiss | ✅ Fait |
| 6 | Chaîne RAG LangChain + Mistral | `src/rag.py` | ⬜ À faire |
| 7 | Jeu de test annoté & évaluation | `data/qa_test.json`, `src/evaluate.py` | ⬜ À faire |
| 8 | Démo live (chatbot en ligne de commande) | `src/chat.py` | ⬜ À faire |
| 9 | Rapport technique (5–10 pages) | `livrables/rapport_technique.pdf` | ⬜ À faire |
| 10 | Présentation (10–15 slides) | `livrables/presentation.pptx` | ⬜ À faire |
| 11 | README final & packaging des livrables | zip de dépôt OpenClassrooms | ⬜ À faire |

**Légende :** ✅ Fait · 🟡 En cours · ⬜ À faire

Les étapes sont menées **dans l'ordre**, une à la fois.

> Le détail des étapes et les critères de validation de chacune sont dans `conv.md` (fichier local,
> non versionné).

---

## 🎯 Objectifs

Les trois compétences évaluées par OpenClassrooms :

1. **Configurer l'environnement de travail** nécessaire à l'exploitation des données.
2. **Mettre en place un processus de nettoyage** afin d'améliorer la qualité des données.
3. **Identifier ou créer un modèle d'apprentissage** adapté aux contraintes et besoins métiers.

Contraintes imposées par l'énoncé :

- Données issues de l'**API OpenAgenda**, limitées à un périmètre géographique et à des évènements
  de **moins d'un an**. Périmètre retenu : la **Seine-Saint-Denis (93)**, soit **4 760 évènements**
  démarrant dans les douze derniers mois ou à venir, **4 559** après nettoyage.
- Base vectorielle **reconstructible sur demande** (scripts de pré-processing et de vectorisation).
- Pas d'historique de conversation dans le POC.

---

## 🧱 Stack technique

| Brique | Outil | Pourquoi |
| --- | --- | --- |
| Langage | Python 3 | Imposé |
| Environnement | `venv` + `requirements.txt` | Imposé (venv ou conda) |
| Source de données | API OpenAgenda | Imposé |
| Manipulation de données | pandas | Recommandé par l'énoncé |
| Embeddings | `mistralai/mistral-embed-2312` | Imposé (Mistral) |
| Génération | modèle de chat Mistral | Imposé (Mistral) |
| Accès aux modèles | OpenRouter | Voir note ci-dessous |
| Base vectorielle | Faiss (`faiss-cpu`) | Imposé |
| Orchestration RAG | LangChain | Imposé |
| Tests | pytest + GitHub Actions | Tests « intégrés sous forme de pipeline » |

Rien d'autre : ni API web, ni Docker, ni interface graphique — l'énoncé ne les demande pas.

> **Note sur l'accès aux modèles.** Les modèles utilisés sont bien ceux de Mistral, comme l'impose
> l'énoncé, mais ils sont appelés via OpenRouter plutôt que par une clé Mistral directe. OpenRouter
> exposant une API compatible OpenAI, le code utilise `langchain-openai` avec un `base_url`
> personnalisé. Repasser sur l'API Mistral native ne demande que de changer ce `base_url` et le nom
> des modèles — c'est la recommandation faite pour la version de production.

---

## 🚀 Reproduire le projet

Python 3.11 ou 3.12 (Faiss n'est pas encore packagé pour les toutes dernières versions).

```bash
git clone <url-du-depot> && cd concevoir-et-deployer-un-systeme-rag
python -m venv .venv
.venv\Scripts\activate          # Windows — sous Linux/macOS : source .venv/bin/activate
pip install -r requirements.txt
python check_env.py               # doit afficher les 8 versions sans erreur
```

Puis copier `.env.example` en `.env` et y renseigner la clé OpenRouter :

```bash
cp .env.example .env
```

---

## 📁 Structure des fichiers

> Cette section sera complétée au fil des étapes.

```
.
├── consigne.md          # énoncé OpenClassrooms intégral
├── README.md            # ce fichier
├── CLAUDE.md            # règles de travail pour l'assistant
├── requirements.txt     # dépendances épinglées
├── .env.example         # variable d'environnement attendue (clé OpenRouter)
├── check_env.py         # vérifie que les bibliothèques sont installées
├── src/
│   ├── extract.py       # extraction des évènements OpenAgenda (Seine-Saint-Denis)
│   ├── preprocess.py    # nettoyage et structuration du dataset
│   └── build_index.py   # chunking, vectorisation Mistral et index Faiss
├── tests/
│   └── test_data_quality.py  # contrôles de qualité du dataset
├── pytest.ini           # rend src/ importable par les tests
├── .github/workflows/
│   └── tests.yml        # pipeline CI : pytest à chaque push
└── data/                # non versionné, reconstruit par les scripts
    ├── raw/             # réponses brutes de l'API
    ├── processed/       # dataset propre, prêt à indexer
    └── faiss_index/     # index vectoriel (index.faiss + métadonnées)
```

Les trois scripts se lancent depuis la racine du dépôt, dans l'ordre :

```bash
python src/extract.py
python src/preprocess.py
python src/build_index.py
```

`preprocess.py` affiche en fin d'exécution le nombre d'évènements en entrée, ceux écartés par chaque
règle de nettoyage et le nombre en sortie.

---

## 🔍 La base vectorielle

`build_index.py` reconstruit l'index de bout en bout à chaque exécution — c'est la contrainte
« base vectorielle reconstructible sur demande » de l'énoncé. Rien n'est versionné : l'index se
régénère à partir de `data/processed/` en quelques minutes, pour environ **0,10 $** d'appels API.

| Choix | Ce qui est fait | Pourquoi |
| --- | --- | --- |
| Texte vectorisé | titre + mots-clés + lieu + ville + dates + description | sans le lieu dans le vecteur, le même spectacle à Montreuil et à Bobigny est indiscernable en recherche sémantique |
| Découpage | 1 000 caractères, recouvrement de 100 | 84 % des évènements tiennent en un seul chunk ; seules les longues programmations sont coupées |
| Embeddings | `mistralai/mistral-embed-2312`, 1024 dimensions, par lots de 50 | modèle imposé par l'énoncé, appelé via OpenRouter |
| Index | `IndexFlatL2`, le défaut de LangChain | recherche exacte, aucun paramètre à régler ; `IVF` et `HNSW` échangent du rappel contre de la vitesse, ce qui n'a d'intérêt qu'à partir de centaines de milliers de vecteurs |

**4 559 évènements → 6 419 chunks → 6 419 vecteurs**, soit 26 Mo d'index et 8 Mo de métadonnées.
Les métadonnées gardées à côté de chaque vecteur sont celles qu'exige l'énoncé (dates, lieux,
descriptions), plus le `uid` qui relie un chunk à son évènement et le lien OpenAgenda.

Deux détails qui se justifient à l'oral :

- les vecteurs Mistral sont **normés** (norme = 1), donc la distance L2 classe exactement comme le
  cosinus — le choix `IndexFlatL2` n'introduit aucun biais par rapport à `IndexFlatIP` ;
- `OpenAIEmbeddings` compte par défaut les tokens avec `tiktoken` et envoie des identifiants de
  tokens OpenAI à la place du texte, ce que l'endpoint Mistral refuse : d'où le
  `check_embedding_ctx_length=False` dans le script.

---

## ✅ Tests

```bash
pytest
```

`tests/test_data_quality.py` vérifie ce qui partira dans la base vectorielle : périmètre
Seine-Saint-Denis, évènements de moins d'un an, absence de doublons, champs indispensables
renseignés. Chaque contrôle tourne deux fois — sur un échantillon de sept évènements construit dans
le fichier de test, puis sur `data/processed/` s'il a été généré.

Ce doublon n'est pas décoratif : l'échantillon rend les tests exécutables partout, y compris dans la
CI qui n'a ni clé API ni données extraites, tandis que le passage sur le dataset réel est le seul à
prouver que les évènements réellement indexés respectent les règles. Quand le dataset est absent, ces
quatre tests sont marqués « skipped » plutôt que faussement verts.

Le pipeline `.github/workflows/tests.yml` installe `requirements.txt` et lance `pytest` à chaque
push — il vérifie donc aussi que l'environnement se réinstalle proprement sur une machine neuve.

---

## 📦 Livrables OpenClassrooms

Dépôt attendu : un zip `Concevez_et_deployez_un_systeme_RAG_zinzen_mathieu` contenant :

| N° | Fichier | Statut |
| :-: | --- | :-: |
| 1 | `Zinzen_Mathieu_1_readme_092026` | ⬜ |
| 2 | `Zinzen_Mathieu_2_gestion_092026` | ⬜ |
| 3 | `Zinzen_Mathieu_3_scripts_092026` | ⬜ |
| 4 | `Zinzen_Mathieu_4_tests_092026` | ⬜ |
| 5 | `Zinzen_Mathieu_5_rag_092026` | ⬜ |
| 6 | `Zinzen_Mathieu_6_rapport_092026` | ⬜ |
| 7 | `Zinzen_Mathieu_7_presentation_092026` | ⬜ |
