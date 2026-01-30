import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:rldc_trading_bot/providers/settings_provider.dart';
import 'package:rldc_trading_bot/providers/websocket_provider.dart';
import 'package:rldc_trading_bot/screens/home_screen.dart';
import 'package:rldc_trading_bot/screens/settings_screen.dart';

void main() {
  runApp(const MyApp());
}

class MyApp extends StatelessWidget {
  const MyApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MultiProvider(
      providers: [
        ChangeNotifierProvider(create: (_) => SettingsProvider()),
        ChangeNotifierProxyProvider<SettingsProvider, WebSocketProvider>(
          create: (context) => WebSocketProvider(
            Provider.of<SettingsProvider>(context, listen: false),
          ),
          update: (context, settings, previous) =>
              previous ?? WebSocketProvider(settings),
        ),
      ],
      child: MaterialApp(
        title: 'RLdC Trading Bot',
        theme: ThemeData(
          colorScheme: ColorScheme.fromSeed(
            seedColor: Colors.blue,
            brightness: Brightness.dark,
          ),
          useMaterial3: true,
        ),
        initialRoute: '/',
        routes: {
          '/': (context) => const HomeScreen(),
          '/settings': (context) => const SettingsScreen(),
        },
      ),
    );
  }
}
