class DangerZone {
  final String id;
  final String source; // 'NINA' | 'KATWARN' | 'GDACS'
  final List<List<double>> polygon; // [[lon, lat], ...]
  final String label;
  final DateTime fetchedAt;

  const DangerZone({
    required this.id,
    required this.source,
    required this.polygon,
    required this.label,
    required this.fetchedAt,
  });

  factory DangerZone.fromJson(Map<String, dynamic> json) => DangerZone(
        id: json['id'] as String,
        source: json['source'] as String,
        polygon: (json['polygon'] as List)
            .map((p) => (p as List).map((v) => (v as num).toDouble()).toList())
            .toList(),
        label: json['label'] as String,
        fetchedAt: DateTime.parse(json['fetchedAt'] as String),
      );

  Map<String, dynamic> toJson() => {
        'id': id,
        'source': source,
        'polygon': polygon,
        'label': label,
        'fetchedAt': fetchedAt.toIso8601String(),
      };
}
