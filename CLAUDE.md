# erikafashion-sos — Share of Search Dashboard

Kompetitivní analýza českého fashion trhu pro erikafashion.cz.

**Live URL:** https://patrikpilous-dev.github.io/erikafashion-sos/
**Repo:** https://github.com/patrikpilous-dev/erikafashion-sos

## Architektura

- `index.html` — statický dashboard, načítá data z `data/history.json` přes `fetch()`
- `data/history.json` — kanonická databáze (25 měsíců historie)
- `logo.svg` — logo erikafashion.cz
- `.github/workflows/deploy.yml` — auto-deploy na GitHub Pages při push do master

## Měsíční aktualizace dat

Nemám standalone Ahrefs API klíč — používám Claude Code s Ahrefs MCP napojením.
Aktualizace probíhá ručně přes Claude Code.

**Postup:**
1. Otevřít tento projekt v Claude Code (`cd C:\Users\patri\.claude\projects\erikafashion-sos`)
2. Říct Claudovi: "Aktualizuj data v dashboardu" nebo použít `/update-sos`
3. Claude projde všechny kroky níže a pushne změny

**Co se má aktualizovat (checklist pro Claude):**

### 1. Brandové hledání (Ahrefs Keywords Explorer, CZ)
Pro každý z 18 brandů (podle `data/history.json` > brands) stáhnout aktuální měsíční volume přes `keywords-explorer-overview` s:
- `country: "CZ"`
- `select: "keyword,volume"`
- `keywords`: všechny brandové varianty (viz `BRAND_KEYWORDS` níže)

Součet variant = nová hodnota pro tento měsíc.

### 2. CZ snapshot (Ahrefs Site Explorer)
Pro každou doménu zavolat `site-explorer-metrics`:
- `country: "CZ"`
- `mode: "subdomains"`
- `date`: dnes

Aktualizovat `snapshot[brandId]` = `{orgTraffic, orgKeywords, orgKeywords1_3}`.

### 3. Historie organického trafficu (Ahrefs Site Explorer)
Pro domény v `organicTraffic` (jen .cz + erikafashion) zavolat `site-explorer-metrics-history`:
- `mode: "subdomains"`
- `history_grouping: "monthly"`
- `date_from`: první den aktuálního měsíce
- BEZ `country` parametru (historie nefunguje s country filter na Standard plánu — globální ≈ CZ pro .cz domény)

Přidat poslední měsíc do pole.

### 4. GSC data (Ahrefs GSC integrace)
Projekt ID: **7274954** (Erikafashion)
Zavolat `gsc-performance-history`:
- `project_id: 7274954`
- `history_grouping: "monthly"`
- `date_from`: předchozí měsíc

Přidat nový kompletní měsíc (pozor: aktuální měsíc obsahuje částečná data, přidávat až když je měsíc uzavřený).

### 5. Uložit a pushnout
1. Aktualizovat `data/history.json`:
   - `lastUpdated` na dnešek
   - Přidat nový měsíc do `dates[]`
   - Přidat hodnoty do `brandSearch[*]`, `organicTraffic[*]`
   - Přepsat `snapshot{}`
   - Přidat do `gsc.*` (pokud je nový kompletní měsíc)
2. `git add -A && git commit -m "Monthly update YYYY-MM" && git push`
3. GitHub Actions automaticky nasadí na GitHub Pages

## BRAND_KEYWORDS (pro reference)

```python
{
    "erikafashion": ["erikafashion", "erika fashion"],
    "sinsay": ["sinsay"],
    "shein": ["shein"],
    "aboutyou": ["about you", "aboutyou"],
    "reserved": ["reserved"],
    "bonprix": ["bonprix"],
    "zalando": ["zalando"],
    "mohito": ["mohito"],
    "lelosi": ["lelosi"],
    "glami": ["glami"],
    "orsay": ["orsay"],
    "buga": ["buga"],
    "evona": ["evona"],
    "miadresses": ["miadresses"],
    "blankastraka": ["blankastraka"],
    "londonclub": ["londonclub", "london club"],
    "coolboutique": ["coolboutique"],
    "bestmoda": ["bestmoda"],
}
```

## Brandové asociace (jednou za kvartál)

Stáhnout znovu přes `keywords-explorer-overview` pro každý brand s asociovanými dotazy
(šaty, sleva, recenze, eshop, kupon, praha, cz atd.). Aktualizovat `brandAssociations{}`
v `history.json`.

Pro erikafashion také `brandTerms[]` — seznam všech brandových variant s volume.

## Tipy

- Batch API calls přes `<function_calls>` s více voláními zároveň — šetří čas
- Units costs: snapshot = 50 units/doména, history = 1 025 units/doména
  (za 25 měsíců), kw overview = 1 525 units za 25 značek
- Celkový měsíční update ~3 000 API units (zhruba 2 % měsíčního limitu 150K)
