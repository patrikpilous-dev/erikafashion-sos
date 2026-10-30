# erikafashion-sos — Share of Search Dashboard

Kompetitivní analýza českého fashion trhu pro erikafashion.cz.

**Live URL:** https://patrikpilous-dev.github.io/erikafashion-sos/
**Repo:** https://github.com/patrikpilous-dev/erikafashion-sos

## Architektura

- `index.html` — statický dashboard se záložkami, čte `data/editions/index.json` a data přes `fetch()`
- `data/history.json` — aktuální edice včetně textů (zjištění, doporučení, metodika)
- `data/editions/<rok-mesic>.json` — zmrazené starší edice, každá je vlastní záložka Archiv
- `data/editions/index.json` — seznam záložek
- `zdroje/` — pracovní data edic, jen lokálně (v .gitignore, repo je veřejné)
- `logo.svg` — logo erikafashion.cz
- `.github/workflows/deploy.yml` — auto-deploy na GitHub Pages při push do master

## Nová edice (zásady platné od 30. 10. 2026)

1. **Zmrazit starou edici:** zkopírovat `data/history.json` do `data/editions/<rok-mesic>.json`, v `content` nastavit `archive: true` a přidat řádek do `data/editions/index.json`.
2. **Stáhnout celou historii znovu, nedoplňovat jen poslední měsíc.** Ahrefs zpětně přepočítává i staré měsíce, jinak vznikne schod. Hromadně: `keywords-explorer-overview` se `select=keyword,volume_monthly_history`, `volume_monthly_date_to` musí být první den měsíce.
3. **Zkontrolovat proti přímým datům Googlu.** Brandové kliky z GSC a Google Trends vedle Ahrefs. 10/2026 se rozcházely o 50 procentních bodů (Ahrefs -10 %, Trends +39 %, GSC +40 %).
4. **Srovnávat rok k roku,** ne měsíc s předchozí edicí, trh je sezónní.
5. **Veřejné repo:** `data/*.json` jde stáhnout i bez hesla. Žádné tržby ani Kč z Ads, jen poměry.
6. Postup této edice je v `nastroje/` (`vytahni_ze_session.py`, `analyza_2026_10.py`, `sestav_edici_2026_10.py`).

7. **Srovnání s minulou edicí:** hledání porovnávat přes stejný výpis (12 měsíců do data minulé edice), ne proti tehdy zveřejněnému číslu. Stav domén a asociace přímo proti minulé edici (`aprCompare`, `brandAssociations[].prev`). U asociací nutné dotáhnout dnešní objem i pro dotazy z minulého výběru.
8. **Záložka AI odpovědi:** `site-explorer-ai-responses-count`, `country=CZ`, `mode=subdomains`, parametr `date` jde i zpětně. Součet šesti platforem bez Groku (u Eriky v 10/2026 prázdný), srovnávat podíly, ne absolutní čísla. Brand Radar na plánu není. Podíl hlasu je z AI trackeru Marketing Mineru (projekt 81b2762c-1199-41a1-8877-877c4b60dbd9), čte se přes přihlášený Chrome: Konkurence, Prompty, Zdroje podle domén, hodnoty modelů a týdnů přes hover na graf. Běží 43 promptů, ne 76 z `projects\erikafashion\prompty-ai-mereni.md`. Prompty se parsují ze záznamu session do `zdroje/2026-10/mm_prompty.json`.

Co zjistila edice 10/2026 o zdrojích:
- GSC v Ahrefs (projekt 7274954) končí červencem 2026, novější data z Marketing Mineru (`https://www.erikafashion.cz/`), překryv sedí na klik.
- `site-explorer-metrics-history` s `country=CZ` jde jen dva roky zpět, proto mezinárodní domény od 11/2024.
- Od září 2025 nesrovnávat zobrazení a pozici s dřívějškem (Google zrušil 100 výsledků na stránku).
- SERP v Ahrefs se u brandu mýlil (homepage není první), pozice ověřovat v GSC.

## Měsíční aktualizace dat

Nemám standalone Ahrefs API klíč — používám Claude Code s Ahrefs MCP napojením.
Aktualizace probíhá ručně přes Claude Code.

**Postup:**
1. Otevřít tento projekt v Claude Code (`cd C:\Users\patri\.claude\projects\erikafashion-sos`)
2. Říct Claudovi: "Aktualizuj data v dashboardu" nebo použít `/update-sos`
3. Claude projde všechny kroky níže a pushne změny

**Co se má aktualizovat (checklist pro Claude):**

### 1. Brandové hledání (Ahrefs Keywords Explorer, CZ)
Pro každý z 20 brandů (podle `data/history.json` > brands) stáhnout aktuální měsíční volume přes `keywords-explorer-overview` s:
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
    "modivo": ["modivo", "modivo.cz", "modivo cz"],
    "sqvele": ["sqvele"],
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
