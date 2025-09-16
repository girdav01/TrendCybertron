# Trend Cybertron Streamlit App

A comprehensive cybersecurity AI assistant powered by Trend Cybertron Primus 8B model, featuring multiple specialized cybersecurity use cases with persistent conversation storage.

## 🚀 Features

### 🔧 Configuration & Setup
- **Multi-Provider Support**: Connect to Ollama or LM Studio
- **Model Selection**: Choose from available models in your provider
- **Multi-Model Comparison**: Compare responses from up to 3 different models side by side
- **Parameter Tuning**: Adjust temperature, max tokens, and other generation parameters
- **Connection Testing**: Verify provider connectivity
- **Data Management**: Export conversations and clear chat history

### 💬 Cybersecurity Use Cases
Each use case is implemented as a separate tab with specialized system prompts:

#### **Traditional Security Use Cases**
1. **Alert Prioritization** - Automate security alert prioritization
2. **YARA Patterns** - Generate malware detection rules
3. **OSINT Reporting** - Open source intelligence analysis
4. **Incident Summarization** - Create incident reports for different audiences
5. **Red Team Planning** - Plan and simulate attack scenarios
6. **Exploit Generation** - Develop proof-of-concept exploits
7. **Threat Intelligence** - Analyze threat actors and campaigns
8. **Vulnerability Assessment** - Assess and prioritize vulnerabilities
9. **Security Policy** - Develop security policies and procedures

#### **CREM (Cyber Risk Exposure Management) Use Cases**
10. **CREM Discover** - Asset and exposure discovery with business context
11. **CREM Predict** - Threat prediction and attack path analysis
12. **CREM Prioritize** - Risk prioritization with business impact analysis
13. **CREM Comply** - Compliance and control mapping automation
14. **CREM Quantify** - Cyber risk quantification and business impact analysis
15. **CREM Mitigate** - Remediation planning and mitigation strategies

### 💾 Data Persistence
- **SQLite Database**: All conversations are stored locally
- **Session Management**: Track conversation sessions
- **Export Functionality**: Export conversations as JSON
- **Search Capabilities**: Search through conversation history

## 📋 Prerequisites

### System Requirements
- **Python**: 3.8 or higher
- **RAM**: Minimum 8GB, Recommended 16GB+
- **Storage**: At least 10GB free space
- **Model Provider**: Ollama OR LM Studio installed and running locally

### Software Installation

#### Option 1: Install Ollama
```bash
# Windows: Download from https://ollama.ai/
# macOS: brew install ollama
# Linux: curl -fsSL https://ollama.ai/install.sh | sh

# Start Ollama Service
ollama serve

# Pull the Model
ollama pull llama-trendcybertron-primus-merged
```

#### Option 2: Install LM Studio
```bash
# Download from https://lmstudio.ai/
# 1. Open LM Studio
# 2. Go to "Local Server" tab
# 3. Load your preferred model
# 4. Start the server (default port 1234)
```

#### 3. Install Python Dependencies
```bash
pip install -r requirements.txt
```

## 🚀 Quick Start

### 1. Clone and Setup
```bash
git clone <repository-url>
cd TrendCybertronApp
pip install -r requirements.txt
```

### 2. Start the Application
```bash
streamlit run app.py
```

### 3. Access the App
Open your browser and navigate to `http://localhost:8501`

## ⚙️ Configuration

### Provider Selection
The app supports two local model providers:

- **Ollama**: Command-line interface for running LLMs locally
- **LM Studio**: GUI-based application with web interface

### Connection Settings
- **Host**: Default `localhost` for both providers
- **Port**: 
  - Ollama: `11434` (default)
  - LM Studio: `1234` (default)
- **Model**: Select from available models in your chosen provider

### Generation Parameters
- **Temperature**: Controls randomness (0.0-1.0)
- **Max Tokens**: Maximum response length (100-8000)
- **Connection Test**: Verify provider connectivity

## 📖 Usage Guide

### Configuration Tab
1. **Provider Selection**: Choose between Ollama or LM Studio
2. **Connection Settings**: Configure host, port, and model selection
3. **Generation Parameters**: Adjust temperature and max tokens
4. **Connection Test**: Verify provider connectivity
5. **Data Management**: Export conversations or clear history

### Chat Tabs
1. **Select a Use Case**: Choose from the dropdown menu
2. **Multi-Model Comparison**: Enable comparison mode to test up to 3 models simultaneously
3. **Start Chatting**: Type your questions or requests
4. **View History**: All conversations are automatically saved

### Multi-Model Comparison Feature
- **Enable Comparison**: Check the "Compare responses from multiple models" checkbox
- **Select Models**: Choose up to 3 different models from dropdowns
- **Side-by-Side Results**: Responses are displayed in columns for easy comparison
- **Model Identification**: Each response is clearly labeled with the model name at the beginning and end
- **Database Storage**: All responses are saved individually for analysis

### System Prompts
Each tab uses specialized system prompts based on Cisco Foundation AI examples and CREM best practices:

#### **Traditional Security Use Cases**
- **Alert Prioritization**: SOC analyst expertise
- **YARA Patterns**: Malware analysis specialist
- **OSINT Reporting**: Threat intelligence analyst
- **Incident Summarization**: Incident response specialist
- **Red Team Planning**: Penetration testing expert
- **Exploit Generation**: Security researcher
- **Threat Intelligence**: Threat intelligence analyst
- **Vulnerability Assessment**: Security assessment specialist
- **Security Policy**: Governance and compliance expert

