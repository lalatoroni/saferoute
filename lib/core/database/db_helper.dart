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
