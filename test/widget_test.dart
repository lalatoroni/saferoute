import 'package:flutter_test/flutter_test.dart';
import 'package:sqflite_common_ffi/sqflite_ffi.dart';
import 'package:saferoute/main.dart';

void main() {
  setUpAll(() {
    sqfliteFfiInit();
    databaseFactory = databaseFactoryFfi;
  });

  testWidgets('App startet und zeigt Onboarding', (tester) async {
    await tester.pumpWidget(const SafeRouteApp());
    expect(find.text('Ich bin dabei'), findsOneWidget);
  });
}
