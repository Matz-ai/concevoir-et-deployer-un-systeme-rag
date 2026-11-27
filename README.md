# Puls-Events — assistant RAG d'évènements culturels

Un chatbot qui recommande des évènements culturels en Seine-Saint-Denis à partir des données
OpenAgenda. Recherche dans un index Faiss, réponse générée par Mistral, le tout avec LangChain.

Projet 11 du parcours Data Engineer OpenClassrooms ([énoncé](consigne.md)).

## Stack

- Python 3.12, `venv`, pandas
- Données : API OpenAgenda, Seine-Saint-Denis, évènements de moins d'un an
- Embeddings `mistral-embed-2312`, génération `mistral-large-2512`, appelés via OpenRouter
  (API compatible OpenAI : repasser sur l'API Mistral, c'est changer le `base_url`)
- Faiss pour l'index, LangChain pour la chaîne
- pytest + GitHub Actions
- V2 : API FastAPI et interface Next.js

## Installation

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env        # y mettre la clé OpenRouter
```

## Reconstruire les données et l'index

Rien n'est versionné, tout se reconstruit (quelques minutes, environ 0,10 $) :

```bash
python src/extract.py       # OpenAgenda -> data/raw/
python src/preprocess.py    # nettoyage -> data/processed/
python src/build_index.py   # chunks + embeddings -> data/faiss_index/
```

Au 25/09/2026 : 4 569 évènements extraits, 2 295 gardés après nettoyage (dont 2 146 ateliers
France Travail écartés), 3 860 vecteurs.

## Utiliser

```bash
python src/chat.py          # chatbot en ligne de commande
python src/evaluate.py      # score sur le jeu de test annoté
pytest                      # tests
```

Interface web : `npm install` dans `web/`, puis `powershell -File demo.ps1` et ouvrir
http://127.0.0.1:3000.

## Choix principaux

- Texte vectorisé : titre, mots-clés, lieu, ville, dates et description. Chunks de 1 000 caractères.
- Index `IndexFlatL2` : recherche exacte, suffisante pour quelques milliers de vecteurs.
- Seuls les évènements à venir sont proposés (filtre sur `date_fin`).
- V2 : recherche hybride BM25 + Faiss, et filtres (ville, dates, âge, thème) lus dans la question.

## Résultats

Jeu de test de 22 questions annotées, réponses jugées par Mistral puis relues à la main.

| | POC | V2 |
| --- | :-: | :-: |
| Réponses correctes | 10 / 22 | 18 / 22 |
| Évènements attendus retrouvés | 12 / 26 | 26 / 26 |

Détail dans `data/evaluation_v1.csv`, `data/evaluation_v2.csv` et dans le
[rapport technique](livrables/rapport_technique.pdf).

## Arborescence

```
src/         extraction, nettoyage, index, chaîne RAG, chatbot, évaluation
api/         API FastAPI (V2)
web/         interface Next.js (V2)
tests/       tests pytest
data/        jeu de test et résultats d'évaluation
livrables/   rapport technique et présentation
```
