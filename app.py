from flask import Flask, request, jsonify, render_template, session, redirect, url_for
from flask_cors import CORS
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
import os
import certifi

from groq import Groq
import PyPDF2
from PIL import Image
import pytesseract
import io
import base64
from werkzeug.utils import secure_filename
from fun import count_tokens
from pymongo import MongoClient
from datetime import datetime, timedelta
import uuid
from authlib.integrations.flask_client import OAuth
from dotenv import load_dotenv
import razorpay
import hmac
import hashlib

# Load environment variables
load_dotenv()

app = Flask(
    __name__,
    static_folder="static",
    template_folder="templates"
)

app.secret_key = os.environ.get("SECRET_KEY", "your-secret-key-change-this")
CORS(app, supports_credentials=True)

# Flask-Login Configuration
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# OAuth Configuration (Google Login) - FIXED VERSION
oauth = OAuth(app)

google = oauth.register(
    name='google',
    client_id=os.environ.get("GOOGLE_CLIENT_ID"),
    client_secret=os.environ.get("GOOGLE_CLIENT_SECRET"),
    server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
    client_kwargs={'scope': 'openid email profile'},
)

# Razorpay Configuration
razorpay_client = razorpay.Client(
    auth=(os.environ.get("RAZORPAY_KEY_ID", ""), os.environ.get("RAZORPAY_KEY_SECRET", ""))
)

# Configure upload folder
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'pdf', 'png', 'jpg', 'jpeg', 'gif', 'bmp', 'tiff'}

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# MongoDB Configuration
# MongoDB Configuration (Render-safe)

MONGO_URI = os.getenv("MONGO_URI")

mongo_client = MongoClient(
    MONGO_URI,
    serverSelectionTimeoutMS=10000,
    connectTimeoutMS=10000
)

db = mongo_client["medical_db"]

users_collection = db["users"]
chats_collection = db["chats"]
reports_collection = db["reports"]
subscriptions_collection = db["subscriptions"]

# Subscription Plans
PLANS = {
    'free': {
        'name': 'Free Plan',
        'questions_per_chat': 5,
        'price': 0,
        'discount': 0,
        'tag': 'Basic'
    },
    'starter': {
        'name': 'Starter Plan',
        'questions_per_chat': 10,
        'price': 49,
        'duration_days': 30,
        'discount': 0,
        'tag': 'Popular',
        'original_price': 49
    },
    'pro': {
        'name': 'Pro Plan',
        'questions_per_chat': 22,
        'price': 89,
        'duration_days': 30,
        'discount': 51,
        'tag': 'Best Value',
        'original_price': 182
    },
    'unlimited': {
        'name': 'Unlimited Plan',
        'questions_per_chat': -1,  # -1 means unlimited
        'price': 999,
        'duration_days': 365,  # 1 year
        'discount': 92,
        'tag': 'Premium',
        'original_price': 12474
    }
}

# User class for Flask-Login
class User(UserMixin):
    def __init__(self, user_data):
        self.id = str(user_data['_id'])
        self.email = user_data['email']
        self.name = user_data.get('name', '')
        self.picture = user_data.get('picture', '')
        self.subscription_plan = user_data.get('subscription_plan', 'free')
        self.subscription_expires = user_data.get('subscription_expires')

@login_manager.user_loader
def load_user(user_id):
    from bson.objectid import ObjectId
    user_data = users_collection.find_one({'_id': ObjectId(user_id)})
    if user_data:
        return User(user_data)
    return None

# Initialize Groq client
def get_groq_client():
    api_key = os.environ.get("GROQ_API_KEY")
    if not api_key:
        raise ValueError("GROQ_API_KEY environment variable not set")
    return Groq(api_key=api_key)

def get_user_subscription(user_id):
    """Get user's current subscription plan"""
    from bson.objectid import ObjectId
    user = users_collection.find_one({'_id': ObjectId(user_id)})
    
    if not user:
        return PLANS['free']
    
    plan = user.get('subscription_plan', 'free')
    expires = user.get('subscription_expires')
    
    # Check if subscription expired
    if plan != 'free' and expires and expires < datetime.utcnow():
        # Reset to free plan
        users_collection.update_one(
            {'_id': ObjectId(user_id)},
            {'$set': {'subscription_plan': 'free', 'subscription_expires': None}}
        )
        return PLANS['free']
    
    return PLANS.get(plan, PLANS['free'])

