# erikafashion-sos

Share of Search dashboard pro erikafashion.cz — kompetitivní analýza českého fashion trhu.

**Live:** https://patrikpilous-dev.github.io/erikafashion-sos/

## Co to je

Interaktivní dashboard, který sleduje 18 značek na českém fashion trhu (Shein, Sinsay, Zalando, About You, erikafashion.cz atd.) přes několik metrik:

- **Share of Search** — podíl brandového hledání v Google (metodika Les Binet, IPA 2020)
- **Organický traffic** — odhad měsíčních návštěv z Ahrefs
- **Google Search Console** — reálná data kliků, impresí a CTR pro erikafashion.cz
- **Brandové asociace** — s čím lidé nejčastěji hledají jednotlivé značky

## Architektura

```
index.html              — statický dashboard (Chart.js + vanilla JS)
data/history.json       — kanonická databáze (25+ měsíců historie)
logo.svg                — logo erikafashion.cz
.github/workflows/
  deploy.yml            — auto-deploy na GitHub Pages při push
.claude/commands/
  update-sos.md         — slash command pro měsíční update
CLAUDE.md               — instrukce pro měsíční update přes Claude Code
```

## Měsíční aktualizace

Aktualizace probíhá ručně přes Claude Code s Ahrefs MCP napojením.

**Postup:**
1. `cd` do tohoto repa v Claude Code
2. `/update-sos` (slash command)
3. Claude stáhne čerstvá data z Ahrefs + GSC, aktualizuje `data/history.json`, commit + push
4. GitHub Pages se automaticky přestaví

## Data

Dashboard načítá `data/history.json` přes `fetch()` a renderuje grafy + tabulky z této datové vrstvy.
