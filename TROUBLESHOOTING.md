# 🔧 Troubleshooting Guide - Common Errors & Solutions

## 🐛 Error: "Client.__init__() got an unexpected keyword argument 'proxies'"

### Problem:
OAuth client initialization error with authlib library.

### Solution 1: Update authlib version
```bash
pip uninstall authlib
pip install authlib==1.2.1
```

### Solution 2: Clear Python cache
```bash
# Delete all __pycache__ directories
find . -type d -name "__pycache__" -exec rm -r {} +

# Delete .pyc files
find . -type f -name "*.pyc" -delete

# Restart application
python app.py
```

### Solution 3: Reinstall dependencies
```bash
# Activate virtual environment
source venv/bin/activate  # Linux/macOS
# OR
venv\Scripts\activate  # Windows

# Reinstall all dependencies
pip install --upgrade --force-reinstall -r requirements.txt

# Restart application
python app.py
```

---

## 🐛 Error: "GROQ_API_KEY environment variable not set"

### Solution:
```bash
# Check if .env file exists
ls -la .env

# If not, create it
cp .env.example .env

# Edit and add your Groq API key
nano .env  # or use any text editor

# Add this line:
GROQ_API_KEY=your-actual-groq-api-key-here

# Restart application
python app.py
```

---

## 🐛 Error: "MongoDB connection refused"

### Solution 1: Start MongoDB service
```bash
# Ubuntu/Debian
sudo systemctl start mongod
sudo systemctl status mongod

# macOS
brew services start mongodb-community

# Windows
# Start MongoDB from Services
```

### Solution 2: Use MongoDB Atlas (Cloud)
```bash
# In .env file, update MONGO_URI:
MONGO_URI=mongodb+srv://username:password@cluster.mongodb.net/medical_assistant?retryWrites=true&w=majority

# Get connection string from MongoDB Atlas dashboard
```

### Solution 3: Check MongoDB is installed
```bash
# Check if MongoDB is installed
mongod --version

# If not installed:
# Ubuntu/Debian
sudo apt-get install -y mongodb

# macOS
brew install mongodb-community

# Windows: Download from https://www.mongodb.com/try/download/community
```

---

## 🐛 Error: "pytesseract.pytesseract.TesseractNotFoundError"

### Solution:
```bash
# Ubuntu/Debian
sudo apt-get update
sudo apt-get install tesseract-ocr tesseract-ocr-hin

# macOS
brew install tesseract tesseract-lang

# Windows
# 1. Download Tesseract: https://github.com/UB-Mannheim/tesseract/wiki
# 2. Install it
# 3. Add to PATH environment variable
# 4. Or specify path in code:
```

In `app.py`, add after imports:
```python
import pytesseract
# For Windows, uncomment and update path:
# pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
```

---

## 🐛 Error: "Google OAuth redirect URI mismatch"

### Solution:
```bash
# 1. Go to Google Cloud Console: https://console.cloud.google.com
# 2. Select your project
# 3. Go to "APIs & Services" > "Credentials"
# 4. Click on your OAuth 2.0 Client ID
# 5. Under "Authorized redirect URIs", add EXACT URL:
#    http://localhost:5000/login/google/authorize
#    
# 6. Make sure there's no trailing slash
# 7. Save and wait 5 minutes for changes to propagate
```

---

## 🐛 Error: "Port 5000 already in use"

### Solution 1: Kill process using port 5000
```bash
# Linux/macOS
lsof -ti:5000 | xargs kill -9

# Windows
netstat -ano | findstr :5000
taskkill /PID <PID> /F
```

### Solution 2: Change port
In `app.py`, change last line:
```python
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8080)  # Changed to 8080
```

Then access: `http://localhost:8080`

---

## 🐛 Error: "ModuleNotFoundError: No module named 'XXX'"

### Solution:
```bash
# Make sure virtual environment is activated
source venv/bin/activate  # Linux/macOS
# OR
venv\Scripts\activate  # Windows

# Install missing module
pip install <module-name>

# Or reinstall all dependencies
pip install -r requirements.txt
```

---

## 🐛 Error: "Secret key must be set"

### Solution:
```bash
# In .env file, add:
SECRET_KEY=$(python -c "import secrets; print(secrets.token_hex(32))")

# Or manually set any random string (minimum 32 characters):
SECRET_KEY=your-super-secret-random-key-change-this-to-something-secure
```

---

## 🐛 Error: "Razorpay payment fails"

### Solution 1: Check if in Test Mode
```bash
# In Razorpay Dashboard:
# 1. Make sure you're in TEST mode (top-left toggle)
# 2. Use test keys (start with rzp_test_)
# 3. Use test card: 4111 1111 1111 1111
```

### Solution 2: Verify keys in .env
```bash
# Make sure these are set:
RAZORPAY_KEY_ID=rzp_test_xxxxx
RAZORPAY_KEY_SECRET=your_secret_key
```

---

## 🐛 Error: "Chat messages not saving"

