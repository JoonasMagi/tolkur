# GitHub issue kasutajalood

## 1. PDF-i tõlkimine eesti keelde paigutust säilitades
**Kasutajalugu**
- *Kasutajana* soovin tõlkida võõrkeelse PDF-i eesti keelde nii, et dokumendi kujundus ja paigutus jäävad samaks, *et* saaksin masina kasutusjuhendi koheselt kasutusele võtta.

**Aktsepteerimiskriteeriumid**
- PDF-i tekst asendatakse eestikeelse tõlkega samas paiknemises (bbox) ja loetava fondisuurusega.
- Algne paigutus (pealkirjad, lõigud, tabelite tekstiplokid) on visuaalselt säilinud.
- Tõlkeprotsess töötab Norra, Saksa ja Inglise keele sisenditega.

## 2. Tõlketeenuse seadistamine API võtmega
**Kasutajalugu**
- *Kasutajana* soovin seadistada tõlketeenuse API võtme ja endpoint’i, *et* saaksin kasutada professionaalset teenust parema kvaliteedi jaoks.

**Aktsepteerimiskriteeriumid**
- API võtme saab anda keskkonnamuutujas või käsurea argumendina.
- Endpoint on konfigureeritav ilma koodi muutmata.
- Vea korral kuvatakse selge veateade (nt autentimis- või võrguviga).

## 3. Tõlke kvaliteedi kontroll ja parandused
**Kasutajalugu**
- *Kasutajana* soovin üle vaadata ja vajadusel korrigeerida tõlgitud PDF-i, *et* tehniline terminoloogia oleks korrektne.

**Aktsepteerimiskriteeriumid**
- Väljundfail on standardne PDF, mida saab avada tavapärastes PDF-lugerites.
- Tõlkija ei lõhu dokumenti (ei tekita tühje lehti ega katkenud paigutust).
- Tõlke teksti saab käsitsi parandada välises PDF-redaktoris.

## 4. Suurte failide tõlkimine ja päringute piirang
**Kasutajalugu**
- *Kasutajana* soovin määrata päringute vahelise viivituse, *et* vältida tõlketeenuse rate limit’i ületamist.

**Aktsepteerimiskriteeriumid**
- Viivitus on seadistatav sekundites.
- Tõlkimine jätkub järjepidevalt ka suurte PDF-ide puhul.
- Dokumenti tõlgitakse plokkide kaupa, et hoida teenuse päringumahud kontrolli all.

## 5. Logimine ja tõrgete tuvastamine
**Kasutajalugu**
- *Kasutajana* soovin näha tõlkimise käigus logisid, *et* mõista protsessi edenemist ja võimalikke vigu.

**Aktsepteerimiskriteeriumid**
- Logitakse vähemalt lehe number ja ploki indeks.
- Tõrgete korral logitakse vea põhjus ja kontekst.
- Logimine on vaikimisi sisse lülitatud ning ei riku PDF-i väljundit.
