# 📁 Project Structure - Medical Report Analyzer

## Complete File Structure

```
medical-report-analyzer/
│
├── 📄 app.py                      # Main Flask application with all routes
├── 📄 fun.py                      # Utility functions (token counting)
├── 📄 init_db.py                  # Database initialization script
├── 📄 requirements.txt            # Python dependencies
├── 📄 .env.example                # Environment variables template
├── 📄 .gitignore                  # Git ignore rules
├── 📄 setup.sh                    # Automated setup script (Linux/macOS)
│
├── 📖 README.md                   # Comprehensive documentation
├── 📖 QUICKSTART.md               # Quick start guide
├── 📖 PROJECT_STRUCTURE.md        # This file
│
├── 📁 templates/
│   ├── index.html                 # Main chat interface (dashboard)
│   └── login.html                 # Login page with Google OAuth
│
└── 📁 uploads/                    # Temporary file storage (auto-created)
```

## 🔍 File Details

### Core Application Files

#### `app.py` (Main Application)
**Size:** ~23 KB | **Lines:** ~600

**Contains:**
- Flask app configuration
- MongoDB connection
- Google OAuth integration
- Razorpay payment integration
- File upload handling (PDF/Images)
- OCR text extraction
- Chat management system
- Subscription management
- User authentication
- API endpoints

**Key Routes:**
```
GET  /                           - Main dashboard (requires login)
GET  /login                      - Login page
GET  /login/google               - Google OAuth redirect
GET  /login/google/authorize     - Google OAuth callback
GET  /logout                     - Logout user

POST /api/analyze                - Upload & analyze report
POST /api/chat                   - Send chat message
GET  /api/chats                  - Get all chats
GET  /api/chat/<chat_id>        - Get specific chat
DELETE /api/chat/<chat_id>      - Delete chat

GET  /api/user/info              - Get user information
GET  /api/subscription/plans     - Get subscription plans
POST /api/subscription/create-order - Create payment order
POST /api/subscription/verify-payment - Verify payment

GET  /api/health                 - Health check endpoint
```

#### `fun.py` (Utilities)
**Size:** ~500 bytes

**Contains:**
- Token counting function for AI model
- Uses tiktoken library
- Approximates tokens for context window management

#### `init_db.py` (Database Setup)
**Size:** ~3 KB

**Contains:**
- MongoDB collection creation
- Index creation for performance
- Sample data creation (optional)
- Database statistics display

**Run with:**
```bash
python init_db.py
```

### Frontend Templates

#### `templates/index.html` (Main Interface)
**Size:** ~35 KB | **Lines:** ~900

**Features:**
- Responsive sidebar with chat history
- Main chat interface
- File upload section
- Message display area
- Typing indicators
- Subscription modal
- User profile section
- Question counter
- Mobile-responsive design

**JavaScript Functions:**
```javascript
loadUserInfo()              - Load user data
loadChatList()              - Load chat history
loadChat(chatId)            - Load specific chat
startNewChat()              - Create new chat
deleteChat(chatId)          - Delete chat
handleFileUpload()          - Handle file upload
sendMessage()               - Send chat message
addMessageToUI()            - Add message to chat
showSubscriptionModal()     - Show subscription popup
subscribeToPlan(plan)       - Handle subscription
```

#### `templates/login.html` (Login Page)
**Size:** ~5 KB

**Features:**
- Modern gradient design
- Google OAuth button
- Feature highlights
- Responsive layout
- Developer credits

### Configuration Files

#### `requirements.txt`
**Python Dependencies:**
```
Flask==3.0.0                # Web framework
flask-cors==4.0.0          # CORS support
groq==0.9.0                # Groq AI client
PyPDF2==3.0.1              # PDF processing
Pillow==10.1.0             # Image processing
pytesseract==0.3.10        # OCR
Werkzeug==3.0.1            # WSGI utilities
pymongo==4.6.1             # MongoDB driver
python-dotenv==1.0.0       # Environment variables
Flask-Login==0.6.3         # User session management
authlib==1.3.0             # OAuth client
requests==2.31.0           # HTTP library
razorpay==1.4.1            # Payment gateway
tiktoken==0.5.2            # Token counting
bcrypt==4.1.2              # Password hashing (future use)
```

#### `.env.example` (Environment Template)
**Required Variables:**
```bash
MONGO_URI                  # MongoDB connection string
GROQ_API_KEY              # Groq AI API key
SECRET_KEY                # Flask secret key
GOOGLE_CLIENT_ID          # Google OAuth client ID
GOOGLE_CLIENT_SECRET      # Google OAuth secret
RAZORPAY_KEY_ID           # Razorpay key ID
RAZORPAY_KEY_SECRET       # Razorpay secret
APP_URL                   # Application URL
```

#### `.gitignore`
Excludes:
- Python cache files
- Virtual environment
- Environment variables
- Uploads folder
- IDE configs
- OS files

### Setup Scripts

#### `setup.sh` (Automated Setup)
**Platform:** Linux/macOS/Windows (Git Bash)

