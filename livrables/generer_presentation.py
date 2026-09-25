"""Génère livrables/presentation.pptx (python-pptx) : relancer après chaque correction du contenu."""

from pptx import Presentation
from pptx.chart.data import CategoryChartData
from pptx.dml.color import RGBColor
from pptx.enum.chart import XL_CHART_TYPE, XL_LABEL_POSITION
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import PP_ALIGN
from pptx.util import Inches, Pt

BLEU, CLAIR, GRIS, FOND = RGBColor(0x14, 0x32, 0x5C), RGBColor(0x2D, 0x5A, 0x94), RGBColor(0x55, 0x5F, 0x6D), RGBColor(0xEE, 0xF2, 0xF7)
BLANC, ORANGE = RGBColor(0xFF, 0xFF, 0xFF), RGBColor(0xE0, 0x7A, 0x1F)

pres = Presentation()
pres.slide_width, pres.slide_height = Inches(13.333), Inches(7.5)


def texte(slide, x, y, l, h, lignes, taille=20, couleur=GRIS, gras=False, align=PP_ALIGN.LEFT):
    cadre = slide.shapes.add_textbox(Inches(x), Inches(y), Inches(l), Inches(h)).text_frame
    cadre.word_wrap = True
    for i, ligne in enumerate(lignes):
        p = cadre.paragraphs[0] if i == 0 else cadre.add_paragraph()
        p.text, p.alignment, p.space_after = ligne, align, Pt(10)
        p.font.size, p.font.color.rgb, p.font.bold = Pt(taille), couleur, gras


def boite(slide, x, y, l, h, lignes, fond=FOND, couleur=BLEU, taille=16):
    forme = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(x), Inches(y), Inches(l), Inches(h))
    forme.fill.solid()
    forme.fill.fore_color.rgb = fond
    forme.line.fill.background()
    cadre = forme.text_frame
    cadre.word_wrap = True
    for i, ligne in enumerate(lignes):
        p = cadre.paragraphs[0] if i == 0 else cadre.add_paragraph()
        p.text, p.alignment = ligne, PP_ALIGN.CENTER
        p.font.size, p.font.color.rgb, p.font.bold = Pt(taille if i == 0 else taille - 3), couleur, i == 0


def fleche(slide, x, y, l=0.5):
    forme = slide.shapes.add_shape(MSO_SHAPE.RIGHT_ARROW, Inches(x), Inches(y), Inches(l), Inches(0.35))
    forme.fill.solid()
    forme.fill.fore_color.rgb = CLAIR
    forme.line.fill.background()


def diapo(titre, numero):
    slide = pres.slides.add_slide(pres.slide_layouts[6])
    bandeau = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, pres.slide_width, Inches(1.1))
    bandeau.fill.solid()
    bandeau.fill.fore_color.rgb = BLEU
    bandeau.line.fill.background()
    texte(slide, 0.6, 0.22, 11, 0.8, [titre], 30, BLANC, True)
    texte(slide, 12.2, 6.95, 1, 0.4, [str(numero)], 12, GRIS, align=PP_ALIGN.RIGHT)
    return slide


def tableau(slide, x, y, l, lignes, largeurs, taille=15):
    forme = slide.shapes.add_table(len(lignes), len(lignes[0]), Inches(x), Inches(y), Inches(l), Inches(0.45 * len(lignes)))
    for j, largeur in enumerate(largeurs):
        forme.table.columns[j].width = Inches(largeur)
    for i, ligne in enumerate(lignes):
        for j, valeur in enumerate(ligne):
            cellule = forme.table.cell(i, j)
            cellule.text = valeur
            cellule.fill.solid()
            cellule.fill.fore_color.rgb = BLEU if i == 0 else (FOND if i % 2 else BLANC)
            p = cellule.text_frame.paragraphs[0]
            p.font.size, p.font.bold = Pt(taille), i == 0 or ligne[0].startswith("Total")
            p.font.color.rgb = BLANC if i == 0 else GRIS


