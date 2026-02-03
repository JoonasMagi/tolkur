# PDF tõlkimine eesti keelde (säilitab kujunduse)

See prototüüp tõlgib võõrkeelse PDF-i eesti keelde ning üritab hoida paigutuse (bbox-id, fondi suurused) muutumatuna. Sobib näiteks puidutöömasinate kasutusjuhendite jaoks.

## Kuidas see töötab
- PDF-ist loetakse tekstiplokid (tekstiline sisu + bbox + fondi info).
- Iga plokk saadetakse tõlketeenusesse.
- Originaaltekst eemaldatakse redaktsioonina ja samasse bbox-i kirjutatakse eestikeelne tõlge.

## Paigaldus

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Kasutamine

```bash
python src/translate_pdf.py input.pdf output.pdf \
  --endpoint https://libretranslate.com/translate \
  --target et
```

### Keskkonnamuutujad
- `TRANSLATE_ENDPOINT` – tõlke API endpoint (nt LibreTranslate või DeepL gateway).
- `TRANSLATE_API_KEY` – API võti (kui teenus nõuab).
- `SOURCE_LANG` – lähtekeel (kui puudub, kasutatakse `auto`).
- `TARGET_LANG` – sihtkeel (vaikimisi `et`).
- `RATE_LIMIT_S` – viivitus päringute vahel.

## Märkused
- Mõned PDF-id kasutavad keerulist paigutust või spetsiaalseid fonte. Sellisel juhul võib tõlge vajada käsitsi järelparandust.
- Kui taust pole valge, tuleb redaktsiooni täitevärvi kohandada.
- Parema kvaliteedi jaoks soovitatav on kasutada professionaalset API-t (DeepL, Google) ning kontrollida fontide ühilduvust.
- Tõlkida tuleb vahel teksti, mis on originaaliga võrreldes pikem. Skript üritab sellisel juhul fonti automaatselt vähendada, et tekst mahuks algsesse plokki.
