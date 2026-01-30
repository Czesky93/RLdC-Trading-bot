# RLdC Trading Bot - Flutter Web Application

This is the Flutter Web frontend for the RLdC Trading Bot. It provides a web-based interface for monitoring and interacting with the trading bot through REST API and WebSocket connections.

## Features

- **Real-time WebSocket Connection**: Live updates from the trading bot
- **Settings Management**: Configure Gateway URLs (REST and WebSocket endpoints)
- **Local Storage**: Settings stored in browser's local storage
- **Responsive Design**: Works on desktop and mobile browsers
- **Message History**: View and track all WebSocket messages
- **Send Messages**: Test WebSocket communication

## Building the Application

### Prerequisites

- Flutter SDK 3.0 or higher
- Dart SDK

### Build for Web

```bash
# Install dependencies
flutter pub get

# Build for production with base-href
flutter build web --release --base-href /app/

# Output will be in: build/web/
```

### Development Mode

```bash
# Run in development mode
flutter run -d chrome --web-port=8080
```

## Configuration

The app allows users to configure Gateway URLs through the Settings screen:

- **REST API Gateway**: Default is `https://twojadomena.pl/api`
- **WebSocket Gateway**: Default is `wss://twojadomena.pl/ws`

These settings are stored in the browser's local storage and can be customized for different deployments.

## Project Structure

```
flutter_app/
├── lib/
│   ├── main.dart                 # App entry point
│   ├── providers/
│   │   ├── settings_provider.dart    # Settings management
│   │   └── websocket_provider.dart   # WebSocket connection
│   └── screens/
│       ├── home_screen.dart          # Main screen
│       └── settings_screen.dart      # Settings screen
├── web/
│   ├── index.html                # HTML template
│   └── manifest.json             # PWA manifest
└── pubspec.yaml                  # Dependencies
```

## Dependencies

- **flutter**: Flutter SDK
- **provider**: State management
- **http**: HTTP client for REST API
- **web_socket_channel**: WebSocket client
- **shared_preferences**: Local storage
- **url_launcher**: URL utilities

## Deployment

See [DEPLOYMENT.md](../docs/DEPLOYMENT.md) for complete deployment instructions.

Quick deployment:

```bash
# Build the app
flutter build web --release --base-href /app/

# Deploy to server
sudo cp -r build/web/* /var/www/rldc_app_web/
sudo chown -R www-data:www-data /var/www/rldc_app_web/
```

## Development

### Adding New Features

1. Create new screens in `lib/screens/`
2. Add routes in `lib/main.dart`
3. Create providers for state management in `lib/providers/`
4. Use the existing `SettingsProvider` to access configuration

### Testing

```bash
# Run tests
flutter test

# Run with coverage
flutter test --coverage
```

## License

This project is part of the RLdC Trading Bot system.