# 1 : titre
slide = pres.slides.add_slide(pres.slide_layouts[6])
slide.background.fill.solid()
slide.background.fill.fore_color.rgb = BLEU
texte(slide, 0.9, 2.2, 11.5, 1.2, ["Un assistant RAG pour recommander des évènements culturels"], 38, BLANC, True)
texte(slide, 0.9, 3.7, 11.5, 0.6, ["POC pour Puls-Events avec OpenAgenda, Faiss, Mistral et LangChain"], 22, RGBColor(0xC9, 0xD8, 0xEE))
texte(slide, 0.9, 5.6, 11.5, 0.9, ["Mathieu Zinzen, Data Engineer", "Soutenance, septembre 2026"], 16, RGBColor(0xC9, 0xD8, 0xEE))

# 2 : le besoin
slide = diapo("Le besoin de Puls-Events", 2)
texte(slide, 0.8, 1.6, 6.2, 4.5, [
    "Puls-Events aide ses utilisateurs à trouver des évènements culturels, à partir des données OpenAgenda.",
    "Le projet : un chatbot à qui on pose une question en français.",
    "Il ne doit proposer que des évènements qui existent vraiment.",
    "Ce POC doit montrer que c'est faisable avant d'aller plus loin."], 20)
boite(slide, 7.6, 1.8, 5, 1.1, ["« Un spectacle de marionnettes", "pour mon fils ? »"], taille=20)
boite(slide, 7.6, 3.2, 5, 1.1, ["« Que faire le 21 juin 2027 ? »"], taille=20)
boite(slide, 7.6, 4.6, 5, 1.1, ["« Qu'est-ce qui passe au Triton ? »"], taille=20)

# 3 : le principe du RAG
slide = diapo("Le RAG en un schéma", 3)
etapes = [("Question", "de l'utilisateur"), ("Recherche", "dans la base vectorielle"),
          ("Contexte", "les évènements trouvés"), ("Génération", "le LLM rédige"), ("Réponse", "+ ses sources")]
for i, (titre, detail) in enumerate(etapes):
    boite(slide, 0.6 + i * 2.55, 2.3, 2.0, 1.5, [titre, detail], fond=BLEU if i in (1, 3) else FOND,
          couleur=BLANC if i in (1, 3) else BLEU, taille=19)
    if i < 4:
        fleche(slide, 2.65 + i * 2.55, 2.88)
texte(slide, 0.8, 4.6, 11.8, 2, [
    "Le modèle ne répond pas de mémoire : il s'appuie sur les évènements qu'on lui transmet.",
    "Retrieval : on cherche les documents utiles. Generation : le modèle rédige la réponse avec."], 20, align=PP_ALIGN.CENTER)

# 4 : architecture
slide = diapo("Architecture retenue", 4)
texte(slide, 0.6, 1.3, 6, 0.5, ["Hors ligne : on reconstruit la base quand on veut"], 17, CLAIR, True)
for i, (titre, detail) in enumerate([("OpenAgenda", "API open data"), ("extract.py", "4 569 bruts"),
                                     ("preprocess.py", "2 295 propres"), ("build_index.py", "chunks + Mistral"),
                                     ("Faiss", "3 860 vecteurs")]):
    boite(slide, 0.6 + i * 2.55, 1.9, 2.0, 1.2, [titre, detail], taille=17)
    if i < 4:
        fleche(slide, 2.65 + i * 2.55, 2.33)
boite(slide, 5.7, 3.3, 2.0, 0.6, ["pytest + CI"], fond=RGBColor(0xFD, 0xEB, 0xD9), couleur=ORANGE, taille=14)
texte(slide, 0.6, 4.2, 12, 0.5, ["En ligne : ce qui se passe quand on pose une question (src/rag.py)"], 17, CLAIR, True)
for i, (titre, detail) in enumerate([("Question", "chat.py"), ("mistral-embed", "vectorise"),
                                     ("Faiss", "10 chunks à venir"), ("Mistral Large", "rédige"),
                                     ("Réponse", "+ sources")]):
    boite(slide, 0.6 + i * 2.55, 4.8, 2.0, 1.2, [titre, detail], fond=BLEU, couleur=BLANC, taille=17)
    if i < 4:
        fleche(slide, 2.65 + i * 2.55, 5.23)
texte(slide, 0.6, 6.3, 12, 0.5, ["Les modèles Mistral sont appelés via OpenRouter. Pour passer directement par l'API Mistral, il suffit de changer l'URL."], 14)

