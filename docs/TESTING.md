# Testing and Validation Guide

This document provides detailed testing procedures for the RLdC Trading Bot Flutter Web application deployment.

## Test Categories

1. Backend API Tests
2. WebSocket Tests
3. Frontend Tests
4. Integration Tests
5. Security Tests
6. Performance Tests

---

## 1. Backend API Tests

### 1.1 Health Check Endpoint

```bash
# Test health endpoint
curl -s http://127.0.0.1:8000/health | python -m json.tool

# Expected output:
# {
#   "status": "healthy",
#   "timestamp": "2024-XX-XXTXX:XX:XX.XXXXXX",
#   "active_connections": 0
# }
```

### 1.2 Root Endpoint

```bash
# Test root endpoint
curl -s http://127.0.0.1:8000/ | python -m json.tool

# Expected: API information with version and endpoints
```

### 1.3 Status Endpoint

```bash
# Test status endpoint
curl -s http://127.0.0.1:8000/status | python -m json.tool

# Expected: Trading bot status information
```

### 1.4 Markets Endpoint

```bash
# Test markets data
curl -s http://127.0.0.1:8000/api/markets | python -m json.tool

# Expected: Market data with BTC, ETH, BNB prices
```

### 1.5 API Documentation

```bash
# Open API documentation in browser
xdg-open http://127.0.0.1:8000/docs
```

---

## 2. WebSocket Tests

### 2.1 Using Python Terminal Tool

```bash
# Connect to WebSocket
python tools/rldc_terminal.py ws://127.0.0.1:8000/ws

# Expected behavior:
# - Connection established
# - Receives connection confirmation
# - Receives periodic updates every 5 seconds
# - Echo messages are returned
```

### 2.2 Using wscat (Node.js)

```bash
# Install wscat
npm install -g wscat

# Connect to WebSocket
wscat -c ws://127.0.0.1:8000/ws

# Commands to test:
> Hello from wscat
< {"type": "echo", "message": "Hello from wscat", ...}
```

### 2.3 Using curl (HTTP Upgrade)

```bash
# Test WebSocket upgrade
curl -i -N -H "Connection: Upgrade" \
     -H "Upgrade: websocket" \
     -H "Sec-WebSocket-Version: 13" \
     -H "Sec-WebSocket-Key: SGVsbG8sIHdvcmxkIQ==" \
     http://127.0.0.1:8000/ws

# Expected: 101 Switching Protocols
```

---

## 3. Frontend Tests

### 3.1 Flutter Web Build

```bash
cd flutter_app

# Clean previous builds
flutter clean

# Get dependencies
flutter pub get

# Build for web
flutter build web --release --base-href /app/

# Verify build output
ls -la build/web/

# Expected files:
# - index.html
# - main.dart.js
# - flutter.js
# - assets/
# - canvaskit/
```

### 3.2 Development Server

```bash
cd flutter_app

# Run in development mode
flutter run -d chrome --web-port=8080

# Test in browser: http://localhost:8080
```

### 3.3 Static File Serving

```bash
# Serve static files locally for testing
cd flutter_app/build/web
python -m http.server 8080

# Access: http://localhost:8080
```

---

## 4. Integration Tests

### 4.1 Nginx Reverse Proxy

#### Test API through Nginx

```bash
# Replace 'localhost' with your domain
DOMAIN="localhost"

# Health check through Nginx
curl -s http://${DOMAIN}/api/health

# Status through Nginx
curl -s http://${DOMAIN}/api/status
```

#### Test WebSocket through Nginx

```bash
# Test WebSocket through Nginx
python tools/rldc_terminal.py ws://${DOMAIN}/ws

# Or with SSL
python tools/rldc_terminal.py wss://${DOMAIN}/ws
```

#### Test Flutter Web through Nginx

```bash
# Check if Flutter app is accessible
curl -I http://${DOMAIN}/app/

# Expected: 200 OK with HTML content
```

### 4.2 End-to-End Test

```bash
# Run comprehensive deployment test
./scripts/test_deployment.sh

# Review results
```

### 4.3 Browser Testing

**Manual Steps:**

1. Open browser: `http://your-domain.com/app/`
2. Verify app loads correctly
3. Click Settings → Update Gateway URLs
4. Save settings
5. Return to home → Click Connect
6. Verify WebSocket connection
7. Send a test message
8. Verify echo response
9. Check update counter increments

**Expected Behavior:**
- ✓ App loads without errors
- ✓ Settings are saved in local storage
- ✓ WebSocket connects successfully
- ✓ Messages are sent and received
- ✓ Update counter increments every 5 seconds

---

## 5. Security Tests

### 5.1 HTTPS/TLS

```bash
# Test HTTPS connection
curl -I https://your-domain.com/app/

# Check TLS certificate
openssl s_client -connect your-domain.com:443 -servername your-domain.com

# Expected: Valid certificate, TLS 1.2 or 1.3
```

### 5.2 CORS Testing

