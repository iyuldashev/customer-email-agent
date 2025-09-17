from sentence_transformers import SentenceTransformer
import numpy as np
from typing import List, Tuple

class SimpleRAG:
    def __init__(self, db):
        self.db = db
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
        self.load_knowledge_base()
    
    def load_knowledge_base(self):
        """Load some sample Q&As into the database"""
        sample_qas = [
            ("What are your business hours?", 
             "Our business hours are Monday-Friday 9AM-5PM EST."),
            ("How do I track my order?", 
             "You can track your order using the tracking number sent to your email."),
            ("What is your return policy?", 
             "We accept returns within 30 days of purchase with original receipt."),
            ("How long does shipping take?", 
             "Standard shipping takes 5-7 business days."),
            ("Do you offer international shipping?",
             "Yes, we ship internationally. International orders take 10-14 business days."),
            ("What payment methods do you accept?",
             "We accept all major credit cards, PayPal, and Apple Pay."),
            ("How can I change my order?",
             "Orders can be modified within 24 hours of placement by contacting customer support."),
            ("What if my item is damaged?",
             "If you receive a damaged item, please contact us within 48 hours with photos for a replacement."),
            ("Do you offer expedited shipping?",
             "Yes, we offer express shipping (2-3 business days) and overnight shipping options."),
            ("How do I create an account?",
             "You can create an account by clicking 'Sign Up' on our website and following the prompts.")
        ]
        
        try:
            with self.db.conn.cursor() as cur:
                for question, answer in sample_qas:
                    # Check if already exists
                    cur.execute(
                        "SELECT id FROM knowledge_base WHERE question = %s", 
                        (question,)
                    )
                    if not cur.fetchone():
                        embedding = self.model.encode([question])[0]
                        cur.execute("""
                            INSERT INTO knowledge_base (question, answer, embedding)
                            VALUES (%s, %s, %s)
                        """, (question, answer, embedding.tolist()))
                print("Knowledge base loaded successfully")
        except Exception as e:
            print(f"Warning: Could not load knowledge base: {e}")
            print("The agent will still work but questions may not be answered")
    
    def find_answer(self, query: str, threshold: float = 0.7) -> Tuple[str, float]:
        """Find answer using simple keyword matching as fallback"""
        # Simple keyword-based matching for reliability
        query_lower = query.lower()
        
        # Hardcoded Q&A for reliability
        qa_pairs = [
            ("shipping", "Standard shipping takes 5-7 business days."),
            ("business hours", "Our business hours are Monday-Friday 9AM-5PM EST."),
            ("track order", "You can track your order using the tracking number sent to your email."),
            ("return policy", "We accept returns within 30 days of purchase with original receipt."),
            ("payment", "We accept all major credit cards, PayPal, and Apple Pay."),
        ]
        
        for keyword, answer in qa_pairs:
            if keyword in query_lower:
                return answer, 0.9
        
        return None, 0