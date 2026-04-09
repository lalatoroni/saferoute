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