```bash
# Test CORS headers
curl -H "Origin: https://another-domain.com" \
     -H "Access-Control-Request-Method: GET" \
     -H "Access-Control-Request-Headers: X-Requested-With" \
     -X OPTIONS http://127.0.0.1:8000/health -v

# Expected: CORS headers in response
```

### 5.3 WebSocket Security

```bash
# Test WSS (WebSocket Secure)
python tools/rldc_terminal.py wss://your-domain.com/ws

# Expected: Successful secure connection
```

### 5.4 Security Headers

```bash
# Check security headers
curl -I https://your-domain.com/app/

# Look for:
# - Strict-Transport-Security
# - X-Content-Type-Options
# - X-Frame-Options (if not embedding)
# - Content-Security-Policy
```

---

## 6. Performance Tests

### 6.1 API Response Time

```bash
# Test API response time
time curl -s http://127.0.0.1:8000/health > /dev/null

# Expected: < 100ms
```

### 6.2 WebSocket Throughput

```bash
# Monitor WebSocket messages
python tools/rldc_terminal.py ws://127.0.0.1:8000/ws

# Expected: Consistent message delivery every 5 seconds
```

### 6.3 Load Testing (Optional)

```bash
# Install Apache Bench
sudo apt install apache2-utils

# Test API load
ab -n 1000 -c 10 http://127.0.0.1:8000/health

# Review results: Requests per second, response times
```

### 6.4 Frontend Performance

**Using Browser DevTools:**

1. Open DevTools (F12)
2. Go to Network tab
3. Reload page
4. Check:
   - Total load time < 3 seconds
   - Number of requests < 50
   - Total size < 5MB

**Lighthouse Audit:**

1. Open Chrome DevTools
2. Go to Lighthouse tab
3. Run audit
4. Target scores:
   - Performance: > 80
   - Accessibility: > 90
   - Best Practices: > 90

---

## 7. Iframe Integration Tests

### 7.1 Basic Iframe Test

Create a test HTML file:

```html
<!DOCTYPE html>
<html>
<head>
    <title>Iframe Test</title>
</head>
<body>
    <h1>RLdC Trading Bot - Iframe Test</h1>
    <iframe 
        src="https://your-domain.com/app/" 
        width="100%" 
        height="800px" 
        frameborder="0"
        style="border: none;">
    </iframe>
</body>
</html>
```

**Test Checklist:**
- ✓ App loads in iframe
- ✓ No console errors
- ✓ Settings work in iframe
- ✓ WebSocket connects in iframe
- ✓ No mixed content warnings (HTTP/HTTPS)

### 7.2 Drupal/Joomla Integration

1. Add iframe to content
2. Test in preview mode
3. Publish and verify
4. Check browser console for errors

---

## 8. Monitoring and Logs

### 8.1 FastAPI Logs

```bash
# If using systemd
sudo journalctl -u rldc-api -f

# If using nohup
tail -f /var/log/rldc-api.log
```

### 8.2 Nginx Logs

```bash
# Access logs
sudo tail -f /var/log/nginx/access.log

# Error logs
sudo tail -f /var/log/nginx/error.log

# Filter for /app/ requests
sudo tail -f /var/log/nginx/access.log | grep "/app/"
```

### 8.3 System Resources

```bash
# Check CPU and memory usage
htop

# Or using ps
ps aux | grep -E 'uvicorn|nginx'

# Check disk space
df -h /var/www/rldc_app_web
```

---

## Test Automation Script

Save as `test_all.sh`:

```bash
#!/bin/bash
set -e

echo "Running all tests..."

# 1. Backend tests
echo "Testing backend..."
curl -sf http://127.0.0.1:8000/health || exit 1

# 2. WebSocket test (quick)
echo "Testing WebSocket..."
timeout 10 python tools/rldc_terminal.py ws://127.0.0.1:8000/ws &
sleep 3
pkill -f rldc_terminal || true

# 3. Nginx tests
echo "Testing Nginx..."
curl -sf http://localhost/api/health || echo "Nginx not configured yet"

# 4. Frontend build
echo "Testing Flutter build..."
[ -d "flutter_app/build/web" ] || echo "Flutter not built yet"

echo "All tests completed!"
```

---

## Troubleshooting Common Issues

| Issue | Test | Solution |
|-------|------|----------|
| API not responding | `curl http://127.0.0.1:8000/health` | Check if service is running |
| WebSocket fails | `python tools/rldc_terminal.py` | Check firewall, Nginx config |
| 404 for /app/ | `ls /var/www/rldc_app_web/` | Rebuild and deploy Flutter app |
| CORS errors | Browser console | Update CORS settings in `api/main.py` |
| Mixed content | Browser console | Ensure HTTPS everywhere |

---

## Success Criteria

All tests should pass with these results:

- ✓ FastAPI health check returns 200 OK
- ✓ WebSocket connects and receives messages
- ✓ Flutter app loads in browser
- ✓ Settings screen saves configurations
- ✓ Nginx proxies all requests correctly
- ✓ HTTPS/WSS work without warnings
- ✓ Iframe integration works
- ✓ No console errors
- ✓ Performance meets targets