**Actions:**
1. Checks Python installation
2. Checks MongoDB
3. Installs Tesseract OCR
4. Creates virtual environment
5. Installs dependencies
6. Creates directories
7. Creates .env template

**Usage:**
```bash
chmod +x setup.sh
./setup.sh
```

### Documentation Files

#### `README.md` (Main Documentation)
**Size:** ~11 KB

**Sections:**
- Features overview
- Installation guide
- API keys setup
- Usage instructions
- Database schema
- Troubleshooting
- Production deployment
- Security notes

#### `QUICKSTART.md` (Quick Guide)
**Size:** ~4 KB

**Sections:**
- 5-minute setup guide
- Step-by-step instructions
- Common issues
- Testing checklist
- Development tips

## 🗄️ Database Collections

### `users`
```javascript
{
  _id: ObjectId,
  email: String (unique, indexed),
  name: String,
  picture: String,
  subscription_plan: String,
  subscription_expires: Date,
  created_at: Date,
  last_active: Date (indexed)
}
```

### `chats`
```javascript
{
  _id: ObjectId,
  user_id: String (indexed),
  chat_id: String (indexed),
  role: String,
  content: String,
  timestamp: Date (indexed),
  report_id: String (optional)
}
```

### `reports`
```javascript
{
  _id: ObjectId,
  user_id: String (indexed),
  filename: String,
  extracted_text: String,
  uploaded_at: Date (indexed)
}
```

### `subscriptions`
```javascript
{
  _id: ObjectId,
  user_id: String (indexed),
  plan: String,
  payment_id: String (unique, indexed),
  order_id: String,
  amount: Number,
  activated_at: Date,
  expires_at: Date (indexed)
}
```

## 📊 Data Flow

### User Registration Flow
```
1. User clicks "Login with Google"
2. Redirects to Google OAuth
3. Google returns user info
4. Check if user exists in database
5. Create/Update user record
6. Create session
7. Redirect to dashboard
```

### Chat Flow
```
1. User uploads medical report
2. Extract text using PyPDF2/Tesseract
3. Save extracted text to reports collection
4. User asks question
5. Check subscription limit
6. Build conversation context
7. Send to Groq AI (Llama 3.3)
8. Save user message and AI response
9. Update question counter
10. Display response
```

### Subscription Flow
```
1. User clicks "Upgrade Plan"
2. Selects plan
3. Creates Razorpay order
4. User completes payment
5. Razorpay sends callback
6. Verify payment signature
7. Update user subscription
8. Save subscription record
9. Refresh user interface
```

## 🔐 Security Features

1. **User Authentication**
   - OAuth 2.0 with Google
   - Session-based authentication
   - Flask-Login for user management

2. **Data Protection**
   - Environment variables for secrets
   - MongoDB connection encryption (optional)
   - HTTPS in production (recommended)

3. **Payment Security**
   - Razorpay payment gateway
   - Signature verification
   - Test mode for development

4. **Input Validation**
   - File type validation
   - File size limits (16MB)
   - Content sanitization

## 📦 Dependencies Graph

```
Flask (Web Framework)
├── Flask-CORS (Cross-Origin)
├── Flask-Login (Authentication)
└── Werkzeug (WSGI Utils)

Database
└── pymongo (MongoDB Driver)

AI & Processing
├── groq (AI Client)
├── tiktoken (Token Counter)
├── PyPDF2 (PDF Processing)
├── Pillow (Image Processing)
└── pytesseract (OCR)

Authentication & Payment
├── authlib (OAuth)
├── requests (HTTP)
└── razorpay (Payment Gateway)

Configuration
└── python-dotenv (Environment)
```

## 🚀 Deployment Checklist

- [ ] Update all API keys in `.env`
- [ ] Change `SECRET_KEY` to strong random string
- [ ] Setup MongoDB (local or Atlas)
- [ ] Configure Google OAuth redirect URI
- [ ] Setup Razorpay (Test → Live mode)
- [ ] Install Tesseract OCR
- [ ] Create `uploads/` directory
- [ ] Run `init_db.py` to setup database
- [ ] Test file upload
- [ ] Test Google login
- [ ] Test chat functionality
- [ ] Test payment flow
- [ ] Enable HTTPS in production
- [ ] Setup domain and SSL certificate
- [ ] Configure CORS for production domain

## 📈 Performance Optimization

1. **Database Indexes**
   - User email (unique)
   - Chat user_id + chat_id (composite)
   - Timestamps for sorting

2. **Caching**
   - Session management
   - User data caching
   - Chat history pagination

3. **File Processing**
   - Temporary file deletion
   - Text extraction optimization
   - Image compression

4. **API Rate Limiting**
   - Groq API context window management
   - Token counting for efficiency

## 🛠️ Development Tools

**Recommended:**
- VS Code / PyCharm
- MongoDB Compass (GUI)
- Postman (API testing)
- Git (version control)

**Extensions:**
- Python
- MongoDB for VS Code
- GitLens
- Prettier

---

**Last Updated:** February 2026  
**Developer:** Prakash Bokarvadiya  
**Version:** 1.0.0
