# Quick Start Guide - Flutter Web Application

This guide will help you quickly set up and run the RLdC Trading Bot Flutter Web application with FastAPI backend.

## Prerequisites

- Python 3.8+
- Flutter SDK 3.0+
- Nginx (for production deployment)

## Development Setup (5 minutes)

### 1. Install Python Dependencies

```bash
cd /path/to/RLdC-Trading-bot
pip install fastapi uvicorn[standard] websockets
```

### 2. Start the FastAPI Backend

```bash
# Start the backend server
python -m uvicorn api.main:app --host 0.0.0.0 --port 8000

# Or use the Python script directly
python api/main.py
```

The API will be available at:
- Health check: http://127.0.0.1:8000/health
- API documentation: http://127.0.0.1:8000/docs
- WebSocket: ws://127.0.0.1:8000/ws

### 3. Test the WebSocket Connection

In a new terminal:

```bash
python tools/rldc_terminal.py ws://127.0.0.1:8000/ws
```

You should see live updates from the WebSocket connection.

### 4. Build the Flutter Web App

```bash
cd flutter_app

# Install dependencies
flutter pub get

# Build for production
flutter build web --release --base-href /app/

# Or run in development mode
flutter run -d chrome --web-port=8080
```

## Production Deployment (15 minutes)

### 1. Build and Deploy Flutter App

```bash
# Build the app
./scripts/build_flutter_web.sh

# Deploy to web server
sudo mkdir -p /var/www/rldc_app_web
sudo cp -r flutter_app/build/web/* /var/www/rldc_app_web/
sudo chown -R www-data:www-data /var/www/rldc_app_web/
```

### 2. Install Nginx Configuration

```bash
# Copy configuration
sudo cp nginx/rldc_app.conf /etc/nginx/sites-available/rldc_app

# Edit to use your domain (replace 'twojadomena.pl')
sudo nano /etc/nginx/sites-available/rldc_app

# Enable site
sudo ln -s /etc/nginx/sites-available/rldc_app /etc/nginx/sites-enabled/

# Test and reload
sudo nginx -t
sudo systemctl reload nginx
```

### 3. Setup FastAPI as a Service

```bash
# Copy systemd service file
sudo cp systemd/rldc-api.service /etc/systemd/system/

# Edit WorkingDirectory to match your installation path
sudo nano /etc/systemd/system/rldc-api.service

# Enable and start service
sudo systemctl daemon-reload
sudo systemctl enable rldc-api
sudo systemctl start rldc-api

# Check status
sudo systemctl status rldc-api
```

### 4. Configure Firewall

```bash
# Allow HTTP/HTTPS traffic
sudo ufw allow 'Nginx Full'
```

### 5. Setup HTTPS (Optional but Recommended)

```bash
# Install Certbot
sudo apt install certbot python3-certbot-nginx -y

# Obtain certificate
sudo certbot --nginx -d your-domain.com

# Certificate will auto-renew
```

## Testing the Deployment

Run the comprehensive test script:

```bash
./scripts/test_deployment.sh
```

Or test manually:

```bash
# Test REST API
curl -s http://127.0.0.1:8000/health

# Test through Nginx (replace with your domain)
curl -s http://your-domain.com/api/health

# Test WebSocket
python tools/rldc_terminal.py ws://127.0.0.1:8000/ws

# Test Flutter Web
# Open browser: http://your-domain.com/app/
```

## Using the Flutter Web App

1. **Open the App**: Navigate to `https://your-domain.com/app/`

2. **Configure Settings**:
   - Click the Settings icon (⚙️) in the top-right
   - Update the Gateway URLs if needed:
     - REST: `https://your-domain.com/api`
     - WebSocket: `wss://your-domain.com/ws`
   - Click "Save Settings"

3. **Connect WebSocket**:
   - Return to the home screen
   - Click the "Connect" button
   - Watch for live updates

4. **Send Messages**:
   - Type a message in the input field
   - Press Enter or click Send
   - See the echo response from the server

## Embedding in Drupal/Joomla

Add an iframe to your CMS:

```html
<iframe 
    src="https://your-domain.com/app/" 
    width="100%" 
    height="800px" 
    frameborder="0"
    style="border: none;">
</iframe>
```

## Troubleshooting

### Backend Won't Start

```bash
# Check if port is already in use
sudo lsof -i :8000

# Check logs
sudo journalctl -u rldc-api -f
```

### Nginx 404 for /app/

```bash
# Verify files exist
ls -la /var/www/rldc_app_web/

# Check permissions
sudo chown -R www-data:www-data /var/www/rldc_app_web/
```

### WebSocket Connection Fails

```bash
# Test backend directly
python tools/rldc_terminal.py ws://127.0.0.1:8000/ws

# Check Nginx configuration
sudo nginx -t

# Check logs
sudo tail -f /var/log/nginx/error.log
```

### CORS Errors

The FastAPI backend has CORS enabled for all origins in development. For production, edit `api/main.py` and update the `allow_origins` list to include only your domain.

## Next Steps

- Read the full [Deployment Guide](../docs/DEPLOYMENT.md)
- Configure authentication for the API
- Set up monitoring and logging
- Add rate limiting
- Integrate with your trading bot backend

## Support

For issues or questions, please refer to:
- Full documentation: `docs/DEPLOYMENT.md`
- API documentation: `http://127.0.0.1:8000/docs`
- GitHub repository issues
