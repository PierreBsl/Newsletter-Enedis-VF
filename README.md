# Newsletter Enedis

Digest quotidien de l'actualité Enedis, lisible en 5 minutes, publié sur GitHub Pages.

**Fonctionnement** : chaque matin, GitHub Actions lance `src/collect.py` (flux RSS des dernières 24 h,
dédoublonnage), `src/digest.py` (synthèse par thèmes avec l'API Claude) puis `src/build.py`
(page `docs/index.html`).

## Mise en route

1. Crée une clé API sur https://console.anthropic.com.
2. Dépôt GitHub > Settings > Secrets and variables > Actions > New repository secret :
   nom `ANTHROPIC_API_KEY`, valeur = ta clé.
3. Dépôt GitHub > Settings > Pages : Source « Deploy from a branch », branche `main`, dossier `/docs`.
4. Onglet Actions > « Newsletter Enedis quotidienne » > Run workflow pour un premier essai.

## Test en local

```bash
pip install -r requirements.txt
export ANTHROPIC_API_KEY=sk-ant-...
python src/collect.py && python src/digest.py && python src/build.py
```

## Personnaliser

- Sources : liste `FEEDS` dans `src/collect.py`.
- Longueur, thèmes, ton : constante `SYSTEM` dans `src/digest.py`.
- Heure d'envoi : ligne `cron` dans `.github/workflows/daily.yml` (heure UTC).
