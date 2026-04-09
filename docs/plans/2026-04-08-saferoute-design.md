# SafeRoute – Design Document
**Version 1.0 | 2026-04-08 | Status: Approved**

---

## 1. Problem & Vision

Menschen in Krisensituationen (Krieg, Naturkatastrophen, Blackout) haben kein Tool, das ihre persönliche Situation kennt und offline funktioniert. SafeRoute kombiniert Offline-Navigation, on-device KI und verifizierte Behörden-Daten zu einer einzigen, radikal einfach bedienbaren App für Zivilisten im DACH-Raum.

**Kernversprechen:** Eine Route. Ein Ziel. Immer offline-fähig.

---

## 2. Onboarding

### Ziel
Der Nutzer soll nach dem Onboarding fühlen: *„Ich bin bereit — wenn es passiert, weiß ich was zu tun."*

### Flow (kein Input vom Nutzer erforderlich)

```
Screen 1 — Trust Statement
─────────────────────────────────────────
Was SafeRoute über dich weiß:
  · Deinen Standort (nur lokal)
  · Dein Gerät

Was SafeRoute nie wissen wird:
  · Deinen Namen
  · Deine Route (kein Upload)
  · Irgendetwas über dich

        [ Ich bin dabei ]
─────────────────────────────────────────
↓ GPS-Berechtigung anfordern
↓ Standort erkannt → nächste Grenze berechnet
↓ Ziel automatisch gesetzt (kein User-Input)
↓ Offline-Karten laden im Hintergrund
↓ Hauptscreen — Route bereit
```

### Entscheidungen
- **Minimal, nicht aktiv:** Kein Profil-Zwang, kein Setup-Wizard.
- **Automatisches Zielland:** Nächste Grenze wird per GPS ermittelt — der Nutzer trifft keine Entscheidung.
- **Profil (Fahrzeug, Personen, Gepäck):** Separater Screen, optional, jederzeit erreichbar. Nicht Teil des Onboardings.

---

## 3. Hauptscreen (Navigation)

### Layout-Prinzipien
- Ein Screen, eine Aktion (Kahneman: System-1-Denken unter Stress)
- Große Schrift, hoher Kontrast — funktioniert mit zitternden Händen, bei Sonnenlicht
- Sync-Zeitstempel immer oben sichtbar

### Elemente
| Element | Position | Beschreibung |
|---|---|---|
| Logo + Sync | Header | „SAFE ROUTE" + „vor X Min." mit grünem Dot |
| Karte | Mitte | OSM-Karten, Straßennetz, Gefahrenzonen-Overlay |
| Route | Karte | Teal Linie mit Glow-Effekt, weicht Sperrzonen aus |
| Nutzerposition | Karte | Weißer Dot mit Teal-Kern + Puls-Ring |
| Grenzmarker | Karte | Teal-Punkt + Label am Routenziel |
| Kompass | Karte, unten rechts | Vereinfacht: N-Pfeil (teal), S-Pfeil (slate), transparent |
| Gefahrenzone | Karte | Orange Polygon + „SPERRZONE"-Label |
| Zielland | Panel unten | Großes Wort, z.B. „SCHWEIZ" |
| Distanz + ETA | Panel unten | Monospace, zwei Spalten |
| Update-Hinweis | Panel unten | Einzeiliger Text: *„Route aktualisiert."* — kein Modal |

### Design-Ästhetik: Notzeiger
- Hintergrund: `#0C0F18` (Nacht-Schwarz mit Blauton)
- Akzentfarbe: `#00CFA8` (Teal — internationales Sicherheits-Grün, modern)
- Warnung: `#FF6B35` (Ember-Orange — Distanz, nicht Alarm)
- Text: `#E4EAF6` (kalt-weiß) / `#7A8CA0` (gedimmt)
- Fonts: BigShoulders Bold (Destinations, Logo) + GeistMono (Daten) + WorkSans (Labels)

---

## 4. Technische Architektur

### Stack

