"""
Database Initialization Script
Ye script MongoDB collections aur indexes create karta hai
"""

from pymongo import MongoClient, ASCENDING, DESCENDING
from datetime import datetime
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# MongoDB connection
MONGO_URI = os.environ.get("MONGO_URI", "mongodb://localhost:27017/")
client = MongoClient(MONGO_URI)
db = client['medical_assistant']

print("🗄️  Initializing Medical Assistant Database...")
print("=" * 50)

# Collections
users_collection = db['users']
chats_collection = db['chats']
reports_collection = db['reports']
subscriptions_collection = db['subscriptions']

# Create indexes for better performance
print("\n📊 Creating indexes...")

# Users collection indexes
print("   - Creating users indexes...")
users_collection.create_index([("email", ASCENDING)], unique=True)
users_collection.create_index([("user_id", ASCENDING)])
users_collection.create_index([("last_active", DESCENDING)])

# Chats collection indexes
print("   - Creating chats indexes...")
chats_collection.create_index([("user_id", ASCENDING), ("chat_id", ASCENDING)])
chats_collection.create_index([("timestamp", DESCENDING)])
chats_collection.create_index([("chat_id", ASCENDING)])

# Reports collection indexes
print("   - Creating reports indexes...")
reports_collection.create_index([("user_id", ASCENDING)])
reports_collection.create_index([("uploaded_at", DESCENDING)])

# Subscriptions collection indexes
print("   - Creating subscriptions indexes...")
subscriptions_collection.create_index([("user_id", ASCENDING)])
subscriptions_collection.create_index([("payment_id", ASCENDING)], unique=True)
subscriptions_collection.create_index([("expires_at", DESCENDING)])

print("\n✅ Indexes created successfully!")

# Display collection stats
print("\n📈 Database Statistics:")
print("=" * 50)

print(f"   Users: {users_collection.count_documents({})}")
print(f"   Chats: {chats_collection.count_documents({})}")
print(f"   Reports: {reports_collection.count_documents({})}")
print(f"   Subscriptions: {subscriptions_collection.count_documents({})}")

# Create sample data (optional - for testing)
create_sample = input("\n🤔 Create sample test user? (y/n): ").lower()

if create_sample == 'y':
    # Check if test user exists
    test_user = users_collection.find_one({'email': 'test@example.com'})
    
    if not test_user:
        test_user_data = {
            'email': 'test@example.com',
            'name': 'Test User',
            'picture': 'https://ui-avatars.com/api/?name=Test+User',
            'subscription_plan': 'free',
            'subscription_expires': None,
            'created_at': datetime.utcnow(),
            'last_active': datetime.utcnow()
        }
        
        result = users_collection.insert_one(test_user_data)
        print(f"\n✅ Test user created with ID: {result.inserted_id}")
        print("   Email: test@example.com")
    else:
        print("\n⚠️  Test user already exists!")

print("\n" + "=" * 50)
print("✨ Database initialization complete!")
print("=" * 50)

# Close connection
client.close()
