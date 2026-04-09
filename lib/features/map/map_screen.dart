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
    try {
      final db = DbHelper();
      await db.init();
      final zones = await db.loadAllDangerZones();
      await db.close();

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
    } catch (_) {
      setState(() => _loading = false);
    }
  }

  Future<void> _locateAndRoute() async {
    try {
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
    } catch (_) {
      setState(() => _loading = false);
    }
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
        : const LatLng(48.13, 11.58);

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
              urlTemplate: 'https://tile.openstreetmap.org/{z}/{x}/{y}.png',
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
        const Positioned(
          right: 16,
          bottom: 16,
          child: CompassWidget(),
        ),
        if (_loading)
          const Center(child: CircularProgressIndicator(color: _teal)),
      ],
    );
  }

  Widget _buildPanel() {
    final country = _destination?.country ?? '—';
    final countryName = {
      'CH': 'SCHWEIZ',
      'AT': 'ÖSTERREICH',
      'FR': 'FRANKREICH',
      'NL': 'NIEDERLANDE',
      'PL': 'POLEN',
      'CZ': 'TSCHECHIEN',
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
                    style: const TextStyle(color: _textMid, fontSize: 14)),
                const SizedBox(height: 4),
                const Text(
                  'Nächste sichere Grenze — automatisch ermittelt',
                  style: TextStyle(color: _textDim, fontSize: 13),
                ),
                const Divider(color: Color(0xFF1A2234), height: 24),
                Row(
                  children: [
                    _Stat(value: '$distKm', unit: 'KM', label: 'Distanz'),
                    Container(
                        width: 1,
                        height: 70,
                        color: const Color(0xFF1A2234)),
                    _Stat(
                        value: hours > 0 ? '${hours}h $mins' : '$mins',
                        unit: 'MIN',
                        label: 'Fahrzeit'),
                  ],
                ),
                const Divider(color: Color(0xFF1A2234), height: 16),
                Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    const Text('Route aktualisiert.',
                        style: TextStyle(color: _textDim, fontSize: 13)),
                    const Text('via Autobahn',
                        style: TextStyle(
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
