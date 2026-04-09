# SafeRoute

**Offline-Navigations-App für Krisensituationen.** SafeRoute zeigt automatisch die nächste sichere Grenze — ohne Tracking, ohne Datenweitergabe, ohne Internetpflicht.

> Dein Name, deine Route, irgendetwas über dich: SafeRoute weiß es nicht und will es nicht wissen.

---

## Features

- Automatische Erkennung des nächsten DACH-Grenzübergangs (Haversine)
- Routing über Valhalla (Open Source)
- Gefahrenzonen-Overlay via NINA-API (Bundesamt für Bevölkerungsschutz)
- Offline-fähig: SQLite-Cache, Tile-Caching
- Background-Sync alle 15 Minuten (WorkManager)
- Kein Account, keine Cloud, keine Werbung

---

## Setup

**Voraussetzungen:**
- Flutter SDK >= 3.11 (`flutter doctor`)
- Xcode (iOS) oder Android Studio (Android)
- Valhalla-Routing-Endpunkt (lokal oder gehostet)

**Lokale Valhalla-Instanz starten (Docker):**
```bash
docker run -p 8002:8002 ghcr.io/valhalla/valhalla:latest
```

**App starten:**
```bash
flutter pub get
flutter run --dart-define=VALHALLA_BASE_URL=http://localhost:8002
```

Ohne `VALHALLA_BASE_URL` wird automatisch `http://localhost:8002` verwendet.

---

## Architektur (Phase 1)

```
lib/
├── main.dart
├── core/
│   ├── data/          # Statische DACH-Grenzübergänge
│   ├── database/      # SQLite (sqflite)
│   ├── models/        # DangerZone, RouteResult
│   └── services/      # NINA, Valhalla, Border, Sync
└── features/
    ├── onboarding/    # Trust-Statement Screen
    └── map/           # Karte + Compass Widget
```

| Schicht | Technologie |
|---|---|
| Karte | `flutter_map` + OSM-Tiles |
| Routing | Valhalla HTTP API |
| Gefahren-Overlay | NINA-API (`nina.api.proxy.bund.dev`) |
| Lokaler Cache | SQLite via `sqflite` |
| Background-Sync | `workmanager` (15 Min.) |
| Grenzerkennung | Haversine, statische DACH-Grenzpunkte |

---

## Tests

```bash
flutter test
flutter analyze
```

Aktueller Stand: 12 Tests (Unit + Widget), 0 Lint-Fehler.

---

## Datenschutz

- Kein Nutzerprofil
- Kein Upload von Standortdaten
- Keine Telemetrie
- Nur öffentliche APIs (NINA, OSM)
- Alle Daten lokal auf dem Gerät

---

## Roadmap

| Feature | Phase 1 | Phase 2 |
|---|---|---|
| Routing | Valhalla HTTP API | On-device via Flutter FFI |
| Offline-Tiles | OSM live (gecacht) | Vollständiger DACH-Download |
| KATWARN | — | Analog zu NINA |
| KI-Assistent | — | On-device Gemma 2B |

Detaillierte Pläne: [`docs/plans/`](docs/plans/)

---

## Lizenz

MIT License — siehe [LICENSE](LICENSE).
