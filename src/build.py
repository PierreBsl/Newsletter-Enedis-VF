"""Étape 3 : génération de la page web docs/index.html."""
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

import markdown

MOIS = ["janvier", "février", "mars", "avril", "mai", "juin", "juillet",
        "août", "septembre", "octobre", "novembre", "décembre"]
JOURS = ["lundi", "mardi", "mercredi", "jeudi", "vendredi", "samedi", "dimanche"]

TEMPLATE = """<!doctype html>
<html lang="fr">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Actu Enedis – {date}</title>
<style>
  :root {{ --bg: #ffffff; --fg: #1d1d1f; --muted: #6b6b70; --accent: #0a6cc4; --line: #e4e4e7; }}
  @media (prefers-color-scheme: dark) {{
    :root {{ --bg: #141416; --fg: #ececee; --muted: #9a9aa2; --accent: #5aa9f0; --line: #2b2b30; }}
  }}
  body {{ margin: 0; background: var(--bg); color: var(--fg);
         font: 17px/1.65 -apple-system, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; }}
  main {{ max-width: 42rem; margin: 0 auto; padding: 2rem 1.25rem 4rem; }}
  header {{ border-bottom: 1px solid var(--line); margin-bottom: 1.5rem; padding-bottom: 1rem; }}
  h1 {{ font-size: 1.7rem; margin: 0 0 .25rem; }}
  .meta {{ color: var(--muted); font-size: .9rem; }}
  h2 {{ font-size: 1.2rem; margin: 2rem 0 .5rem; }}
  a {{ color: var(--accent); }}
  footer {{ color: var(--muted); font-size: .8rem; margin-top: 3rem; }}
</style>
</head>
<body>
<main>
<header>
  <h1>Actu Enedis</h1>
  <div class="meta">{date} · {minutes} min de lecture</div>
</header>
{content}
<footer>Généré automatiquement à partir de la presse en ligne. Les résumés peuvent comporter des erreurs : vérifie les sources.</footer>
</main>
</body>
</html>
"""


def main():
    md_text = Path("data/digest.md").read_text(encoding="utf-8")
    now = datetime.now(ZoneInfo("Europe/Paris"))
    date = f"{JOURS[now.weekday()]} {now.day} {MOIS[now.month - 1]} {now.year}"
    minutes = max(1, round(len(md_text.split()) / 200))
    html = TEMPLATE.format(
        date=date,
        minutes=minutes,
        content=markdown.markdown(md_text, extensions=["extra"]),
    )
    out = Path("docs/index.html")
    out.parent.mkdir(exist_ok=True)
    out.write_text(html, encoding="utf-8")
    print(f"Page générée : {out} ({minutes} min)")


if __name__ == "__main__":
    main()
