import 'package:flutter_test/flutter_test.dart';
import 'package:saferoute/core/services/border_service.dart';

void main() {
  final service = BorderService();

  test('findet AT als nächste Grenze von München aus', () {
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
