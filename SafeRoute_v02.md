# SafeRoute – Projektkonzept
**Offline-KI-Fluchtrouten-App für die Zivilbevölkerung**
Version 0.2 | April 2026 | Status: Ideenphase (bereinigt nach Beratungsrunden 1–4)

---

## 1. Vision & Elevator Pitch

> *„SafeRoute ist die erste Krisen-App, die nicht nur warnt – sondern dich persönlich und offline durch die Krise navigiert. Verlässlich. Einfach. Ohne Cloud."*

Menschen in Krisensituationen (Krieg, Naturkatastrophen, Blackout) haben kein Tool, das ihre persönliche Situation kennt. NINA warnt – aber zeigt keine Route. Google Maps braucht Internet. SafeRoute kombiniert Offline-Navigation, on-device KI und verifizierte Behörden-Daten zu einer einzigen, radikal einfach bedienbaren App – für jeden Bürger, nicht für Behörden.

**Kernversprechen:** Eine Route. Ein Ziel. Immer aktuell. Immer offline-fähig.

---

## 2. Problem

| Problem | Konsequenz heute |
|---|---|
| Warn-Apps (NINA, Katwarn) haben kein Routing | Nutzer wissen, dass Gefahr besteht – aber nicht wie sie wegkommen |
| Navigations-Apps (Google Maps) brauchen Internet | Im Krisenfall fällt Mobilnetz oft aus |
| Keine Personalisierung | App kennt weder Fahrzeug noch Familiensituation |
| Militärische/polizeiliche Sperren nicht abgebildet | Standardrouten führen in Gefahrenzonen |
| Offizielle APIs haben Latenz | Gefahrenlagen ändern sich schneller als Behörden-Feeds |

---

## 3. Lösung – Was SafeRoute macht

### Kernfunktionen (MVP)

1. **Eine Fluchtroute** – Das System berechnet automatisch die kürzeste sichere Route. Keine Auswahl zwischen A/B/C. Der Nutzer wählt nur das Zielland.
2. **Persönliches Profil** – Fahrzeug, Tankgröße, Personenanzahl, Gepäck → beeinflusst Routenwahl aktiv
3. **Offline-KI-Assistent** – Gemma 4 (2B) lokal auf dem Gerät: Fragen stellen, Situationsanalyse, Entscheidungshilfe
4. **Gefahren-Layer** – Echtzeit-Warnungen von NINA, KATWARN, GDACS, DWD als Overlay auf der Karte
5. **Background-Sync** – App aktualisiert Gefahrendaten im Hintergrund ohne aktive Öffnung. Letzter Sync-Zeitpunkt immer prominent sichtbar.
6. **Social-Media-Routing** – Öffentliche Social-Media-Signale (Telegram, X) werden on-device auf Plausibilität geprüft (Anti-Fake) und fließen gewichtet ins Routing ein. Verifizierte Meldungen erscheinen zusätzlich als Gefahren-Layer auf der Karte. Der Nutzer sieht nur einen einzeiligen Hinweis: *„Soziale Quellen einbezogen."* oder *„Nur Behördendaten."*

### Routing-Gewichtungslogik (intern, nicht sichtbar für Nutzer)

```
Quelle                        | Gewicht | Bedingung
------------------------------|---------|------------------------------------------------
NINA                          |   10    | Immer
KATWARN                       |    9    | Immer
GDACS / DWD                   |    8    | Immer
Social Media (verifiziert)    |    5    | Anti-Fake bestanden (Score ≥ 70)
Social Media (nicht verifiz.) |    2    | Geo-Tag + min. 50 Weiterleitungen / 100 Interakt.
```

Anti-Fake-Prüfung (on-device, Gemma 2B): Geo-Konsistenz · Zeitfenster (≤ 2h) · Quellenstreuung (≥ 3 unabh. Accounts) · Clickbait-Erkennung → Score 0–100; Routing-Einfluss nur ab Score ≥ 70.

UI-Hinweis: Einzeiliger, nicht-modaler Text — *„Route aktualisiert."* + *„Soziale Quellen einbezogen."* / *„Nur Behördendaten."*

### Erweiterungen (Post-MVP)

