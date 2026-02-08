# 🚀 Quick Start Guide - Medical Report Analyzer

5 minutes में अपना chatbot setup करें!

## ⚡ Step-by-Step Setup (Hindi)

### 1️⃣ Download & Extract
```bash
# Project folder में जाएं
cd medical-report-analyzer
```

### 2️⃣ Setup Script चलाएं (Automatic)
```bash
# Linux/macOS
chmod +x setup.sh
./setup.sh

# Windows (Git Bash में)
bash setup.sh
```

### 3️⃣ API Keys प्राप्त करें

#### Groq API Key (FREE) - 2 minutes
1. Open: https://console.groq.com
2. Sign up with Google/Email
3. Dashboard > API Keys > Create API Key
4. Copy key

#### Google OAuth (FREE) - 5 minutes
1. Open: https://console.cloud.google.com
2. Create New Project
3. APIs & Services > Credentials > Create Credentials > OAuth 2.0 Client ID
4. Application type: Web application
5. Authorized redirect URIs:
   ```
   http://localhost:5000/login/google/authorize
   ```
6. Copy Client ID और Secret

#### Razorpay (FREE Test Mode) - 3 minutes
1. Open: https://razorpay.com
2. Sign up
3. Switch to Test Mode (top left)
4. Settings > API Keys > Generate Test Keys
5. Copy Key ID और Secret

### 4️⃣ .env File Update करें
```bash
# .env file खोलें और update करें:
nano .env
# या
code .env
```

Minimal required:
```env
MONGO_URI=mongodb://localhost:27017/
GROQ_API_KEY=gsk_...  # आपकी Groq key
SECRET_KEY=random-secret-key-123  # कोई भी random string
GOOGLE_CLIENT_ID=your-id.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=your-secret
RAZORPAY_KEY_ID=rzp_test_...
RAZORPAY_KEY_SECRET=your-secret
```

### 5️⃣ Virtual Environment Activate करें
```bash
# Linux/macOS
source venv/bin/activate

# Windows (Command Prompt)
venv\Scripts\activate

# Windows (PowerShell)
venv\Scripts\Activate.ps1
```

### 6️⃣ Application चलाएं
```bash
python app.py
```

### 7️⃣ Browser में खोलें
```
http://localhost:5000
```

## ✅ Testing Checklist

- [ ] Login page दिख रहा है?
- [ ] Google login काम कर रहा है?
- [ ] Dashboard load हो रहा है?
- [ ] File upload हो रहा है?
- [ ] Chat response मिल रहा है?
- [ ] Subscription modal खुल रहा है?

## 🐛 Common Issues

### ❌ MongoDB Connection Error
```bash
# MongoDB start करें
sudo systemctl start mongod

# या MongoDB Atlas use करें और MONGO_URI update करें
```

### ❌ Tesseract not found
```bash
# Ubuntu/Debian
sudo apt-get install tesseract-ocr

# macOS
brew install tesseract
```

### ❌ Google Login fails
- Redirect URI check करें (exact match होना चाहिए)
- OAuth consent screen configure करें

### ❌ Port 5000 already in use
```bash
# Port बदलें app.py में:
app.run(debug=True, host='0.0.0.0', port=8080)
```

## 🎯 Test Payment

Test mode में payment test करने के लिए:

**Test Card Details:**
```
Card Number: 4111 1111 1111 1111
CVV: Any 3 digits
Expiry: Any future date
```

## 📱 Features to Test

1. **Upload Report**
   - PDF upload
   - Image upload
   - Text extraction

2. **Chat**
   - Ask questions in Hindi
   - Ask questions in English
   - Check question counter

3. **Chat Management**
   - Create new chat
   - Switch between chats
   - Delete chat

4. **Subscription**
   - Open subscription modal
   - Test payment flow
   - Check plan upgrade

## 🔧 Development Tips

### Run in Debug Mode
```bash
# Auto-reload on code changes
export FLASK_DEBUG=1
python app.py
```

### Check MongoDB Data
```bash
mongo
use medical_assistant
db.users.find().pretty()
db.chats.find().limit(5).pretty()
```

### Clear Test Data
```bash
mongo
use medical_assistant
db.users.deleteMany({})
db.chats.deleteMany({})
db.reports.deleteMany({})
```

## 📚 Additional Resources

- **Detailed Guide:** README.md
- **Groq Documentation:** https://console.groq.com/docs
- **MongoDB Tutorial:** https://docs.mongodb.com/manual/tutorial/
- **Flask Documentation:** https://flask.palletsprojects.com/

## 🎉 Success!

Agar sab kuch काम कर रहा है, तो आप ready हैं! 

Questions? Contact:
- **Email:** prakasbokarvadiya0@gmail.com
- **LinkedIn:** https://www.linkedin.com/in/prakash-bokarvadiya-609001369

---

**Happy Coding! 🚀**
