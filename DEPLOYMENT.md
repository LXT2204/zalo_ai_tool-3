# 🚀 Deployment Guide - Real Zalo Integration

This guide explains how to deploy your Zalo AI tool with **real Zalo message monitoring** (not simulated).

## 🎯 **Deployment Options**

### **Option 1: Railway.app (Recommended for Real Zalo Integration)**

Railway supports browser automation and can run Selenium with Chrome.

#### **Step 1: Create Railway Account**
1. Go to [railway.app](https://railway.app)
2. Sign up with GitHub
3. Create a new project

#### **Step 2: Connect Repository**
1. Click "Deploy from GitHub repo"
2. Select your `zalo_ai_tool_3` repository
3. Railway will automatically detect the `railway.json` and `nixpacks.toml` files

#### **Step 3: Set Environment Variables**
1. Go to "Variables" tab
2. Add: `GEMINI_API_KEY` = your API key
3. Add: `RAILWAY_ENVIRONMENT` = `production`

#### **Step 4: Deploy**
1. Railway will automatically build and deploy
2. Wait for build completion (5-10 minutes)
3. Your app will be available at the provided URL

#### **Step 5: Access Zalo Web**
1. Start the bot from the dashboard
2. The bot will open Zalo Web in headless mode
3. **Note**: You cannot manually log in in cloud environments
4. The bot will monitor for messages from pre-authenticated sessions

### **Option 2: Local Server with Real Zalo Integration**

For the best experience with real Zalo integration:

#### **Requirements:**
- VPS or dedicated server
- Ubuntu/Debian Linux
- Chrome browser support

#### **Step 1: Server Setup**
```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Python and dependencies
sudo apt install python3 python3-pip python3-venv -y

# Install Chrome
wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | sudo apt-key add -
echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" | sudo tee /etc/apt/sources.list.d/google-chrome.list
sudo apt update
sudo apt install google-chrome-stable -y

# Install ChromeDriver
sudo apt install chromium-chromedriver -y
```

#### **Step 2: Deploy Application**
```bash
# Clone repository
git clone https://github.com/your-username/zalo_ai_tool_3.git
cd zalo_ai_tool_3

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Set environment variable
export GEMINI_API_KEY="your_api_key_here"

# Run application
python app.py
```

#### **Step 3: Use with Screen/Tmux**
```bash
# Install screen
sudo apt install screen -y

# Create new screen session
screen -S zalo-bot

# Run the application
python app.py

# Detach from screen (Ctrl+A, then D)
# Reattach: screen -r zalo-bot
```

### **Option 3: Docker Deployment**

Create a Dockerfile for containerized deployment:

```dockerfile
FROM python:3.9-slim

# Install Chrome and dependencies
RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    unzip \
    && wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | apt-key add - \
    && echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" > /etc/apt/sources.list.d/google-chrome.list \
    && apt-get update \
    && apt-get install -y google-chrome-stable \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Install ChromeDriver
RUN wget -O /tmp/chromedriver.zip https://chromedriver.storage.googleapis.com/$(curl -sS chromedriver.storage.googleapis.com/LATEST_RELEASE)/chromedriver_linux64.zip \
    && unzip /tmp/chromedriver.zip chromedriver -d /usr/local/bin/ \
    && rm /tmp/chromedriver.zip

# Set up application
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 5000

CMD ["gunicorn", "app:app", "--bind", "0.0.0.0:5000"]
```

## 🔧 **Environment Variables**

| Variable | Description | Required |
|----------|-------------|----------|
| `GEMINI_API_KEY` | Your Google Gemini API key | Yes |
| `RAILWAY_ENVIRONMENT` | Set to `production` for Railway | No |
| `RENDER` | Set to `true` for Render | No |

## 📱 **How Real Zalo Integration Works**

### **Local Environment:**
1. ✅ Opens visible Chrome window
2. ✅ You can manually log in to Zalo
3. ✅ Real-time message monitoring
4. ✅ Full functionality

### **Cloud Environment (Railway):**
1. ✅ Opens headless Chrome
2. ❌ Cannot manually log in
3. ✅ Can monitor pre-authenticated sessions
4. ⚠️ Requires session persistence

### **Render/Heroku:**
1. ❌ No browser automation support
2. ❌ Cannot run Selenium
3. ❌ Falls back to simulated messages

## 🚨 **Important Notes**

### **For Real Zalo Integration:**
- **Railway.app** is the best cloud option
- **Local server** provides the best experience
- **Render/Heroku** don't support browser automation

### **Session Management:**
- In cloud environments, you need to handle Zalo session persistence
- Consider using Zalo API tokens if available
- Local deployment gives you full control

### **Security:**
- Never commit API keys to Git
- Use environment variables
- Consider adding authentication to the web dashboard

## 🎯 **Recommended Approach**

1. **For Development/Testing**: Use local deployment
2. **For Production with Real Zalo**: Use Railway.app
3. **For Demo/Simulation**: Use Render with `app_render.py`

## 🔍 **Troubleshooting**

### **Chrome/ChromeDriver Issues:**
```bash
# Check Chrome version
google-chrome --version

# Check ChromeDriver version
chromedriver --version

# Update ChromeDriver if needed
pip install --upgrade webdriver-manager
```

### **Permission Issues:**
```bash
# Fix Chrome permissions
sudo chmod +x /usr/bin/google-chrome
sudo chmod +x /usr/local/bin/chromedriver
```

### **Memory Issues:**
```bash
# Add swap space if needed
sudo fallocate -l 2G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
```

## 📞 **Support**

If you encounter issues:
1. Check the application logs
2. Verify environment variables
3. Test locally first
4. Check browser automation compatibility 