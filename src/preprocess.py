"""Nettoyage des évènements OpenAgenda bruts vers le dataset indexable data/processed/."""

import html
import json
import re
from pathlib import Path

import pandas as pd

ENTREE = Path("data/raw/evenements_93.json")
SORTIE = Path("data/processed/evenements_93.csv")
DEPARTEMENT = "Seine-Saint-Denis"
DESCRIPTION_MINI = 30  # en deçà, la description ne fait que répéter le titre

COLONNES = {  # les 12 champs retenus sur les 56 de la source, et leur nom en sortie
    "uid": "uid",
    "title_fr": "titre",
    "description": "description",
    "keywords_fr": "mots_cles",
    "firstdate_begin": "date_debut",
    "lastdate_end": "date_fin",
    "daterange_fr": "dates_texte",
    "location_name": "lieu",
    "location_address": "adresse",
    "location_city": "ville",
    "location_department": "departement",
    "canonicalurl": "lien",
}


def en_texte_brut(valeur):
    """Débarrasse une description de son balisage.

    Les longues descriptions sont saisies dans un éditeur riche et arrivent en HTML :
    balises, entités (`&nbsp;`) et retours à la ligne n'apportent rien au modèle
    d'embeddings et gonflent inutilement le texte à vectoriser.
    """
    texte = html.unescape(str(valeur or ""))
    texte = re.sub(r"<[^>]+>", " ", texte)
    return re.sub(r"\s+", " ", texte).strip()


def meilleure_description(evenement):
    """Retient la plus informative des deux descriptions de l'évènement.

    `description_fr` est un résumé tronqué à 200 caractères, toujours présent ;
    `longdescription_fr` est le texte intégral, mais il manque pour un évènement sur
    quinze. On garde donc la plus longue des deux une fois nettoyées.
    """
    courte = en_texte_brut(evenement["description_fr"])
    longue = en_texte_brut(evenement["longdescription_fr"])
    return longue if len(longue) > len(courte) else courte


def nettoyer(bruts):
    """Applique les règles de nettoyage et renvoie le dataset propre avec le journal des écarts.

    Les règles s'enchaînent dans l'ordre : périmètre géographique, agenda France Travail
    (ateliers emploi publiés sur OpenAgenda, hors sujet pour Puls-Events), fenêtre d'un an,
    évènements annulés, doublons de publication, puis descriptions inexploitables.
    Chaque règle note combien de lignes elle écarte, pour que le récapitulatif final
    soit traçable.
    """
    df = pd.DataFrame(bruts)
    journal = {}

    def garder(masque, raison):
        nonlocal df
        journal[raison] = int((~masque).sum())
        df = df[masque]

    garder(df["location_department"] == DEPARTEMENT, "hors Seine-Saint-Denis")
    garder(~df["canonicalurl"].str.contains("openagenda.com/francetravail/"), "agenda France Travail (emploi, pas culture)")
    debut = pd.to_datetime(df["firstdate_begin"], format="ISO8601", utc=True)
    garder(debut >= pd.Timestamp.now(tz="UTC") - pd.DateOffset(years=1), "commencé il y a plus d'un an")
    garder(df["status"].map(lambda s: json.loads(s)["label"]["fr"]) != "Annulé", "annulé par l'organisateur")
    garder(~df.duplicated(subset=["title_fr", "firstdate_begin", "location_name"]), "doublon (même titre, date et lieu)")

    df = df.assign(description=df.apply(meilleure_description, axis=1))
    garder(df["description"].str.len() >= DESCRIPTION_MINI, "description inexploitable")

    df = df.assign(keywords_fr=df["keywords_fr"].map(lambda m: ", ".join(m) if isinstance(m, list) else ""))
    return df[list(COLONNES)].rename(columns=COLONNES), journal


if __name__ == "__main__":
    propre, journal = nettoyer(json.loads(ENTREE.read_text(encoding="utf-8")))
    SORTIE.parent.mkdir(parents=True, exist_ok=True)
    propre.to_csv(SORTIE, index=False, encoding="utf-8")

    print(f"{len(propre) + sum(journal.values())} évènements en entrée")
    for raison, nombre in journal.items():
        print(f"  - {nombre:4d} écartés : {raison}")
    print(f"{len(propre)} évènements écrits dans {SORTIE}")