def count_chat_questions(chat_id):
    """Count questions in current chat session"""
    count = chats_collection.count_documents({
        'chat_id': chat_id,
        'role': 'user'
    })
    return count

def can_ask_question(user_id, chat_id):
    """Check if user can ask more questions in current chat"""
    subscription = get_user_subscription(user_id)
    
    # Unlimited plan
    if subscription['questions_per_chat'] == -1:
        return True, subscription
    
    # Count questions in this chat
    question_count = count_chat_questions(chat_id)
    
    if question_count >= subscription['questions_per_chat']:
        return False, subscription
    
    return True, subscription

def save_chat_message(user_id, chat_id, role, content, report_id=None):
    """Save chat message to MongoDB"""
    chat_data = {
        'user_id': user_id,
        'chat_id': chat_id,
        'role': role,
        'content': content,
        'timestamp': datetime.utcnow()
    }
    
    if report_id:
        chat_data['report_id'] = report_id
    
    chats_collection.insert_one(chat_data)

def get_chat_history(user_id, chat_id, limit=50):
    """Get chat history for specific chat"""
    chats = chats_collection.find(
        {'user_id': user_id, 'chat_id': chat_id}
    ).sort('timestamp', 1).limit(limit)
    
    history = []
    for chat in chats:
        history.append({
            'role': chat['role'],
            'content': chat['content'],
            'timestamp': chat['timestamp'].isoformat()
        })
    
    return history

