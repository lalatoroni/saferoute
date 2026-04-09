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