- Familien-Tracking: Wo sind meine Kontakte?
- Mehrsprachigkeit (140+ Sprachen via Gemma 4)
- Kamera-Funktion: Schild fotografieren → KI übersetzt und erklärt
- Crowdsourced Sperrzonen (Community-Meldungen)

---

## 4. Zielgruppe

**Primär: B2C – Einfache Zivilbevölkerung im DACH-Raum**

> SafeRoute gehört allen — kostenlos, open source, ohne Institutionen als Mittler. Behördenprojekte erreichen den normalen Bürger strukturell kaum. Diese App ist direkt für die Menschen gemacht.

| Segment | Beschreibung | Bedürfnis |
|---|---|---|
| Familien mit Kindern | Sicherheitsorientiert, wenig Technik-Affinität | Einfache Bedienung, Familienkoordination |
| Pendler / Stadtbewohner | Alltäglich mobil, bewusst für Risiken | Schnelle Nutzung im Notfall |
| Outdoor / Reisende | Oft offline unterwegs | Zuverlässige Offline-Navigation |
| Ältere Generation | Hohe Krisenangst seit Ukraine-Krieg | Sehr einfache UI, große Schrift |
| Expats & Touristen | International, Sprachbarriere | Mehrsprachigkeit, grenzübergreifend |

---

## 5. Alleinstellungsmerkmale (USPs)

1. **100% offline-fähig** – funktioniert auch ohne Strom-/Mobilfunknetz
2. **Radikal einfach** – eine Route, eine Entscheidung (Zielland), kein Overload
3. **Persönliches Profil beeinflusst Route** – kein anderes Tool macht das
4. **KI lokal auf dem Gerät** – keine Daten in die Cloud, volle Privatsphäre
5. **Transparente Datenaktualität** – Sync-Zeitstempel immer sichtbar, nicht versteckt
6. **Open Source** – Code-Transparenz als ethische Grundlage, nicht als Marketingstrategie
7. **DACH-spezifisch** – Deutsche, österreichische und Schweizer Behörden-APIs integriert

---

## 6. UX-Prinzipien

> Basierend auf verhaltenspsychologischen Erkenntnissen (Kahneman: System-1-Denken in Stresssituationen)

- **Ein Bildschirm, eine Aktion** – keine Menüs im Krisenmoment
- **Erster Onboarding-Screen = Vertrauensvertrag** – keine Willkommensbotschaft, sondern klare Aussage: *„Hier ist genau, was diese App über dich weiß – und was sie nie wissen wird."*
- **Routenänderungen still kommunizieren** – *„Route aktualisiert."* – kein Modal, kein Alert, kein Alarm
- **Sync-Zeitstempel prominent** – oben, immer sichtbar, kein Untermenü
- **Große Schrift, hoher Kontrast** – funktioniert mit zitternden Händen, auf hellem Sonnenlicht

---

## 7. Technischer Stack

```
┌─────────────────────────────────────────┐
│              SafeRoute App              │
│         (Flutter – iOS & Android)       │
├──────────────┬──────────────────────────┤
│ Offline-Kern │ Online-Layer (optional)  │
│              │                          │
│ OSM-Karten   │ NINA / KATWARN API       │
│ GraphHopper  │ GDACS / DWD              │
│ Gemma 4 (2B) │ Telegram / X (Routing)   │
│ SQLite lokal │ Background-Sync Service  │
└──────────────┴──────────────────────────┘
```

| Komponente | Technologie | Lizenz | Kosten |
|---|---|---|---|
| App-Framework | Flutter | Open Source | kostenlos |
| Offline-Karten | OpenStreetMap | ODbL | kostenlos |
| Routing-Engine | GraphHopper | Apache 2.0 | kostenlos |
| On-Device KI | Gemma 4 (2B) | Apache 2.0 | kostenlos |
| Gefahren-Feeds | NINA, KATWARN, GDACS, DWD | Öffentlich | kostenlos |
| Social Routing | Telegram API, X API | Lizenzpflichtig | gering |
| Datenbank lokal | SQLite | Open Source | kostenlos |

### KI-Scope (fixiert – nicht erweiterbar ohne explizite Entscheidung)

