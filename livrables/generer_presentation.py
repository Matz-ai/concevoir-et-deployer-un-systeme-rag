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
texte(slide, 0.9, 5.6, 11.5, 0.9, ["Mathieu Zinzen, Data Engineer", "Novembre 2026"], 16, RGBColor(0xC9, 0xD8, 0xEE))

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
for i, (titre, detail) in enumerate([("Question", "en français"), ("Mistral", "lit les filtres"),
                                     ("BM25 + Faiss", "10 chunks filtrés"), ("Mistral Large", "rédige"),
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
for i, (titre, detail) in enumerate([("1. Lire la question", "Mistral remplit ville, dates, âge, thème"),
                                     ("2. Chercher", "BM25 (mots exacts) + Faiss (sens), filtrés"),
                                     ("3. Répondre", "seulement avec les évènements trouvés")]):
    boite(slide, 0.6 + i * 4.2, 1.5, 3.7, 1.4, [titre, detail], fond=BLEU, couleur=BLANC, taille=19)
    if i < 2:
        fleche(slide, 4.35 + i * 4.2, 2.03)
texte(slide, 0.8, 3.3, 6, 3.5, [
    "Pas d'agent : chaque question suit toujours ces trois étapes.",
    "« Ce week-end » devient deux vraies dates, appliquées aux métadonnées.",
    "Les évènements terminés sont écartés par le code, pas par le modèle.",
    "Question trop vague : l'assistant demande une précision."], 18)
boite(slide, 7.3, 3.4, 5.3, 2.8, ["Pourquoi LangChain ?", "Imposé par l'énoncé, mais surtout des briques déjà testées : BM25, fusion des classements, sortie structurée, nouvelles tentatives, streaming, comptage des jetons. Et un standard que l'équipe connaît."], taille=18)

# 9 : protocole
slide = diapo("Protocole d'évaluation", 9)
texte(slide, 0.8, 1.5, 6, 5, [
    "22 questions écrites à la main à partir d'évènements présents dans l'index.",
    "8 sur un thème, 5 sur un lieu, 4 sur une date, 3 hors sujet, 2 trop vagues.",
    "Critère de l'énoncé : même sens et mêmes informations que la réponse attendue.",
    "Un modèle Mistral juge, et j'ai relu chaque verdict.",
    "On mesure aussi, sans LLM, si la recherche a trouvé les bons évènements."], 19)
tableau(slide, 7.2, 1.6, 5.5, [["Autre méthode", "Pourquoi je ne l'ai pas gardée"], ["Comparaison exacte", "refuse toute reformulation"],
                               ["Mots-clés", "ne comprend pas une réponse négative"], ["Similarité", "ne vérifie ni les dates ni les lieux"]], [2.3, 3.2], 16)

# 10 : résultats
slide = diapo("Résultats : de 10 à 18 sur 22", 10)
donnees = CategoryChartData()
donnees.categories = ["Thème (8)", "Lieu (5)", "Date (4)", "Hors corpus (3)", "Vague (2)"]
donnees.add_series("Faiss seul", (5, 1, 1, 3, 0))
donnees.add_series("Hybride + filtres", (6, 4, 4, 2, 2))
graphique = slide.shapes.add_chart(XL_CHART_TYPE.COLUMN_CLUSTERED, Inches(0.6), Inches(1.4), Inches(7.2), Inches(5.3), donnees).chart
graphique.has_title = False
graphique.has_legend, graphique.legend.include_in_layout = True, False
graphique.legend.font.size = Pt(14)
graphique.plots[0].has_data_labels = True
graphique.plots[0].data_labels.position = XL_LABEL_POSITION.OUTSIDE_END
graphique.plots[0].data_labels.font.size = Pt(14)
for serie, couleur in zip(graphique.plots[0].series, (ORANGE, CLAIR)):
    serie.format.fill.solid()
    serie.format.fill.fore_color.rgb = couleur
graphique.value_axis.maximum_scale, graphique.value_axis.has_major_gridlines = 9, False
graphique.value_axis.visible = False
graphique.category_axis.tick_labels.font.size = Pt(14)
texte(slide, 8.1, 1.5, 4.8, 5.3, [
    "Avec Faiss seul, la recherche ratait le jazz (rangs 114 et 388) et les dates.",
    "BM25 et les filtres : le rappel passe de 12 à 26 sur 26.",
    "Le maillon faible est maintenant la génération : le modèle oublie un concert de jazz.",
    "Relu à la main : 19 sur 22."], 18)

# 11 : l'application
slide = diapo("L'application", 11)
slide.shapes.add_picture("livrables/captures/reponse-shakespeare.jpg", Inches(0.6), Inches(1.45), height=Inches(5.3))
texte(slide, 8.0, 1.5, 4.9, 5.3, [
    "Une API FastAPI et une interface Next.js autour de la même chaîne.",
    "Les sources s'affichent avant le texte, qui s'écrit au fil de l'eau.",
    "Chaque citation mène à sa fiche, et une carte montre les lieux.",
    "Une page Qualité suit le score, les avis, le coût (0,001 €) et le temps (3,5 s) par question."], 18)

# 12 : démo
slide = pres.slides.add_slide(pres.slide_layouts[6])
slide.background.fill.solid()
slide.background.fill.fore_color.rgb = BLEU
texte(slide, 0.9, 2.4, 11.5, 1, ["Démo live"], 48, BLANC, True, PP_ALIGN.CENTER)
texte(slide, 0.9, 3.7, 11.5, 0.6, ["L'application dans le navigateur, avec python src/chat.py en secours"], 24, RGBColor(0xC9, 0xD8, 0xEE), align=PP_ALIGN.CENTER)
texte(slide, 0.9, 4.6, 11.5, 1, ["Un thème, un lieu, une date, une question vague et une question hors sujet, puis la page Qualité"], 18,
      RGBColor(0xC9, 0xD8, 0xEE), align=PP_ALIGN.CENTER)

# 13 : limites et recommandations
slide = diapo("Limites et recommandations", 13)
tableau(slide, 0.6, 1.5, 12.1, [["Priorité", "Recommandation", "Ce que ça corrige"],
                                ["1", "API Mistral directe, quota dédié", "erreurs 429 d'OpenRouter"],
                                ["1", "Mise à jour quotidienne et incrémentale", "fraîcheur des évènements"],
                                ["2", "Rejeu automatique du jeu de test et alertes", "dérives de qualité"],
                                ["3", "Base vectorielle (Qdrant, pgvector) à l'échelle nationale", "mémoire, filtrage, mises à jour"]],
        [1.3, 6.4, 4.4], 16)
texte(slide, 0.6, 4.6, 12, 2, [
    "L'évaluation a d'abord montré que la recherche était le problème, puis mesuré l'effet de la correction.",
    "Le jeu de test vieillit avec les évènements : il faudra annoter de nouvelles questions."], 18)

pres.save("livrables/presentation.pptx")