def get_all_chats(user_id):
    """Get all chat sessions for user"""
    pipeline = [
        {'$match': {'user_id': user_id}},
        {'$group': {
            '_id': '$chat_id',
            'last_message': {'$last': '$content'},
            'last_timestamp': {'$last': '$timestamp'},
            'message_count': {'$sum': 1}
        }},
        {'$sort': {'last_timestamp': -1}}
    ]
    
    chats = list(chats_collection.aggregate(pipeline))
    
    result = []
    for chat in chats:
        # Get first user message as title
        first_message = chats_collection.find_one(
            {'chat_id': chat['_id'], 'role': 'user'},
            sort=[('timestamp', 1)]
        )
        
        title = first_message['content'][:50] + '...' if first_message and len(first_message['content']) > 50 else (first_message['content'] if first_message else 'New Chat')
        
        result.append({
            'chat_id': chat['_id'],
            'title': title,
            'last_message': chat['last_message'][:50] + '...' if len(chat['last_message']) > 50 else chat['last_message'],
            'last_timestamp': chat['last_timestamp'].isoformat(),
            'message_count': chat['message_count']
        })
    
    return result

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def extract_text_from_pdf(file_path):
    """Extract text from PDF file"""
    try:
        text = ""
        with open(file_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            for page in pdf_reader.pages:
                text += page.extract_text() + "\n"
        return text.strip()
    except Exception as e:
        return f"Error extracting PDF: {str(e)}"

def extract_text_from_image(file_path):
    """Extract text from image using OCR"""
    try:
        image = Image.open(file_path)
        text = pytesseract.image_to_string(image)
        return text.strip()
    except Exception as e:
        return f"Error extracting from image: {str(e)}"

# Routes
@app.route('/')
def index():
    if current_user.is_authenticated:
        return render_template('index.html')
    return redirect(url_for('login'))

@app.route('/login')
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    return render_template('login.html')

@app.route('/login/google')
def google_login():
    redirect_uri = url_for('google_authorize', _external=True)
    return google.authorize_redirect(redirect_uri)

@app.route('/login/google/authorize')
def google_authorize():
    try:
        token = google.authorize_access_token()
        user_info = token.get('userinfo')
        
        if not user_info:
            print("No user info received from Google")
            return redirect(url_for('login'))
        
        # Check if user exists
        user_data = users_collection.find_one({'email': user_info['email']})
        
        if not user_data:
            # Create new user
            user_data = {
                'email': user_info['email'],
                'name': user_info.get('name', ''),
                'picture': user_info.get('picture', ''),
                'subscription_plan': 'free',
                'subscription_expires': None,
                'created_at': datetime.utcnow(),
                'last_active': datetime.utcnow()
            }
            result = users_collection.insert_one(user_data)
            user_data['_id'] = result.inserted_id
        else:
            # Update last active
            users_collection.update_one(
                {'_id': user_data['_id']},
                {'$set': {'last_active': datetime.utcnow()}}
            )
        
        # Login user
        user = User(user_data)
        login_user(user)
        
        print(f"User logged in successfully: {user_info['email']}")
        return redirect(url_for('index'))
        
    except Exception as e:
        print(f"Login error: {str(e)}")
        import traceback
        traceback.print_exc()
        return redirect(url_for('login'))

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/api/user/info', methods=['GET'])
@login_required
def user_info():
    """Get current user information"""
    subscription = get_user_subscription(current_user.id)
    
    return jsonify({
        'success': True,
        'user': {
            'name': current_user.name,
            'email': current_user.email,
            'picture': current_user.picture,
            'subscription_plan': current_user.subscription_plan,
            'subscription_expires': current_user.subscription_expires.isoformat() if current_user.subscription_expires else None,
            'plan_details': subscription
        }
    })

@app.route('/api/analyze', methods=['POST'])
@login_required
def analyze_report():
    try:
        # Check if file is present
        if 'file' not in request.files:
            return jsonify({'error': 'No file uploaded'}), 400
        
        file = request.files['file']
        chat_id = request.form.get('chat_id', str(uuid.uuid4()))
        selected_language = request.form.get('language', 'english')  # Get selected language
        
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        if not allowed_file(file.filename):
            return jsonify({'error': 'Invalid file type. Please upload PDF or image files.'}), 400
        
        # Save file temporarily
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)
        
        # Extract text based on file type
        file_ext = filename.rsplit('.', 1)[1].lower()
        if file_ext == 'pdf':
            extracted_text = extract_text_from_pdf(file_path)
        else:
            extracted_text = extract_text_from_image(file_path)
        
        # Clean up uploaded file
        os.remove(file_path)
        
        if not extracted_text or len(extracted_text) < 10:
            return jsonify({'error': 'Could not extract meaningful text from the file. Please ensure the file is clear and readable.'}), 400
        
        # Save report to database
        report_data = {
            'user_id': current_user.id,
            'filename': filename,
            'extracted_text': extracted_text,
            'uploaded_at': datetime.utcnow()
        }
        result = reports_collection.insert_one(report_data)
        report_id = str(result.inserted_id)
        
        # Save file upload event to chat history
        save_chat_message(
            current_user.id,
            chat_id,
            'system',
            f'File uploaded: {filename}',
            report_id=report_id
        )
        
        # Generate automatic explanation in selected language
        auto_explanation = generate_report_explanation(extracted_text, selected_language)
        
        # Save the auto-explanation to chat history
        if auto_explanation:
            save_chat_message(
                current_user.id,
                chat_id,
                'assistant',
                auto_explanation
            )
        
        return jsonify({
            'success': True,
            'extracted_text': extracted_text,
            'chat_id': chat_id,
            'report_id': report_id,
            'message': 'Report analyzed successfully. You can now ask questions about it.',
            'auto_explanation': auto_explanation
        })
        
    except Exception as e:
        return jsonify({'error': f'Server error: {str(e)}'}), 500

