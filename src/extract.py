"""Extraction des évènements OpenAgenda de Seine-Saint-Denis vers data/raw/."""

import json
from pathlib import Path

import requests

API = "https://public.opendatasoft.com/api/explore/v2.1/catalog/datasets/evenements-publics-openagenda/records"
DEPARTEMENT = "Seine-Saint-Denis"
FENETRE = "firstdate_begin >= now(years=-1)"  # évènements de moins d'un an
PAGE = 100  # maximum autorisé par l'API Opendatasoft
SORTIE = Path("data/raw/evenements_93.json")


def extraire():
    """Pagine l'open data OpenAgenda et renvoie les évènements bruts du département.

    Les filtres géographique et temporel sont appliqués côté serveur : l'API refuse
    un offset supérieur à 10 000, il faut donc descendre sous ce seuil avant de paginer.
    """
    evenements = []
    while True:
        reponse = requests.get(API, params={
            "where": f'location_department="{DEPARTEMENT}" and {FENETRE}',
            "order_by": "uid",
            "limit": PAGE,
            "offset": len(evenements),
        }, timeout=60)
        reponse.raise_for_status()
        page = reponse.json()["results"]
        evenements += page
        if len(page) < PAGE:
            return evenements


if __name__ == "__main__":
    evenements = extraire()
    SORTIE.parent.mkdir(parents=True, exist_ok=True)
    SORTIE.write_text(json.dumps(evenements, ensure_ascii=False), encoding="utf-8")
    print(f"{len(evenements)} évènements écrits dans {SORTIE}")
