#!/bin/bash

# Medical Report Analyzer - Setup Script
# This script automates the installation process

echo "🏥 Medical Report Analyzer - Setup Script"
echo "=========================================="
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.8 or higher."
    exit 1
fi

echo "✅ Python 3 found: $(python3 --version)"
echo ""

# Check if pip is installed
if ! command -v pip3 &> /dev/null; then
    echo "❌ pip3 is not installed. Please install pip3."
    exit 1
fi

echo "✅ pip3 found"
echo ""

# Check if MongoDB is installed or running
if command -v mongod &> /dev/null; then
    echo "✅ MongoDB found"
    
    # Try to start MongoDB
    if command -v systemctl &> /dev/null; then
        sudo systemctl start mongod 2>/dev/null || true
        echo "📊 MongoDB service started"
    fi
else
    echo "⚠️  MongoDB not found locally. You can:"
    echo "   1. Install MongoDB locally"
    echo "   2. Use MongoDB Atlas (cloud) - Update MONGO_URI in .env"
fi

echo ""

# Check if Tesseract is installed
if ! command -v tesseract &> /dev/null; then
    echo "⚠️  Tesseract OCR not found. Installing..."
    
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        sudo apt-get update
        sudo apt-get install -y tesseract-ocr tesseract-ocr-hin
        echo "✅ Tesseract installed"
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        brew install tesseract tesseract-lang
        echo "✅ Tesseract installed"
    else
        echo "❌ Please install Tesseract manually from:"
        echo "   https://github.com/UB-Mannheim/tesseract/wiki"
    fi
else
    echo "✅ Tesseract OCR found: $(tesseract --version | head -n1)"
fi

echo ""

# Create virtual environment
echo "📦 Creating virtual environment..."
python3 -m venv venv

if [ $? -eq 0 ]; then
    echo "✅ Virtual environment created"
else
    echo "❌ Failed to create virtual environment"
    exit 1
fi

echo ""

# Activate virtual environment and install dependencies
echo "📥 Installing Python dependencies..."

if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
    # Windows
    source venv/Scripts/activate
else
    # Linux/macOS
    source venv/bin/activate
fi

pip install --upgrade pip
pip install -r requirements.txt

if [ $? -eq 0 ]; then
    echo "✅ Dependencies installed successfully"
else
    echo "❌ Failed to install dependencies"
    exit 1
fi

echo ""

# Create necessary directories
echo "📁 Creating directories..."
mkdir -p uploads
mkdir -p templates

echo "✅ Directories created"
echo ""

# Check if .env file exists
if [ ! -f .env ]; then
    echo "⚠️  .env file not found. Creating template..."
    cat > .env << 'EOL'
# MongoDB Configuration
MONGO_URI=mongodb://localhost:27017/

# Groq AI API Key (Get from: https://console.groq.com)
GROQ_API_KEY=your-groq-api-key-here

# Flask Secret Key (Generate random string)
SECRET_KEY=change-this-to-random-secret-key

# Google OAuth Configuration (Get from: https://console.cloud.google.com)
GOOGLE_CLIENT_ID=your-google-client-id.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=your-google-client-secret

# Razorpay Payment Gateway (Get from: https://razorpay.com)
RAZORPAY_KEY_ID=your-razorpay-key-id
RAZORPAY_KEY_SECRET=your-razorpay-key-secret

# Application URL
APP_URL=http://localhost:5000
EOL
    echo "✅ .env template created. Please update it with your API keys."
else
    echo "✅ .env file exists"
fi

echo ""
echo "=========================================="
echo "✨ Setup Complete!"
echo "=========================================="
echo ""
echo "📝 Next Steps:"
echo ""
echo "1. Update .env file with your API keys:"
echo "   - Groq API Key: https://console.groq.com"
echo "   - Google OAuth: https://console.cloud.google.com"
echo "   - Razorpay Keys: https://razorpay.com"
echo ""
echo "2. Activate virtual environment:"
if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
    echo "   venv\\Scripts\\activate"
else
    echo "   source venv/bin/activate"
fi
echo ""
echo "3. Run the application:"
echo "   python app.py"
echo ""
echo "4. Open browser:"
echo "   http://localhost:5000"
echo ""
echo "📖 For detailed instructions, see README.md"
echo ""
