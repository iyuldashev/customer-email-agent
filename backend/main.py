import time
import os
import logging
from dotenv import load_dotenv
from database import Database
from email_listener import GmailListener
from rag import SimpleRAG
from agent import EmailAgent

load_dotenv()

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('email_agent.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def main():
    logger.info("Starting Email Agent...")
    
    try:
        # Initialize components
        db = Database()
        db.add_sample_data()  # Add sample orders for testing
        gmail = GmailListener()
        rag = SimpleRAG(db)
        agent = EmailAgent(db, rag, gmail)
        
        logger.info("Email Agent is running. Listening for new emails...")
        
        # Main loop - check for new emails every 30 seconds
        while True:
            try:
                emails = gmail.get_unread_emails()
                
                for email in emails:
                    logger.info(f"Processing email from {email['from']}: {email['subject']}")
                    agent.process_email(email)
                
                if emails:
                    logger.info(f"Processed {len(emails)} emails")
                
                time.sleep(30)  # Check every 30 seconds
                
            except KeyboardInterrupt:
                logger.info("Shutting down...")
                break
            except Exception as e:
                logger.error(f"Error in main loop: {e}")
                time.sleep(60)  # Wait longer on error
                
    except Exception as e:
        logger.critical(f"Failed to initialize Email Agent: {e}")
        raise

if __name__ == "__main__":
    main()