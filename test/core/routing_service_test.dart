import 'package:flutter_test/flutter_test.dart';
import 'package:dio/dio.dart';
import 'package:saferoute/core/services/routing_service.dart';

class _FakeDio extends Fake implements Dio {
  final Map<String, dynamic>? _responseData;
  final bool _shouldThrow;

  _FakeDio({Map<String, dynamic>? responseData, bool shouldThrow = false})
      : _responseData = responseData,
        _shouldThrow = shouldThrow;

  @override
  Future<Response<T>> post<T>(
    String path, {
    Object? data,
    Map<String, dynamic>? queryParameters,
    Options? options,
    CancelToken? cancelToken,
    ProgressCallback? onSendProgress,
    ProgressCallback? onReceiveProgress,
  }) async {
    if (_shouldThrow) {
      throw DioException(
        requestOptions: RequestOptions(path: path),
        type: DioExceptionType.connectionError,
      );
    }
    return Response<T>(
      data: _responseData as T,
      statusCode: 200,
      requestOptions: RequestOptions(path: path),
    );
  }
}

void main() {
  test('gibt RouteResult zurück bei erfolgreichem Valhalla-Response', () async {
    final fakeDio = _FakeDio(responseData: {
      'trip': {
        'summary': {'length': 247.3, 'time': 12000},
        'legs': [
          {'shape': ''}
        ]
      }
    });
    final service = RoutingService(dio: fakeDio);

    final result = await service.route(
      fromLon: 11.58, fromLat: 48.13,
      toLon: 12.85, toLat: 47.67,
    );

    expect(result, isNotNull);
    expect(result!.distanceKm, closeTo(247.3, 0.1));
    expect(result.durationMinutes, 200); // 12000s / 60
  });

  test('gibt null zurück bei Routing-Fehler', () async {
    final fakeDio = _FakeDio(shouldThrow: true);
    final service = RoutingService(dio: fakeDio);

    final result = await service.route(
      fromLon: 11.58, fromLat: 48.13,
      toLon: 12.85, toLat: 47.67,
    );
    expect(result, isNull);
  });
}
