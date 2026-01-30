# Deployment Guide - RLdC Trading Bot Flutter Web Application

This guide provides step-by-step instructions for deploying the RLdC Trading Bot Flutter Web application with Nginx reverse proxy.

## Architecture Overview

```
┌─────────────────────────────────────────────────────────┐
│                     Nginx (Port 80/443)                 │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  /app/     →  Flutter Web (Static Files)                │
│                 /var/www/rldc_app_web/                  │
│                                                          │
│  /api/     →  FastAPI Backend (REST)                    │
│                 http://127.0.0.1:8000/                  │
│                                                          │
│  /ws       →  FastAPI WebSocket                         │
│                 http://127.0.0.1:8000/ws                │
│                                                          │
└─────────────────────────────────────────────────────────┘
```

## Prerequisites

- Ubuntu 20.04+ or similar Linux distribution
- Root or sudo access
- Python 3.8+
- Flutter SDK (for building the web app)
- Nginx
- Domain name (twojadomena.pl - replace with your actual domain)

## Step 1: Install Dependencies

### Install Python Dependencies

```bash
cd /path/to/RLdC-Trading-bot
pip install -r requirements.txt
```

This will install:
- FastAPI
- Uvicorn (ASGI server)
- WebSockets
- Other required Python packages

### Install Flutter SDK

```bash
# Download Flutter
cd ~
wget https://storage.googleapis.com/flutter_infra_release/releases/stable/linux/flutter_linux_3.16.0-stable.tar.xz
tar xf flutter_linux_3.16.0-stable.tar.xz

# Add to PATH
echo 'export PATH="$PATH:$HOME/flutter/bin"' >> ~/.bashrc
source ~/.bashrc

# Verify installation
flutter --version
flutter doctor
```

### Install Nginx

```bash
sudo apt update
sudo apt install nginx -y
```

## Step 2: Build Flutter Web Application

### Build the application

```bash
cd /path/to/RLdC-Trading-bot
./scripts/build_flutter_web.sh
```

Or manually:

```bash
cd flutter_app
flutter pub get
flutter build web --release --base-href /app/
```

### Deploy to web directory

```bash
# Create the deployment directory
sudo mkdir -p /var/www/rldc_app_web

# Copy build files
sudo cp -r flutter_app/build/web/* /var/www/rldc_app_web/

# Set proper permissions
sudo chown -R www-data:www-data /var/www/rldc_app_web/
sudo chmod -R 755 /var/www/rldc_app_web/
```

## Step 3: Configure Nginx

### Copy the configuration file

```bash
# Copy the configuration
sudo cp nginx/rldc_app.conf /etc/nginx/sites-available/rldc_app

# Edit the configuration to use your domain
sudo nano /etc/nginx/sites-available/rldc_app
# Replace 'twojadomena.pl' with your actual domain name

# Create a symbolic link to enable the site
sudo ln -s /etc/nginx/sites-available/rldc_app /etc/nginx/sites-enabled/

# Test the configuration
sudo nginx -t

# If the test passes, reload Nginx
sudo systemctl reload nginx
```

### Verify Nginx is running

```bash
sudo systemctl status nginx
```

## Step 4: Start the FastAPI Backend

### Run FastAPI with Uvicorn

```bash
cd /path/to/RLdC-Trading-bot

# Run in the foreground (for testing)
python -m uvicorn api.main:app --host 0.0.0.0 --port 8000

# Or run in the background
nohup python -m uvicorn api.main:app --host 0.0.0.0 --port 8000 > /var/log/rldc_api.log 2>&1 &
```

### Create a systemd service (recommended for production)

Create `/etc/systemd/system/rldc-api.service`:

```ini
[Unit]
Description=RLdC Trading Bot API
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/path/to/RLdC-Trading-bot
Environment="PATH=/usr/bin"
ExecStart=/usr/bin/python3 -m uvicorn api.main:app --host 127.0.0.1 --port 8000
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Then enable and start the service:

```bash
sudo systemctl daemon-reload
sudo systemctl enable rldc-api
sudo systemctl start rldc-api
sudo systemctl status rldc-api
```

## Step 5: Testing

### Test REST API endpoint

```bash
# Health check
curl -s http://127.0.0.1:8000/health
curl -s http://localhost/api/health

