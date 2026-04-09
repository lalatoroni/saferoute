# SafeRoute

**Offline-Navigations-App für Krisensituationen.** SafeRoute zeigt dir automatisch die nächste sichere Grenze — ohne Tracking, ohne Datenweitergabe, ohne Internetpflicht.

> Dein Name, deine Route, irgendetwas über dich: SafeRoute weiß es nicht und will es nicht wissen.

---

## Setup

**Voraussetzungen:**
- Flutter SDK ≥ 3.19 (`flutter doctor` grün)
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

| Schicht | Technologie |
|---|---|
| Karte | `flutter_map` + OSM-Tiles |
| Routing | Valhalla HTTP API (gecachte Routen) |
| Gefahren-Overlay | NINA-API (`nina.api.proxy.bund.dev`) |
| Lokaler Cache | SQLite via `sqflite` |
| Background-Sync | `workmanager` (15 Min. Intervall) |
| Grenzerkennung | Haversine-Berechnung, statische DACH-Grenzpunkte |

---

## Tests ausführen

```bash
flutter test
flutter analyze
```

---

## Roadmap

Detaillierte Pläne: [`docs/plans/`](docs/plans/)

| Feature | Phase 1 | Phase 2 |
|---|---|---|
| Routing | Valhalla HTTP API | On-device via Flutter FFI |
| Offline-Tiles | OSM live (gecacht) | Vollständiger DACH-Download (~1,5 GB) |
| KATWARN | — | Analog zu NINA |
| KI-Assistent | — | On-device Gemma 2B |
| Nutzerprofil | — | Fahrzeug, Personenanzahl |
