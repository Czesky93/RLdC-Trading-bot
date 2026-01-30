#!/bin/bash
# Build script for Flutter Web application
# This script builds the Flutter Web app and copies it to the deployment directory

set -e

echo "🚀 Building Flutter Web Application..."

# Navigate to the Flutter app directory
cd "$(dirname "$0")/../flutter_app"

# Check if Flutter is installed
if ! command -v flutter &> /dev/null; then
    echo "❌ Flutter is not installed. Please install Flutter first."
    echo "Visit: https://docs.flutter.dev/get-started/install"
    exit 1
fi

# Get dependencies
echo "📦 Installing dependencies..."
flutter pub get

# Build for web with release mode and base-href
echo "🔨 Building for web (release mode)..."
flutter build web --release --base-href /app/

# Check if build was successful
if [ ! -d "build/web" ]; then
    echo "❌ Build failed - build/web directory not found"
    exit 1
fi

echo "✅ Build completed successfully!"
echo ""
echo "📁 Build output location: $(pwd)/build/web"
echo ""
echo "📋 Deployment Instructions:"
echo "1. Copy the build output to the server:"
echo "   sudo cp -r $(pwd)/build/web/* /var/www/rldc_app_web/"
echo ""
echo "2. Set proper permissions:"
echo "   sudo chown -R www-data:www-data /var/www/rldc_app_web/"
echo "   sudo chmod -R 755 /var/www/rldc_app_web/"
echo ""
echo "3. Ensure Nginx is configured and reload:"
echo "   sudo nginx -t"
echo "   sudo systemctl reload nginx"
echo ""
echo "4. Access the app at: https://twojadomena.pl/app/"