# Should return:
# {"status":"healthy","timestamp":"...","active_connections":0}
```

### Test WebSocket endpoint

Using the provided terminal tool:

```bash
cd /path/to/RLdC-Trading-bot
python tools/rldc_terminal.py ws://127.0.0.1:8000/ws
```

Or using wscat (install with: `npm install -g wscat`):

```bash
wscat -c ws://127.0.0.1:8000/ws
```

### Test Flutter Web Frontend

Open your browser and navigate to:
- `http://your-server-ip/app/` (if using IP)
- `http://twojadomena.pl/app/` (if DNS is configured)

## Step 6: Setup TLS/HTTPS (Production)

### Install Certbot for Let's Encrypt

```bash
sudo apt install certbot python3-certbot-nginx -y
```

### Obtain SSL certificate

```bash
sudo certbot --nginx -d twojadomena.pl
```

Follow the prompts to complete the certificate installation.

### Update Nginx configuration for HTTPS

The Nginx configuration file already includes commented sections for HTTPS. After obtaining the certificate, update `/etc/nginx/sites-available/rldc_app`:

```nginx
server {
    listen 443 ssl http2;
    server_name twojadomena.pl;
    
    ssl_certificate /etc/letsencrypt/live/twojadomena.pl/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/twojadomena.pl/privkey.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    
    # ... rest of configuration ...
}

server {
    listen 80;
    server_name twojadomena.pl;
    return 301 https://$server_name$request_uri;
}
```

Then reload Nginx:

```bash
sudo nginx -t
sudo systemctl reload nginx
```

### Update Flutter app settings

After enabling HTTPS, update the default Gateway URLs in the Flutter app settings screen:
- REST: `https://twojadomena.pl/api`
- WebSocket: `wss://twojadomena.pl/ws`

## Step 7: Configure Firewall

```bash
# Allow HTTP and HTTPS traffic
sudo ufw allow 'Nginx Full'

# Check firewall status
sudo ufw status
```

## Step 8: Iframe Integration (Drupal/Joomla)

To embed the Flutter app in Drupal or Joomla, use an iframe:

```html
<iframe 
    src="https://twojadomena.pl/app/" 
    width="100%" 
    height="800px" 
    frameborder="0"
    style="border: none;"
    allowfullscreen>
</iframe>
```

### Important Notes for Iframe Integration:
- Ensure HTTPS is enabled to avoid mixed content warnings
- Set appropriate `X-Frame-Options` in Nginx if needed
- Test WebSocket connections work within the iframe

## Monitoring and Logs

### View FastAPI logs

```bash
# If using systemd service
sudo journalctl -u rldc-api -f

# If using nohup
tail -f /var/log/rldc_api.log
```

### View Nginx logs

```bash
# Access logs
sudo tail -f /var/log/nginx/access.log

# Error logs
sudo tail -f /var/log/nginx/error.log
```

## Troubleshooting

### Issue: Nginx returns 404 for /app/

**Solution:** Check if files exist in `/var/www/rldc_app_web/` and permissions are correct.

```bash
ls -la /var/www/rldc_app_web/
sudo chown -R www-data:www-data /var/www/rldc_app_web/
```

### Issue: WebSocket connection fails

**Solution:** Ensure FastAPI is running and check Nginx WebSocket configuration.

```bash
# Check if FastAPI is running
curl http://127.0.0.1:8000/health

# Test WebSocket directly
python tools/rldc_terminal.py ws://127.0.0.1:8000/ws
```

### Issue: CORS errors

**Solution:** CORS is configured in `api/main.py`. For production, update `allow_origins` to include your specific domain.

### Issue: Mixed content warnings

**Solution:** Ensure both the main site and API use HTTPS/WSS.

## Updating the Application

### Update Flutter Web App

```bash
cd /path/to/RLdC-Trading-bot
./scripts/build_flutter_web.sh
sudo cp -r flutter_app/build/web/* /var/www/rldc_app_web/
```

### Update FastAPI Backend

```bash
cd /path/to/RLdC-Trading-bot
git pull  # or update your code
sudo systemctl restart rldc-api
```

## Security Recommendations

1. **Use HTTPS/WSS in production** - Never use HTTP/WS with sensitive data
2. **Configure firewall** - Only allow necessary ports
3. **Regular updates** - Keep system packages and dependencies updated
4. **Authentication** - Add authentication to the API endpoints
5. **Rate limiting** - Implement rate limiting in Nginx or FastAPI
6. **Monitoring** - Set up proper monitoring and alerting

## Additional Resources

- [Flutter Web Deployment](https://docs.flutter.dev/deployment/web)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Nginx WebSocket Proxying](http://nginx.org/en/docs/http/websocket.html)
- [Let's Encrypt](https://letsencrypt.org/)

## Support

For issues or questions, please refer to the project repository or documentation.
