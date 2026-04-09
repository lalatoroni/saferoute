import 'package:workmanager/workmanager.dart';
import 'nina_service.dart';
import '../database/db_helper.dart';

const _syncTaskName = 'saferoute.dangerSync';

@pragma('vm:entry-point')
void callbackDispatcher() {
  Workmanager().executeTask((task, inputData) async {
    if (task == _syncTaskName) {
      final nina = NinaService();
      final db = DbHelper();
      await db.init();
      final zones = await nina.fetchDangerZones();
      for (final zone in zones) {
        await db.upsertDangerZone(zone);
      }
      await db.close();
    }
    return true;
  });
}

class SyncService {
  static Future<void> init() async {
    await Workmanager().initialize(callbackDispatcher, isInDebugMode: false);
  }

  static Future<void> schedulePeriodicSync() async {
    await Workmanager().registerPeriodicTask(
      'dangerSyncTask',
      _syncTaskName,
      frequency: const Duration(minutes: 15),
      constraints: Constraints(networkType: NetworkType.connected),
      existingWorkPolicy: ExistingWorkPolicy.keep,
    );
  }
}
