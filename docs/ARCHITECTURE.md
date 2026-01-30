# Architecture Overview

This document provides a comprehensive overview of the RLdC Trading Bot Flutter Web application architecture.

## System Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                         Client Browser                               │
│  ┌────────────────────────────────────────────────────────────────┐ │
│  │              Flutter Web Application                           │ │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────────┐    │ │
│  │  │   Home       │  │   Settings   │  │  WebSocket       │    │ │
│  │  │   Screen     │  │   Screen     │  │  Provider        │    │ │
│  │  └──────────────┘  └──────────────┘  └──────────────────┘    │ │
│  │         │                  │                   │               │ │
│  │         └──────────────────┴───────────────────┘               │ │
│  │                            │                                   │ │
│  │                  ┌─────────▼──────────┐                       │ │
│  │                  │  Settings Provider │                       │ │
│  │                  │  (Local Storage)   │                       │ │
│  │                  └────────────────────┘                       │ │
│  └────────────────────────────────────────────────────────────────┘ │
│                            │                                         │
│                   HTTP/WebSocket                                     │
└────────────────────────────┼─────────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    Nginx Reverse Proxy (Port 80/443)                │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  /app/    →  Static Files (/var/www/rldc_app_web/)                 │
│               - Flutter Web Build                                   │
│               - HTML, JS, CSS, Assets                               │
│                                                                      │
│  /api/    →  FastAPI Backend (127.0.0.1:8000)                      │
│               - REST API Endpoints                                  │
│               - Health, Status, Markets, Trades                     │
│                                                                      │
│  /ws      →  FastAPI WebSocket (127.0.0.1:8000/ws)                 │
│               - Real-time Updates                                   │
│               - Bidirectional Communication                         │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    FastAPI Backend (Port 8000)                       │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  ┌────────────────┐  ┌─────────────────┐  ┌──────────────────┐    │
│  │  REST Routes   │  │  WebSocket      │  │  Connection      │    │
│  │                │  │  Handler        │  │  Manager         │    │
│  │  /health       │  │                 │  │                  │    │
│  │  /status       │  │  - Accept       │  │  - Track clients │    │
│  │  /api/markets  │  │  - Send updates │  │  - Broadcast     │    │
│  │  /api/trades   │  │  - Echo msgs    │  │  - Disconnect    │    │
│  └────────────────┘  └─────────────────┘  └──────────────────┘    │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

## Component Details

### 1. Flutter Web Application

**Technology Stack:**
- Flutter SDK 3.0+
- Dart
- Material Design 3

**Key Components:**

#### Screens
- **HomeScreen**: Main dashboard with WebSocket connection status, message history, and send functionality
- **SettingsScreen**: Gateway URL configuration with form validation and local storage

#### Providers (State Management)
- **SettingsProvider**: Manages REST and WebSocket gateway URLs using SharedPreferences
- **WebSocketProvider**: Handles WebSocket connection, message sending/receiving, and state updates

#### Services
- **HTTP Client**: REST API communication
- **WebSocket Channel**: Real-time bidirectional communication
- **Local Storage**: Browser-based settings persistence

**Features:**
- Real-time WebSocket connection monitoring
- Configurable gateway URLs
- Message history (last 100 messages)
- Echo message testing
- Update counter display
- Material Design 3 UI
- Responsive layout

### 2. FastAPI Backend

**Technology Stack:**
- Python 3.8+
- FastAPI framework
- Uvicorn ASGI server
- WebSockets library

**Endpoints:**

#### REST API
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | API information and version |
| `/health` | GET | Health check with connection count |
| `/status` | GET | Trading bot status |
| `/api/markets` | GET | Market data (BTC, ETH, BNB) |
| `/api/trades` | GET | Recent trades |
| `/api/broadcast` | POST | Broadcast to all WS clients |

#### WebSocket
| Endpoint | Protocol | Description |
|----------|----------|-------------|
| `/ws` | WebSocket | Real-time bidirectional communication |

**Message Types:**
- `connection`: Initial connection confirmation
- `update`: Periodic status updates (every 5 seconds)
- `echo`: Echo back client messages

**Features:**
- CORS enabled for cross-origin requests
- Connection manager for WebSocket clients
- Automatic cleanup of disconnected clients
- JSON message format
- Error handling and logging

### 3. Nginx Reverse Proxy

**Configuration:**
- Routes `/app/` to static Flutter Web files
- Routes `/api/` to FastAPI REST endpoints
- Routes `/ws` to FastAPI WebSocket endpoint
- Proper headers for WebSocket upgrade
- Cache control for static assets
- SSL/TLS termination (when configured)

**Features:**
- HTTP to HTTPS redirect (optional)
- WebSocket proxy with timeout settings
- Static file caching
- Gzip compression
- Security headers

### 4. Deployment Components

**Systemd Service:**
- Auto-start on boot
- Automatic restart on failure
- Logging to system journal
- Security restrictions (PrivateTmp, ProtectSystem)

