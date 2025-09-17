import re
from typing import Dict, Tuple
from openai_service import OpenAIService

class EmailAgent:
    def __init__(self, db, rag, gmail):
        self.db = db
        self.rag = rag
        self.gmail = gmail
        self.openai = OpenAIService()
    
    def categorize_email(self, email_body: str) -> str:
        """Simple keyword-based categorization"""
        body_lower = email_body.lower()
        
        # Check for refund keywords
        refund_keywords = ['refund', 'return', 'money back', 'reimbursement']
        if any(keyword in body_lower for keyword in refund_keywords):
            return 'REFUND'
        
        # Check for question indicators
        question_indicators = ['?', 'how', 'what', 'when', 'where', 'why', 'can you', 'could you']
        if any(indicator in body_lower for indicator in question_indicators):
            return 'QUESTION'
        
        return 'OTHER'
    
    def extract_order_id(self, text: str) -> str:
        """Extract order ID from text (assumes format: ORD-XXXXX)"""
        pattern = r'ORD-\d{5}'
        match = re.search(pattern, text.upper())
        return match.group(0) if match else None
    
    def assess_importance(self, email_body: str) -> str:
        """Simple importance assessment"""
        urgent_keywords = ['urgent', 'asap', 'immediately', 'emergency']
        body_lower = email_body.lower()
        
        if any(keyword in body_lower for keyword in urgent_keywords):
            return 'HIGH'
        return 'NORMAL'
    
    def process_email(self, email: Dict):
        """Main email processing logic"""
        category = self.categorize_email(email['body'])
        
        if category == 'QUESTION':
            self.handle_question(email)
        elif category == 'REFUND':
            self.handle_refund(email)
        else:
            self.handle_other(email)
    
    def handle_question(self, email: Dict):
        """Handle question emails using AI + RAG fallback"""
        # Try OpenAI first
        if self.openai.is_available():
            # Get knowledge base info as context
            rag_answer, _ = self.rag.find_answer(email['body'])
            
            ai_response = self.openai.generate_question_response(
                email['body'], 
                knowledge_base_info=rag_answer
            )
            
            if ai_response:
                self.gmail.send_reply(
                    email['from'],
                    email['subject'],
                    ai_response,
                    email['thread_id']
                )
                return
        
        # Fallback to template-based response
        answer, confidence = self.rag.find_answer(email['body'])
        
        if answer:
            # Send template response
            self.gmail.send_reply(
                email['from'],
                email['subject'],
                f"Thank you for your question.\n\n{answer}\n\nBest regards,\nCustomer Support",
                email['thread_id']
            )
        else:
            # Save as unhandled with high importance
            self.db.save_unhandled_email(
                email['from'],
                email['subject'],
                email['body'],
                'QUESTION',
                'HIGH'
            )
    
    def handle_refund(self, email: Dict):
        """Handle refund requests"""
        order_id = self.extract_order_id(email['body'])
        
        # Check conversation context
        context = self.get_conversation_context(email['thread_id'])
        
        if not order_id:
            # Check if we were already waiting for order ID
            if context and 'awaiting_order_id' in context:
                # User replied with something that's not an order ID
                self.db.save_not_found_refund(email['from'], None, email['body'])
                
                # Generate AI response or use template
                if self.openai.is_available():
                    ai_response = self.openai.generate_refund_response(
                        context="Customer didn't provide order ID after being asked", 
                        order_id=None, 
                        order_found=None
                    )
                    response_text = ai_response if ai_response else "I couldn't find a valid order ID in your message. Please provide your order ID in the format ORD-XXXXX."
                else:
                    response_text = "I couldn't find a valid order ID in your message. Please provide your order ID in the format ORD-XXXXX."
                
                self.gmail.send_reply(
                    email['from'],
                    email['subject'],
                    response_text,
                    email['thread_id']
                )
                return
            
            # First refund request - ask for order ID
            if self.openai.is_available():
                ai_response = self.openai.generate_refund_response(
                    context=email['body'],
                    order_id=None,
                    order_found=None
                )
                response_text = ai_response if ai_response else "Thank you for contacting us about a refund. Please provide your order ID (format: ORD-XXXXX) so we can process your request."
            else:
                response_text = "Thank you for contacting us about a refund. Please provide your order ID (format: ORD-XXXXX) so we can process your request."
            
            self.gmail.send_reply(
                email['from'],
                email['subject'],
                response_text,
                email['thread_id']
            )
            # Update context
            self.update_conversation_context(email['thread_id'], email['from'], 'REFUND', 'awaiting_order_id')
        else:
            order = self.db.get_order(order_id)
            
            if order:
                # Process refund
                self.db.mark_refund_requested(order_id)
                
                # Generate AI response or use template
                if self.openai.is_available():
                    ai_response = self.openai.generate_refund_response(
                        context=f"Refund approved for order {order_id}",
                        order_id=order_id,
                        order_found=True
                    )
                    response_text = ai_response if ai_response else f"Your refund for order {order_id} has been approved and will be processed within 3 days."
                else:
                    response_text = f"Your refund for order {order_id} has been approved and will be processed within 3 days."
                
                self.gmail.send_reply(
                    email['from'],
                    email['subject'],
                    response_text,
                    email['thread_id']
                )
                # Clear context after successful processing
                self.update_conversation_context(email['thread_id'], email['from'], 'REFUND', 'completed')
            else:
                # Check if this is a repeated invalid ID
                invalid_order_key = f'invalid_order_{order_id}'
                if context and invalid_order_key in context:
                    # Second time with same invalid ID
                    self.db.save_not_found_refund(email['from'], order_id, email['body'])
                    
                    if self.openai.is_available():
                        ai_response = self.openai.generate_follow_up_response(
                            f"Customer repeatedly provided invalid order ID {order_id}",
                            email['body']
                        )
                        response_text = ai_response if ai_response else f"Order ID {order_id} is still not found in our system. Your request has been logged for manual review."
                    else:
                        response_text = f"Order ID {order_id} is still not found in our system. Your request has been logged for manual review."
                    
                    self.gmail.send_reply(
                        email['from'],
                        email['subject'],
                        response_text,
                        email['thread_id']
                    )
                else:
                    # First time with this invalid ID
                    if self.openai.is_available():
                        ai_response = self.openai.generate_refund_response(
                            context=f"Order ID {order_id} not found in system",
                            order_id=order_id,
                            order_found=False
                        )
                        response_text = ai_response if ai_response else f"Order ID {order_id} not found. Please check and provide the correct order ID."
                    else:
                        response_text = f"Order ID {order_id} not found. Please check and provide the correct order ID."
                    
                    self.gmail.send_reply(
                        email['from'],
                        email['subject'],
                        response_text,
                        email['thread_id']
                    )
                    self.update_conversation_context(
                        email['thread_id'], 
                        email['from'], 
                        'REFUND', 
                        invalid_order_key
                    )
    
    def handle_other(self, email: Dict):
        """Handle other/nonsense emails"""
        importance = self.assess_importance(email['body'])
        self.db.save_unhandled_email(
            email['from'],
            email['subject'],
            email['body'],
            'OTHER',
            importance
        )
    
    def get_conversation_context(self, thread_id: str) -> str:
        """Get conversation context from DB"""
        with self.db.conn.cursor() as cur:
            cur.execute(
                "SELECT context FROM email_conversations WHERE thread_id = %s",
                (thread_id,)
            )
            result = cur.fetchone()
            return result[0] if result else None
    
    def update_conversation_context(self, thread_id: str, email_from: str, category: str, context: str):
        """Update conversation context"""
        with self.db.conn.cursor() as cur:
            cur.execute("""
                INSERT INTO email_conversations (thread_id, email_from, last_category, context)
                VALUES (%s, %s, %s, %s)
                ON CONFLICT (thread_id) DO UPDATE
                SET last_category = EXCLUDED.last_category,
                    context = EXCLUDED.context,
                    updated_at = CURRENT_TIMESTAMP
            """, (thread_id, email_from, category, context))