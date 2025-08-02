# 🚀 Unified Project Dashboard

A comprehensive Streamlit dashboard that integrates all your existing Python projects into a modern, interactive web interface. Built with Streamlit, this dashboard provides a unified platform for AI tools, Docker management, Linux operations, machine learning predictions, Python utilities, and web development tools.

## ✨ Features

### 🤖 AI Toolkit
- **Agentic Ideation**: Transform startup ideas into refined, market-ready concepts
- **Language Translator**: Translate text between 40+ languages using AI
- **AI Shell Assistant**: Execute shell commands using natural language
- **Symptom Checker**: AI-powered health guidance (with medical disclaimers)

### 🐳 Docker Manager
- Launch, stop, start, and remove containers
- Pull images from Docker Hub
- List containers and images
- Real-time Docker system management
- Command output display

### 🐧 Remote Linux Assistant
- Execute remote Linux commands via SSH
- 50+ pre-configured system commands
- Custom command support
- Real-time command execution and output display

### 📈 Machine Learning Models
- **Construction Cost Predictor**: Estimate construction costs based on project parameters
- **Student Marks Predictor**: Predict pass/fail based on marks
- **Salary Predictor**: Estimate salary based on years of experience

### 🛠️ Python Multi-Tool
- System monitoring (RAM, CPU usage)
- Performance analysis (List vs Tuple comparison)
- Face detection and comparison
- Image capture and processing
- Google search integration
- Website downloader

### 🌐 WebDev Task Runner
- Email sending with attachments
- File upload and processing
- Media file handling
- Web scraping utilities

## 🛠️ Technology Stack

- **Frontend**: Streamlit
- **AI/ML**: Google Gemini, LangChain, scikit-learn
- **Computer Vision**: OpenCV, MediaPipe
- **System Tools**: psutil, subprocess
- **Web Scraping**: BeautifulSoup, requests
- **Data Processing**: pandas, numpy

## 📋 Prerequisites

- Python 3.8 or higher
- pip (Python package installer)
- Git (for cloning the repository)

## 🚀 Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd final-project
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   
   # On Windows
   venv\Scripts\activate
   
   # On macOS/Linux
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   Create a `.env` file in the root directory:
   ```env
   GOOGLE_API_KEY=your_google_api_key_here
   EMAIL_ADDRESS=your_email@gmail.com
   EMAIL_APP_PASSWORD=your_email_app_password
   TWILIO_ACCOUNT_SID=your_twilio_sid
   TWILIO_AUTH_TOKEN=your_twilio_token
   TWILIO_PHONE_NUMBER=your_twilio_phone
   TWILIO_WHATSAPP_NUMBER=whatsapp:+1234567890
   SERPAPI_API_KEY=your_serpapi_key
   MAILGUN_DOMAIN=your_mailgun_domain
   MAILGUN_API_KEY=your_mailgun_api_key
   ```

5. **Run the application**
   ```bash
   streamlit run app.py
   ```

6. **Access the dashboard**
   Open your browser and navigate to: `http://localhost:8501`

## 📁 Project Structure

```
final-project/
├── app.py                          # Main Streamlit application
├── requirements.txt                # Python dependencies
├── README.md                      # This file
├── .env                          # Environment variables (create this)
├── ai/                           # AI tools source files
│   ├── agentic ai/
│   │   ├── agentic_ai_ideation.py
│   │   ├── agentic_ai_language_translator.py
│   │   └── agentic_ai_shell_tool.py
│   └── symptom_ai using gemini/
│       └── symptom_checker_ai.py
├── docker menu task/
│   └── docker_menu.py
├── linux menu task/
│   └── fifty_remote_menu.py
├── machine learning task/
│   ├── construction cost prediction/
│   │   └── construction_cost.py
│   ├── predict your marks/
│   │   ├── my_marks_model.pkl
│   │   └── test.py
│   └── predict your salary/
│       ├── my_salary_model.pkl
│       └── salary.py
├── python menu task/
│   ├── multitool_tasks.py
│   ├── face1.jpg
│   └── face2.jpg
└── webdev menu task/
    └── app.py
```

## 🔧 Configuration

### Required API Keys

1. **Google AI API Key** (Required for AI tools)
   - Get from: https://aistudio.google.com/app/apikey
   - Used for: Gemini AI models, language translation, ideation

2. **Email Configuration** (Optional for email features)
   - Gmail App Password or SMTP credentials
   - Used for: Sending emails with attachments