```
┌─────────────────────────────────────────────┐
│               Flutter App                    │
│            (iOS & Android)                   │
├──────────────────┬──────────────────────────┤
│   Dart Layer     │   Native Layer (C++)      │
│                  │                           │
│ flutter_map      │ Valhalla Engine           │
│ (OSM Tiles)      │ → Routing-Anfragen        │
│                  │ → Gefahren-Gewichtung      │
│ SQLite           │                           │
│ (Gefahren-Cache) │ OSM DACH (~1.5 GB)        │
└──────────────────┴──────────────────────────┘
         ↑ Background Sync (WorkManager / BGTaskScheduler)
         NINA · KATWARN · GDACS · DWD
```

### Routing-Engine: Valhalla

**Warum Valhalla statt GraphHopper:**
- C++-Engine, Memory-Footprint ~200 MB vs. 300–600 MB bei GraphHopper
- Vorkompilierte Tiles — kein On-Device-Kompilieren
- Bessere Performance auf älteren Geräten (Zielgruppe: ältere Generation)
- Flutter-Integration via FFI (C-Bindings)

**Routing-Flow:**
1. App-Start → Valhalla lädt OSM-Graph einmalig
2. GPS-Standort → nearest border crossing berechnet
3. Route gecacht in SQLite (offline verfügbar auch ohne GPS-Neuberechnung)
4. Gefahrenzonen → Valhalla cost penalties auf betroffenen Straßensegmenten
5. Route weicht automatisch aus → UI zeigt nur: *„Route aktualisiert."*

### Gefahren-Daten: Pull-Strategie

**Technologie:** Flutter `WorkManager` (Android) / `BGTaskScheduler` (iOS)

**Ablauf:**
```
Alle 5–10 Min. (Background Task)
  → HTTP GET: NINA / KATWARN / GDACS / DWD
  → JSON/XML parsen
  → Gefahrenzonen → SQLite schreiben
  → Valhalla-Penalties aktualisieren
  → Sync-Timestamp UI aktualisieren
```

**Kein Push, kein WebSocket** — pure Pull-Strategie, minimaler Batterieverbrauch.

**KPI:** Sync-Latenz ≤ 10 Minuten zwischen realem Ereignis und Layer-Update.

### Gewichtungslogik (intern, nicht in UI)

| Quelle | Gewicht | Bedingung |
|---|---|---|
| NINA | 10 | Immer |
| KATWARN | 9 | Immer |
| GDACS / DWD | 8 | Immer |
| Telegram (öffentl.) | 3 | Geo-Tag + min. 50 Weiterleitungen |
| X (öffentl.) | 2 | Geo-Tag + min. 100 Interaktionen |

### KI-Scope (Gemma 4 2B, on-device)

Genau drei Funktionen — nicht erweiterbar ohne explizite Entscheidung:
1. Situationsfragen des Nutzers
2. Plausibilitätsprüfung Social-Media-Signale
3. Aggregation Gewichtungsscores → finale Routenwahl

### Komponenten-Übersicht

| Komponente | Technologie | Lizenz |
|---|---|---|
| App-Framework | Flutter | Open Source |
| Offline-Karten | OpenStreetMap | ODbL |
| Routing-Engine | Valhalla | MIT |
| On-Device KI | Gemma 4 (2B) | Apache 2.0 |
| Gefahren-Feeds | NINA, KATWARN, GDACS, DWD | Öffentlich |
| Lokale DB | SQLite | Open Source |

---

## 5. Datenschutz

| Bereich | Entscheidung |
|---|---|
| GPS | Nur lokal, nie in Cloud |
| Nutzerprofil | Opt-in, lokal verschlüsselt |
| Social-Media-Daten | Nur anonymes Routing-Signal, nie gespeichert, nie an Nutzer ausgegeben |
| DSGVO | DSFA vor Launch |
| Haftung | Klarer Disclaimer: Hilfestellung, keine Garantie |

---

## 6. Offene Entscheidungen (Post-MVP)

- Familien-Tracking (Wo sind meine Kontakte?)
- Mehrsprachigkeit via Gemma 4
- Kamera → KI übersetzt Schilder
- Crowdsourced Sperrzonen

---

*Design genehmigt: 2026-04-08 | Nächster Schritt: Implementierungsplan Phase 1*
