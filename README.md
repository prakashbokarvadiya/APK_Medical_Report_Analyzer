# 🏥 Medical Report Analyzer - Full Stack Application

एक complete medical report analyzer chatbot जो AI-powered है और user authentication, subscription management, और chat history के साथ आता है।

## ✨ Features

### 🔐 User Authentication
- Google OAuth login integration
- Session-based authentication
- Secure user data management

### 💬 Chat System
- Unlimited chat sessions
- Chat history sidebar
- Delete individual chats
- Real-time messaging
- Typing indicators

### 📊 Subscription Plans
1. **Free Plan** (₹0)
   - 15 questions per chat
   - Unlimited chats
   - Basic support

2. **Basic Plan** (₹49/month)
   - 30 questions per chat
   - Unlimited chats
   - Priority support

3. **Unlimited Plan** (₹100/month)
   - Unlimited questions
   - Unlimited chats
   - 24/7 Premium support

### 💳 Payment Integration
- Razorpay payment gateway
- Secure payment processing
- Automatic subscription activation

### 📱 Responsive Design
- Mobile-friendly interface
- Sidebar navigation
- Touch-optimized controls

### 🗄️ Data Management
- User profiles with MongoDB
- Chat history storage
- Report text extraction and storage
- Subscription tracking

## 🚀 Installation Guide

### Step 1: System Requirements

**Ubuntu/Debian:**
```bash
sudo apt-get update
sudo apt-get install -y tesseract-ocr tesseract-ocr-hin python3-pip mongodb
```

**macOS:**
```bash
brew install tesseract tesseract-lang mongodb-community
brew services start mongodb-community
```

**Windows:**
1. Install Tesseract: https://github.com/UB-Mannheim/tesseract/wiki
2. Install MongoDB: https://www.mongodb.com/try/download/community
3. Install Python 3.8+: https://www.python.org/downloads/

### Step 2: Clone/Download Project

```bash
# If using git
git clone <your-repo-url>
cd medical-report-analyzer

# Or extract the zip file
unzip medical-report-analyzer.zip
cd medical-report-analyzer
```

### Step 3: Create Virtual Environment

```bash
# Create virtual environment
python -m venv venv

# Activate it
# On Linux/macOS:
source venv/bin/activate

# On Windows:
venv\Scripts\activate
```

### Step 4: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 5: Setup MongoDB

**Option 1: Local MongoDB (Recommended for Development)**
```bash
# Start MongoDB service
# Ubuntu/Debian:
sudo systemctl start mongod
sudo systemctl enable mongod

# macOS:
brew services start mongodb-community

# Windows: MongoDB should start automatically after installation
```

**Option 2: MongoDB Atlas (Cloud - Free)**
1. जाएं: https://www.mongodb.com/cloud/atlas
2. Free account बनाएं
3. Create a free cluster
4. Get connection string
5. `.env` file में `MONGO_URI` update करें

### Step 6: Setup Environment Variables

`.env` file create करें project root में:

```bash
# MongoDB (Local)
MONGO_URI=mongodb://localhost:27017/

# MongoDB Atlas (Cloud) - अगर Atlas use कर रहे हैं
# MONGO_URI=mongodb+srv://username:password@cluster.mongodb.net/medical_assistant?retryWrites=true&w=majority

# Groq AI API Key
GROQ_API_KEY=your-groq-api-key-here

# Flask Secret Key (random string generate करें)
SECRET_KEY=your-super-secret-random-key-here

# Google OAuth Configuration
GOOGLE_CLIENT_ID=your-google-client-id.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=your-google-client-secret

# Razorpay Payment Gateway
RAZORPAY_KEY_ID=your-razorpay-key-id
RAZORPAY_KEY_SECRET=your-razorpay-key-secret

# Application URL
APP_URL=http://localhost:5000
```

### Step 7: Get API Keys

#### 7.1 Groq API Key (FREE)
1. जाएं: https://console.groq.com
2. Sign up करें
3. API Keys section में जाएं
4. Create new API key
5. Copy करके `.env` में paste करें

#### 7.2 Google OAuth Setup (FREE)
1. जाएं: https://console.cloud.google.com
2. New Project बनाएं
3. "APIs & Services" > "Credentials" में जाएं
4. "Create Credentials" > "OAuth 2.0 Client ID"
5. Application type: "Web application"
6. Authorized redirect URIs add करें:
   ```
   http://localhost:5000/login/google/authorize
   ```
7. Client ID और Client Secret copy करके `.env` में paste करें

#### 7.3 Razorpay Setup (FREE for Testing)
1. जाएं: https://razorpay.com
2. Sign up करें
3. Test mode में switch करें
4. Settings > API Keys
5. Generate Test Keys
6. Key ID और Key Secret copy करके `.env` में paste करें

**Note:** Production के लिए Live keys use करें और KYC complete करें।

### Step 8: Create Required Directories

```bash
mkdir uploads
mkdir templates
```

### Step 9: Run the Application

```bash
python app.py
```

Server start हो जाएगा: `http://localhost:5000`

## 📖 Usage Guide

### First Time Setup
1. Browser में `http://localhost:5000` खोलें
2. "Continue with Google" पर click करें
3. Google account से login करें
4. Free plan के साथ automatically start हो जाएगा

### Upload Report & Chat
1. Main dashboard में "Upload Report" button click करें
2. Medical report (PDF/Image) select करें
3. Report analyze होने के बाद questions पूछें
4. Hindi या English में पूछ सकते हैं

