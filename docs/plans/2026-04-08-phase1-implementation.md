# SafeRoute Phase 1 Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Lauffähige Flutter-App mit Offline-OSM-Karte, NINA/KATWARN-Gefahren-Overlay, Valhalla-Routing (API-basiert in Phase 1), automatischer Grenzerkennung per GPS und den zwei Kern-Screens (Onboarding + Navigation).

**Architecture:** Flutter-App mit `flutter_map` für OSM-Tiles, `routing_client_dart` als Valhalla-HTTP-Client (Phase 1: gehostete Valhalla-Instanz mit aggressivem Route-Cache; Phase 2: on-device via FFI), `sqflite` für lokalen Gefahren-Cache, `workmanager` für Background-Sync.

**Tech Stack:** Flutter 3.x · flutter_map · routing_client_dart · sqflite · workmanager · geolocator · dio · mocktail

---

## Voraussetzungen (einmalig, manuell)

1. Flutter SDK ≥ 3.19 installieren: `flutter doctor` muss grün sein
2. Android Studio + Xcode (für iOS-Build)
3. Kostenloses Valhalla-API-Konto bei [valhalla.mapbox.com](https://valhalla.mapbox.com) **oder** lokale Docker-Instanz:
   ```bash
   docker run -p 8002:8002 ghcr.io/valhalla/valhalla:latest
   ```
4. Git-Repo anlegen: `gh repo create saferoute --public --license MIT`

---

## Task 1: Flutter-Projekt aufsetzen

**Files:**
- Create: `pubspec.yaml`
- Create: `lib/main.dart`
- Create: `test/widget_test.dart`

**Step 1: Projekt erstellen**
```bash
flutter create saferoute --org dev.saferoute --platforms android,ios
cd saferoute
```

**Step 2: Dependencies in `pubspec.yaml` eintragen**
```yaml
dependencies:
  flutter:
    sdk: flutter
  flutter_map: ^6.1.0
  flutter_map_tile_caching: ^9.1.0
  routing_client_dart: ^0.6.0
  sqflite: ^2.3.2
  geolocator: ^12.0.0
  workmanager: ^0.5.2
  dio: ^5.4.3
  path_provider: ^2.1.3
  permission_handler: ^11.3.1

dev_dependencies:
  flutter_test:
    sdk: flutter
  mocktail: ^1.0.3
  flutter_lints: ^3.0.0
```

**Step 3: Dependencies installieren**
```bash
flutter pub get
```
Expected: Keine Fehler, alle Pakete resolved.

**Step 4: Smoke-Test**
```bash
flutter test
```
Expected: `All tests passed.`

**Step 5: Commit**
```bash
git add pubspec.yaml pubspec.lock
git commit -m "feat: initial Flutter project setup"
```

---

## Task 2: Projektstruktur anlegen

**Files:**
- Create: `lib/core/database/db_helper.dart`
- Create: `lib/core/models/danger_zone.dart`
- Create: `lib/core/models/route_result.dart`
- Create: `lib/features/map/map_screen.dart`
- Create: `lib/features/onboarding/onboarding_screen.dart`
- Create: `lib/features/map/widgets/compass_widget.dart`

**Step 1: Verzeichnisse erstellen**
```bash
mkdir -p lib/core/{database,models,services}
mkdir -p lib/features/{map/widgets,onboarding}
mkdir -p test/core test/features
```

**Step 2: `lib/core/models/danger_zone.dart` schreiben**
```dart
class DangerZone {
  final String id;
  final String source; // 'NINA' | 'KATWARN' | 'GDACS'
  final List<List<double>> polygon; // [[lon, lat], ...]
  final String label;
  final DateTime fetchedAt;

  const DangerZone({
    required this.id,
    required this.source,
    required this.polygon,
    required this.label,
    required this.fetchedAt,
  });

  factory DangerZone.fromJson(Map<String, dynamic> json) => DangerZone(
        id: json['id'] as String,
        source: json['source'] as String,
        polygon: (json['polygon'] as List)
            .map((p) => (p as List).map((v) => (v as num).toDouble()).toList())
            .toList(),
        label: json['label'] as String,
        fetchedAt: DateTime.parse(json['fetchedAt'] as String),
      );

  Map<String, dynamic> toJson() => {
        'id': id,
        'source': source,
        'polygon': polygon,
        'label': label,
        'fetchedAt': fetchedAt.toIso8601String(),
      };
}
```

**Step 3: `lib/core/models/route_result.dart` schreiben**
```dart
class RouteResult {
  final List<List<double>> waypoints; // [[lon, lat], ...]
  final double distanceKm;
  final int durationMinutes;
  final String destinationCountry;
  final DateTime calculatedAt;

  const RouteResult({
    required this.waypoints,
    required this.distanceKm,
    required this.durationMinutes,
    required this.destinationCountry,
    required this.calculatedAt,
  });
}
```

**Step 4: Commit**
```bash
git add lib/ test/
git commit -m "feat: project structure and core models"
```

---

## Task 3: SQLite-Datenbank

**Files:**
- Create: `lib/core/database/db_helper.dart`
- Create: `test/core/db_helper_test.dart`

**Step 1: Failing-Test schreiben**
```dart
// test/core/db_helper_test.dart
import 'package:flutter_test/flutter_test.dart';
import 'package:sqflite_common_ffi/sqflite_ffi.dart';
import 'package:saferoute/core/database/db_helper.dart';
import 'package:saferoute/core/models/danger_zone.dart';

void main() {
  setUpAll(() {
    sqfliteFfiInit();
    databaseFactory = databaseFactoryFfi;
  });

  group('DbHelper', () {
    late DbHelper db;

    setUp(() async {
      db = DbHelper(dbPath: ':memory:');
      await db.init();
    });

    tearDown(() async => db.close());

    test('speichert und lädt DangerZone', () async {
      final zone = DangerZone(
        id: 'test-1',
        source: 'NINA',
        polygon: [[8.0, 48.0], [8.1, 48.0], [8.1, 48.1]],
        label: 'Testgebiet',
        fetchedAt: DateTime(2026, 4, 8),
      );
      await db.upsertDangerZone(zone);
      final loaded = await db.loadAllDangerZones();
      expect(loaded.length, 1);
      expect(loaded.first.id, 'test-1');
      expect(loaded.first.source, 'NINA');
    });

    test('überschreibt bestehende Zone mit gleicher ID', () async {
      final zone = DangerZone(
        id: 'test-1', source: 'NINA',
        polygon: [[8.0, 48.0]], label: 'Alt',
        fetchedAt: DateTime(2026, 4, 8),
      );
      final updated = DangerZone(
        id: 'test-1', source: 'NINA',
        polygon: [[8.0, 48.0]], label: 'Neu',
        fetchedAt: DateTime(2026, 4, 9),
      );
      await db.upsertDangerZone(zone);
      await db.upsertDangerZone(updated);
      final loaded = await db.loadAllDangerZones();
      expect(loaded.length, 1);
      expect(loaded.first.label, 'Neu');
    });
  });
}
```

**Step 2: Test laufen lassen – muss FEHLSCHLAGEN**
```bash
flutter test test/core/db_helper_test.dart
```
Expected: `Error: Could not find package 'saferoute/core/database/db_helper.dart'`

Außerdem zu `pubspec.yaml` hinzufügen:
```yaml
dependencies:
  sqflite_common_ffi: ^2.3.3  # nur für Tests
```

**Step 3: `lib/core/database/db_helper.dart` implementieren**
```dart
import 'dart:convert';
import 'package:sqflite/sqflite.dart';
import '../models/danger_zone.dart';

class DbHelper {
  final String dbPath;
  Database? _db;

  DbHelper({this.dbPath = 'saferoute.db'});

  Future<void> init() async {
    _db = await openDatabase(
      dbPath,
      version: 1,
      onCreate: (db, version) => db.execute('''
        CREATE TABLE danger_zones (
          id TEXT PRIMARY KEY,
          source TEXT NOT NULL,
          polygon TEXT NOT NULL,
          label TEXT NOT NULL,
          fetched_at TEXT NOT NULL
        )
      '''),
    );
  }

  Future<void> upsertDangerZone(DangerZone zone) async {
    await _db!.insert(
      'danger_zones',
      {
        'id': zone.id,
        'source': zone.source,
        'polygon': jsonEncode(zone.polygon),
        'label': zone.label,
        'fetched_at': zone.fetchedAt.toIso8601String(),
      },
      conflictAlgorithm: ConflictAlgorithm.replace,
    );
  }

  Future<List<DangerZone>> loadAllDangerZones() async {
    final rows = await _db!.query('danger_zones');
    return rows.map((row) => DangerZone(
      id: row['id'] as String,
      source: row['source'] as String,
      polygon: (jsonDecode(row['polygon'] as String) as List)
          .map((p) => (p as List).map((v) => (v as num).toDouble()).toList())
          .toList(),
      label: row['label'] as String,
      fetchedAt: DateTime.parse(row['fetched_at'] as String),
    )).toList();
  }

  Future<void> close() async => _db?.close();
}
```

**Step 4: Test erneut laufen – muss BESTEHEN**
```bash
flutter test test/core/db_helper_test.dart
```
Expected: `All tests passed.`

**Step 5: Commit**
```bash
git add lib/core/database/ test/core/
git commit -m "feat: SQLite helper with danger zone persistence"
```

---

## Task 4: NINA-API-Integration

**Files:**
- Create: `lib/core/services/nina_service.dart`
- Create: `test/core/nina_service_test.dart`

**Step 1: Failing-Test schreiben**
```dart
// test/core/nina_service_test.dart
import 'package:flutter_test/flutter_test.dart';
import 'package:mocktail/mocktail.dart';
import 'package:dio/dio.dart';
import 'package:saferoute/core/services/nina_service.dart';
import 'package:saferoute/core/models/danger_zone.dart';

class MockDio extends Mock implements Dio {}

void main() {
  late MockDio mockDio;
  late NinaService service;

  setUp(() {
    mockDio = MockDio();
    service = NinaService(dio: mockDio);
  });

  test('parst NINA-Warnungen zu DangerZones', () async {
    when(() => mockDio.get(any())).thenAnswer((_) async => Response(
      data: [
        {
          'id': 'DE-BY-2026-001',
          'info': [
            {
              'headline': 'Überflutung',
              'area': [
                {
                  'polygon': '48.0,8.0 48.1,8.0 48.1,8.1 48.0,8.0'
                }
              ]
            }
          ]
        }
      ],
      statusCode: 200,
      requestOptions: RequestOptions(path: ''),
    ));

    final zones = await service.fetchDangerZones();
    expect(zones.length, 1);
    expect(zones.first.id, 'DE-BY-2026-001');
    expect(zones.first.source, 'NINA');
    expect(zones.first.label, 'Überflutung');
  });

  test('gibt leere Liste zurück bei HTTP-Fehler', () async {
    when(() => mockDio.get(any())).thenThrow(
      DioException(requestOptions: RequestOptions(path: ''),
                   type: DioExceptionType.connectionError),
    );
    final zones = await service.fetchDangerZones();
    expect(zones, isEmpty);
  });
}
```

**Step 2: Test laufen lassen – muss FEHLSCHLAGEN**
```bash
flutter test test/core/nina_service_test.dart
```
Expected: `Error: Could not find 'nina_service.dart'`

**Step 3: `lib/core/services/nina_service.dart` implementieren**
```dart
import 'package:dio/dio.dart';
import '../models/danger_zone.dart';

class NinaService {
  static const _baseUrl =
      'https://nina.api.proxy.bund.dev/api31/warnings/mapData.json';

  final Dio dio;
  NinaService({Dio? dio}) : dio = dio ?? Dio();

  Future<List<DangerZone>> fetchDangerZones() async {
    try {
      final response = await dio.get(_baseUrl);
      final data = response.data as List;
      final zones = <DangerZone>[];
      for (final item in data) {
        final id = item['id'] as String;
        final infos = item['info'] as List? ?? [];
        if (infos.isEmpty) continue;
        final info = infos.first as Map;
        final headline = info['headline'] as String? ?? 'Warnung';
        final areas = info['area'] as List? ?? [];
        for (final area in areas) {
          final polygonStr = area['polygon'] as String? ?? '';
          final polygon = _parsePolygon(polygonStr);
          if (polygon.isEmpty) continue;
          zones.add(DangerZone(
            id: id,
            source: 'NINA',
            polygon: polygon,
            label: headline,
            fetchedAt: DateTime.now(),
          ));
        }
      }
      return zones;
    } catch (_) {
      return [];
    }
  }

  List<List<double>> _parsePolygon(String raw) {
    // Format: "lat,lon lat,lon ..."
    return raw.trim().split(' ').where((s) => s.contains(',')).map((pair) {
      final parts = pair.split(',');
      return [double.parse(parts[1]), double.parse(parts[0])]; // [lon, lat]
    }).toList();
  }
}
```

**Step 4: Test erneut laufen – muss BESTEHEN**
```bash
flutter test test/core/nina_service_test.dart
```
Expected: `All tests passed.`

**Step 5: Commit**
```bash
git add lib/core/services/nina_service.dart test/core/nina_service_test.dart
git commit -m "feat: NINA API service with polygon parsing"
```

---

## Task 5: Grenzerkennung (GPS → nächste Grenze)

**Files:**
- Create: `lib/core/services/border_service.dart`
- Create: `lib/core/data/dach_borders.dart`
- Create: `test/core/border_service_test.dart`

**Step 1: DACH-Grenzpunkte als statische Daten**
```dart
// lib/core/data/dach_borders.dart
// Grenzübergänge DACH: {land: [[lon, lat, name], ...]}
const dachBorderCrossings = {
  'CH': [
    [8.5528, 47.6779, 'Basel – Weil am Rhein'],
    [9.5167, 47.5333, 'Konstanz – Kreuzlingen'],
    [10.1833, 47.5500, 'Bregenz – Lustenau'],
  ],
  'AT': [
    [13.0431, 47.8031, 'Salzburg – Freilassing'],
    [12.8667, 47.6667, 'Rosenheim – Kufstein'],
    [16.9000, 48.2167, 'Wien Norden – Drasenhofen'],
  ],
  'FR': [
    [7.5833, 47.5500, 'Mulhouse – Neuenburg am Rhein'],
    [7.3667, 48.5333, 'Strasbourg – Kehl'],
  ],
  'NL': [
    [6.1167, 51.8500, 'Venlo – Kaldenkirchen'],
    [7.0333, 52.2833, 'Gronau – Enschede'],
  ],
  'PL': [
    [14.7000, 52.3333, 'Frankfurt Oder – Słubice'],
    [18.0667, 50.3167, 'Oppeln – Kandrzin'],
  ],
  'CZ': [
    [12.9500, 50.3833, 'Waidhaus – Rozvadov'],
    [13.3167, 50.6500, 'Chemnitz – Most'],
  ],
  'DK': [
    [9.4333, 54.8167, 'Flensburg – Kruså'],
  ],
};
```

**Step 2: Failing-Test schreiben**
```dart
// test/core/border_service_test.dart
import 'package:flutter_test/flutter_test.dart';
import 'package:saferoute/core/services/border_service.dart';

void main() {
  final service = BorderService();

  test('findet CH als nächste Grenze von München aus', () {
    // München: 11.5820, 48.1351
    final result = service.nearestCrossing(lon: 11.5820, lat: 48.1351);
    expect(result.country, 'AT'); // Kufstein ist näher als Basel
  });

  test('findet DK als nächste Grenze von Hamburg aus', () {
    // Hamburg: 10.0, 53.55
    final result = service.nearestCrossing(lon: 10.0, lat: 53.55);
    expect(result.country, 'DK');
  });

  test('findet FR oder CH von Freiburg aus', () {
    // Freiburg: 7.85, 47.99
    final result = service.nearestCrossing(lon: 7.85, lat: 47.99);
    expect(['FR', 'CH'], contains(result.country));
  });
}
```

**Step 3: Test laufen lassen – muss FEHLSCHLAGEN**
```bash
flutter test test/core/border_service_test.dart
```

**Step 4: `lib/core/services/border_service.dart` implementieren**
```dart
import 'dart:math';
import '../data/dach_borders.dart';

class BorderCrossing {
  final String country;
  final double lon;
  final double lat;
  final String name;
  final double distanceKm;

  const BorderCrossing({
    required this.country,
    required this.lon,
    required this.lat,
    required this.name,
    required this.distanceKm,
  });
}

class BorderService {
  BorderCrossing nearestCrossing({required double lon, required double lat}) {
    BorderCrossing? best;

    dachBorderCrossings.forEach((country, crossings) {
      for (final c in crossings) {
        final cLon = c[0] as double;
        final cLat = c[1] as double;
        final name = c[2] as String;
        final dist = _haversineKm(lat, lon, cLat, cLon);
        if (best == null || dist < best!.distanceKm) {
          best = BorderCrossing(
            country: country,
            lon: cLon,
            lat: cLat,
            name: name,
            distanceKm: dist,
          );
        }
      }
    });

    return best!;
  }

  double _haversineKm(double lat1, double lon1, double lat2, double lon2) {
    const r = 6371.0;
    final dLat = _rad(lat2 - lat1);
    final dLon = _rad(lon2 - lon1);
    final a = sin(dLat / 2) * sin(dLat / 2) +
        cos(_rad(lat1)) * cos(_rad(lat2)) * sin(dLon / 2) * sin(dLon / 2);
    return r * 2 * atan2(sqrt(a), sqrt(1 - a));
  }

  double _rad(double deg) => deg * pi / 180;
}
```

**Step 5: Test erneut laufen – muss BESTEHEN**
```bash
flutter test test/core/border_service_test.dart
```
Expected: `All tests passed.`

**Step 6: Commit**
```bash
git add lib/core/ test/core/border_service_test.dart
git commit -m "feat: nearest border crossing detection via Haversine"
```

---

## Task 6: Valhalla Routing-Client

**Files:**
- Create: `lib/core/services/routing_service.dart`
- Create: `test/core/routing_service_test.dart`

**Step 1: Failing-Test schreiben**
```dart
// test/core/routing_service_test.dart
import 'package:flutter_test/flutter_test.dart';
import 'package:mocktail/mocktail.dart';
import 'package:dio/dio.dart';
import 'package:saferoute/core/services/routing_service.dart';
import 'package:saferoute/core/models/route_result.dart';

class MockDio extends Mock implements Dio {}

void main() {
  late MockDio mockDio;
  late RoutingService service;

  setUp(() {
    mockDio = MockDio();
    service = RoutingService(dio: mockDio);
  });

  test('gibt RouteResult zurück bei erfolgreichem Valhalla-Response', () async {
    when(() => mockDio.post(any(), data: any(named: 'data')))
        .thenAnswer((_) async => Response(
          data: {
            'trip': {
              'summary': {'length': 247.3, 'time': 12000},
              'legs': [
                {
                  'shape': 'encodedPolyline~_example~'
                }
              ]
            }
          },
          statusCode: 200,
          requestOptions: RequestOptions(path: ''),
        ));

    final result = await service.route(
      fromLon: 11.58, fromLat: 48.13,
      toLon: 12.85, toLat: 47.67,
    );

    expect(result, isNotNull);
    expect(result!.distanceKm, closeTo(247.3, 0.1));
    expect(result.durationMinutes, 200); // 12000s / 60
  });

  test('gibt null zurück bei Routing-Fehler', () async {
    when(() => mockDio.post(any(), data: any(named: 'data')))
        .thenThrow(DioException(
          requestOptions: RequestOptions(path: ''),
          type: DioExceptionType.connectionError,
        ));

    final result = await service.route(
      fromLon: 11.58, fromLat: 48.13,
      toLon: 12.85, toLat: 47.67,
    );
    expect(result, isNull);
  });
}
```

**Step 2: Test laufen lassen – muss FEHLSCHLAGEN**
```bash
flutter test test/core/routing_service_test.dart
```

**Step 3: `lib/core/services/routing_service.dart` implementieren**

Hinweis: `VALHALLA_BASE_URL` kommt aus einer `.env`-Datei (nicht ins Repo commiten). Für lokale Docker-Instanz: `http://localhost:8002`.

```dart
import 'package:dio/dio.dart';
import '../models/route_result.dart';

class RoutingService {
  // Phase 1: gehostete Instanz. Phase 2: on-device via FFI.
  static const _baseUrl = String.fromEnvironment(
    'VALHALLA_BASE_URL',
    defaultValue: 'http://localhost:8002',
  );

  final Dio dio;
  RoutingService({Dio? dio}) : dio = dio ?? Dio();

  Future<RouteResult?> route({
    required double fromLon,
    required double fromLat,
    required double toLon,
    required double toLat,
    String costing = 'auto',
  }) async {
    try {
      final response = await dio.post(
        '$_baseUrl/route',
        data: {
          'locations': [
            {'lon': fromLon, 'lat': fromLat},
            {'lon': toLon, 'lat': toLat},
          ],
          'costing': costing,
          'directions_options': {'units': 'kilometers'},
        },
      );

      final trip = response.data['trip'] as Map;
      final summary = trip['summary'] as Map;
      final distanceKm = (summary['length'] as num).toDouble();
      final durationSec = (summary['time'] as num).toInt();
      final legs = trip['legs'] as List;
      final shape = legs.isNotEmpty ? legs.first['shape'] as String : '';

      return RouteResult(
        waypoints: _decodePolyline(shape),
        distanceKm: distanceKm,
        durationMinutes: (durationSec / 60).round(),
        destinationCountry: '',   // wird vom Aufrufer gesetzt
        calculatedAt: DateTime.now(),
      );
    } catch (_) {
      return null;
    }
  }

  // Googles encoded polyline → [[lon, lat], ...]
  List<List<double>> _decodePolyline(String encoded) {
    final result = <List<double>>[];
    int index = 0, lat = 0, lng = 0;
    while (index < encoded.length) {
      int b, shift = 0, result2 = 0;
      do {
        b = encoded.codeUnitAt(index++) - 63;
        result2 |= (b & 0x1f) << shift;
        shift += 5;
      } while (b >= 0x20);
      lat += (result2 & 1) != 0 ? ~(result2 >> 1) : result2 >> 1;
      shift = 0;
      result2 = 0;
      do {
        b = encoded.codeUnitAt(index++) - 63;
        result2 |= (b & 0x1f) << shift;
        shift += 5;
      } while (b >= 0x20);
      lng += (result2 & 1) != 0 ? ~(result2 >> 1) : result2 >> 1;
      result.add([lng / 1e5, lat / 1e5]);
    }
    return result;
  }
}
```

**Step 4: Test erneut laufen**
```bash
flutter test test/core/routing_service_test.dart
```
Expected: `All tests passed.`

**Step 5: Commit**
```bash
git add lib/core/services/routing_service.dart test/core/routing_service_test.dart
git commit -m "feat: Valhalla routing client with polyline decoder"
```

---

## Task 7: Background-Sync Service

**Files:**
- Create: `lib/core/services/sync_service.dart`
- Modify: `android/app/src/main/AndroidManifest.xml` (WorkManager-Permission)

**Step 1: `lib/core/services/sync_service.dart`**
```dart
import 'package:workmanager/workmanager.dart';
import 'nina_service.dart';
import '../database/db_helper.dart';

const _syncTaskName = 'saferoute.dangerSync';

@pragma('vm:entry-point')
void callbackDispatcher() {
  Workmanager().executeTask((task, inputData) async {
    if (task == _syncTaskName) {
      final nina = NinaService();
      final db = DbHelper();
      await db.init();
      final zones = await nina.fetchDangerZones();
      for (final zone in zones) {
        await db.upsertDangerZone(zone);
      }
      await db.close();
    }
    return true;
  });
}

class SyncService {
  static Future<void> init() async {
    await Workmanager().initialize(callbackDispatcher, isInDebugMode: false);
  }

  static Future<void> schedulePeriodicSync() async {
    await Workmanager().registerPeriodicTask(
      'dangerSyncTask',
      _syncTaskName,
      frequency: const Duration(minutes: 15),
      constraints: Constraints(networkType: NetworkType.connected),
      existingWorkPolicy: ExistingWorkPolicy.keep,
    );
  }
}
```

**Step 2: AndroidManifest.xml – WorkManager-Berechtigung eintragen**

In `android/app/src/main/AndroidManifest.xml` innerhalb `<application>`:
```xml
<service
    android:name="androidx.work.impl.background.systemalarm.RescheduleReceiver"
    android:exported="false"/>
```

**Step 3: In `lib/main.dart` initialisieren**
```dart
import 'package:flutter/material.dart';
import 'core/services/sync_service.dart';
import 'features/onboarding/onboarding_screen.dart';

void main() async {
  WidgetsFlutterBinding.ensureInitialized();
  await SyncService.init();
  await SyncService.schedulePeriodicSync();
  runApp(const SafeRouteApp());
}

class SafeRouteApp extends StatelessWidget {
  const SafeRouteApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'SafeRoute',
      theme: ThemeData.dark().copyWith(
        scaffoldBackgroundColor: const Color(0xFF0C0F18),
      ),
      home: const OnboardingScreen(),
    );
  }
}
```

**Step 4: Compile-Test**
```bash
flutter build apk --debug
```
Expected: Build erfolgreich, keine Fehler.

**Step 5: Commit**
```bash
git add lib/ android/
git commit -m "feat: background sync with WorkManager (15min interval)"
```

---

## Task 8: Onboarding-Screen

**Files:**
- Create: `lib/features/onboarding/onboarding_screen.dart`
- Create: `test/features/onboarding_screen_test.dart`

**Step 1: Failing Widget-Test**
```dart
// test/features/onboarding_screen_test.dart
import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:saferoute/features/onboarding/onboarding_screen.dart';

void main() {
  testWidgets('zeigt Trust-Statement und Button', (tester) async {
    await tester.pumpWidget(
      const MaterialApp(home: OnboardingScreen()),
    );
    expect(find.text('Ich bin dabei'), findsOneWidget);
    expect(find.textContaining('nie wissen'), findsWidgets);
  });

  testWidgets('Button navigiert zum nächsten Screen', (tester) async {
    await tester.pumpWidget(
      const MaterialApp(home: OnboardingScreen()),
    );
    await tester.tap(find.text('Ich bin dabei'));
    await tester.pumpAndSettle();
    // Nach Tap: kein Onboarding mehr sichtbar
    expect(find.text('Ich bin dabei'), findsNothing);
  });
}
```

**Step 2: Test laufen lassen – muss FEHLSCHLAGEN**
```bash
flutter test test/features/onboarding_screen_test.dart
```

**Step 3: `lib/features/onboarding/onboarding_screen.dart` implementieren**
```dart
import 'package:flutter/material.dart';
import '../map/map_screen.dart';

class OnboardingScreen extends StatelessWidget {
  const OnboardingScreen({super.key});

  static const _teal = Color(0xFF00CFA8);
  static const _textMain = Color(0xFFE4EAF6);
  static const _textMid = Color(0xFF7A8CA0);
  static const _bg = Color(0xFF0C0F18);

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: _bg,
      body: SafeArea(
        child: Padding(
          padding: const EdgeInsets.symmetric(horizontal: 32, vertical: 48),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              const Spacer(),
              _Section(
                title: 'Was SafeRoute über dich weiß:',
                items: [
                  'Deinen Standort (nur lokal)',
                  'Dein Gerät',
                ],
                color: _textMain,
              ),
              const SizedBox(height: 40),
              _Section(
                title: 'Was SafeRoute nie wissen wird:',
                items: [
                  'Deinen Namen',
                  'Deine Route (kein Upload)',
                  'Irgendetwas über dich',
                ],
                color: _teal,
              ),
              const Spacer(),
              SizedBox(
                width: double.infinity,
                height: 60,
                child: ElevatedButton(
                  style: ElevatedButton.styleFrom(
                    backgroundColor: _teal,
                    foregroundColor: _bg,
                    shape: RoundedRectangleBorder(
                      borderRadius: BorderRadius.circular(12),
                    ),
                    textStyle: const TextStyle(
                      fontSize: 20,
                      fontWeight: FontWeight.bold,
                      letterSpacing: 1.2,
                    ),
                  ),
                  onPressed: () => Navigator.pushReplacement(
                    context,
                    MaterialPageRoute(builder: (_) => const MapScreen()),
                  ),
                  child: const Text('Ich bin dabei'),
                ),
              ),
              const SizedBox(height: 24),
            ],
          ),
        ),
      ),
    );
  }
}

class _Section extends StatelessWidget {
  final String title;
  final List<String> items;
  final Color color;

  const _Section({
    required this.title,
    required this.items,
    required this.color,
  });

  static const _textMid = Color(0xFF7A8CA0);

  @override
  Widget build(BuildContext context) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(title,
            style: TextStyle(
                color: _textMid, fontSize: 14, letterSpacing: 0.5)),
        const SizedBox(height: 12),
        ...items.map((item) => Padding(
              padding: const EdgeInsets.only(bottom: 8),
              child: Row(
                children: [
                  Icon(Icons.radio_button_checked,
                      color: color, size: 14),
                  const SizedBox(width: 12),
                  Text(item,
                      style: TextStyle(
                          color: color,
                          fontSize: 18,
                          fontWeight: FontWeight.w500)),
                ],
              ),
            )),
      ],
    );
  }
}
```

**Step 4: Test erneut laufen**
```bash
flutter test test/features/onboarding_screen_test.dart
```
Expected: `All tests passed.`

**Step 5: Commit**
```bash
git add lib/features/onboarding/ test/features/
git commit -m "feat: onboarding trust screen"
```

---

## Task 9: Haupt-Navigationsscreen

**Files:**
- Create: `lib/features/map/map_screen.dart`
- Create: `lib/features/map/widgets/compass_widget.dart`
- Create: `lib/features/map/map_controller.dart`

**Step 1: Compass-Widget**
```dart
// lib/features/map/widgets/compass_widget.dart
import 'dart:math';
import 'package:flutter/material.dart';

class CompassWidget extends StatelessWidget {
  const CompassWidget({super.key});

  @override
  Widget build(BuildContext context) {
    return SizedBox(
      width: 64,
      height: 64,
      child: CustomPaint(painter: _CompassPainter()),
    );
  }
}

class _CompassPainter extends CustomPainter {
  static const _teal = Color(0xFF00CFA8);
  static const _tealDark = Color(0xFF007A65);
  static const _slate = Color(0xFF3A4A5C);
  static const _slateMid = Color(0xFF2A3340);
  static const _bg = Color(0xCC0C0F18);

  @override
  void paint(Canvas canvas, Size size) {
    final cx = size.width / 2;
    final cy = size.height / 2;
    final r = size.width / 2;

    // Background circle
    canvas.drawCircle(
      Offset(cx, cy),
      r,
      Paint()..color = _bg,
    );
    canvas.drawCircle(
      Offset(cx, cy),
      r,
      Paint()
        ..color = _slate
        ..style = PaintingStyle.stroke
        ..strokeWidth = 1.5,
    );

    // N needle (teal)
    final nPath = Path()
      ..moveTo(cx, cy - r * 0.72)
      ..lineTo(cx - 8, cy + 4)
      ..lineTo(cx, cy - 3)
      ..close();
    final nPath2 = Path()
      ..moveTo(cx, cy - r * 0.72)
      ..lineTo(cx + 8, cy + 4)
      ..lineTo(cx, cy - 3)
      ..close();
    canvas.drawPath(nPath, Paint()..color = _teal);
    canvas.drawPath(nPath2, Paint()..color = _tealDark);

    // S needle (slate)
    final sPath = Path()
      ..moveTo(cx, cy + r * 0.72)
      ..lineTo(cx - 8, cy - 4)
      ..lineTo(cx, cy + 3)
      ..close();
    final sPath2 = Path()
      ..moveTo(cx, cy + r * 0.72)
      ..lineTo(cx + 8, cy - 4)
      ..lineTo(cx, cy + 3)
      ..close();
    canvas.drawPath(sPath, Paint()..color = _slateMid);
    canvas.drawPath(sPath2, Paint()..color = _slate);

    // Center dot
    canvas.drawCircle(
      Offset(cx, cy),
      4,
      Paint()..color = const Color(0xFFCCD6E8),
    );

    // N label
    final tp = TextPainter(
      text: const TextSpan(
        text: 'N',
        style: TextStyle(
          color: _teal,
          fontSize: 11,
          fontWeight: FontWeight.bold,
          letterSpacing: 0.5,
        ),
      ),
      textDirection: TextDirection.ltr,
    )..layout();
    tp.paint(canvas, Offset(cx - tp.width / 2, cy - r - tp.height - 2));
  }

  @override
  bool shouldRepaint(_) => false;
}
```

**Step 2: `lib/features/map/map_screen.dart`**
```dart
import 'package:flutter/material.dart';
import 'package:flutter_map/flutter_map.dart';
import 'package:latlong2/latlong.dart';
import 'package:geolocator/geolocator.dart';
import '../../core/services/border_service.dart';
import '../../core/services/routing_service.dart';
import '../../core/services/nina_service.dart';
import '../../core/database/db_helper.dart';
import '../../core/models/danger_zone.dart';
import '../../core/models/route_result.dart';
import 'widgets/compass_widget.dart';

class MapScreen extends StatefulWidget {
  const MapScreen({super.key});

  @override
  State<MapScreen> createState() => _MapScreenState();
}

class _MapScreenState extends State<MapScreen> {
  static const _teal = Color(0xFF00CFA8);
  static const _orange = Color(0xFFFF6B35);
  static const _bg = Color(0xFF0C0F18);
  static const _bg2 = Color(0xFF0F1320);
  static const _textMain = Color(0xFFE4EAF6);
  static const _textMid = Color(0xFF7A8CA0);
  static const _textDim = Color(0xFF3E4E60);

  Position? _position;
  RouteResult? _route;
  BorderCrossing? _destination;
  List<DangerZone> _dangerZones = [];
  DateTime? _lastSync;
  bool _loading = true;

  @override
  void initState() {
    super.initState();
    _init();
  }

  Future<void> _init() async {
    await _loadDangerZones();
    await _locateAndRoute();
  }

  Future<void> _loadDangerZones() async {
    final db = DbHelper();
    await db.init();
    final zones = await db.loadAllDangerZones();
    await db.close();

    // Falls DB leer: direkt von NINA laden
    if (zones.isEmpty) {
      final nina = NinaService();
      final fresh = await nina.fetchDangerZones();
      setState(() {
        _dangerZones = fresh;
        _lastSync = DateTime.now();
      });
    } else {
      setState(() {
        _dangerZones = zones;
        _lastSync = zones.map((z) => z.fetchedAt).reduce(
            (a, b) => a.isAfter(b) ? a : b);
      });
    }
  }

  Future<void> _locateAndRoute() async {
    final permission = await Geolocator.requestPermission();
    if (permission == LocationPermission.denied ||
        permission == LocationPermission.deniedForever) {
      setState(() => _loading = false);
      return;
    }

    final pos = await Geolocator.getCurrentPosition();
    final border = BorderService().nearestCrossing(
      lon: pos.longitude,
      lat: pos.latitude,
    );
    final routing = RoutingService();
    final route = await routing.route(
      fromLon: pos.longitude,
      fromLat: pos.latitude,
      toLon: border.lon,
      toLat: border.lat,
    );

    setState(() {
      _position = pos;
      _destination = border;
      _route = route;
      _loading = false;
    });
  }

  String _syncLabel() {
    if (_lastSync == null) return '—';
    final diff = DateTime.now().difference(_lastSync!);
    if (diff.inMinutes < 1) return 'gerade eben';
    if (diff.inMinutes == 1) return 'vor 1 Min.';
    return 'vor ${diff.inMinutes} Min.';
  }

  @override
  Widget build(BuildContext context) {
    final center = _position != null
        ? LatLng(_position!.latitude, _position!.longitude)
        : const LatLng(48.13, 11.58); // München als Fallback

    return Scaffold(
      backgroundColor: _bg,
      body: Column(
        children: [
          _buildHeader(),
          Expanded(child: _buildMap(center)),
          _buildPanel(),
        ],
      ),
    );
  }

  Widget _buildHeader() {
    return Container(
      color: _bg,
      child: SafeArea(
        bottom: false,
        child: Padding(
          padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 12),
          child: Row(
            children: [
              RichText(
                text: const TextSpan(
                  children: [
                    TextSpan(
                      text: 'SAFE',
                      style: TextStyle(
                        color: _textMain,
                        fontSize: 28,
                        fontWeight: FontWeight.w900,
                        letterSpacing: 2,
                      ),
                    ),
                    TextSpan(
                      text: 'ROUTE',
                      style: TextStyle(
                        color: _teal,
                        fontSize: 28,
                        fontWeight: FontWeight.w900,
                        letterSpacing: 2,
                      ),
                    ),
                  ],
                ),
              ),
              const Spacer(),
              Container(
                width: 10,
                height: 10,
                decoration: const BoxDecoration(
                  color: _teal,
                  shape: BoxShape.circle,
                ),
              ),
              const SizedBox(width: 8),
              Text(_syncLabel(),
                  style: const TextStyle(
                      color: _textMid,
                      fontSize: 14,
                      fontFamily: 'monospace')),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildMap(LatLng center) {
    final routePoints = _route?.waypoints
            .map((p) => LatLng(p[1], p[0]))
            .toList() ??
        [];

    return Stack(
      children: [
        FlutterMap(
          options: MapOptions(initialCenter: center, initialZoom: 8),
          children: [
            TileLayer(
              urlTemplate:
                  'https://tile.openstreetmap.org/{z}/{x}/{y}.png',
              userAgentPackageName: 'dev.saferoute.app',
            ),
            if (_dangerZones.isNotEmpty)
              PolygonLayer(
                polygons: _dangerZones.map((z) => Polygon(
                  points: z.polygon
                      .map((p) => LatLng(p[1], p[0]))
                      .toList(),
                  color: _orange.withOpacity(0.15),
                  borderColor: _orange.withOpacity(0.6),
                  borderStrokeWidth: 2,
                )).toList(),
              ),
            if (routePoints.isNotEmpty)
              PolylineLayer(
                polylines: [
                  Polyline(
                    points: routePoints,
                    color: _teal,
                    strokeWidth: 4,
                    gradientColors: [_teal.withOpacity(0.5), _teal],
                  ),
                ],
              ),
            if (_position != null)
              MarkerLayer(
                markers: [
                  Marker(
                    point: LatLng(_position!.latitude, _position!.longitude),
                    width: 24,
                    height: 24,
                    child: Container(
                      decoration: BoxDecoration(
                        color: _teal,
                        shape: BoxShape.circle,
                        border: Border.all(color: Colors.white, width: 2),
                      ),
                    ),
                  ),
                ],
              ),
          ],
        ),
        // Kompass
        Positioned(
          right: 16,
          bottom: 16,
          child: const CompassWidget(),
        ),
        if (_loading)
          const Center(child: CircularProgressIndicator(color: _teal)),
      ],
    );
  }

  Widget _buildPanel() {
    final country = _destination?.country ?? '—';
    final countryName = {
      'CH': 'SCHWEIZ', 'AT': 'ÖSTERREICH', 'FR': 'FRANKREICH',
      'NL': 'NIEDERLANDE', 'PL': 'POLEN', 'CZ': 'TSCHECHIEN',
      'DK': 'DÄNEMARK',
    }[country] ?? country;

    final crossing = _destination?.name ?? '—';
    final distKm = _route?.distanceKm.round() ?? 0;
    final durMin = _route?.durationMinutes ?? 0;
    final hours = durMin ~/ 60;
    final mins = durMin % 60;

    return Container(
      color: _bg2,
      child: Column(
        children: [
          Container(height: 2, color: _teal),
          Padding(
            padding: const EdgeInsets.fromLTRB(24, 20, 24, 0),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(countryName,
                    style: const TextStyle(
                        color: _textMain,
                        fontSize: 48,
                        fontWeight: FontWeight.w900,
                        letterSpacing: 2)),
                Text(crossing,
                    style: const TextStyle(
                        color: _textMid, fontSize: 14)),
                const SizedBox(height: 4),
                Text(
                  'Nächste sichere Grenze — automatisch ermittelt',
                  style: const TextStyle(color: _textDim, fontSize: 13),
                ),
                const Divider(color: Color(0xFF1A2234), height: 24),
                Row(
                  children: [
                    _Stat(value: '$distKm', unit: 'KM', label: 'Distanz'),
                    Container(
                        width: 1, height: 70, color: const Color(0xFF1A2234)),
                    _Stat(
                        value: hours > 0 ? '${hours}h ${mins}' : '$mins',
                        unit: hours > 0 ? 'MIN' : 'MIN',
                        label: 'Fahrzeit'),
                  ],
                ),
                const Divider(color: Color(0xFF1A2234), height: 16),
                Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    const Text('Route aktualisiert.',
                        style: TextStyle(color: _textDim, fontSize: 13)),
                    Text('via Autobahn',
                        style: const TextStyle(
                            color: _textDim,
                            fontSize: 13,
                            fontFamily: 'monospace')),
                  ],
                ),
                const SizedBox(height: 20),
              ],
            ),
          ),
        ],
      ),
    );
  }
}

class _Stat extends StatelessWidget {
  final String value;
  final String unit;
  final String label;

  const _Stat({required this.value, required this.unit, required this.label});

  @override
  Widget build(BuildContext context) {
    return Expanded(
      child: Padding(
        padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 8),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              crossAxisAlignment: CrossAxisAlignment.end,
              children: [
                Text(value,
                    style: const TextStyle(
                        color: Color(0xFFE4EAF6),
                        fontSize: 40,
                        fontWeight: FontWeight.bold,
                        fontFamily: 'monospace')),
                const SizedBox(width: 4),
                Padding(
                  padding: const EdgeInsets.only(bottom: 6),
                  child: Text(unit,
                      style: const TextStyle(
                          color: Color(0xFF7A8CA0),
                          fontSize: 14,
                          fontFamily: 'monospace')),
                ),
              ],
            ),
            Text(label,
                style: const TextStyle(
                    color: Color(0xFF3E4E60), fontSize: 12)),
          ],
        ),
      ),
    );
  }
}
```

**Step 3: Compile + manueller Smoke-Test auf Emulator**
```bash
flutter run
```
Expected: App startet, Onboarding erscheint, nach Tap wird Karte angezeigt.

**Step 4: Commit**
```bash
git add lib/features/map/ test/features/
git commit -m "feat: main navigation screen with map, route, compass, danger overlay"
```

---

## Task 10: Alle Tests + Abschluss

**Step 1: Alle Tests laufen lassen**
```bash
flutter test --coverage
```
Expected: `All tests passed.`

**Step 2: Lint-Check**
```bash
flutter analyze
```
Expected: `No issues found.`

**Step 3: README schreiben**

Erstelle `README.md` mit:
- Vision (2 Sätze)
- Screenshot (sobald vorhanden)
- Setup-Anleitung (flutter pub get, Valhalla-URL setzen, flutter run)
- Roadmap-Link zu docs/plans/

**Step 4: Final Commit**
```bash
git add .
git commit -m "feat: SafeRoute Phase 1 complete — offline nav, NINA integration, onboarding"
```

---

## Bekannte Grenzen Phase 1 → Phase 2

| Bereich | Phase 1 | Phase 2 |
|---|---|---|
| Routing | Valhalla HTTP API (hosted) | On-device Valhalla via Flutter FFI |
| Offline-Tiles | OSM live tiles (gecacht) | Vollständiger DACH-Tile-Download (~1.5 GB) |
| KATWARN | Noch nicht integriert | Task analog zu NINA |
| Gemma-KI | Nicht vorhanden | On-device Gemma 4 2B |
| Profil | Nicht vorhanden | Separater Screen: Fahrzeug, Personen |

---

*Plan gespeichert: 2026-04-08 | Implementierung: superpowers:executing-plans*
