
# Customer Support Email Agent

AI-powered email agent that automatically processes Gmail emails and responds to customer inquiries.

## Features

- **AI Responses**: OpenAI GPT-3.5-turbo integration with template fallback
- **Email Categorization**: Questions, Refunds, Other/Spam
- **RAG System**: Knowledge base for accurate responses
- **Refund Processing**: Automated order lookup and approval
- **Multi-Account**: Connect multiple Gmail accounts
- **Database Storage**: PostgreSQL with conversation tracking

## Tech Stack

- **Backend**: Python, PostgreSQL, OpenAI API, Gmail API
- **Frontend**: Streamlit
- **Infrastructure**: Docker

## Quick Setup

1. **Database**: `docker-compose up -d`
2. **Dependencies**: `pip install -r backend/requirements.txt`
3. **Environment**: Copy `.env.example` to `.env` and add OpenAI API key
4. **Gmail API**: Download `credentials.json` from Google Cloud Console
5. **Run**: Backend: `python backend/main.py` Frontend: `streamlit run app.py` 

## Project Structure

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

