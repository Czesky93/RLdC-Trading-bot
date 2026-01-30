#!/bin/bash
# Test script for RLdC Trading Bot deployment
# Tests REST API, WebSocket, and web frontend

set -e

echo "=========================================="
echo "RLdC Trading Bot - Deployment Tests"
echo "=========================================="
echo ""

# Configuration
API_HOST="${API_HOST:-127.0.0.1}"
API_PORT="${API_PORT:-8000}"
DOMAIN="${DOMAIN:-localhost}"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Test counter
PASSED=0
FAILED=0

# Helper functions
test_passed() {
    echo -e "${GREEN}✓ PASSED${NC}: $1"
    ((PASSED++))
}

test_failed() {
    echo -e "${RED}✗ FAILED${NC}: $1"
    ((FAILED++))
}

test_warning() {
    echo -e "${YELLOW}⚠ WARNING${NC}: $1"
}

# Test 1: Check if FastAPI is running
echo "Test 1: Checking if FastAPI is running..."
if curl -s -f http://${API_HOST}:${API_PORT}/health > /dev/null 2>&1; then
    test_passed "FastAPI is running on http://${API_HOST}:${API_PORT}"
else
    test_failed "FastAPI is not running on http://${API_HOST}:${API_PORT}"
    test_warning "Start FastAPI with: python -m uvicorn api.main:app --host 0.0.0.0 --port 8000"
fi

# Test 2: REST API Health Check
echo ""
echo "Test 2: Testing REST API health endpoint..."
HEALTH_RESPONSE=$(curl -s http://${API_HOST}:${API_PORT}/health)
if echo "$HEALTH_RESPONSE" | grep -q "healthy"; then
    test_passed "Health endpoint returned: $HEALTH_RESPONSE"
else
    test_failed "Health endpoint did not return expected response"
    echo "Response: $HEALTH_RESPONSE"
fi

# Test 3: REST API Root Endpoint
echo ""
echo "Test 3: Testing REST API root endpoint..."
ROOT_RESPONSE=$(curl -s http://${API_HOST}:${API_PORT}/)
if echo "$ROOT_RESPONSE" | grep -q "RLdC Trading Bot API"; then
    test_passed "Root endpoint returned correct response"
else
    test_failed "Root endpoint did not return expected response"
fi

# Test 4: REST API Status Endpoint
echo ""
echo "Test 4: Testing REST API status endpoint..."
STATUS_RESPONSE=$(curl -s http://${API_HOST}:${API_PORT}/status)
if echo "$STATUS_RESPONSE" | grep -q "bot_status"; then
    test_passed "Status endpoint returned: $STATUS_RESPONSE"
else
    test_failed "Status endpoint did not return expected response"
fi

# Test 5: Check if Python WebSocket client is available
echo ""
echo "Test 5: Checking Python WebSocket dependencies..."
if python3 -c "import websockets" 2>/dev/null; then
    test_passed "websockets module is installed"
else
    test_failed "websockets module is not installed"
    test_warning "Install with: pip install websockets"
fi

# Test 6: Check if Nginx is installed
echo ""
echo "Test 6: Checking Nginx installation..."
if command -v nginx &> /dev/null; then
    NGINX_VERSION=$(nginx -v 2>&1)
    test_passed "Nginx is installed: $NGINX_VERSION"
else
    test_warning "Nginx is not installed (required for production deployment)"
    echo "Install with: sudo apt install nginx"
fi

# Test 7: Check if Flutter Web build directory exists
echo ""
echo "Test 7: Checking Flutter Web build..."
if [ -d "flutter_app/build/web" ]; then
    test_passed "Flutter Web build directory exists"
    echo "   Files: $(ls -1 flutter_app/build/web | wc -l) files found"
else
    test_warning "Flutter Web build not found"
    echo "Build with: cd flutter_app && flutter build web --release --base-href /app/"
fi

# Test 8: Check deployment directory (if running with sudo/permissions)
echo ""
echo "Test 8: Checking deployment directory..."
if [ -d "/var/www/rldc_app_web" ]; then
    test_passed "Deployment directory /var/www/rldc_app_web exists"
    FILE_COUNT=$(sudo ls -1 /var/www/rldc_app_web 2>/dev/null | wc -l || echo "0")
    echo "   Files deployed: $FILE_COUNT"
else
    test_warning "Deployment directory /var/www/rldc_app_web does not exist"
    echo "Create with: sudo mkdir -p /var/www/rldc_app_web"
fi

# Test 9: Check Nginx configuration
echo ""
echo "Test 9: Checking Nginx configuration..."
if [ -f "/etc/nginx/sites-available/rldc_app" ]; then
    test_passed "Nginx configuration file exists"
    if [ -L "/etc/nginx/sites-enabled/rldc_app" ]; then
        test_passed "Nginx configuration is enabled"
    else
        test_warning "Nginx configuration is not enabled"
        echo "Enable with: sudo ln -s /etc/nginx/sites-available/rldc_app /etc/nginx/sites-enabled/"
    fi
else
    test_warning "Nginx configuration file not found at /etc/nginx/sites-available/rldc_app"
fi

# Test 10: Test Nginx proxy to API (if Nginx is running)
echo ""
echo "Test 10: Testing Nginx proxy to API..."
if curl -s -f http://${DOMAIN}/api/health > /dev/null 2>&1; then
    test_passed "Nginx proxy to API is working"
else
    test_warning "Nginx proxy to API not accessible (may not be configured yet)"
    echo "URL tested: http://${DOMAIN}/api/health"
fi

# Test 11: Test Flutter Web access through Nginx
echo ""
echo "Test 11: Testing Flutter Web through Nginx..."
if curl -s -f http://${DOMAIN}/app/ > /dev/null 2>&1; then
    test_passed "Flutter Web is accessible through Nginx"
else
    test_warning "Flutter Web not accessible through Nginx"
    echo "URL tested: http://${DOMAIN}/app/"
fi

# Test 12: Check if terminal tool exists
echo ""
echo "Test 12: Checking WebSocket terminal tool..."
if [ -f "tools/rldc_terminal.py" ]; then
    test_passed "WebSocket terminal tool found"
    echo "   Test with: python tools/rldc_terminal.py ws://${API_HOST}:${API_PORT}/ws"
else
    test_failed "WebSocket terminal tool not found"
fi

# Summary
echo ""
echo "=========================================="
echo "Test Summary"
echo "=========================================="
echo -e "${GREEN}Passed: $PASSED${NC}"
echo -e "${RED}Failed: $FAILED${NC}"
echo ""

if [ $FAILED -eq 0 ]; then
    echo -e "${GREEN}All critical tests passed!${NC}"
    exit 0
else
    echo -e "${YELLOW}Some tests failed. Please review the output above.${NC}"
    exit 1
fi
