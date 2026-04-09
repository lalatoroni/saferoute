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
    try {
      return raw.trim().split(' ').where((s) => s.contains(',')).map((pair) {
        final parts = pair.split(',');
        if (parts.length < 2) return <double>[];
        return [double.parse(parts[1]), double.parse(parts[0])]; // [lon, lat]
      }).where((p) => p.length == 2).toList();
    } catch (_) {
      return [];
    }
  }
}