#### **CREM Use Cases**
- **CREM Discover**: EASM/ASRM specialist with asset discovery expertise
- **CREM Predict**: Threat prediction specialist with attack path analysis
- **CREM Prioritize**: Risk prioritization expert with business context analysis
- **CREM Comply**: Compliance specialist with cross-framework control mapping
- **CREM Quantify**: Cyber risk quantification expert with FAIR methodology
- **CREM Mitigate**: Remediation specialist with ITSM integration expertise

## 🏗️ Architecture

### File Structure
```
TrendCybertronApp/
├── app.py                 # Main Streamlit application
├── requirements.txt       # Python dependencies
├── README.md             # This file
├── utils/
│   ├── database_manager.py    # SQLite database operations
│   ├── ollama_client.py       # Ollama API client
│   └── prompt_templates.py    # System prompt templates
├── database/
│   └── conversations.db       # SQLite database (created automatically)
└── prompts/
    └── (future prompt files)
```

### Key Components

#### 1. Main Application (`app.py`)
- Streamlit interface and routing
- Session state management
- Tab navigation and rendering
- User interface components

#### 2. Database Manager (`utils/database_manager.py`)
- SQLite database operations
- Conversation persistence
- Session management
- Data export functionality

#### 3. Ollama Client (`utils/ollama_client.py`)
- Ollama API communication
- Model management
- Response generation
- Connection testing

#### 4. Prompt Templates (`utils/prompt_templates.py`)
- Specialized system prompts
- Use case-specific templates
- Custom prompt generation

## 🔧 Configuration

### Environment Variables
```bash
# Optional: Set custom database path
export TREND_CYBERTRON_DB_PATH="/path/to/database.db"

# Optional: Set custom Ollama host/port
export OLLAMA_HOST="localhost"
export OLLAMA_PORT="11434"
```

### Database Configuration
The app automatically creates a SQLite database at `database/conversations.db` with the following tables:
- `conversations`: Stores all chat messages
- `sessions`: Tracks conversation sessions

### Model Configuration
- **Default Model**: `llama-trendcybertron-primus-merged`
- **Temperature**: 0.7 (adjustable via UI)
- **Max Tokens**: 1000 (adjustable via UI)
- **Context Window**: 2048 tokens

## 🛠️ Development

### Adding New Use Cases
1. Add system prompt to `prompt_templates.py`
2. Add tab to the `tabs` dictionary in `app.py`
3. Update the tab rendering logic

### Customizing Prompts
Edit the prompt templates in `utils/prompt_templates.py` to customize the AI's behavior for each use case.

### Database Schema
```sql
-- Conversations table
CREATE TABLE conversations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tab_name TEXT NOT NULL,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    user_message TEXT NOT NULL,
    assistant_response TEXT NOT NULL,
    system_prompt TEXT,
    model TEXT,
    temperature REAL,
    max_tokens INTEGER,
    session_id TEXT
);

-- Sessions table
CREATE TABLE sessions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id TEXT UNIQUE NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    last_activity DATETIME DEFAULT CURRENT_TIMESTAMP,
    total_messages INTEGER DEFAULT 0
);
```

## 🐛 Troubleshooting

### Common Issues

#### "Connection refused" Error
```bash
# Check if Ollama is running
ollama serve

# Test connection
curl http://localhost:11434/api/tags
```

#### "Model not found" Error
```bash
# List available models
ollama list

# Pull the model
ollama pull llama-trendcybertron-primus-merged
```

#### Database Errors
```bash
# Check database permissions
ls -la database/

# Reset database (will lose all conversations)
rm database/conversations.db
```

#### Performance Issues
- Reduce `max_tokens` parameter
- Lower `temperature` for faster responses
- Close other applications to free up RAM
- Use a quantized model version

### Logs and Debugging
- Check Streamlit logs in the terminal
- Enable debug mode: `streamlit run app.py --logger.level=debug`
- Check Ollama logs: `ollama logs`

## 📊 Performance

### Response Times
- **Local GPU**: 2-5 seconds
- **Local CPU**: 10-30 seconds
- **Network**: Depends on connection speed

### Memory Usage
- **Original Model**: ~16GB RAM
- **8-bit Quantized**: ~8GB RAM
- **4-bit Quantized**: ~4GB RAM

### Database Size
- **Typical**: 1-10MB for 1000 conversations
- **Large**: 50-100MB for 10,000+ conversations

## 🔒 Security Considerations

### Data Privacy
- All conversations stored locally
- No data sent to external services
- Ollama runs locally on your machine

### Best Practices
- Use strong authentication for production deployments
- Regularly backup conversation database
- Monitor system resources and performance
- Keep Ollama and dependencies updated

## 🤝 Contributing

### Development Setup
```bash
git clone <repository-url>
cd TrendCybertronApp
pip install -r requirements.txt
streamlit run app.py
```

### Adding Features
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

### Reporting Issues
- Use GitHub Issues for bug reports
- Include system information and error logs
- Provide steps to reproduce the issue

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- **Trend Micro**: For the Trend Cybertron Primus 8B model
- **Cisco Foundation AI**: For the original use case examples
- **Ollama**: For the local model serving framework
- **Streamlit**: For the web application framework

## 📞 Support

- **Documentation**: Check this README and inline comments
- **Issues**: Report bugs via GitHub Issues
- **Community**: Join the Trend Cybertron community discussions
- **Professional Support**: Contact Trend Micro for enterprise support