# 5 : données
slide = diapo("Les données OpenAgenda", 5)
for i, (chiffre, legende) in enumerate([("4 569", "évènements extraits"), ("2 295", "après nettoyage"), ("276", "encore à venir")]):
    texte(slide, 0.8 + i * 4.1, 1.7, 3.6, 1, [chiffre], 54, BLEU, True, PP_ALIGN.CENTER)
    texte(slide, 0.8 + i * 4.1, 2.8, 3.6, 0.6, [legende], 18, GRIS, align=PP_ALIGN.CENTER)
texte(slide, 0.8, 4.0, 11.8, 3, [
    "Périmètre : la Seine-Saint-Denis (93). Assez d'évènements, et un index rapide à reconstruire.",
    "Période : un an d'historique et les évènements à venir, filtrés directement par l'API.",
    "Source : le jeu open data evenements-publics-openagenda, sans clé. On garde 12 champs sur 56.",
    "Villes principales : Saint-Denis (421), Saint-Ouen (300), Montreuil (201)."], 19)

# 6 : nettoyage et qualité
slide = diapo("Pré-processing et qualité des données", 6)
tableau(slide, 0.6, 1.5, 6.4, [["Règle de nettoyage", "Écartés"], ["Agenda France Travail (emploi)", "2 146"],
                               ["Description inexploitable", "83"], ["Doublon titre + date + lieu", "43"],
                               ["Annulé", "2"], ["Hors 93 ou plus d'un an", "0"]], [5.0, 1.4])
texte(slide, 7.5, 1.5, 5.3, 5.5, [
    "Presque la moitié des données brutes étaient des ateliers France Travail. Je l'ai vu en explorant le jeu de données.",
    "Les descriptions sont nettoyées du HTML, et on garde la version la plus complète.",
    "Les tests pytest vérifient le périmètre, la date, les doublons et les champs obligatoires.",
    "Ils tournent sur un petit échantillon dans GitHub Actions, et sur le vrai dataset en local."], 18)

# 7 : vectorisation et Faiss
slide = diapo("Vectorisation et index Faiss", 7)
tableau(slide, 0.6, 1.5, 12.1, [["Choix", "Ce qui est fait", "Pourquoi"],
                                ["Texte vectorisé", "titre + mots-clés + lieu + dates + description", "distinguer un spectacle joué dans deux villes"],
                                ["Chunks", "1 000 caractères, recouvrement 100", "74 % des évènements tiennent en un chunk"],
                                ["Embeddings", "mistral-embed, 1 024 dimensions", "imposé par l'énoncé"],
                                ["Index", "IndexFlatL2 (recherche exacte)", "3 860 vecteurs : quelques ms, 16 Mo"]],
        [2.4, 5.2, 4.5], 16)
texte(slide, 0.6, 4.6, 12, 2, [
    "Les vecteurs Mistral sont normés : la distance L2 donne le même classement que le cosinus.",
    "Des index comme IVF ou HNSW deviennent utiles à partir de quelques centaines de milliers de vecteurs.",
    "Reconstruire tout l'index prend quelques minutes et coûte environ 0,10 $."], 18)

# 8 : la chaîne
slide = diapo("La chaîne LangChain + Mistral", 8)
texte(slide, 0.8, 1.5, 6, 5, [
    "Recherche : 10 chunks, seulement parmi les évènements pas encore terminés.",
    "On ajoute la date complète à chaque chunk, car OpenAgenda n'affiche pas l'année.",
    "Génération : mistral-large, température 0, environ 0,002 $ par question.",
    "Le prompt demande de répondre seulement avec les évènements fournis, et de le dire s'il n'y a rien.",
    "Pas d'historique : chaque question est traitée à part."], 19)
boite(slide, 7.3, 1.6, 5.3, 2.2, ["Pourquoi LangChain ?", "Chaque brique (découpage, embeddings, Faiss, prompt, modèle) se remplace facilement, et la chaîne tient en quelques lignes."], taille=19)
boite(slide, 7.3, 4.2, 5.3, 2.0, ["Pourquoi filtrer les dates ?", "Quand on demandait au modèle d'ignorer les évènements passés, il ne le faisait pas toujours. Avec un filtre, c'est garanti."], taille=19)

# 9 : protocole
slide = diapo("Protocole d'évaluation", 9)
texte(slide, 0.8, 1.5, 6, 5, [
    "20 questions écrites à la main à partir d'évènements présents dans l'index.",
    "8 sur un thème, 5 sur un lieu, 4 sur une date et 3 hors sujet.",
    "Critère de l'énoncé : même sens et mêmes informations que la réponse attendue.",
    "C'est un modèle Mistral qui juge. J'ai relu ses 20 verdicts et je suis d'accord sur 18.",
    "On mesure aussi, sans LLM, si la recherche a trouvé les bons évènements."], 19)