### Manage Chats
- **New Chat:** Sidebar में "+ New" button
- **Switch Chat:** Sidebar में किसी भी chat पर click करें
- **Delete Chat:** Chat पर hover करके 🗑️ icon click करें

### Upgrade Subscription
1. Sidebar में "⭐ Upgrade Plan" click करें
2. अपनी पसंद का plan select करें
3. Razorpay payment gateway से pay करें
4. Subscription automatically activate हो जाएगा

## 🗃️ Database Schema

### Users Collection
```javascript
{
  _id: ObjectId,
  email: String,
  name: String,
  picture: String (URL),
  subscription_plan: String ('free', 'basic', 'unlimited'),
  subscription_expires: Date,
  created_at: Date,
  last_active: Date
}
```

### Chats Collection
```javascript
{
  _id: ObjectId,
  user_id: String,
  chat_id: String,
  role: String ('user', 'assistant', 'system'),
  content: String,
  timestamp: Date,
  report_id: String (optional)
}
```

### Reports Collection
```javascript
{
  _id: ObjectId,
  user_id: String,
  filename: String,
  extracted_text: String,
  uploaded_at: Date
}
```

### Subscriptions Collection
```javascript
{
  _id: ObjectId,
  user_id: String,
  plan: String,
  payment_id: String,
  order_id: String,
  amount: Number,
  activated_at: Date,
  expires_at: Date
}
```

## 🔧 Configuration

### Change Port
`app.py` के last line में:
```python
app.run(debug=True, host='0.0.0.0', port=8080)  # Port change करें
```

### Update Plans
`app.py` में `PLANS` dictionary edit करें:
```python
PLANS = {
    'free': {
        'name': 'Free Plan',
        'questions_per_chat': 15,
        'price': 0
    },
    # ... add/modify plans
}
```

### File Upload Limits
`app.py` में:
```python
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB
```

## 🛠️ Troubleshooting

### Problem: MongoDB Connection Error
**Solution:**
```bash
# Check if MongoDB is running
sudo systemctl status mongod

# Start MongoDB
sudo systemctl start mongod

# Or use MongoDB Atlas and update MONGO_URI in .env
```

### Problem: Google Login Not Working
**Solution:**
1. Check `GOOGLE_CLIENT_ID` and `GOOGLE_CLIENT_SECRET` in `.env`
2. Verify redirect URI in Google Console matches exactly
3. Make sure OAuth consent screen is configured

### Problem: Payment Not Working
**Solution:**
1. Check Razorpay keys are in Test mode
2. Use test card: 4111 1111 1111 1111
3. Verify webhook signatures if using live mode

### Problem: Tesseract Not Found
**Solution:**
```bash
# Ubuntu/Debian
sudo apt-get install tesseract-ocr

# macOS
brew install tesseract

# Windows: Add Tesseract to PATH
```

### Problem: Port Already in Use
**Solution:**
```bash
# Find process using port 5000
sudo lsof -i :5000

# Kill the process
sudo kill -9 <PID>

# Or change port in app.py
```

## 📁 Project Structure

```
medical-report-analyzer/
│
├── app.py                 # Main Flask application
├── fun.py                 # Utility functions (token counting)
├── requirements.txt       # Python dependencies
├── .env                   # Environment variables (create this)
├── .gitignore            # Git ignore rules
├── README.md             # This file
│
├── templates/
│   ├── index.html        # Main chat interface
│   └── login.html        # Login page
│
└── uploads/              # Temporary file storage (auto-created)
```

## 🔒 Security Notes

1. **Never commit `.env` file** to Git
2. Use **strong SECRET_KEY** in production
3. Enable **HTTPS** in production
4. Use **MongoDB authentication** in production
5. Switch to **Razorpay Live keys** after KYC
6. Implement **rate limiting** for API endpoints
7. Add **CORS whitelist** in production

## 🚀 Production Deployment

### Using Gunicorn (Recommended)
```bash
# Install gunicorn
pip install gunicorn

# Run application
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

### Using Docker
```dockerfile
# Dockerfile example
FROM python:3.9
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "app:app"]
```

### Environment Variables for Production
```bash
# Set these in your hosting platform
MONGO_URI=mongodb+srv://...  # MongoDB Atlas
GROQ_API_KEY=...
SECRET_KEY=...  # Strong random string
GOOGLE_CLIENT_ID=...
GOOGLE_CLIENT_SECRET=...
RAZORPAY_KEY_ID=...  # Live key
RAZORPAY_KEY_SECRET=...  # Live secret
APP_URL=https://yourdomain.com
```

## 📊 Monitoring & Analytics

### Add Basic Analytics
```python
# In app.py, add after each route
from datetime import datetime
analytics_collection.insert_one({
    'event': 'chat_message',
    'user_id': current_user.id,
    'timestamp': datetime.utcnow()
})
```

### Monitor Database
```bash
# MongoDB shell
mongo
use medical_assistant
db.users.count()
db.chats.count()
db.subscriptions.find().pretty()
```

## 🤝 Support

Issues या questions के लिए:
- **Email:** prakasbokarvadiya0@gmail.com
- **LinkedIn:** https://www.linkedin.com/in/prakash-bokarvadiya-609001369

## 📄 License

This project is for educational and personal use. Free to use and modify.

## 🙏 Credits

- **Developer:** Prakash Bokarvadiya
- **AI Model:** MRA 1.5.0 
- **Authentication:** Google OAuth
- **Payments:** Razorpay
- **Database:** MongoDB

---

**Made with ❤️ for better health awareness**

Happy Coding! 🚀
