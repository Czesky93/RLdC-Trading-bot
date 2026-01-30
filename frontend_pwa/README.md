# RLdC Portal - Progressive Web Application

A Progressive Web Application (PWA) template for the RLdC Trading Bot portal.

## Features

- **Single-Page Application**: Fast, smooth navigation without page reloads
- **Offline Support**: Service Worker caching for offline functionality
- **Installable**: Can be installed as a standalone app on desktop and mobile
- **Responsive Design**: Works seamlessly on all screen sizes
- **Modern UI**: Cyberpunk-inspired interface with smooth animations

## Files

- **index.html** - Main application file with all views and functionality
- **manifest.webmanifest** - PWA configuration and app metadata
- **sw.js** - Service Worker for caching and offline support

## Views

1. **Dashboard** - Trading statistics and performance metrics
2. **Orderbook** - Market depth visualization with real-time order data
3. **Logs** - System activity log with different severity levels
4. **Modules** - Trading modules overview with status indicators
5. **Settings** - Configuration interface for API keys and parameters

## Running Locally

You can serve the PWA using any static HTTP server:

```bash
# Using Python 3
cd frontend_pwa
python3 -m http.server 8080

# Using Node.js http-server
npx http-server frontend_pwa -p 8080

# Using PHP
cd frontend_pwa
php -S localhost:8080
```

Then open `http://localhost:8080` in your browser.

## Installing as PWA

1. Open the PWA in a supported browser (Chrome, Edge, Safari)
2. Click the install icon in the address bar
3. Follow the prompts to install the app
4. The app will be available in your applications menu

## Browser Support

- Chrome/Edge: Full PWA support
- Firefox: Partial PWA support
- Safari: iOS 11.3+ supports PWA installation
- Opera: Full PWA support

## Security Notes

- API credentials are protected with `autocomplete="off"`
- Service Worker uses cache-first strategy with network fallback
- All sensitive data should be transmitted over HTTPS in production

## Customization

You can customize the PWA by editing:

- **Colors**: Modify CSS variables in the `<style>` section
- **App Name**: Update in `manifest.webmanifest`
- **Cached Files**: Modify `urlsToCache` array in `sw.js`
- **Views**: Add/remove sections in the HTML

## Production Deployment

For production deployment:

1. Serve over HTTPS (required for Service Workers)
2. Update `start_url` in manifest.webmanifest if not deploying to root
3. Replace placeholder data with real API endpoints
4. Consider removing console.log statements from sw.js
5. Generate proper app icons in multiple sizes

## License

Part of the RLdC Trading Bot project.
