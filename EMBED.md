# Embed Dashboard — Návod pro patrikpilous.cz

Dashboard je dostupný na: `https://patrikpilous-dev.github.io/erikafashion-sos/`

## Varianta 1 — Jednoduchý iframe s pevnou výškou (doporučeno)

Do Elementor HTML widget vloz:

```html
<iframe
  src="https://patrikpilous-dev.github.io/erikafashion-sos/"
  style="width:100%;border:0;min-height:100vh;height:8000px;display:block"
  allowfullscreen
  loading="lazy"></iframe>
```

**Proč `height:8000px`:** Obsah dashboardu (po přihlášení) je kolem 7 000–8 000 pixelů díky všem grafům a tabulkám. Pevná vysoká výška zajistí, že se nic neořízne.

## Varianta 2 — Auto-resize iframe (pokročilé)

Dashboard posílá `postMessage` s aktuální výškou. Přidej na stránku tento snippet:

```html
<iframe
  id="sos-iframe"
  src="https://patrikpilous-dev.github.io/erikafashion-sos/"
  style="width:100%;border:0;min-height:800px;display:block"
  allowfullscreen
  loading="lazy"></iframe>

<script>
(function() {
  window.addEventListener('message', function(e) {
    if (e.data && e.data.type === 'sos-resize' && e.data.height) {
      var iframe = document.getElementById('sos-iframe');
      if (iframe) iframe.style.height = (e.data.height + 20) + 'px';
    }
  });
})();
</script>
```

Iframe se automaticky přizpůsobí na výšku obsahu po každé změně (login → dashboard, toggle brand filtrů).

## Tipy pro Elementor

1. **Šablona stránky:** "Elementor Canvas" (bez hlavičky/patičky) — to už máš nastavené
2. **Widget:** Use "HTML" widget (ne "Shortcode"), vlož kompletní snippet
3. **Container width:** nastav na "Full Width" aby iframe zabral celou šířku
4. **Padding:** odstran horní/dolní padding z Elementor containeru, aby dashboard začínal hned

## Heslo pro vstup

`erikafashion2026`

Můžeš ho změnit v `index.html` — najdi `ACCESS_HASH` a nahrad hash nového hesla (SHA-256).

Na Linux/Mac vygeneruješ hash takto:
```bash
echo -n "nove-heslo" | sha256sum
```

Na Windows PowerShell:
```powershell
$h = [System.Security.Cryptography.SHA256]::Create()
[System.BitConverter]::ToString($h.ComputeHash([Text.Encoding]::UTF8.GetBytes("nove-heslo"))).Replace("-","").ToLower()
```
