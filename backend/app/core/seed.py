import os
import sys
from datetime import datetime, timedelta, timezone

# Add backend directory to sys.path
backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../backend"))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from app.core.database import Base, engine, SessionLocal
from app.core.security import get_password_hash
from app.models.user import User
from app.models.business import Customer, Order, Product, SupportTicket, Sale
from app.models.memory import Memory
from app.models.document import Document
from app.rag.document_loader import DocumentLoader
from app.rag.text_splitter import RecursiveTextSplitter
from app.rag.vector_store import vector_store

def seed_database():
    print("[Seed] Creating database tables...")
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    try:
        # 1. Create Default Users
        user = db.query(User).filter(User.email == "analyst@enterprise.ai").first()
        if not user:
            user = User(
                id="demo-user-123",
                email="analyst@enterprise.ai",
                hashed_password=get_password_hash("password123"),
                full_name="Alex Mercer (Lead AI Operations)",
                role="admin",
                is_active=True
            )
            db.add(user)
            db.commit()
            print("[Seed] Created default user: analyst@enterprise.ai")
        else:
            print("[Seed] Default user already exists.")

        # 2. Seed Customers
        if db.query(Customer).count() == 0:
            cust1 = Customer(
                id="cust-101",
                customer_code="CUST-1001",
                name="Jane Doe",
                email="jane.doe@globaltech.com",
                phone="+1 (555) 234-5678",
                company="GlobalTech Enterprises",
                tier="Enterprise"
            )
            cust2 = Customer(
                id="cust-102",
                customer_code="CUST-1002",
                name="Bruce Wayne",
                email="bruce@wayneenterprises.com",
                phone="+1 (555) 987-6543",
                company="Wayne Enterprises",
                tier="Premium"
            )
            cust3 = Customer(
                id="cust-103",
                customer_code="CUST-1003",
                name="Sarah Connor",
                email="s.connor@cyberdyne.org",
                phone="+1 (555) 345-6789",
                company="Cyberdyne Systems",
                tier="Standard"
            )
            db.add_all([cust1, cust2, cust3])
            db.commit()
            print("[Seed] Seeded 3 enterprise customers.")

        # 3. Seed Products
        if db.query(Product).count() == 0:
            p1 = Product(
                sku="SKU-HW-EDGE",
                name="Edge AI Gateway Server (4-Port)",
                category="Hardware",
                price=2499.00,
                stock=45,
                description="Ruggedized on-premise AI acceleration appliance.",
                warranty_days=365
            )
            p2 = Product(
                sku="SKU-LIC-ENT",
                name="Enterprise Cloud Suite Annual License",
                category="Software",
                price=12000.00,
                stock=999,
                description="Full SaaS subscription with 99.95% uptime SLA.",
                warranty_days=30
            )
            p3 = Product(
                sku="SKU-CAM-4K",
                name="Industrial 4K Vision Sensor",
                category="Hardware",
                price=850.00,
                stock=120,
                description="High precision optical inspection module.",
                warranty_days=180
            )
            db.add_all([p1, p2, p3])
            db.commit()
            print("[Seed] Seeded enterprise product catalog.")

        # 4. Seed Orders (Including benchmark Order #1024)
        if db.query(Order).count() == 0:
            now = datetime.now(timezone.utc)
            order_1024 = Order(
                id="ord-1024",
                order_number="1024",
                customer_id="cust-101",
                order_date=now - timedelta(days=16),
                delivery_date=now - timedelta(days=12),  # 12 days ago, within 30-day policy
                status="delivered",
                total_amount=2499.00,
                currency="USD",
                refund_status="none",
                items=[{
                    "sku": "SKU-HW-EDGE",
                    "name": "Edge AI Gateway Server (4-Port)",
                    "qty": 1,
                    "unit_price": 2499.00,
                    "condition": "Defective (Failed boot diagnostics after 12 days)",
                    "returnable": True
                }],
                shipping_address="100 Enterprise Way, Suite 400, Austin, TX",
                notes="Customer reported device reboot loop upon firmware update."
            )

            order_1025 = Order(
                id="ord-1025",
                order_number="1025",
                customer_id="cust-102",
                order_date=now - timedelta(days=5),
                delivery_date=now - timedelta(days=2),
                status="delivered",
                total_amount=1700.00,
                currency="USD",
                refund_status="none",
                items=[{
                    "sku": "SKU-CAM-4K",
                    "name": "Industrial 4K Vision Sensor",
                    "qty": 2,
                    "unit_price": 850.00,
                    "condition": "Unopened",
                    "returnable": True
                }],
                shipping_address="1007 Mountain Drive, Gotham, NJ",
                notes="Standard priority shipment."
            )
            db.add_all([order_1024, order_1025])
            db.commit()
            print("[Seed] Seeded orders (including Order #1024).")

        # 5. Seed Support Tickets
        if db.query(SupportTicket).count() == 0:
            ticket_501 = SupportTicket(
                id="tick-501",
                ticket_number="TICK-501",
                customer_id="cust-101",
                order_id="ord-1024",
                subject="Defective Edge AI Gateway on Order #1024 - Requesting Full Refund",
                issue_description="The Edge AI Gateway received 12 days ago has repeated kernel crashes and hardware parity errors. Customer is requesting an immediate full refund under warranty.",
                status="open",
                priority="high"
            )
            db.add(ticket_501)
            db.commit()
            print("[Seed] Seeded support ticket TICK-501 for Order #1024.")

        # 6. Seed Sales Data (Q1 - Q4 2024)
        if db.query(Sale).count() == 0:
            sales_records = [
                Sale(region="North America", quarter="Q3", year=2024, product_sku="SKU-HW-EDGE", units_sold=180, revenue=450000.0, target_revenue=400000.0),
                Sale(region="EMEA", quarter="Q3", year=2024, product_sku="SKU-HW-EDGE", units_sold=108, revenue=270000.0, target_revenue=250000.0),
                Sale(region="APAC", quarter="Q3", year=2024, product_sku="SKU-HW-EDGE", units_sold=95, revenue=237500.0, target_revenue=260000.0),
                Sale(region="North America", quarter="Q2", year=2024, product_sku="SKU-LIC-ENT", units_sold=40, revenue=480000.0, target_revenue=450000.0),
                Sale(region="North America", quarter="Q1", year=2024, product_sku="SKU-LIC-ENT", units_sold=35, revenue=420000.0, target_revenue=400000.0),
            ]
            db.add_all(sales_records)
            db.commit()
            print("[Seed] Seeded sales performance data for Q1-Q3 2024.")

        # 7. Seed Sample Long-Term Memories
        if db.query(Memory).count() == 0:
            mem1 = Memory(
                id="mem-1",
                user_id="demo-user-123",
                category="preference",
                content="User prefers responses to include explicit policy citations and concise bullet points.",
                importance=1.0,
                confidence=1.0
            )
            mem2 = Memory(
                id="mem-2",
                user_id="demo-user-123",
                category="fact",
                content="User oversees enterprise return authorizations and escalation workflows.",
                importance=0.9,
                confidence=0.95
            )
            db.add_all([mem1, mem2])
            db.commit()
            print("[Seed] Seeded initial long-term user memories.")

        # 8. Ingest Documents into RAG Vector Store
        docs_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../data/documents"))
        splitter = RecursiveTextSplitter(chunk_size=600, chunk_overlap=100)
        
        sample_files = [
            "refund_policy.pdf",
            "employee_handbook.pdf",
            "product_documentation.pdf",
            "customer_support_policy.pdf"
        ]

        for fname in sample_files:
            fpath = os.path.join(docs_dir, fname)
            if not os.path.exists(fpath):
                continue
            
            # Check if document already tracked in DB
            existing_doc = db.query(Document).filter(Document.filename == fname).first()
            if existing_doc:
                continue

            try:
                sections = DocumentLoader.load_file(fpath)
                all_chunks = []
                doc_id = f"doc_{fname.replace('.', '_')}"

                for text_content, meta in sections:
                    meta["document_id"] = doc_id
                    chunks = splitter.create_chunks_with_metadata(text_content, meta)
                    all_chunks.extend(chunks)

                vector_store.add_chunks(all_chunks)

                doc_entry = Document(
                    id=doc_id,
                    filename=fname,
                    file_type=fname.split(".")[-1],
                    file_size=os.path.getsize(fpath),
                    chunk_count=len(all_chunks),
                    checksum=DocumentLoader.calculate_checksum(fpath),
                    status="indexed",
                    doc_metadata={"chunk_count": len(all_chunks), "source": "sample_seed"}
                )
                db.add(doc_entry)
                db.commit()
                print(f"[Seed] Indexed {fname} ({len(all_chunks)} chunks) into Chroma vector store.")
            except Exception as e:
                print(f"[Seed] Error indexing {fname}: {e}")

    finally:
        db.close()
    print("[Seed] Enterprise database and vector store initialization complete!")

if __name__ == "__main__":
    seed_database()