Gemma 2B beantwortet in SafeRoute genau vier Dinge:
1. **Situationsfragen des Nutzers** – „Ist diese Route sicher?" / „Was soll ich mitnehmen?"
2. **Plausibilitätsprüfung Social-Routing-Signale** – Einfache Geo/Interaktions-Prüfung für stilles Routing (Gewicht 2–3)
3. **Anti-Fake-Analyse für Social-Gefahren-Layer** – Vollständige 5-stufige Plausibilitätsprüfung (Geo, Zeit, Quellenstreuung, Sprache) → Vertrauens-Score 0–100; Anzeige nur ab ≥ 70
4. **Routenentscheidungslogik** – Aggregation aller Gewichtungsscores zur finalen Routenwahl

Alles andere ist kein KI-Problem.

### Technische Kennzahl (KPI Phase 1)

> **Maximale Sync-Latenz: ≤ 10 Minuten** zwischen realem Ereignis und Gefahren-Layer-Update.
> Wird in Phase 2 gemessen und dokumentiert.

---

## 8. Datenschutz & Rechtliches

| Bereich | Ansatz |
|---|---|
| GPS-Daten | Nur lokal gespeichert, nie in Cloud |
| Nutzerprofil | Opt-in, lokal verschlüsselt |
| Social-Media-Daten | Nur als anonymes Routing-Signal, nie gespeichert, nie an Nutzer ausgegeben |
| DSGVO | Datenschutz-Folgenabschätzung (DSFA) vor Launch |
| Haftung | Klarer Disclaimer: App ist Hilfestellung, keine Garantie |
| OSM-Lizenz | ODbL-Attribution in der App |
| App Store | DSA-konforme Impressum + Datenschutzerklärung |
| Open Source | Vollständige Code-Transparenz auf GitHub – ethische Grundlage, keine PR-Maßnahme |

---

## 9. Roadmap

```
Phase 1 – Fundament (Monate 1–3)              [Hobby | Experiment]
├── GitHub Repository aufsetzen (Public, MIT)
├── README mit Vision + Roadmap
├── Offline-Karte DACH integrieren (OSM)
├── Basis-Routing mit GraphHopper
├── NINA-API + KATWARN anbinden
└── → Phase 1 ist ein Experiment, kein Launch.
    Ziel: 10 Testnutzer in simulierter Stresssituation.

Phase 2 – KI & Profil (Monate 4–6)            [Hobby+]
├── Gemma 4 (2B) on-device integrieren
├── KI-Scope fixiert umsetzen (3 Funktionen, nicht mehr)
├── Nutzerprofil (Fahrzeug, Personen, Gepäck)
├── Eine Route mit Profil-Logik + Landauswahl
├── Background-Sync + Timestamp UI
└── Sync-Latenz messen → KPI ≤ 10 Min. validieren

Phase 3 – Social Routing (Monate 7–9)         [Open Source Launch]
├── Telegram / X Feed anbinden (öffentliche Geo-getaggte Posts)
├── Anti-Fake-Pipeline on-device (Gemma 2B): Geo · Zeit · Quellenstreuung · Sprache
├── Routing-Gewichtungslogik implementieren (Score ≥ 70 → Einfluss)
├── Gefahren-Layer Karte: verifizierte Social-Meldungen sichtbar machen
├── UI-Hinweis: „Soziale Quellen einbezogen." / „Nur Behördendaten." (einzeilig, kein Modal)
├── Verhaltenstest: mit vs. ohne Social Routing
└── Community-Onboarding + Contributor Guidelines

Phase 4 – Skalierung (ab Monat 10)            [ggf. Prototype Fund]
├── iOS + Android App Store Launch
├── Mehrsprachigkeit (DE/AT/CH/EN)
├── Post-Krisen-Feedback-Schleife aktivieren
└── Barrierefreiheit prüfen (große Schrift, Kontrast, Screenreader)
```

---

## 10. Post-Krisen-Feedback-Schleife

> Empfehlung aus verhaltenspsychologischer Forschung: Der wertvollste Datenpunkt ist nicht die Performance der App während der Krise – sondern das Nutzerverhalten danach.

