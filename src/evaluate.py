"""Évaluation de la chaîne RAG sur le jeu de test annoté : un juge Mistral compare chaque réponse
générée à la réponse attendue, et on mesure à part si la recherche a remonté les bons évènements."""

import json

import pandas as pd

from rag import chaine, modele

JUGE = """Tu évalues un assistant qui recommande des évènements culturels.
Une réponse est correcte si elle a le même sens et contient les mêmes informations que la réponse
attendue. Des informations supplémentaires (autres évènements, dates, horaires, précisions) ne la
rendent pas incorrecte ; un évènement, une date ou un lieu attendu qui manque ou qui est faux, si.

Question : {question}
Réponse attendue : {attendue}
Réponse de l'assistant : {generee}

Réponds sur la première ligne par CORRECT ou INCORRECT, puis justifie en une phrase."""

# le pool Mistral partagé d'OpenRouter sature par rafales : on espace les nouvelles tentatives
chaine, juge = chaine.with_retry(stop_after_attempt=6), modele.with_retry(stop_after_attempt=6)

lignes = []
for qa in json.load(open("data/qa_test.json", encoding="utf-8")):
    resultat = chaine.invoke(qa["question"])
    recuperes = {d.metadata["uid"] for d in resultat["documents"]}
    trouves = len(recuperes & set(qa["evenements"]))
    verdict = juge.invoke(JUGE.format(question=qa["question"], attendue=qa["reponse_attendue"],
                                       generee=resultat["reponse"])).content.strip()
    lignes.append({"question": qa["question"][:45], "type": qa["type"],
                   "recherche": f"{trouves}/{len(qa['evenements'])}" if qa["evenements"] else "-",
                   "correct": verdict.lstrip("*# ").startswith("CORRECT"),  # Mistral met parfois le verdict en gras
                   "justification": verdict.split("\n", 1)[-1].strip(), "reponse": resultat["reponse"]})

resultats = pd.DataFrame(lignes)
resultats.to_csv("data/evaluation.csv", index=False)  # détail relu à la main et repris dans le rapport
print(resultats.drop(columns=["justification", "reponse"]).to_string(), "\n")
print(resultats.groupby("type").correct.mean().map("{:.0%}".format).to_string(), "\n")
print(f"Score global : {resultats.correct.sum()}/{len(resultats)} réponses correctes")
