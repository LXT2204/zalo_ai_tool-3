# Zalo AI Tool - Web Dashboard

A web-based dashboard for managing an AI-powered Zalo chatbot that monitors your real-time messages and provides AI responses based on keywords.

## 🚀 **New Feature: Real-time Zalo Message Monitoring**

The bot now opens a real Zalo Web window where you can:
- **Log in to your Zalo account**
- **Send messages to anyone**
- **See your messages displayed in real-time on the dashboard**
- **Get AI responses when your messages contain keywords**

## Features

- 🤖 **Bot Control**: Start/stop the AI chatbot
- 🌐 **Real Zalo Integration**: Opens actual Zalo Web window for login
- 📱 **Live Message Monitoring**: See your sent/received messages in real-time
- 🔑 **Keyword Management**: Configure trigger keywords
- 🧠 **AI Testing**: Test AI responses in real-time
- 📊 **Chat Logs**: View conversation history with AI responses
- ⚙️ **Settings**: Configure auto-reply and check intervals
- 🎨 **Modern UI**: Beautiful, responsive dashboard

## How It Works

1. **Start the Bot**: Click "Khởi động Bot" in the dashboard
2. **Zalo Window Opens**: A Chrome window will open with Zalo Web
3. **Login to Zalo**: Log in to your Zalo account in the opened window
4. **Send Messages**: Send messages to anyone in Zalo
5. **Real-time Display**: Your messages appear instantly in the dashboard
6. **AI Responses**: Messages containing keywords trigger AI responses
7. **View History**: All interactions are logged in the chat history

## Local Development

### Prerequisites

- Python 3.9+
- Google Gemini API key
- Chrome browser (for Selenium)

### Installation

1. Clone the repository:
```bash
git clone <your-repo-url>
cd zalo_ai_tool_3
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment variables:
```bash
# Create a .env file or set environment variables
export GEMINI_API_KEY="your_gemini_api_key_here"
```

4. Run the application:
```bash
python app.py
```

5. Open your browser and go to `http://localhost:5000`

## Deployment on Render

### Method 1: Using Render Dashboard (Recommended)

1. **Create a Render Account**
   - Go to [render.com](https://render.com)
   - Sign up for a free account

2. **Connect Your Repository**
   - Click "New +" → "Web Service"
   - Connect your GitHub/GitLab repository
   - Select the repository containing this project

3. **Configure the Service**
   - **Name**: `zalo-ai-tool` (or any name you prefer)
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn app_render:app` (uses simulated messages for Render)
   - **Plan**: Free (or choose a paid plan for better performance)

4. **Set Environment Variables**
   - Go to the "Environment" tab
   - Add the following environment variable:
     - **Key**: `GEMINI_API_KEY`
     - **Value**: Your Google Gemini API key

5. **Deploy**
   - Click "Create Web Service"
   - Render will automatically build and deploy your application

### Method 2: Using render.yaml (Blueprints)

1. **Push your code to GitHub/GitLab** with the `render.yaml` file included

2. **Create a Blueprint Instance**
   - Go to [render.com](https://render.com)
   - Click "New +" → "Blueprint"
   - Connect your repository
   - Render will automatically detect the `render.yaml` file

3. **Set Environment Variables**
   - After the blueprint is created, go to your service settings
   - Add the `GEMINI_API_KEY` environment variable

4. **Deploy**
   - The service will be automatically deployed

## Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `GEMINI_API_KEY` | Your Google Gemini API key | Yes |

## File Structure

```
zalo_ai_tool_3/
├── app.py                 # Main Flask application (with real Zalo integration)
├── app_render.py          # Render-compatible version (simulated messages)
├── zalo_ai.py            # AI integration module
├── config.py             # Configuration settings
├── main.py               # Original CLI version
├── requirements.txt      # Python dependencies
├── render.yaml           # Render deployment config
├── templates/
│   └── index.html        # Web dashboard template
├── keywords.json         # Trigger keywords
├── ai_response_log.json  # Chat logs
└── README.md            # This file
```

## API Endpoints

- `GET /` - Main dashboard
- `POST /api/start_bot` - Start the bot (opens Zalo window)
- `POST /api/stop_bot` - Stop the bot
- `GET/POST /api/keywords` - Manage keywords
- `POST /api/test_ai` - Test AI response
- `GET /api/chat_logs` - Get chat logs
- `GET /api/current_messages` - Get real-time messages
- `POST /api/clear_logs` - Clear chat logs
- `GET /api/bot_status` - Get bot status

## Message Types

The dashboard displays different types of messages with distinct styling:

- **🔵 Sent Messages** (`[Bạn]`): Messages you send in Zalo
- **🔴 Received Messages** (`[Người khác]`): Messages you receive
- **🟢 AI Responses** (`[AI Bot]`): AI-generated responses to keyword-triggered messages

## Security Notes

- The `config.py` file is excluded from version control to protect API keys
- Use environment variables for sensitive configuration in production
- The web interface is designed for internal use - consider adding authentication for public deployment
- Zalo Web window runs locally and requires manual login

## Troubleshooting

### Common Issues

1. **Chrome window doesn't open**
   - Ensure Chrome browser is installed
   - Check if ChromeDriver is properly installed
   - Try running locally first

2. **Messages not appearing**
   - Make sure you're logged into Zalo Web
   - Check that you're in an active chat
   - Verify the bot is running

3. **AI responses not working**
   - Verify the `GEMINI_API_KEY` is set correctly
   - Check that your message contains keywords
   - Test AI functionality with the test button

4. **Build fails on Render**
   - Use `app_render.py` for Render deployment (simulated messages)
   - Check that all dependencies are in `requirements.txt`
   - Ensure Python version is compatible (3.9+)

### Getting Help

- Check the browser console for JavaScript errors
- Verify environment variables are set correctly
- Test locally first to ensure everything works
- Check the Render logs in your service dashboard

## License

This project is for educational and personal use. Please ensure compliance with Zalo's terms of service and Google's API usage policies. 