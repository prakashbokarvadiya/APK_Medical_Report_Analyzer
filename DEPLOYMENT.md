# 🚀 Production Deployment Guide

Complete guide to deploy Medical Report Analyzer on production servers.

## 📋 Table of Contents

1. [Pre-deployment Checklist](#pre-deployment-checklist)
2. [Deploy on Heroku](#deploy-on-heroku)
3. [Deploy on DigitalOcean](#deploy-on-digitalocean)
4. [Deploy on AWS EC2](#deploy-on-aws-ec2)
5. [Deploy on Railway](#deploy-on-railway)
6. [MongoDB Atlas Setup](#mongodb-atlas-setup)
7. [Domain & SSL Setup](#domain--ssl-setup)
8. [Environment Variables](#environment-variables)

---

## 🔍 Pre-deployment Checklist

### ✅ Required Services Setup

- [ ] MongoDB Atlas account (या local MongoDB)
- [ ] Groq API key
- [ ] Google OAuth credentials (production)
- [ ] Razorpay Live keys (KYC complete)
- [ ] Domain name (optional)
- [ ] SSL certificate (recommended)

### ✅ Code Preparation

- [ ] All environment variables in `.env`
- [ ] `SECRET_KEY` changed to strong random string
- [ ] Razorpay में Test mode से Live mode switch
- [ ] Google OAuth redirect URI production URL update
- [ ] CORS settings production domain के लिए update
- [ ] Debug mode OFF (`debug=False`)

---

## 🌐 Deploy on Heroku (Free Tier Available)

### Step 1: Install Heroku CLI
```bash
# Install
curl https://cli-assets.heroku.com/install.sh | sh

# Login
heroku login
```

### Step 2: Create Heroku App
```bash
# Create app
heroku create medical-report-analyzer

# Or with custom name
heroku create your-app-name
```

### Step 3: Add Buildpacks
```bash
# Python buildpack
heroku buildpacks:add heroku/python

# Tesseract buildpack
heroku buildpacks:add https://github.com/heroku/heroku-buildpack-apt
```

### Step 4: Create `Aptfile`
```bash
cat > Aptfile << EOL
tesseract-ocr
tesseract-ocr-hin
tesseract-ocr-eng
EOL
```

### Step 5: Create `Procfile`
```bash
cat > Procfile << EOL
web: gunicorn app:app
EOL
```

### Step 6: Add Gunicorn to requirements.txt
```bash
echo "gunicorn==21.2.0" >> requirements.txt
```

### Step 7: Set Environment Variables
```bash
heroku config:set MONGO_URI="your-mongodb-atlas-uri"
heroku config:set GROQ_API_KEY="your-groq-key"
heroku config:set SECRET_KEY="your-secret-key"
heroku config:set GOOGLE_CLIENT_ID="your-google-client-id"
heroku config:set GOOGLE_CLIENT_SECRET="your-google-secret"
heroku config:set RAZORPAY_KEY_ID="your-razorpay-key"
heroku config:set RAZORPAY_KEY_SECRET="your-razorpay-secret"
heroku config:set APP_URL="https://your-app-name.herokuapp.com"
```

### Step 8: Deploy
```bash
# Initialize git (if not done)
git init
git add .
git commit -m "Initial commit"

# Deploy to Heroku
git push heroku main

# Or if using master branch
git push heroku master
```

### Step 9: Open App
```bash
heroku open
```

### Step 10: Monitor Logs
```bash
heroku logs --tail
```

---

## 💧 Deploy on DigitalOcean

### Step 1: Create Droplet
1. Login to DigitalOcean
2. Create Droplet
3. Choose Ubuntu 22.04 LTS
4. Select plan ($6/month minimum)
5. Add SSH key
6. Create Droplet

### Step 2: Connect to Server
```bash
ssh root@your-droplet-ip
```

### Step 3: System Setup
```bash
# Update system
apt update && apt upgrade -y

# Install dependencies
apt install -y python3 python3-pip python3-venv nginx mongodb tesseract-ocr tesseract-ocr-hin

# Start MongoDB
systemctl start mongodb
systemctl enable mongodb
```

### Step 4: Deploy Application
```bash
# Create app directory
mkdir -p /var/www/medical-app
cd /var/www/medical-app

# Clone your code (या upload करें)
git clone your-repo-url .

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
pip install gunicorn
```

### Step 5: Create .env File
```bash
nano .env
# Add all environment variables
```

### Step 6: Create Systemd Service
```bash
nano /etc/systemd/system/medical-app.service
```

Add:
```ini
[Unit]
Description=Medical Report Analyzer
After=network.target

[Service]
User=www-data
WorkingDirectory=/var/www/medical-app
Environment="PATH=/var/www/medical-app/venv/bin"
ExecStart=/var/www/medical-app/venv/bin/gunicorn -w 4 -b 127.0.0.1:5000 app:app

[Install]
WantedBy=multi-user.target
```

```bash
# Start service
systemctl start medical-app
systemctl enable medical-app
systemctl status medical-app
```

### Step 7: Configure Nginx
```bash
nano /etc/nginx/sites-available/medical-app
```

Add:
```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }

    client_max_body_size 16M;
}
```

```bash
# Enable site
ln -s /etc/nginx/sites-available/medical-app /etc/nginx/sites-enabled/
nginx -t
systemctl restart nginx
```

### Step 8: Setup SSL (Free with Let's Encrypt)
```bash
# Install Certbot
apt install -y certbot python3-certbot-nginx

# Get certificate
certbot --nginx -d your-domain.com

# Auto-renewal
certbot renew --dry-run
```

---

## ☁️ Deploy on AWS EC2

### Step 1: Launch EC2 Instance
1. Login to AWS Console
2. Launch EC2 Instance
3. Choose Ubuntu Server 22.04 LTS
4. Select t2.micro (Free Tier)
5. Configure security group:
   - SSH (22)
   - HTTP (80)
   - HTTPS (443)
6. Create/Select key pair
7. Launch instance

### Step 2: Connect
```bash
ssh -i your-key.pem ubuntu@your-ec2-public-ip
```

### Step 3: Follow DigitalOcean Steps 3-8

Same as DigitalOcean deployment from Step 3 onwards.

---

## 🚂 Deploy on Railway (Easiest)

### Step 1: Create Account
1. जाएं: https://railway.app
2. Sign up with GitHub

### Step 2: Create New Project
1. Click "New Project"
2. Select "Deploy from GitHub repo"
3. Connect your repository

### Step 3: Add Environment Variables
Railway dashboard में:
```
MONGO_URI=your-mongodb-atlas-uri
GROQ_API_KEY=your-groq-key
SECRET_KEY=your-secret-key
GOOGLE_CLIENT_ID=your-client-id
GOOGLE_CLIENT_SECRET=your-secret
RAZORPAY_KEY_ID=your-key
RAZORPAY_KEY_SECRET=your-secret
```

### Step 4: Configure Build
Railway automatically detects Python और build करता है।

Railway Procfile की जरूरत नहीं है, लेकिन बना सकते हैं:
```
web: gunicorn app:app
```

### Step 5: Deploy
Railway automatically deploy करता है on every git push!

---

## 🍃 MongoDB Atlas Setup (Cloud Database)

### Step 1: Create Account
1. जाएं: https://www.mongodb.com/cloud/atlas
2. Free account बनाएं

### Step 2: Create Cluster
1. "Build a Database" click करें
2. Free tier (M0) select करें
3. Region select करें (nearest)
4. Cluster name दें
5. Create cluster

### Step 3: Setup Database Access
1. Database Access में जाएं
2. Add New Database User
3. Username/Password note करें
4. "Add User" click करें

### Step 4: Setup Network Access
1. Network Access में जाएं
2. Add IP Address
3. "Allow Access from Anywhere" (0.0.0.0/0) - Development के लिए
4. Production में specific IPs allow करें

### Step 5: Get Connection String
1. Cluster में "Connect" click करें
2. "Connect your application" select करें
3. Python driver select करें
4. Connection string copy करें
5. `<password>` को actual password से replace करें
6. Database name add करें

Example:
```
mongodb+srv://username:password@cluster0.xxxxx.mongodb.net/medical_assistant?retryWrites=true&w=majority
```

---

## 🌐 Domain & SSL Setup

### Buy Domain (Optional but Recommended)
**Providers:**
- Namecheap: ~$10/year
- GoDaddy: ~$12/year
- Google Domains: ~$12/year

### Point Domain to Server
1. Domain provider के DNS settings में जाएं
2. A Record add करें:
   ```
   Type: A
   Name: @
   Value: your-server-ip
   TTL: 300
   ```

### SSL Certificate (Free)
```bash
# Install Certbot
sudo apt install certbot python3-certbot-nginx

# Get certificate
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com

# Test auto-renewal
sudo certbot renew --dry-run
```

---

## 🔐 Environment Variables (Production)

### Required Variables
```bash
# Database
MONGO_URI=mongodb+srv://user:pass@cluster.mongodb.net/medical_assistant

# AI API
GROQ_API_KEY=gsk_xxxxxxxxxxxxxxxxx

# Security
SECRET_KEY=random-super-secret-key-min-32-chars

# Google OAuth (Production)
GOOGLE_CLIENT_ID=xxxxx.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=GOCSPX-xxxxx

# Payment Gateway (Live)
RAZORPAY_KEY_ID=rzp_live_xxxxx
RAZORPAY_KEY_SECRET=xxxxx

# App URL
APP_URL=https://yourdomain.com
```

### Generate Strong SECRET_KEY
```python
python -c "import secrets; print(secrets.token_hex(32))"
```

---

## 🔧 Production Code Changes

### app.py में changes:

```python
# Change debug mode
if __name__ == '__main__':
    # Development
    # app.run(debug=True, host='0.0.0.0', port=5000)
    
    # Production
    app.run(debug=False, host='0.0.0.0', port=5000)
```

### CORS Configuration
```python
# Add specific origins
CORS(app, supports_credentials=True, origins=[
    "https://yourdomain.com",
    "https://www.yourdomain.com"
])
```

---

## 📊 Monitoring & Maintenance

### Setup Logging
```python
import logging

logging.basicConfig(
    filename='app.log',
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
```

### Database Backups
```bash
# MongoDB Atlas automatic backups
# या manual backup:
mongodump --uri="mongodb+srv://..." --out=/backup/$(date +%Y%m%d)
```

### Monitor Application
```bash
# Check service status
systemctl status medical-app

# View logs
journalctl -u medical-app -f

# Check Nginx logs
tail -f /var/log/nginx/access.log
tail -f /var/log/nginx/error.log
```

---

## 🐛 Troubleshooting Production

### Application Not Starting
```bash
# Check logs
journalctl -u medical-app -n 50

# Check gunicorn
ps aux | grep gunicorn

# Restart service
systemctl restart medical-app
```

### Database Connection Issues
```bash
# Test MongoDB connection
mongo "mongodb+srv://..."

# Check firewall
ufw status
```

### SSL Certificate Issues
```bash
# Renew certificate
certbot renew

# Check certificate
certbot certificates
```

---

## 📞 Support

Issues के लिए contact करें:
- **Email:** prakasbokarvadiya0@gmail.com
- **LinkedIn:** https://www.linkedin.com/in/prakash-bokarvadiya-609001369

---

**Happy Deploying! 🚀**
