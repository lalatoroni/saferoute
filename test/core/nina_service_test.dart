import 'package:flutter_test/flutter_test.dart';
import 'package:mocktail/mocktail.dart';
import 'package:dio/dio.dart';
import 'package:saferoute/core/services/nina_service.dart';

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
      DioException(
        requestOptions: RequestOptions(path: ''),
        type: DioExceptionType.connectionError,
      ),
    );
    final zones = await service.fetchDangerZones();
    expect(zones, isEmpty);
  });
}
