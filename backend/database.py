import psycopg2
from psycopg2.extras import RealDictCursor
from datetime import datetime
import os

class Database:
    def __init__(self):
        self.conn = psycopg2.connect(
            host=os.getenv('DB_HOST', 'localhost'),
            database=os.getenv('DB_NAME', 'email_agent'),
            user=os.getenv('DB_USER', 'postgres'),
            password=os.getenv('DB_PASSWORD', 'password')
        )
        self.conn.autocommit = True  # Enable autocommit to prevent transaction blocks
        self.create_tables()
    
    def create_tables(self):
        with self.conn.cursor() as cur:
            # Enable vector extension first (if available)
            try:
                cur.execute("CREATE EXTENSION IF NOT EXISTS vector")
            except Exception as e:
                print(f"Warning: Could not create vector extension: {e}")
                print("Vector search will fall back to numpy implementation")
            
            # Orders table
            cur.execute("""
                CREATE TABLE IF NOT EXISTS orders (
                    id SERIAL PRIMARY KEY,
                    order_id VARCHAR(100) UNIQUE NOT NULL,
                    customer_email VARCHAR(255),
                    refund_requested BOOLEAN DEFAULT FALSE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Unhandled emails table
            cur.execute("""
                CREATE TABLE IF NOT EXISTS unhandled_emails (
                    id SERIAL PRIMARY KEY,
                    email_from VARCHAR(255),
                    subject TEXT,
                    body TEXT,
                    category VARCHAR(50),
                    importance VARCHAR(20),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Not found refund requests
            cur.execute("""
                CREATE TABLE IF NOT EXISTS not_found_refunds (
                    id SERIAL PRIMARY KEY,
                    email_from VARCHAR(255),
                    order_id VARCHAR(100),
                    message TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Knowledge base for RAG
            try:
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS knowledge_base (
                        id SERIAL PRIMARY KEY,
                        question TEXT,
                        answer TEXT,
                        embedding VECTOR(384)  -- Using sentence-transformers
                    )
                """)
            except Exception:
                # Fallback without vector type if extension not available
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS knowledge_base (
                        id SERIAL PRIMARY KEY,
                        question TEXT,
                        answer TEXT,
                        embedding TEXT  -- JSON array fallback
                    )
                """)
            
            # Email conversations tracking
            cur.execute("""
                CREATE TABLE IF NOT EXISTS email_conversations (
                    id SERIAL PRIMARY KEY,
                    thread_id VARCHAR(255) UNIQUE NOT NULL,
                    email_from VARCHAR(255),
                    last_category VARCHAR(50),
                    context TEXT,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Create indexes for performance
            cur.execute("CREATE INDEX IF NOT EXISTS idx_orders_order_id ON orders(order_id)")
            cur.execute("CREATE INDEX IF NOT EXISTS idx_unhandled_emails_category ON unhandled_emails(category)")
            cur.execute("CREATE INDEX IF NOT EXISTS idx_unhandled_emails_importance ON unhandled_emails(importance)")
            cur.execute("CREATE INDEX IF NOT EXISTS idx_conversations_thread_id ON email_conversations(thread_id)")
            cur.execute("CREATE INDEX IF NOT EXISTS idx_not_found_refunds_email ON not_found_refunds(email_from)")
    
    def get_order(self, order_id):
        with self.conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("SELECT * FROM orders WHERE order_id = %s", (order_id,))
            return cur.fetchone()
    
    def mark_refund_requested(self, order_id):
        with self.conn.cursor() as cur:
            cur.execute(
                "UPDATE orders SET refund_requested = TRUE WHERE order_id = %s",
                (order_id,)
            )
    
    def save_unhandled_email(self, email_from, subject, body, category, importance):
        with self.conn.cursor() as cur:
            cur.execute("""
                INSERT INTO unhandled_emails (email_from, subject, body, category, importance)
                VALUES (%s, %s, %s, %s, %s)
            """, (email_from, subject, body, category, importance))
    
    def save_not_found_refund(self, email_from, order_id, message):
        with self.conn.cursor() as cur:
            cur.execute("""
                INSERT INTO not_found_refunds (email_from, order_id, message)
                VALUES (%s, %s, %s)
            """, (email_from, order_id, message))
    
    def add_sample_data(self):
        """Add sample orders for testing"""
        sample_orders = [
            ('ORD-12345', 'customer1@example.com'),
            ('ORD-67890', 'customer2@example.com'),
            ('ORD-11111', 'test@example.com'),
            ('ORD-22222', 'demo@example.com'),
            ('ORD-33333', 'sample@example.com')
        ]
        
        with self.conn.cursor() as cur:
            for order_id, customer_email in sample_orders:
                cur.execute("""
                    INSERT INTO orders (order_id, customer_email)
                    VALUES (%s, %s)
                    ON CONFLICT (order_id) DO NOTHING
                """, (order_id, customer_email))
            print("Sample orders added to database")