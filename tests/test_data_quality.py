"""Contrôles de qualité du dataset indexable : périmètre, fraîcheur, unicité, complétude."""

import pandas as pd
import pytest

from preprocess import DEPARTEMENT, DESCRIPTION_MINI, SORTIE, nettoyer

MAINTENANT = pd.Timestamp.now(tz="UTC")
PROGRAMME = '{"label": {"fr": "Programmé"}}'


def evenement(**champs):
    """Un enregistrement brut OpenAgenda réduit aux champs dont le nettoyage se sert."""
    return {
        "uid": 1,
        "title_fr": "Concert de jazz",
        "description_fr": "Le conservatoire de Bobigny ouvre sa saison avec un concert de jazz.",
        "longdescription_fr": "",
        "keywords_fr": ["concert", "jazz"],
        "firstdate_begin": (MAINTENANT - pd.Timedelta(days=30)).isoformat(),
        "lastdate_end": (MAINTENANT - pd.Timedelta(days=30)).isoformat(),
        "daterange_fr": "Samedi 12 septembre, 20h00",
        "location_name": "Conservatoire",
        "location_address": "1 rue Gaston Roulaud 93000 Bobigny",
        "location_city": "Bobigny",
        "location_department": DEPARTEMENT,
        "status": PROGRAMME,
        "canonicalurl": "https://openagenda.com/evenement",
    } | champs


ECHANTILLON = [  # deux évènements valides, puis une violation de chacune des cinq règles
    evenement(),
    evenement(uid=2, title_fr="Exposition photo", location_name="Médiathèque"),
    evenement(uid=3, title_fr="Concert symphonique", location_department="Paris",
              location_name="Philharmonie", location_city="Paris"),
    evenement(uid=4, firstdate_begin=(MAINTENANT - pd.DateOffset(years=2)).isoformat()),
    evenement(uid=5, title_fr="Atelier de gravure", status='{"label": {"fr": "Annulé"}}'),
    evenement(uid=6),  # même titre, même date et même lieu que le premier
    evenement(uid=7, title_fr="Brocante", description_fr="Brocante."),
]


@pytest.fixture(params=["échantillon", "dataset réel"])
def evenements(request):
    """Rejoue chaque contrôle sur l'échantillon versionné puis sur le dataset produit localement.

    L'échantillon suffit à la CI, qui n'a ni clé API ni données extraites ; le dataset
    réel est le seul à prouver que ce qui partira dans l'index respecte les règles.
    """
    if request.param == "échantillon":
        return nettoyer(ECHANTILLON)[0]
    if not SORTIE.exists():
        pytest.skip(f"{SORTIE} absent : lancer extract.py puis preprocess.py")
    return pd.read_csv(SORTIE)


def test_perimetre_geographique(evenements):
    assert (evenements["departement"] == DEPARTEMENT).all()


def test_evenements_de_moins_d_un_an(evenements):
    debut = pd.to_datetime(evenements["date_debut"], format="ISO8601", utc=True)
    assert (debut >= MAINTENANT - pd.DateOffset(years=1)).all()


def test_pas_de_doublons(evenements):
    assert not evenements.duplicated(subset=["titre", "date_debut", "lieu"]).any()


def test_champs_indispensables_a_l_indexation(evenements):
    assert evenements[["uid", "titre", "date_debut", "lieu"]].notna().all().all()
    assert (evenements["description"].str.len() >= DESCRIPTION_MINI).all()


def test_chaque_regle_de_nettoyage_ecarte_son_evenement():
    _, journal = nettoyer(ECHANTILLON)
    assert list(journal.values()) == [1, 1, 1, 1, 1]