### Solution:
```bash
# Initialize database
python init_db.py

# Check MongoDB connection
mongo
use medical_assistant
db.chats.find().pretty()

# If empty, check if user is logged in
# Check if chat_id is being generated
# Check browser console for JavaScript errors
```

---

## 🐛 Error: "File upload fails"

### Solution 1: Check file size
```python
# Files must be < 16MB
# To increase limit, in app.py:
app.config['MAX_CONTENT_LENGTH'] = 32 * 1024 * 1024  # 32MB
```

### Solution 2: Check uploads directory
```bash
# Create uploads directory if missing
mkdir uploads
chmod 777 uploads  # Linux/macOS

# Make sure it's writable
ls -la uploads/
```

### Solution 3: Check file type
```bash
# Allowed extensions in app.py:
ALLOWED_EXTENSIONS = {'pdf', 'png', 'jpg', 'jpeg', 'gif', 'bmp', 'tiff'}
```

---

## 🐛 Error: "Session/Login not persisting"

### Solution:
```bash
# 1. Check browser cookies are enabled
# 2. Check SECRET_KEY is set in .env
# 3. Clear browser cache and cookies
# 4. Check Flask session configuration:
```

In `app.py`, add after SECRET_KEY:
```python
app.config['SESSION_COOKIE_SECURE'] = False  # True only for HTTPS
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
```

---

## 🐛 Error: "Groq API quota exceeded"

### Solution:
```bash
# Groq free tier has limits
# 1. Check your usage: https://console.groq.com
# 2. Wait for quota to reset (daily)
# 3. Or upgrade to paid plan
# 4. Or use multiple API keys (rotate)
```

---

## 🐛 Error: "Database index error"

### Solution:
```bash
# Drop and recreate indexes
mongo
use medical_assistant
db.users.dropIndexes()
db.chats.dropIndexes()
db.reports.dropIndexes()
db.subscriptions.dropIndexes()
exit

# Reinitialize database
python init_db.py
```

---

## 🐛 Error: "CORS error in browser"

### Solution:
In `app.py`, update CORS:
```python
CORS(app, 
     supports_credentials=True,
     origins=["http://localhost:5000", "http://127.0.0.1:5000"],
     allow_headers=["Content-Type", "Authorization"],
     methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"]
)
```

---

## 🐛 Error: "Question limit not working"

### Solution:
```bash
# Check subscription plan
mongo
use medical_assistant
db.users.find({email: "your-email@example.com"}).pretty()

# Update subscription manually if needed
db.users.updateOne(
  {email: "your-email@example.com"},
  {$set: {subscription_plan: "unlimited"}}
)
```

---

## 🐛 Error: "Chat history not loading"

### Solution:
```bash
# Check browser console for errors (F12)
# Check network tab for API call failures
# Verify MongoDB has chat data:

mongo
use medical_assistant
db.chats.find({user_id: "your-user-id"}).limit(5).pretty()

# If chats exist but don't show, check frontend JavaScript
# Open browser DevTools > Console for errors
```

---

## 🛠️ General Debugging Tips

### 1. Enable Debug Mode
```python
# In app.py
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
```

### 2. Check Logs
```bash
# Terminal where app is running shows all logs
# Add more logging in app.py:

import logging
logging.basicConfig(level=logging.DEBUG)
```

### 3. Browser DevTools
```
Press F12 in browser
- Console tab: See JavaScript errors
- Network tab: See API requests/responses
- Application tab: Check cookies/session
```

### 4. Test API Endpoints
```bash
# Use curl to test endpoints
curl -X GET http://localhost:5000/api/health

# Or use Postman for more complex requests
```

### 5. Check Environment Variables
```bash
# Print all environment variables (for debugging)
python -c "from dotenv import load_dotenv; import os; load_dotenv(); print(os.environ.get('GROQ_API_KEY'))"
```

### 6. Restart Everything
```bash
# Sometimes the simplest solution:
# 1. Stop Flask app (Ctrl+C)
# 2. Restart MongoDB
sudo systemctl restart mongod
# 3. Clear Python cache
find . -name "*.pyc" -delete
find . -type d -name "__pycache__" -exec rm -r {} +
# 4. Restart Flask app
python app.py
```

---

## 📞 Still Having Issues?

If none of these solutions work:

1. **Check the full error message** - Copy complete error from terminal
2. **Check browser console** - F12 > Console tab
3. **Verify all API keys** - GROQ, Google OAuth, Razorpay
4. **Test with fresh virtual environment**:
   ```bash
   deactivate
   rm -rf venv
   python -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   python app.py
   ```

5. **Contact Support:**
   - Email: prakasbokarvadiya0@gmail.com
   - LinkedIn: https://www.linkedin.com/in/prakash-bokarvadiya-609001369

---

**Remember:** Most errors are due to:
- Missing environment variables in `.env`
- MongoDB not running
- Virtual environment not activated
- Old Python cache files

**Pro Tip:** Always check terminal output and browser console (F12) for detailed error messages!