Nach jeder dokumentierten Nutzung in einer realen Krisenlage:
- Was hat funktioniert?
- Was hat verwirrt?
- Was haben Nutzer tatsächlich getan – vs. was die App empfohlen hat?

**Format:** Opt-in In-App-Umfrage, 3 Fragen, 48h nach Krisenende auslösbar.
**Zweck:** Produkt-Iteration auf Basis echter Evidenz, nicht Annahmen.

---

## 11. Open Source Haltung

SafeRoute ist und bleibt Open Source — nicht als Marketingstrategie, sondern als ethische Grundlage.

**Kostenlos. Für alle. Ohne Ausnahme.** SafeRoute hat kein Freemium-Modell, keine Premium-Stufe, keine Paywall. Eine App für Krisensituationen darf nicht davon abhängen, ob jemand ein Abo bezahlt hat.

**MIT-Lizenz.** Jeder kann den Code lesen, prüfen, forken, verbessern. Keine versteckten Algorithmen, keine Black-Box-Entscheidungen über Routen.

**Warum das wichtig ist:** Eine App, die Menschen in Krisensituationen navigiert, muss vollständig transparent sein. Code-Transparenz ist hier kein Nice-to-have, sondern Voraussetzung für Vertrauen.

**Haltung gegenüber externen Interessen:** Wenn kommerzielle oder staatliche Interessen an SafeRoute herantreten, gilt: Open-Source-Lizenz und Community-Governance haben Vorrang. Schriftliche Haltungsdefinition wird vor dem ersten Release veröffentlicht.

**Contributor-Prinzipien:**
- Keine Features ohne explizite Entscheidung (Anti-Scope-Creep)
- KI-Scope bleibt fixiert — Erweiterungen nur durch dokumentierten Community-Entscheid
- Sicherheitslücken werden öffentlich disclosed, nicht still gepatcht

---

## 12. Risiken

| Risiko | Wahrscheinlichkeit | Maßnahme |
|---|---|---|
| Falsche Routen im Krisenfall | Mittel | Disclaimer + konservative Gewichtungslogik + Latenz-KPI |
| Social-Media-Signal erzeugt Fehlerroute | Mittel | Anti-Fake Score < 70 → kein Routing-Einfluss; unverifizierte Signale max. Gewicht 2 |
| Fake-Meldung übersteht Anti-Fake-Prüfung | Niedrig | Konservative Score-Schwelle (≥ 70) + Quellenstreuung (≥ 3 Accounts) als Doppelschutz |
| Datenschutzverletzung | Niedrig | Alles lokal, Social-Daten nie gespeichert, DSFA vor Launch |
| Scope Creep | Hoch | KI-Scope fixiert (3 Funktionen), Phase-by-Phase, kein Feature ohne Entscheidung |
| Vertrauensverlust durch stille Routenänderung | Mittel | Einzeiliger UI-Hinweis „Route aktualisiert." – kein Modal |
| Externe Interessen nach Wachstum | Mittel | Open Source + schriftliche Haltungsdefinition vor erstem Release |
| App Store Ablehnung | Niedrig | Frühzeitig Richtlinien prüfen, kein militärisches Framing |

---

## 13. Nächste Schritte

- [ ] GitHub Repository anlegen (`saferoute`) – Public, MIT-Lizenz
- [ ] README mit Vision, Warum und Roadmap schreiben
- [ ] Flutter-Grundgerüst aufsetzen
- [ ] OSM-Karte DACH herunterladen und integrieren
- [ ] KI-Scope schriftlich fixieren (3 Funktionen – vor erster Codezeile)
- [ ] Onboarding-Screen als Datentransparenz-Statement formulieren
- [ ] Ersten Verhaltenstest planen (10 Probanden, simulierter Stress, Phase 1 Ende)
- [ ] Haltungsdokument schreiben: Was tun wir, wenn Interessen kommen?
- [ ] Rechtlichen Disclaimer formulieren
- [ ] Ersten Entwicklungspartner / Mitstreiter suchen

---

*Dokument erstellt: April 2026 | Version 0.2 | Überarbeitet nach Beratungsrunden 1–4*
*Nächste Review: nach Phase 1 (Verhaltenstest abgeschlossen)*
