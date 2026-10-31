import os
import sys
import pytest

# Ensure backend root is on sys.path
backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from app.core.database import Base, engine, SessionLocal
from app.core.security import get_password_hash
from app.models.user import User
from app.models.business import Customer, Order, Product, SupportTicket, Sale


@pytest.fixture(scope="session", autouse=True)
def setup_database_schema_and_seed():
    """Ensure database tables exist and essential seed data is available for test suite."""
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    # Seed default user if not present
    user = db.query(User).filter(User.email == "analyst@enterprise.ai").first()
    if not user:
        user = User(
            id="demo-user-123",
            email="analyst@enterprise.ai",
            hashed_password=get_password_hash("password123"),
            full_name="Alex Mercer (Lead AI Operations)",
            role="admin",
            is_active=True,
        )
        db.add(user)
        db.commit()

    # Seed customer and order if not present (needed by order lookup & db query tests)
    cust = db.query(Customer).filter(Customer.id == "cust-101").first()
    if not cust:
        cust = Customer(
            id="cust-101",
            customer_code="CUST-1001",
            name="Jane Doe",
            email="jane.doe@globaltech.com",
            phone="+1 (555) 234-5678",
            company="GlobalTech Enterprises",
            tier="Enterprise",
        )
        db.add(cust)
        db.commit()

    order = db.query(Order).filter(Order.order_number == "1024").first()
    if not order:
        from datetime import datetime, timezone
        order = Order(
            id="ord-1024",
            order_number="1024",
            customer_id=cust.id,
            status="delivered",
            total_amount=2499.00,
            currency="USD",
            items=[{"sku": "ENT-SRV-01", "name": "AI Gateway Appliance", "quantity": 1, "unit_price": 2499.00}],
            order_date=datetime.now(timezone.utc),
        )
        db.add(order)
        db.commit()

    # Seed sales data if not present (needed by query_database tool test)
    sale = db.query(Sale).filter(Sale.quarter == "Q3", Sale.year == 2024).first()
    if not sale:
        sale = Sale(
            id="sale-q3-2024",
            region="North America",
            quarter="Q3",
            year=2024,
            product_sku="ENT-SRV-01",
            units_sold=42,
            revenue=1250000.0,
            target_revenue=1200000.0,
        )
        db.add(sale)
        db.commit()

    db.close()
    yield
