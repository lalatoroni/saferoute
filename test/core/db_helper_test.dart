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
