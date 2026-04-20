---
description: Aktualizuje data v Share of Search dashboardu pro erikafashion.cz
---

Spusť měsíční aktualizaci dat v Share of Search dashboardu podle postupu v `CLAUDE.md`.

Kroky:

1. **Načti aktuální stav** `data/history.json` (Read)
2. **Zkontroluj, jestli aktuální měsíc už v databázi je** — pokud ano, pouze přepiš snapshot a GSC. Pokud ne, přidej nový měsíc.
3. **Stáhni brandové volume** pro všech 18 brandů přes `keywords-explorer-overview` (CZ, 1 call pro všechny brandy zároveň s comma-separated keywords)
4. **Stáhni CZ snapshot** pro všech 18 domén přes `site-explorer-metrics` (country=CZ, paralelně)
5. **Stáhni historii organického trafficu** pro .cz domény (erikafashion, glami, aboutyou, bonprix, orsay, londonclub, miadresses, zalando) přes `site-explorer-metrics-history` (bez country filtru, paralelně)
6. **Stáhni GSC data** přes `gsc-performance-history` (project_id=7274954)
7. **Aktualizuj `data/history.json`:**
   - `lastUpdated` → dnes
   - Přidej aktuální měsíc do `dates[]` (pokud ještě není)
   - Přidej hodnoty do `brandSearch[*]` a `organicTraffic[*]`
   - Přepiš `snapshot{}`
   - Přidej nový kompletní měsíc do `gsc.*` (ne aktuální měsíc — ten je částečný)
8. **Commit + push** na GitHub:
   ```bash
   git add data/history.json
   git commit -m "Monthly update $(date +%Y-%m)"
   git push
   ```

Pokud narazíš na problém (např. prázdný response z API), oznam to a požádej o další instrukce.

Před začátkem ukaž krátký plán (co přesně budeš stahovat a odhad API units), pak pokračuj.
