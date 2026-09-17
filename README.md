# POC RAG — Assistant de recommandation d'évènements culturels

Proof of Concept d'un système **Retrieval-Augmented Generation** pour Puls-Events : un chatbot qui
recommande des évènements culturels en s'appuyant sur les données publiques **OpenAgenda**, une base
vectorielle **Faiss** et le modèle **Mistral**, orchestrés par **LangChain**.

Projet 11 du parcours Data Engineer OpenClassrooms — [énoncé complet](consigne.md).

---

## 📊 Où en est le projet ?

**Avancement : 4 / 12** ▓▓▓▓░░░░░░░░ 33 %

| # | Étape | Ce qui est produit | Statut |
| :-: | --- | --- | :-: |
| 0 | Cadrage & documentation | `consigne.md`, `README.md`, dépôt git | ✅ Fait |
| 1 | Environnement de travail | `requirements.txt`, `.venv`, `check_env.py` | ✅ Fait |
| 2 | Extraction OpenAgenda | `src/extract.py`, données brutes | ✅ Fait |
| 3 | Pré-processing & nettoyage | `src/preprocess.py`, dataset propre | ✅ Fait |
| 4 | Tests unitaires + pipeline CI | `tests/`, GitHub Actions | ⬜ À faire |
| 5 | Chunking, embeddings & index Faiss | `src/build_index.py`, index Faiss | ⬜ À faire |
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
│   └── preprocess.py    # nettoyage et structuration du dataset
└── data/                # non versionné, reconstruit par les scripts
    ├── raw/             # réponses brutes de l'API
    └── processed/       # dataset propre, prêt à indexer
```

Les deux scripts se lancent depuis la racine du dépôt, dans l'ordre :

```bash
python src/extract.py
python src/preprocess.py
```

`preprocess.py` affiche en fin d'exécution le nombre d'évènements en entrée, ceux écartés par chaque
règle de nettoyage et le nombre en sortie.

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
