"""Étape 1 : collecte des articles Enedis des dernières 24 h via flux RSS."""
import difflib
import json
import re
from datetime import datetime, timedelta, timezone
from pathlib import Path
from urllib.parse import quote_plus

import feedparser

CUTOFF_HOURS = 24
MAX_ARTICLES = 40


def google_news(query: str) -> str:
    return (
        "https://news.google.com/rss/search?q="
        + quote_plus(f"{query} when:1d")
        + "&hl=fr&gl=FR&ceid=FR:fr"
    )


# (nom, url, filtrer_sur_mot_clé)
# Pour ajouter une source : ajoute une ligne avec son flux RSS.
# Mets True en 3e valeur si le flux n'est pas centré sur Enedis (filtre par mot-clé).
FEEDS = [
    ("Google Actualités : Enedis", google_news("Enedis"), False),
    ("Google Actualités : Linky", google_news("Linky Enedis"), False),
    (
        "Google Actualités : réseau",
        google_news("Enedis raccordement OR coupure OR tempête OR investissement OR flexibilité"),
        False,
    ),
]

KEYWORDS = ("enedis", "linky")


def clean(text: str) -> str:
    text = re.sub(r"<[^>]+>", " ", text or "")
    return re.sub(r"\s+", " ", text).strip()


def normalize_title(title: str) -> str:
    # Google Actualités ajoute " - Nom du média" à la fin des titres
    title = re.sub(r"\s+-\s+[^-]{2,40}$", "", title)
    return re.sub(r"[^a-z0-9àâçéèêëîïôûùüÿœ ]", "", title.lower()).strip()


def entry_date(entry):
    parsed = entry.get("published_parsed") or entry.get("updated_parsed")
    if not parsed:
        return None
    return datetime(*parsed[:6], tzinfo=timezone.utc)


def main():
    cutoff = datetime.now(timezone.utc) - timedelta(hours=CUTOFF_HOURS)
    articles = []

    for name, url, needs_filter in FEEDS:
        feed = feedparser.parse(url)
        print(f"{name}: {len(feed.entries)} entrées")
        for e in feed.entries:
            published = entry_date(e)
            if published and published < cutoff:
                continue
            title = clean(e.get("title", ""))
            summary = clean(e.get("summary", ""))
            if needs_filter and not any(k in f"{title} {summary}".lower() for k in KEYWORDS):
                continue
            source = ""
            if isinstance(e.get("source"), dict):
                source = e["source"].get("title", "")
            articles.append(
                {
                    "title": title,
                    "summary": summary[:400],
                    "source": source or name,
                    "link": e.get("link", ""),
                    "published": published.isoformat() if published else "",
                }
            )

    # Déduplication : titres quasi identiques = même sujet repris par plusieurs médias
    articles.sort(key=lambda a: a["published"], reverse=True)
    kept, seen = [], []
    for a in articles:
        norm = normalize_title(a["title"])
        if not norm or any(difflib.SequenceMatcher(None, norm, s).ratio() > 0.8 for s in seen):
            continue
        seen.append(norm)
        kept.append(a)

    kept = kept[:MAX_ARTICLES]
    out = Path("data")
    out.mkdir(exist_ok=True)
    (out / "articles.json").write_text(json.dumps(kept, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"{len(kept)} articles retenus -> data/articles.json")


if __name__ == "__main__":
    main()
