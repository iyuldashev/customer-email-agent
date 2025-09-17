# Customer Support Email Agent 🤖📧

An intelligent customer support email agent that automatically processes incoming Gmail emails using AI-powered responses and smart categorization.

## Features ✨

- **AI-Powered Responses**: Uses OpenAI GPT-3.5-turbo for natural, contextual replies
- **Smart Email Categorization**: Automatically categorizes emails into Questions, Refunds, or Other
- **RAG (Retrieval-Augmented Generation)**: Knowledge base integration for accurate responses
- **Refund Processing**: Automated order lookup and refund approval workflow
- **Multi-Account Support**: Connect multiple Gmail accounts via web interface
- **Conversation Tracking**: Maintains context across email threads
- **Fallback System**: Template responses when AI is unavailable
- **Real-time Processing**: Continuously monitors Gmail for new emails

## Architecture 🏗️

### Backend Components
- **Email Listener**: Gmail API integration for email monitoring
- **AI Agent**: Email processing and response generation
- **OpenAI Service**: GPT-3.5-turbo integration with fallback handling
- **RAG System**: Knowledge base search and retrieval
- **Database**: PostgreSQL with pgvector for vector storage

### Client App
- **Streamlit Interface**: Simple web UI for Gmail account management
- **OAuth Integration**: Secure Gmail authentication flow

## Tech Stack 💻

- **Backend**: Python, PostgreSQL, OpenAI API, Gmail API
- **Frontend**: Streamlit
- **AI**: OpenAI GPT-3.5-turbo, sentence-transformers
- **Database**: PostgreSQL with pgvector extension
- **Infrastructure**: Docker, Docker Compose

## Quick Start 🚀

### Prerequisites
- Python 3.8+
- Docker & Docker Compose
- OpenAI API key
- Gmail API credentials

### 1. Clone & Setup
```bash
git clone <your-repo>
cd customer-email-agent
```

### 2. Start Database
```bash
docker-compose up -d
```

### 3. Install Dependencies
```bash
# Backend
cd backend
pip install -r requirements.txt

# Client
cd ../client  
pip install -r requirements.txt
```

### 4. Configure Environment
```bash
# Copy environment template
cp backend/.env.example backend/.env

# Edit .env file with your keys:
# OPENAI_API_KEY=sk-your-openai-key
# DB_HOST=localhost
# DB_NAME=email_agent
# DB_USER=postgres
# DB_PASSWORD=password
```

### 5. Gmail API Setup
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create new project or select existing
3. Enable Gmail API
4. Create OAuth 2.0 credentials (Desktop application)
5. Download as `credentials.json`
6. Place in both `backend/` and `client/` directories

### 6. Run the System
```bash
# Terminal 1: Start client app
cd client
streamlit run app.py

# Terminal 2: Start backend
cd backend
python main.py
```

### 7. Connect Gmail
1. Open http://localhost:8501
2. Enter account name and click "Connect Account"
3. Complete OAuth flow in browser
4. Backend will automatically use connected account

## Usage 📋

### Test Email Categories

**Questions:**
```
Subject: Shipping Question
Body: How long does shipping take?
```

**Refund Requests:**
```
Subject: Refund Request  
Body: I want a refund for order ORD-12345
```

**Other/Spam:**
```
Subject: Random Content
Body: Hello, random message here...
```

### Database Monitoring
```bash
# View processed emails
docker exec email_agent_db psql -U postgres -d email_agent -c "SELECT * FROM unhandled_emails ORDER BY created_at DESC LIMIT 5;"

# View orders
docker exec email_agent_db psql -U postgres -d email_agent -c "SELECT * FROM orders;"

# View conversations
docker exec email_agent_db psql -U postgres -d email_agent -c "SELECT * FROM email_conversations;"
```

## Configuration ⚙️

### Database Tables
- `orders` - Customer orders for refund processing
- `unhandled_emails` - Emails that couldn't be automatically handled
- `knowledge_base` - Q&A pairs for RAG responses
- `email_conversations` - Conversation context tracking
- `not_found_refunds` - Invalid refund requests

### AI Response Types
- **Questions**: Uses knowledge base + OpenAI for comprehensive answers
- **Refunds**: Validates order IDs and processes refunds automatically  
- **Follow-ups**: Maintains conversation context for complex flows
- **Fallback**: Template responses when OpenAI unavailable

### Environment Variables
```bash
# Required
OPENAI_API_KEY=your_openai_api_key
DB_HOST=localhost
DB_NAME=email_agent
DB_USER=postgres
DB_PASSWORD=password

# Optional
DB_PORT=5432
```

## Project Structure 📁

```
customer-email-agent/
├── backend/
│   ├── agent.py              # Main email processing logic
│   ├── database.py           # Database models and operations
│   ├── email_listener.py     # Gmail API integration
│   ├── openai_service.py     # OpenAI API wrapper
│   ├── rag.py                # Knowledge base and RAG
│   ├── main.py               # Application entry point
│   ├── requirements.txt      # Python dependencies
│   ├── credentials.json      # Gmail API credentials
│   └── .env                  # Environment variables
├── client/
│   ├── app.py                # Streamlit web interface
│   ├── requirements.txt      # Client dependencies
│   └── credentials.json      # Gmail API credentials
├── docker-compose.yml        # PostgreSQL setup
└── README.md                 # This file
```

## Features Deep Dive 🔍

### Email Processing Flow
1. **Monitor**: Continuously polls Gmail for unread emails
2. **Parse**: Extracts sender, subject, body, and thread info
3. **Categorize**: Uses keyword matching to classify emails
4. **Process**: Routes to appropriate handler (Question/Refund/Other)
5. **Respond**: Generates AI response or stores as unhandled
6. **Track**: Updates conversation context and database

### AI Integration
- **Primary**: OpenAI GPT-3.5-turbo for natural responses
- **Context**: Uses knowledge base information as context
- **Fallback**: Template responses if AI fails
- **Error Handling**: Graceful degradation with logging

### Refund Workflow
1. **Order ID Detection**: Regex pattern matching (ORD-XXXXX)
2. **Database Lookup**: Validates order exists
3. **Status Update**: Marks order as refund requested
4. **Response**: Confirms 3-day processing timeline
5. **Follow-up**: Handles invalid IDs and repeat requests

## Troubleshooting 🔧

### Common Issues

**Database Connection:**
```bash
# Check if database is running
docker ps | grep email_agent_db

# Restart database
docker-compose down && docker-compose up -d
```

**Gmail Authentication:**
```bash
# Remove token files to re-authenticate
rm backend/token*.pickle
rm client/token*.pickle
```

**OpenAI Rate Limits:**
- System automatically falls back to templates
- Check logs for API error details
- Verify API key is correct in .env

### Logs
- **Backend logs**: `backend/email_agent.log`
- **Console output**: Real-time processing status
- **Database logs**: Check Docker container logs

## Contributing 🤝

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

## License 📄

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support 💬

For questions or issues:
1. Check the logs first
2. Verify all credentials are properly configured
3. Ensure database is running and accessible
4. Test with simple emails before complex scenarios

---

**Built with ❤️ using OpenAI, PostgreSQL, and Gmail API**