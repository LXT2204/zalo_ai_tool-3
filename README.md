# Zalo AI Tool - Web Dashboard

A web-based dashboard for managing an AI-powered Zalo chatbot that automatically responds to messages containing specific keywords.

## Features

- 🤖 **Bot Control**: Start/stop the AI chatbot
- 🔑 **Keyword Management**: Configure trigger keywords
- 🧠 **AI Testing**: Test AI responses in real-time
- 📊 **Chat Logs**: View conversation history
- ⚙️ **Settings**: Configure auto-reply and check intervals
- 🌐 **Web Interface**: Modern, responsive dashboard

## Local Development

### Prerequisites

- Python 3.9+
- Google Gemini API key

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
   - **Start Command**: `gunicorn app:app`
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
├── app.py                 # Main Flask application
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
- `POST /api/start_bot` - Start the bot
- `POST /api/stop_bot` - Stop the bot
- `GET/POST /api/keywords` - Manage keywords
- `POST /api/test_ai` - Test AI response
- `GET /api/chat_logs` - Get chat logs
- `POST /api/clear_logs` - Clear chat logs

## Security Notes

- The `config.py` file is excluded from version control to protect API keys
- Use environment variables for sensitive configuration in production
- The web interface is designed for internal use - consider adding authentication for public deployment

## Troubleshooting

### Common Issues

1. **Build fails on Render**
   - Check that all dependencies are in `requirements.txt`
   - Ensure Python version is compatible (3.9+)

2. **API key not working**
   - Verify the `GEMINI_API_KEY` environment variable is set correctly
   - Check that the API key has the necessary permissions

3. **Bot not starting**
   - Check the logs in Render dashboard
   - Ensure all required files are present

### Getting Help

- Check the Render logs in your service dashboard
- Verify environment variables are set correctly
- Test locally first to ensure everything works

## License

This project is for educational and personal use. Please ensure compliance with Zalo's terms of service and Google's API usage policies. 