def generate_report_explanation(report_text, language='english'):
    """Generate automatic report explanation in selected language"""
    try:
        client = get_groq_client()
        
        # Language-specific prompts
        language_prompts = {
            'hindi': """कृपया इस मेडिकल रिपोर्ट का पूर्ण विश्लेषण हिंदी में प्रदान करें। निम्नलिखित बिंदुओं को कवर करें:

1. **रिपोर्ट का सारांश**: यह रिपोर्ट किस बारे में है?
2. **महत्वपूर्ण निष्कर्ष**: रिपोर्ट में क्या पाया गया?
3. **असामान्य मान**: कौन से टेस्ट परिणाम सामान्य सीमा से बाहर हैं?
4. **सामान्य भाषा में स्पष्टीकरण**: मेडिकल शब्दों को सरल हिंदी में समझाएं
5. **सुझाव**: क्या कोई सावधानियां या अगले कदम हैं?

कृपया सरल और समझने योग्य हिंदी में जवाब दें। हमेशा डॉक्टर से परामर्श की सलाह दें।""",
            
            'english': """Please provide a complete analysis of this medical report in English. Cover the following points:

1. **Report Summary**: What is this report about?
2. **Key Findings**: What was found in the report?
3. **Abnormal Values**: Which test results are outside normal range?
4. **Plain Language Explanation**: Explain medical terms in simple English
5. **Recommendations**: Any precautions or next steps?

Please respond in simple and understandable English. Always recommend consulting a doctor.""",
            
            'gujarati': """કૃપા કરીને આ મેડિકલ રિપોર્ટનું સંપૂર્ણ વિશ્લેષણ ગુજરાતીમાં પ્રદાન કરો. નીચેના મુદ્દાઓને આવરી લો:

1. **રિપોર્ટનો સારાંશ**: આ રિપોર્ટ શેના વિશે છે?
2. **મહત્વના તારણો**: રિપોર્ટમાં શું મળ્યું?
3. **અસામાન્ય મૂલ્યો**: કયા ટેસ્ટ પરિણામો સામાન્ય મર્યાદાની બહાર છે?
4. **સરળ ભાષામાં સમજૂતી**: મેડિકલ શબ્દોને સરળ ગુજરાતીમાં સમજાવો
5. **ભલામણો**: કોઈ સાવધાનીઓ અથવા આગળના પગલાં?

કૃપા કરીને સરળ અને સમજી શકાય તેવા ગુજરાતીમાં જવાબ આપો. હંમેશા ડૉક્ટર સાથે પરામર્શ કરવાની સલાહ આપો."""
        }
        
        # Get the appropriate prompt
        language_prompt = language_prompts.get(language, language_prompts['english'])
        
        # Create message for AI
        messages = [
            {
                "role": "system",
                "content": """You are a helpful medical assistant AI. Provide clear, comprehensive medical report analysis.
Be empathetic, explain medical terms simply, and always recommend consulting a doctor for specific medical advice."""
            },
            {
                "role": "user",
                "content": f"{language_prompt}\n\nMedical Report Content:\n\n{report_text}"
            }
        ]
        
        # Calculate tokens
        prompt_tokens = count_tokens(messages)
        context_window = 131072
        max_output_tokens = 32768
        safety_buffer = 1000
        
        max_allowed_output = min(
            max_output_tokens,
            context_window - prompt_tokens - safety_buffer
        )
        
        if max_allowed_output < 100:
            return None
        
        # Get response from Groq
        chat_completion = client.chat.completions.create(
            messages=messages,
            model="llama-3.3-70b-versatile",
            temperature=0.3,
            max_tokens=max_allowed_output,
            top_p=0.9
        )
        
        explanation = chat_completion.choices[0].message.content
        return explanation
        
    except Exception as e:
        print(f"Error generating explanation: {str(e)}")
        return None

