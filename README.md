# POC RAG — Assistant de recommandation d'évènements culturels

Proof of Concept d'un système **Retrieval-Augmented Generation** pour Puls-Events : un chatbot qui
recommande des évènements culturels en s'appuyant sur les données publiques **OpenAgenda**, une base
vectorielle **Faiss** et le modèle **Mistral**, orchestrés par **LangChain**.

Projet 11 du parcours Data Engineer OpenClassrooms — [énoncé complet](consigne.md).

---

## 📊 Où en est le projet ?

**Avancement : 1 / 12** ▓░░░░░░░░░░░ 8 %

| # | Étape | Ce qui est produit | Statut |
| :-: | --- | --- | :-: |
| 0 | Cadrage & documentation | `consigne.md`, `README.md`, dépôt git | ✅ Fait |
| 1 | Environnement de travail | `requirements.txt`, `.venv`, `check_env.py` | ⬜ À faire |
| 2 | Extraction OpenAgenda | `src/extract.py`, données brutes | ⬜ À faire |
| 3 | Pré-processing & nettoyage | `src/preprocess.py`, dataset propre | ⬜ À faire |
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
  de **moins d'un an**. Périmètre retenu : la **Seine-Saint-Denis (93)**.
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
| Embeddings & LLM | API Mistral | Imposé |
| Base vectorielle | Faiss (`faiss-cpu`) | Imposé |
| Orchestration RAG | LangChain | Imposé |
| Tests | pytest + GitHub Actions | Tests « intégrés sous forme de pipeline » |

Rien d'autre : ni API web, ni Docker, ni interface graphique — l'énoncé ne les demande pas.

---

## 🚀 Reproduire le projet

> Cette section sera complétée à l'étape 1.

```bash
# à venir
```

---

## 📁 Structure des fichiers

> Cette section sera complétée au fil des étapes.

```
.
├── consigne.md          # énoncé OpenClassrooms intégral
├── README.md            # ce fichier
└── CLAUDE.md            # règles de travail pour l'assistant
```

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
