import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:rldc_trading_bot/providers/settings_provider.dart';

class SettingsScreen extends StatefulWidget {
  const SettingsScreen({super.key});

  @override
  State<SettingsScreen> createState() => _SettingsScreenState();
}

class _SettingsScreenState extends State<SettingsScreen> {
  final _formKey = GlobalKey<FormState>();
  late TextEditingController _restUrlController;
  late TextEditingController _wsUrlController;

  @override
  void initState() {
    super.initState();
    final settings = Provider.of<SettingsProvider>(context, listen: false);
    _restUrlController = TextEditingController(text: settings.restGatewayUrl);
    _wsUrlController = TextEditingController(text: settings.wsGatewayUrl);
  }

  @override
  void dispose() {
    _restUrlController.dispose();
    _wsUrlController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Settings'),
      ),
      body: Consumer<SettingsProvider>(
        builder: (context, settings, child) {
          return SingleChildScrollView(
            padding: const EdgeInsets.all(16),
            child: Form(
              key: _formKey,
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    'Gateway URL Configuration',
                    style: Theme.of(context).textTheme.headlineSmall,
                  ),
                  const SizedBox(height: 8),
                  Text(
                    'Configure the gateway URLs for REST API and WebSocket connections. '
                    'These settings are stored locally in your browser.',
                    style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                          color: Colors.grey,
                        ),
                  ),
                  const SizedBox(height: 24),

                  // REST API URL
                  TextFormField(
                    controller: _restUrlController,
                    decoration: const InputDecoration(
                      labelText: 'REST API Gateway URL',
                      hintText: 'https://twojadomena.pl/api',
                      border: OutlineInputBorder(),
                      helperText: 'Base URL for REST API endpoints',
                    ),
                    validator: (value) {
                      if (value == null || value.isEmpty) {
                        return 'Please enter a REST API URL';
                      }
                      if (!value.startsWith('http://') &&
                          !value.startsWith('https://')) {
                        return 'URL must start with http:// or https://';
                      }
                      return null;
                    },
                  ),
                  const SizedBox(height: 16),

                  // WebSocket URL
                  TextFormField(
                    controller: _wsUrlController,
                    decoration: const InputDecoration(
                      labelText: 'WebSocket Gateway URL',
                      hintText: 'wss://twojadomena.pl/ws',
                      border: OutlineInputBorder(),
                      helperText: 'WebSocket endpoint for real-time updates',
                    ),
                    validator: (value) {
                      if (value == null || value.isEmpty) {
                        return 'Please enter a WebSocket URL';
                      }
                      if (!value.startsWith('ws://') &&
                          !value.startsWith('wss://')) {
                        return 'WebSocket URL must start with ws:// or wss://';
                      }
                      return null;
                    },
                  ),
                  const SizedBox(height: 24),

                  // Current Settings Info
                  Card(
                    child: Padding(
                      padding: const EdgeInsets.all(16),
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text(
                            'Current Settings',
                            style: Theme.of(context).textTheme.titleMedium,
                          ),
                          const SizedBox(height: 8),
                          _buildInfoRow(
                            'REST API',
                            settings.restGatewayUrl,
                          ),
                          const SizedBox(height: 4),
                          _buildInfoRow(
                            'WebSocket',
                            settings.wsGatewayUrl,
                          ),
                        ],
                      ),
                    ),
                  ),
                  const SizedBox(height: 24),

                  // Action Buttons
                  Row(
                    children: [
                      Expanded(
                        child: ElevatedButton.icon(
                          onPressed: () async {
                            if (_formKey.currentState!.validate()) {
                              final success =
                                  await settings.updateGatewayUrls(
                                restUrl: _restUrlController.text.trim(),
                                wsUrl: _wsUrlController.text.trim(),
                              );

                              if (context.mounted) {
                                ScaffoldMessenger.of(context).showSnackBar(
                                  SnackBar(
                                    content: Text(
                                      success
                                          ? 'Settings saved successfully'
                                          : 'Failed to save settings',
                                    ),
                                    backgroundColor:
                                        success ? Colors.green : Colors.red,
                                  ),
                                );
                              }
                            }
                          },
                          icon: const Icon(Icons.save),
                          label: const Text('Save Settings'),
                        ),
                      ),
                      const SizedBox(width: 16),
                      Expanded(
                        child: OutlinedButton.icon(
                          onPressed: () async {
                            final confirmed = await showDialog<bool>(
                              context: context,
                              builder: (context) => AlertDialog(
                                title: const Text('Reset to Defaults'),
                                content: const Text(
                                  'Are you sure you want to reset to default gateway URLs?',
                                ),
                                actions: [
                                  TextButton(
                                    onPressed: () =>
                                        Navigator.pop(context, false),
                                    child: const Text('Cancel'),
                                  ),
                                  TextButton(
                                    onPressed: () =>
                                        Navigator.pop(context, true),
                                    child: const Text('Reset'),
                                  ),
                                ],
                              ),
                            );

                            if (confirmed == true) {
                              await settings.resetToDefaults();
                              _restUrlController.text =
                                  settings.restGatewayUrl;
                              _wsUrlController.text = settings.wsGatewayUrl;

                              if (context.mounted) {
                                ScaffoldMessenger.of(context).showSnackBar(
                                  const SnackBar(
                                    content: Text(
                                      'Settings reset to defaults',
                                    ),
                                    backgroundColor: Colors.blue,
                                  ),
                                );
                              }
                            }
                          },
                          icon: const Icon(Icons.restore),
                          label: const Text('Reset to Defaults'),
                        ),
                      ),
                    ],
                  ),
                  const SizedBox(height: 24),

                  // Usage Instructions
                  Card(
                    color: Colors.blue.withOpacity(0.1),
                    child: Padding(
                      padding: const EdgeInsets.all(16),
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Row(
                            children: [
                              const Icon(Icons.info_outline, size: 20),
                              const SizedBox(width: 8),
                              Text(
                                'Usage Instructions',
                                style: Theme.of(context).textTheme.titleSmall,
                              ),
                            ],
                          ),
                          const SizedBox(height: 8),
                          const Text(
                            '• Replace "twojadomena.pl" with your actual domain\n'
                            '• Use HTTPS/WSS in production for security\n'
                            '• Settings are stored in browser local storage\n'
                            '• Reconnect WebSocket after changing URLs',
                            style: TextStyle(fontSize: 13),
                          ),
                        ],
                      ),
                    ),
                  ),
                ],
              ),
            ),
          );
        },
      ),
    );
  }

  Widget _buildInfoRow(String label, String value) {
    return Row(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        SizedBox(
          width: 100,
          child: Text(
            '$label:',
            style: const TextStyle(fontWeight: FontWeight.bold),
          ),
        ),
        Expanded(
          child: Text(
            value,
            style: const TextStyle(fontFamily: 'monospace'),
          ),
        ),
      ],
    );
  }
}