tableau(slide, 7.2, 1.6, 5.5, [["Autre méthode", "Pourquoi je ne l'ai pas gardée"], ["Comparaison exacte", "refuse toute reformulation"],
                               ["Mots-clés", "ne comprend pas une réponse négative"], ["Similarité", "ne vérifie ni les dates ni les lieux"]], [2.3, 3.2], 16)

# 10 : résultats
slide = diapo("Résultats : 9 réponses correctes sur 20", 10)
donnees = CategoryChartData()
donnees.categories = ["Thème (8)", "Lieu (5)", "Date (4)", "Hors corpus (3)"]
donnees.add_series("Correctes (%)", (50, 40, 25, 67))
graphique = slide.shapes.add_chart(XL_CHART_TYPE.COLUMN_CLUSTERED, Inches(0.6), Inches(1.4), Inches(6.6), Inches(5.3), donnees).chart
graphique.has_legend, graphique.has_title = False, False
graphique.plots[0].has_data_labels = True
graphique.plots[0].data_labels.number_format, graphique.plots[0].data_labels.number_format_is_linked = '0"%"', False
graphique.plots[0].data_labels.position = XL_LABEL_POSITION.OUTSIDE_END
graphique.plots[0].series[0].format.fill.solid()
graphique.plots[0].series[0].format.fill.fore_color.rgb = CLAIR
graphique.value_axis.maximum_scale, graphique.value_axis.has_major_gridlines = 100, False
graphique.value_axis.visible = False
graphique.category_axis.tick_labels.font.size = Pt(14)
texte(slide, 7.6, 1.6, 5.2, 5.3, [
    "La recherche retrouve en moyenne 52 % des évènements attendus.",
    "Sur les 11 erreurs, 10 viennent d'une recherche incomplète.",
    "Quand la recherche trouve tout, 6 réponses sur 7 sont justes.",
    "C'est donc la recherche qu'il faut améliorer en priorité.",
    "Exemple : les concerts de jazz sortent aux rangs 114 et 388, car « jazz » n'est que dans leurs mots-clés."], 18)

# 11 : démo
slide = pres.slides.add_slide(pres.slide_layouts[6])
slide.background.fill.solid()
slide.background.fill.fore_color.rgb = BLEU
texte(slide, 0.9, 2.4, 11.5, 1, ["Démo live"], 48, BLANC, True, PP_ALIGN.CENTER)
texte(slide, 0.9, 3.7, 11.5, 0.6, ["python src/chat.py"], 24, RGBColor(0xC9, 0xD8, 0xEE), align=PP_ALIGN.CENTER)
texte(slide, 0.9, 4.6, 11.5, 1, ["Cinq questions : une simple, un lieu, une date, une recommandation et une hors sujet"], 18,
      RGBColor(0xC9, 0xD8, 0xEE), align=PP_ALIGN.CENTER)

# 12 : limites et recommandations
slide = diapo("Limites et recommandations", 12)
tableau(slide, 0.6, 1.5, 12.1, [["Priorité", "Recommandation", "Ce que ça corrige"],
                                ["1", "Recherche hybride BM25 + vecteurs", "thèmes, noms de lieux"],
                                ["1", "Filtres date et ville extraits de la question", "questions par date et par lieu"],
                                ["2", "API Mistral directe, quota dédié", "erreurs 429 d'OpenRouter"],
                                ["2", "Mise à jour quotidienne et incrémentale", "fraîcheur des évènements"],
                                ["3", "Base vectorielle (Qdrant, pgvector) à l'échelle nationale", "mémoire, filtrage, mises à jour"],
                                ["3", "Jeu de test rejoué chaque semaine + suivi", "dérives de qualité"]],
        [1.3, 6.4, 4.4], 16)
texte(slide, 0.6, 5.3, 12, 1.5, [
    "Le POC marche de bout en bout, et l'évaluation montre où l'améliorer.",
    "Le jeu de test n'est valable que jusqu'au 30 octobre 2026 : il faudra le mettre à jour."], 18)

pres.save("livrables/presentation.pptx")