**Build Scripts:**
- `build_flutter_web.sh`: Builds Flutter app with base-href
- `test_deployment.sh`: Comprehensive deployment testing

**Tools:**
- `rldc_terminal.py`: WebSocket testing and debugging

## Data Flow

### 1. Initial Page Load

```
Browser → Nginx → Static Files → Flutter App
                                    ↓
                            Load Settings from
                            Local Storage
```

### 2. REST API Request

```
Flutter App → HTTP Request → Nginx (/api/) → FastAPI → Response
                                                ↓
                                         Process Data
                                                ↓
                                         JSON Response
```

### 3. WebSocket Connection

```
Flutter App → WS Connect → Nginx (/ws) → FastAPI
                                            ↓
                                    Accept Connection
                                            ↓
                                    Add to Manager
                                            ↓
                                    Send Confirmation
                                            ↓
                              ┌─────────────┴──────────────┐
                              ↓                            ↓
                    Periodic Updates              Client Messages
                    (every 5 sec)                        ↓
                              ↓                      Echo Back
                        All Clients
```

### 4. Settings Update

```
Settings Screen → Update Form → Validate
                                    ↓
                             Save to Local Storage
                                    ↓
                          Update Providers
                                    ↓
                          Notify Listeners
                                    ↓
                             Update UI
```

## Security Architecture

### Transport Security
- HTTPS/TLS for all HTTP traffic
- WSS (WebSocket Secure) for WebSocket connections
- TLS 1.2+ only
- Strong cipher suites

### Application Security
- CORS configuration
- Input validation
- No credentials in client-side code
- Secure headers (HSTS, CSP, etc.)
- XSS protection

### Network Security
- Firewall rules (UFW)
- Rate limiting (Nginx)
- DDoS protection
- Intrusion detection

## Scalability Considerations

### Horizontal Scaling
- Multiple FastAPI workers (--workers flag)
- Load balancer in front of Nginx
- Redis for shared WebSocket state
- Database for persistent data

### Vertical Scaling
- Increase FastAPI workers
- Optimize WebSocket message handling
- Database query optimization
- CDN for static assets

### Performance Optimization
- Static file caching (1 year for assets)
- Gzip compression
- Code splitting in Flutter
- Lazy loading
- Connection pooling

## Monitoring and Observability

### Logs
- FastAPI: `/var/log/rldc-api.log`
- Nginx: `/var/log/nginx/access.log`, `/var/log/nginx/error.log`
- Systemd: `journalctl -u rldc-api`

### Metrics
- WebSocket connection count
- API response times
- Error rates
- Resource usage (CPU, memory)

### Health Checks
- `/health` endpoint for API
- Nginx status endpoint
- Systemd service status

## Development Workflow

```
1. Code Changes
   ↓
2. Local Testing (Flutter run, Python uvicorn)
   ↓
3. Build Flutter Web (flutter build web)
   ↓
4. Deploy to Staging
   ↓
5. Run Tests (test_deployment.sh)
   ↓
6. Deploy to Production
   ↓
7. Monitor Logs
```

## File Structure

```
RLdC-Trading-bot/
├── api/
│   ├── __init__.py
│   └── main.py                 # FastAPI application
├── flutter_app/
│   ├── lib/
│   │   ├── main.dart           # App entry point
│   │   ├── providers/          # State management
│   │   └── screens/            # UI screens
│   ├── web/
│   │   ├── index.html          # HTML template
│   │   └── manifest.json       # PWA manifest
│   ├── pubspec.yaml            # Dependencies
│   └── build/web/              # Build output
├── nginx/
│   └── rldc_app.conf           # Nginx configuration
├── systemd/
│   └── rldc-api.service        # Systemd service
├── tools/
│   └── rldc_terminal.py        # WebSocket testing
├── scripts/
│   ├── build_flutter_web.sh    # Build script
│   └── test_deployment.sh      # Test script
└── docs/
    ├── DEPLOYMENT.md           # Deployment guide
    ├── QUICKSTART.md           # Quick start
    └── TESTING.md              # Testing guide
```

## Technology Stack Summary

| Component | Technology | Version |
|-----------|-----------|---------|
| Frontend | Flutter Web | 3.0+ |
| Language | Dart | 3.0+ |
| Backend | FastAPI | Latest |
| Server | Uvicorn | Latest |
| Web Server | Nginx | 1.18+ |
| Protocol | HTTP/2, WebSocket | - |
| Security | TLS 1.2/1.3 | - |
| Service Manager | systemd | - |

## Future Enhancements

- [ ] Authentication and authorization
- [ ] Database integration
- [ ] Real trading data integration
- [ ] Advanced charting
- [ ] Mobile app support
- [ ] Push notifications
- [ ] Redis for caching
- [ ] Docker containerization
- [ ] Kubernetes orchestration
- [ ] CI/CD pipeline