@app.route('/api/chat', methods=['POST'])
@login_required
def chat():
    try:
        data = request.json
        user_message = data.get('message', '')
        report_text = data.get('report_text', '')
        chat_id = data.get('chat_id', str(uuid.uuid4()))
        
        if not user_message:
            return jsonify({'error': 'No message provided'}), 400
        
        # Check if user can ask more questions
        can_ask, subscription = can_ask_question(current_user.id, chat_id)
        
        if not can_ask:
            question_count = count_chat_questions(chat_id)
            return jsonify({
                'error': 'question_limit_reached',
                'message': f'You have reached the limit of {subscription["questions_per_chat"]} questions for free plan.',
                'current_plan': subscription['name'],
                'questions_used': question_count,
                'questions_limit': subscription['questions_per_chat'],
                'upgrade_required': True
            }), 403
        
        # Save user message
        save_chat_message(current_user.id, chat_id, 'user', user_message)
        
        # Initialize Groq client
        client = get_groq_client()
        
        # Get chat history from database
        db_history = get_chat_history(current_user.id, chat_id, limit=50)
        
        # Build conversation context
        messages = [
            {
                "role": "system",
                "content": """You are a helpful medical assistant AI that can help with medical questions and report analysis.

IMPORTANT INSTRUCTIONS:
1. Automatically detect the user's language from their question and respond in THE SAME LANGUAGE
2. If user asks in Hindi/Hinglish, respond in Hindi
3. If user asks in English, respond in English
4. If user asks in Gujarati, respond in Gujarati
5. Explain medical terms in simple, easy-to-understand language
6. Be empathetic and supportive
7. Always suggest consulting a doctor for serious health concerns
8. Never provide definitive diagnoses - provide general information only
9. Keep responses concise but informative

YOU CAN HELP WITH:
- General medical questions and health information
- Explaining medical terms and conditions
- Understanding symptoms (while recommending doctor consultation)
- Health and wellness advice
- Medical report analysis (when a report is uploaded)
- Medication information
- Disease prevention and healthy lifestyle tips

WHEN NO REPORT IS UPLOADED:
- Answer general medical and health questions
- Provide educational health information
- Explain diseases, symptoms, and treatments in simple terms
- Give preventive health advice
- Always remind users to consult healthcare professionals for personalized advice

WHEN A MEDICAL REPORT IS PROVIDED:
- Analyze the report and explain findings
- Clarify test results and their meanings
- Identify normal vs abnormal values
- Explain medicines mentioned
- Provide health recommendations based on the report

DEVELOPER INFORMATION:
- If anyone asks who developed this application/chatbot/system, tell them: "This medical report analyzer was developed by Prakash Bokarvadiya"
- If they ask for contact information: 
   email: prakasbokarvadiya0@gmail.com
  LinkedIn: https://www.linkedin.com/in/prakash-bokarvadiya-609001369
- The AI model used is MRA 1.5.1 by synexachat, but the application itself was built by Prakash Bokarvadiya

IMPORTANT: You can answer questions even without a medical report. Provide helpful, general medical information while always recommending professional consultation for specific health issues. or suggest tow question for next question"""
            }
        ]
        
        # Add report context if available
        if report_text:
            messages.append({
                "role": "system",
                "content": f"Medical Report Content:\n\n{report_text}"
            })
        
        # Add chat history from database (last 10 messages for context)
        for msg in db_history[-10:]:
            if msg['role'] != 'system':
                messages.append({
                    'role': msg['role'],
                    'content': msg['content']
                })
        
        # Calculate tokens and respect Groq's limits
        prompt_tokens = count_tokens(messages)
        context_window = 131072
        max_output_tokens = 32768
        safety_buffer = 1000
        
        max_allowed_output = min(
            max_output_tokens,
            context_window - prompt_tokens - safety_buffer
        )
        
        if max_allowed_output < 100:
            return jsonify({
                'error': 'The report is too long. Please try a shorter report or ask a specific question.'
            }), 400
        
        # Get response from Groq
        chat_completion = client.chat.completions.create(
            messages=messages,
            model="llama-3.3-70b-versatile",
            temperature=0.3,
            max_tokens=max_allowed_output,
            top_p=0.9
        )
        
        assistant_response = chat_completion.choices[0].message.content
        
        # Save assistant response
        save_chat_message(current_user.id, chat_id, 'assistant', assistant_response)
        
        # Get updated question count
        question_count = count_chat_questions(chat_id)
        
        return jsonify({
            'success': True,
            'response': assistant_response,
            'chat_id': chat_id,
            'questions_used': question_count,
            'questions_limit': subscription['questions_per_chat'],
            'plan_name': subscription['name']
        })
        
    except Exception as e:
        return jsonify({'error': f'Chat error: {str(e)}'}), 500

@app.route('/api/chats', methods=['GET'])
@login_required
def get_chats():
    """Get all chat sessions for current user"""
    try:
        chats = get_all_chats(current_user.id)
        return jsonify({
            'success': True,
            'chats': chats
        })
    except Exception as e:
        return jsonify({'error': f'Error fetching chats: {str(e)}'}), 500

@app.route('/api/chat/<chat_id>', methods=['GET'])
@login_required
def get_chat(chat_id):
    """Get specific chat history"""
    try:
        history = get_chat_history(current_user.id, chat_id)
        subscription = get_user_subscription(current_user.id)
        question_count = count_chat_questions(chat_id)
        
        return jsonify({
            'success': True,
            'history': history,
            'chat_id': chat_id,
            'questions_used': question_count,
            'questions_limit': subscription['questions_per_chat'],
            'plan_name': subscription['name']
        })
    except Exception as e:
        return jsonify({'error': f'Error fetching chat: {str(e)}'}), 500

