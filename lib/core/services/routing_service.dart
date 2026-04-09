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
        destinationCountry: '', // wird vom Aufrufer gesetzt
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
