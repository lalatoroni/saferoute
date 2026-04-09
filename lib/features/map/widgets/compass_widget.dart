import 'package:flutter/material.dart';

class CompassWidget extends StatelessWidget {
  const CompassWidget({super.key});

  @override
  Widget build(BuildContext context) {
    return SizedBox(
      width: 64,
      height: 64,
      child: CustomPaint(painter: _CompassPainter()),
    );
  }
}

class _CompassPainter extends CustomPainter {
  static const _teal = Color(0xFF00CFA8);
  static const _tealDark = Color(0xFF007A65);
  static const _slate = Color(0xFF3A4A5C);
  static const _slateMid = Color(0xFF2A3340);
  static const _bg = Color(0xCC0C0F18);

  @override
  void paint(Canvas canvas, Size size) {
    final cx = size.width / 2;
    final cy = size.height / 2;
    final r = size.width / 2;

    canvas.drawCircle(Offset(cx, cy), r, Paint()..color = _bg);
    canvas.drawCircle(
      Offset(cx, cy),
      r,
      Paint()
        ..color = _slate
        ..style = PaintingStyle.stroke
        ..strokeWidth = 1.5,
    );

    final nPath = Path()
      ..moveTo(cx, cy - r * 0.72)
      ..lineTo(cx - 8, cy + 4)
      ..lineTo(cx, cy - 3)
      ..close();
    final nPath2 = Path()
      ..moveTo(cx, cy - r * 0.72)
      ..lineTo(cx + 8, cy + 4)
      ..lineTo(cx, cy - 3)
      ..close();
    canvas.drawPath(nPath, Paint()..color = _teal);
    canvas.drawPath(nPath2, Paint()..color = _tealDark);

    final sPath = Path()
      ..moveTo(cx, cy + r * 0.72)
      ..lineTo(cx - 8, cy - 4)
      ..lineTo(cx, cy + 3)
      ..close();
    final sPath2 = Path()
      ..moveTo(cx, cy + r * 0.72)
      ..lineTo(cx + 8, cy - 4)
      ..lineTo(cx, cy + 3)
      ..close();
    canvas.drawPath(sPath, Paint()..color = _slateMid);
    canvas.drawPath(sPath2, Paint()..color = _slate);

    canvas.drawCircle(Offset(cx, cy), 4, Paint()..color = const Color(0xFFCCD6E8));

    final tp = TextPainter(
      text: const TextSpan(
        text: 'N',
        style: TextStyle(
          color: _teal,
          fontSize: 11,
          fontWeight: FontWeight.bold,
          letterSpacing: 0.5,
        ),
      ),
      textDirection: TextDirection.ltr,
    )..layout();
    tp.paint(canvas, Offset(cx - tp.width / 2, cy - r - tp.height - 2));
  }

  @override
  bool shouldRepaint(_) => false;
}
