import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:sqflite_common_ffi/sqflite_ffi.dart';
import 'package:saferoute/features/onboarding/onboarding_screen.dart';

void main() {
  setUpAll(() {
    sqfliteFfiInit();
    databaseFactory = databaseFactoryFfi;
  });

  testWidgets('zeigt Trust-Statement und Button', (tester) async {
    await tester.pumpWidget(
      const MaterialApp(home: OnboardingScreen()),
    );
    expect(find.text('Ich bin dabei'), findsOneWidget);
    expect(find.textContaining('nie wissen'), findsWidgets);
  });

  testWidgets('Button navigiert zum nächsten Screen', (tester) async {
    await tester.pumpWidget(
      const MaterialApp(home: OnboardingScreen()),
    );
    await tester.tap(find.text('Ich bin dabei'));
    // Einen Frame pumpen damit die Navigation startet
    await tester.pump();
    await tester.pump(const Duration(milliseconds: 500));
    // Nach Navigation: Onboarding nicht mehr sichtbar
    expect(find.text('Ich bin dabei'), findsNothing);
  });
}
