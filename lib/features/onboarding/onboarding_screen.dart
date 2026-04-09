import 'package:flutter/material.dart';
import '../map/map_screen.dart';

class OnboardingScreen extends StatelessWidget {
  const OnboardingScreen({super.key});

  static const _teal = Color(0xFF00CFA8);
  static const _textMain = Color(0xFFE4EAF6);
  static const _bg = Color(0xFF0C0F18);

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: _bg,
      body: SafeArea(
        child: Padding(
          padding: const EdgeInsets.symmetric(horizontal: 32, vertical: 48),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              const Spacer(),
              _Section(
                title: 'Was SafeRoute über dich weiß:',
                items: [
                  'Deinen Standort (nur lokal)',
                  'Dein Gerät',
                ],
                color: _textMain,
              ),
              const SizedBox(height: 40),
              _Section(
                title: 'Was SafeRoute nie wissen wird:',
                items: [
                  'Deinen Namen',
                  'Deine Route (kein Upload)',
                  'Irgendetwas über dich',
                ],
                color: _teal,
              ),
              const Spacer(),
              SizedBox(
                width: double.infinity,
                height: 60,
                child: ElevatedButton(
                  style: ElevatedButton.styleFrom(
                    backgroundColor: _teal,
                    foregroundColor: _bg,
                    shape: RoundedRectangleBorder(
                      borderRadius: BorderRadius.circular(12),
                    ),
                    textStyle: const TextStyle(
                      fontSize: 20,
                      fontWeight: FontWeight.bold,
                      letterSpacing: 1.2,
                    ),
                  ),
                  onPressed: () => Navigator.pushReplacement(
                    context,
                    MaterialPageRoute(builder: (_) => const MapScreen()),
                  ),
                  child: const Text('Ich bin dabei'),
                ),
              ),
              const SizedBox(height: 24),
            ],
          ),
        ),
      ),
    );
  }
}

class _Section extends StatelessWidget {
  final String title;
  final List<String> items;
  final Color color;

  const _Section({
    required this.title,
    required this.items,
    required this.color,
  });

  static const _textMid = Color(0xFF7A8CA0);

  @override
  Widget build(BuildContext context) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(title,
            style: const TextStyle(
                color: _textMid, fontSize: 14, letterSpacing: 0.5)),
        const SizedBox(height: 12),
        ...items.map((item) => Padding(
              padding: const EdgeInsets.only(bottom: 8),
              child: Row(
                children: [
                  Icon(Icons.radio_button_checked, color: color, size: 14),
                  const SizedBox(width: 12),
                  Text(item,
                      style: TextStyle(
                          color: color,
                          fontSize: 18,
                          fontWeight: FontWeight.w500)),
                ],
              ),
            )),
      ],
    );
  }
}
