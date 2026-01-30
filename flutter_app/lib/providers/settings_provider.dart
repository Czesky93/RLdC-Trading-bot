import 'package:flutter/foundation.dart';
import 'package:shared_preferences/shared_preferences.dart';

class SettingsProvider extends ChangeNotifier {
  static const String _restUrlKey = 'rest_gateway_url';
  static const String _wsUrlKey = 'ws_gateway_url';
  
  // Default Gateway URLs
  String _restGatewayUrl = 'https://twojadomena.pl/api';
  String _wsGatewayUrl = 'wss://twojadomena.pl/ws';
  
  bool _isLoading = true;

  String get restGatewayUrl => _restGatewayUrl;
  String get wsGatewayUrl => _wsGatewayUrl;
  bool get isLoading => _isLoading;

  SettingsProvider() {
    _loadSettings();
  }

  Future<void> _loadSettings() async {
    try {
      final prefs = await SharedPreferences.getInstance();
      _restGatewayUrl = prefs.getString(_restUrlKey) ?? 'https://twojadomena.pl/api';
      _wsGatewayUrl = prefs.getString(_wsUrlKey) ?? 'wss://twojadomena.pl/ws';
      _isLoading = false;
      notifyListeners();
    } catch (e) {
      if (kDebugMode) {
        print('Error loading settings: $e');
      }
      _isLoading = false;
      notifyListeners();
    }
  }

  Future<bool> updateGatewayUrls({
    required String restUrl,
    required String wsUrl,
  }) async {
    try {
      final prefs = await SharedPreferences.getInstance();
      await prefs.setString(_restUrlKey, restUrl);
      await prefs.setString(_wsUrlKey, wsUrl);
      
      _restGatewayUrl = restUrl;
      _wsGatewayUrl = wsUrl;
      notifyListeners();
      return true;
    } catch (e) {
      if (kDebugMode) {
        print('Error saving settings: $e');
      }
      return false;
    }
  }

  Future<void> resetToDefaults() async {
    await updateGatewayUrls(
      restUrl: 'https://twojadomena.pl/api',
      wsUrl: 'wss://twojadomena.pl/ws',
    );
  }
}
