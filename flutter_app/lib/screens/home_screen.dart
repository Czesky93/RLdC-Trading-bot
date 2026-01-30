import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:rldc_trading_bot/providers/websocket_provider.dart';
import 'package:rldc_trading_bot/providers/settings_provider.dart';

class HomeScreen extends StatefulWidget {
  const HomeScreen({super.key});

  @override
  State<HomeScreen> createState() => _HomeScreenState();
}

class _HomeScreenState extends State<HomeScreen> {
  final TextEditingController _messageController = TextEditingController();

  @override
  void dispose() {
    _messageController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('RLdC Trading Bot'),
        actions: [
          IconButton(
            icon: const Icon(Icons.settings),
            onPressed: () {
              Navigator.pushNamed(context, '/settings');
            },
          ),
        ],
      ),
      body: Consumer2<WebSocketProvider, SettingsProvider>(
        builder: (context, wsProvider, settingsProvider, child) {
          if (settingsProvider.isLoading) {
            return const Center(child: CircularProgressIndicator());
          }

          return Column(
            children: [
              // Connection Status Card
              Card(
                margin: const EdgeInsets.all(16),
                child: Padding(
                  padding: const EdgeInsets.all(16),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Row(
                        children: [
                          Icon(
                            wsProvider.isConnected
                                ? Icons.check_circle
                                : Icons.cancel,
                            color: wsProvider.isConnected
                                ? Colors.green
                                : Colors.red,
                          ),
                          const SizedBox(width: 8),
                          Text(
                            wsProvider.isConnected
                                ? 'Connected'
                                : 'Disconnected',
                            style: Theme.of(context).textTheme.titleLarge,
                          ),
                          const Spacer(),
                          ElevatedButton(
                            onPressed: wsProvider.isConnected
                                ? wsProvider.disconnect
                                : wsProvider.connect,
                            child: Text(
                              wsProvider.isConnected
                                  ? 'Disconnect'
                                  : 'Connect',
                            ),
                          ),
                        ],
                      ),
                      const SizedBox(height: 16),
                      Text(
                        'WebSocket: ${settingsProvider.wsGatewayUrl}',
                        style: Theme.of(context).textTheme.bodySmall,
                      ),
                      Text(
                        'REST API: ${settingsProvider.restGatewayUrl}',
                        style: Theme.of(context).textTheme.bodySmall,
                      ),
                      if (wsProvider.isConnected)
                        Padding(
                          padding: const EdgeInsets.only(top: 8),
                          child: Text(
                            'Update Counter: ${wsProvider.updateCounter}',
                            style: Theme.of(context).textTheme.bodyMedium,
                          ),
                        ),
                    ],
                  ),
                ),
              ),

              // Send Message Section
              if (wsProvider.isConnected)
                Padding(
                  padding: const EdgeInsets.symmetric(horizontal: 16),
                  child: Row(
                    children: [
                      Expanded(
                        child: TextField(
                          controller: _messageController,
                          decoration: const InputDecoration(
                            labelText: 'Send Message',
                            border: OutlineInputBorder(),
                          ),
                          onSubmitted: (value) {
                            if (value.isNotEmpty) {
                              wsProvider.sendMessage(value);
                              _messageController.clear();
                            }
                          },
                        ),
                      ),
                      const SizedBox(width: 8),
                      IconButton(
                        icon: const Icon(Icons.send),
                        onPressed: () {
                          final message = _messageController.text;
                          if (message.isNotEmpty) {
                            wsProvider.sendMessage(message);
                            _messageController.clear();
                          }
                        },
                      ),
                    ],
                  ),
                ),

              const SizedBox(height: 16),

              // Messages List
              Padding(
                padding: const EdgeInsets.symmetric(horizontal: 16),
                child: Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    Text(
                      'Messages (${wsProvider.messages.length})',
                      style: Theme.of(context).textTheme.titleMedium,
                    ),
                    if (wsProvider.messages.isNotEmpty)
                      TextButton(
                        onPressed: wsProvider.clearMessages,
                        child: const Text('Clear'),
                      ),
                  ],
                ),
              ),

              Expanded(
                child: wsProvider.messages.isEmpty
                    ? const Center(
                        child: Text('No messages yet'),
                      )
                    : ListView.builder(
                        itemCount: wsProvider.messages.length,
                        itemBuilder: (context, index) {
                          final message = wsProvider.messages[index];
                          return Card(
                            margin: const EdgeInsets.symmetric(
                              horizontal: 16,
                              vertical: 4,
                            ),
                            child: ListTile(
                              title: Text(
                                message['data']['type']?.toString() ??
                                    'Unknown',
                                style: const TextStyle(
                                  fontWeight: FontWeight.bold,
                                ),
                              ),
                              subtitle: Column(
                                crossAxisAlignment: CrossAxisAlignment.start,
                                children: [
                                  Text(
                                    _formatMessageData(message['data']),
                                    maxLines: 3,
                                    overflow: TextOverflow.ellipsis,
                                  ),
                                  const SizedBox(height: 4),
                                  Text(
                                    _formatTimestamp(message['timestamp']),
                                    style: const TextStyle(fontSize: 11),
                                  ),
                                ],
                              ),
                              isThreeLine: true,
                            ),
                          );
                        },
                      ),
              ),
            ],
          );
        },
      ),
    );
  }

  String _formatMessageData(Map<String, dynamic> data) {
    if (data['type'] == 'connection') {
      return 'Status: ${data['status']}';
    } else if (data['type'] == 'update') {
      final counter = data['data']?['counter'] ?? '?';
      return 'Update #$counter';
    } else if (data['type'] == 'echo') {
      return 'Echo: ${data['message']}';
    }
    return data.toString();
  }

  String _formatTimestamp(String timestamp) {
    try {
      final dt = DateTime.parse(timestamp);
      return '${dt.hour.toString().padLeft(2, '0')}:'
          '${dt.minute.toString().padLeft(2, '0')}:'
          '${dt.second.toString().padLeft(2, '0')}';
    } catch (e) {
      return timestamp;
    }
  }
}
