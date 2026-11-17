"""Étape 2 : synthèse des articles en un digest d'environ 5 minutes de lecture."""
import json
import sys
from pathlib import Path

import anthropic

MODEL = "claude-sonnet-5-5"

SYSTEM = """Tu rédiges chaque matin une newsletter de veille sur Enedis (gestionnaire du réseau \
public de distribution d'électricité en France) pour un lecteur pressé.

Consignes :
- Longueur cible : 800 à 1 000 mots (environ 5 minutes de lecture). Moins si l'actualité est mince.
- Commence par un court paragraphe « L'essentiel » (2 à 3 phrases).
- Regroupe ensuite les sujets par thèmes, chacun sous un titre de niveau 2 (## ). Exemples de thèmes : \
réseau et investissements, Linky et compteurs, raccordement et énergies renouvelables, flexibilité et \
pilotage, météo et incidents, réglementation et tarifs, vie de l'entreprise. N'utilise que les thèmes utiles.
- Pour chaque sujet : 2 à 4 phrases, en reformulant avec tes propres mots (ne recopie pas les articles), \
puis la source sous la forme [Nom du média](lien).
- Quand plusieurs articles traitent du même sujet, fusionne-les en un seul point.
- N'invente rien : appuie-toi uniquement sur les articles fournis. Si une information est incertaine \
ou vient d'une seule source, dis-le.
- Ignore les articles hors sujet (ex. : homonymes, annonces sans lien avec Enedis).
- N'ajoute pas de titre principal (H1) ni de conclusion. Écris en français, ton clair et factuel.
- Réponds uniquement avec le Markdown de la newsletter."""


def main():
    articles = json.loads(Path("data/articles.json").read_text(encoding="utf-8"))
    out = Path("data/digest.md")

    if not articles:
        out.write_text(
            "Aucune actualité notable sur Enedis dans les dernières 24 heures.", encoding="utf-8"
        )
        print("Aucun article : digest vide.")
        return

    lines = []
    for i, a in enumerate(articles, 1):
        lines.append(
            f"{i}. {a['title']}\n   Média : {a['source']}\n   Date : {a['published']}\n"
            f"   Lien : {a['link']}\n   Extrait : {a['summary']}"
        )
    user_msg = "Voici les articles des dernières 24 heures :\n\n" + "\n\n".join(lines)

    client = anthropic.Anthropic()  # lit la variable d'environnement ANTHROPIC_API_KEY
    message = client.messages.create(
        model=MODEL,
        max_tokens=2500,
        system=SYSTEM,
        messages=[{"role": "user", "content": user_msg}],
    )
    text = "".join(b.text for b in message.content if b.type == "text").strip()
    if not text:
        sys.exit("Réponse vide de l'API.")
    out.write_text(text, encoding="utf-8")
    print(f"Digest écrit ({len(text.split())} mots) -> data/digest.md")


if __name__ == "__main__":
    main()