3. **Twilio Credentials** (Optional for messaging features)
   - Account SID, Auth Token, Phone Number
   - Used for: SMS, WhatsApp, voice calls

4. **SerpAPI Key** (Optional for search features)
   - Get from: https://serpapi.com/
   - Used for: Google search integration

## 🎯 Usage Guide

### AI Toolkit

1. **Agentic Ideation**
   - Navigate to AI Toolkit → Agentic Ideation
   - Enter your startup idea in the text area
   - Click "Refine Idea", "Market Research", or "Business Model" buttons
   - Get AI-generated insights and analysis

2. **Language Translator**
   - Navigate to AI Toolkit → Language Translator
   - Enter text and select target language
   - Get instant translation with copy and audio options

3. **AI Shell Assistant**
   - Navigate to AI Toolkit → AI Shell Tool
   - Ask natural language questions about system operations
   - AI will execute appropriate shell commands

4. **Symptom Checker**
   - Navigate to AI Toolkit → Symptom Checker
   - Describe your symptoms in the chat interface
   - Get AI-powered health guidance (with medical disclaimers)

### Docker Manager

1. **Container Operations**
   - Use the dropdown to select Docker actions
   - Enter container names and image names as required
   - Click execute buttons to run commands
   - View real-time command output

2. **System Management**
   - Monitor Docker system resources
   - List containers and images
   - Pull new images from Docker Hub

### Remote Linux Assistant

1. **Setup**
   - Enter remote username and IP address
   - Ensure SSH access is configured

2. **Command Execution**
   - Choose from 50+ pre-configured commands
   - Execute custom commands
   - View real-time output

### Machine Learning Models

1. **Construction Cost Predictor**
   - Fill in project specifications (size, location, materials)
   - Get instant cost estimates
   - View detailed predictions

2. **Student Marks Predictor**
   - Enter student marks (0-100)
   - Get pass/fail prediction

3. **Salary Predictor**
   - Enter years of experience
   - Get salary estimates

### Python Multi-Tool

1. **System Monitoring**
   - Monitor RAM usage and system performance
   - Compare list vs tuple performance
   - Capture images from webcam

2. **Face Detection**
   - Upload images for face comparison
   - Face swap functionality (advanced)

### WebDev Task Runner

1. **Email Tools**
   - Send emails with text and attachments
   - Upload photos and videos
   - Process media files

2. **Web Scraping**
   - Download website content
   - Extract information from web pages
   - Analyze website structure

## 🔒 Security Considerations

- Store API keys in environment variables, never in code
- Use HTTPS in production
- Implement proper authentication for sensitive operations
- Validate all user inputs
- Use secure file upload handling

## 🚀 Deployment

### Local Development
```bash
streamlit run app.py
```

### Production Deployment
1. Use Streamlit Cloud or similar platform
2. Set up environment variables in the deployment platform
3. Configure proper logging
4. Use environment variables for configuration

Example with Streamlit Cloud:
1. Push code to GitHub
2. Connect repository to Streamlit Cloud
3. Set environment variables in Streamlit Cloud dashboard
4. Deploy automatically

## 🐛 Troubleshooting

### Common Issues

1. **Import Errors**
   - Ensure all dependencies are installed: `pip install -r requirements.txt`
   - Check Python version compatibility

2. **API Key Errors**
   - Verify API keys are correctly set in `.env` file
   - Check API key permissions and quotas

3. **Docker Commands Not Working**
   - Ensure Docker is installed and running
   - Check Docker permissions

4. **SSH Connection Issues**
   - Verify SSH keys are configured
   - Check network connectivity
   - Ensure SSH service is running on remote host

### Debug Mode
Enable debug mode for development:
```bash
streamlit run app.py --logger.level debug
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- Streamlit for the web framework
- Google Gemini for AI capabilities
- All contributors and open-source libraries used

## 📞 Support

For support and questions:
- Create an issue in the repository
- Check the troubleshooting section
- Review the documentation

---

**Note**: This dashboard integrates existing Python projects. Ensure you have the necessary permissions and licenses for all integrated components.

## 🎉 Quick Start

1. **Install dependencies**: `pip install -r requirements.txt`
2. **Set API key**: Add your Google AI API key to `.env` file
3. **Run app**: `streamlit run app.py`
4. **Open browser**: Navigate to `http://localhost:8501`

Enjoy your unified project dashboard! 🚀 