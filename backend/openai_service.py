import os
import openai
from typing import Optional, Dict
import json

class OpenAIService:
    def __init__(self):
        self.client = openai.OpenAI(
            api_key=os.getenv('OPENAI_API_KEY')
        )
        self.model = "gpt-3.5-turbo"
    
    def generate_question_response(self, question: str, knowledge_base_info: str = None) -> Optional[str]:
        """Generate response for customer questions"""
        try:
            # Truncate question if too long (keep within token limits)
            max_question_length = 2000  # chars, roughly 500 tokens
            if len(question) > max_question_length:
                question = question[:max_question_length] + "... [truncated]"
            
            system_prompt = """You are a helpful customer support agent for an e-commerce company. 
            Your responses should be:
            - Professional and friendly
            - Concise but informative
            - Helpful and solution-oriented
            - Always end with "Best regards, Customer Support Team"
            
            Company Information:
            - Business hours: Monday-Friday 9AM-5PM EST
            - Standard shipping: 5-7 business days
            - Express shipping: 2-3 business days
            - International shipping: 10-14 business days
            - Payment methods: Major credit cards, PayPal, Apple Pay
            - Return policy: 30 days with original receipt
            - Damaged items: Contact within 48 hours with photos
            """
            
            if knowledge_base_info:
                system_prompt += f"\n\nRelevant information: {knowledge_base_info}"
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"Customer question: {question}"}
                ],
                max_tokens=300,
                temperature=0.7
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            print(f"OpenAI API error in question response: {e}")
            return None
    
    def generate_refund_response(self, context: str, order_id: str = None, order_found: bool = None) -> Optional[str]:
        """Generate response for refund requests"""
        try:
            system_prompt = """You are a customer support agent handling refund requests.
            Your responses should be:
            - Empathetic and understanding
            - Professional and clear
            - Provide specific next steps
            - Always end with "Best regards, Customer Support Team"
            
            Company refund policy:
            - Refunds processed within 3 business days
            - Order ID format: ORD-XXXXX
            - Customer needs to provide valid order ID
            """
            
            if order_id and order_found:
                user_message = f"Customer is requesting a refund for order {order_id}. The order exists in our system."
            elif order_id and not order_found:
                user_message = f"Customer provided order ID {order_id}, but it doesn't exist in our system."
            else:
                user_message = f"Customer is requesting a refund but didn't provide an order ID. Context: {context}"
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_message}
                ],
                max_tokens=200,
                temperature=0.5
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            print(f"OpenAI API error in refund response: {e}")
            return None
    
    def generate_follow_up_response(self, conversation_history: str, latest_message: str) -> Optional[str]:
        """Generate follow-up responses for complex conversations"""
        try:
            system_prompt = """You are a customer support agent continuing a conversation.
            Be helpful, professional, and try to resolve the customer's issue.
            Always end with "Best regards, Customer Support Team"
            """
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"Conversation history: {conversation_history}\n\nLatest message: {latest_message}"}
                ],
                max_tokens=250,
                temperature=0.6
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            print(f"OpenAI API error in follow-up response: {e}")
            return None
    
    def is_available(self) -> bool:
        """Check if OpenAI service is available"""
        return bool(os.getenv('OPENAI_API_KEY'))