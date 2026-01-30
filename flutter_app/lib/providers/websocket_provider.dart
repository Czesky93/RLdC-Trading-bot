import 'dart:async';
import 'dart:convert';
import 'package:flutter/foundation.dart';
import 'package:web_socket_channel/web_socket_channel.dart';
import 'package:rldc_trading_bot/providers/settings_provider.dart';

class WebSocketProvider extends ChangeNotifier {
  final SettingsProvider _settingsProvider;
  WebSocketChannel? _channel;
  StreamSubscription? _subscription;
  
  bool _isConnected = false;
  String _lastMessage = '';
  List<Map<String, dynamic>> _messages = [];
  int _updateCounter = 0;

  bool get isConnected => _isConnected;
  String get lastMessage => _lastMessage;
  List<Map<String, dynamic>> get messages => _messages;
  int get updateCounter => _updateCounter;

  WebSocketProvider(this._settingsProvider);

  void connect() {
    if (_isConnected) {
      if (kDebugMode) {
        print('WebSocket already connected');
      }
      return;
    }

    try {
      final wsUrl = _settingsProvider.wsGatewayUrl;
      if (kDebugMode) {
        print('Connecting to WebSocket: $wsUrl');
      }

      _channel = WebSocketChannel.connect(Uri.parse(wsUrl));
      
      _subscription = _channel!.stream.listen(
        _onMessage,
        onError: _onError,
        onDone: _onDone,
      );

      _isConnected = true;
      notifyListeners();
    } catch (e) {
      if (kDebugMode) {
        print('WebSocket connection error: $e');
      }
      _isConnected = false;
      notifyListeners();
    }
  }

  void _onMessage(dynamic message) {
    try {
      final data = jsonDecode(message);
      _lastMessage = message;
      _messages.insert(0, {
        'timestamp': DateTime.now().toIso8601String(),
        'data': data,
      });
      
      // Keep only last 100 messages
      if (_messages.length > 100) {
        _messages = _messages.sublist(0, 100);
      }

      // Update counter from messages
      if (data['type'] == 'update' && data['data'] != null) {
        _updateCounter = data['data']['counter'] ?? _updateCounter;
      }

      if (kDebugMode) {
        print('WebSocket message: $data');
      }
      
      notifyListeners();
    } catch (e) {
      if (kDebugMode) {
        print('Error parsing WebSocket message: $e');
      }
    }
  }

  void _onError(dynamic error) {
    if (kDebugMode) {
      print('WebSocket error: $error');
    }
    _isConnected = false;
    notifyListeners();
  }

  void _onDone() {
    if (kDebugMode) {
      print('WebSocket connection closed');
    }
    _isConnected = false;
    notifyListeners();
  }

  void disconnect() {
    if (kDebugMode) {
      print('Disconnecting WebSocket');
    }
    _subscription?.cancel();
    _channel?.sink.close();
    _isConnected = false;
    notifyListeners();
  }

  void sendMessage(String message) {
    if (_isConnected && _channel != null) {
      _channel!.sink.add(message);
      if (kDebugMode) {
        print('Sent message: $message');
      }
    }
  }

  void clearMessages() {
    _messages.clear();
    notifyListeners();
  }

  @override
  void dispose() {
    disconnect();
    super.dispose();
  }
}
