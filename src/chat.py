"""Démo en ligne de commande : pose une question, lit la réponse et les évènements qui la fondent."""

from rag import chaine

# le pool Mistral partagé d'OpenRouter sature par rafales : une 429 ne doit pas couper la démo
chaine = chaine.with_retry(stop_after_attempt=6)

print("Assistant Puls-Events — une question par ligne, « q » pour quitter.\n")
while True:
    question = input("> ").strip()
    if question.lower() in ("q", "quit", "exit"):
        break
    if not question:
        continue
    resultat = chaine.invoke(question)
    print("\n" + resultat["reponse"] + "\n")
    # les sources prouvent que la réponse vient de l'index et non de la mémoire du modèle
    print("Évènements utilisés :")
    for d in {d.metadata["uid"]: d for d in resultat["documents"]}.values():  # un évènement long = plusieurs chunks
        print("  -", d.metadata["titre"], "|", d.metadata["dates_texte"], "|", d.metadata["lieu"], "|", d.metadata["ville"])
    print()