@app.route('/api/chat/<chat_id>', methods=['DELETE'])
@login_required
def delete_chat(chat_id):
    """Delete specific chat"""
    try:
        chats_collection.delete_many({
            'user_id': current_user.id,
            'chat_id': chat_id
        })
        
        return jsonify({
            'success': True,
            'message': 'Chat deleted successfully'
        })
    except Exception as e:
        return jsonify({'error': f'Error deleting chat: {str(e)}'}), 500

@app.route('/api/subscription/plans', methods=['GET'])
def get_plans():
    """Get all subscription plans"""
    return jsonify({
        'success': True,
        'plans': PLANS
    })

@app.route('/api/subscription/create-order', methods=['POST'])
@login_required
def create_subscription_order():
    """Create Razorpay order for subscription"""
    try:
        data = request.json
        plan_type = data.get('plan')
        
        if plan_type not in PLANS or plan_type == 'free':
            return jsonify({'error': 'Invalid plan'}), 400
        
        plan = PLANS[plan_type]
        
        # Create Razorpay order
        order_data = {
            'amount': plan['price'] * 100,  # Amount in paise
            'currency': 'INR',
            'receipt': f'sub_{current_user.id}_{uuid.uuid4().hex[:8]}',
            'notes': {
                'user_id': current_user.id,
                'plan': plan_type,
                'email': current_user.email
            }
        }
        
        order = razorpay_client.order.create(data=order_data)
        
        return jsonify({
            'success': True,
            'order_id': order['id'],
            'amount': order['amount'],
            'currency': order['currency'],
            'key_id': os.environ.get('RAZORPAY_KEY_ID')
        })
        
    except Exception as e:
        return jsonify({'error': f'Order creation failed: {str(e)}'}), 500

@app.route('/api/subscription/verify-payment', methods=['POST'])
@login_required
def verify_payment():
    """Verify Razorpay payment and activate subscription"""
    try:
        from bson.objectid import ObjectId
        
        data = request.json
        payment_id = data.get('razorpay_payment_id')
        order_id = data.get('razorpay_order_id')
        signature = data.get('razorpay_signature')
        plan_type = data.get('plan')
        
        # Verify signature
        message = f"{order_id}|{payment_id}"
        secret = os.environ.get('RAZORPAY_KEY_SECRET')
        
        generated_signature = hmac.new(
            secret.encode(),
            message.encode(),
            hashlib.sha256
        ).hexdigest()
        
        if generated_signature != signature:
            return jsonify({'error': 'Invalid payment signature'}), 400
        
        # Activate subscription
        plan = PLANS[plan_type]
        expires_at = datetime.utcnow() + timedelta(days=plan['duration_days'])
        
        users_collection.update_one(
            {'_id': ObjectId(current_user.id)},
            {
                '$set': {
                    'subscription_plan': plan_type,
                    'subscription_expires': expires_at
                }
            }
        )
        
        # Save subscription record
        subscriptions_collection.insert_one({
            'user_id': current_user.id,
            'plan': plan_type,
            'payment_id': payment_id,
            'order_id': order_id,
            'amount': plan['price'],
            'activated_at': datetime.utcnow(),
            'expires_at': expires_at
        })
        
        return jsonify({
            'success': True,
            'message': f'{plan["name"]} activated successfully!',
            'expires_at': expires_at.isoformat()
        })
        
    except Exception as e:
        return jsonify({'error': f'Payment verification failed: {str(e)}'}), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    try:
        # Check if GROQ_API_KEY is set
        api_key = os.environ.get("GROQ_API_KEY")
        if not api_key:
            return jsonify({
                'status': 'error',
                'message': 'GROQ_API_KEY not configured'
            }), 500
        
        # Check MongoDB connection
        try:
            mongo_client.server_info()
            db_status = 'connected'
        except:
            db_status = 'disconnected'
        
        return jsonify({
            'status': 'ok',
            'message': 'Server is running',
            'database': db_status
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
