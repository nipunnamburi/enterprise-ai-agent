from typing import Dict, Any, Optional
from datetime import datetime, timezone
from app.core.database import SessionLocal
from app.models.business import Customer, Order, SupportTicket
from app.tools.base import BaseTool

class CustomerOrderLookupTool(BaseTool):
    name = "customer_order_lookup"
    description = (
        "Retrieves comprehensive customer profile, order history, ordered item details, "
        "delivery dates, days elapsed since delivery, and associated support tickets. "
        "Use this tool when investigating a specific customer or order request (e.g. Order #1024 or Customer CUST-1001)."
    )
    category = "business_lookup"

    def get_parameters_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "order_number": {
                    "type": "string",
                    "description": "Order number identifier, e.g. '1024' or 'ORD-1024'."
                },
                "customer_code": {
                    "type": "string",
                    "description": "Customer account code, e.g. 'CUST-1001'."
                },
                "email": {
                    "type": "string",
                    "description": "Customer email address."
                }
            }
        }

    def run(
        self, 
        order_number: Optional[str] = None, 
        customer_code: Optional[str] = None, 
        email: Optional[str] = None, 
        **kwargs
    ) -> Dict[str, Any]:
        db = SessionLocal()
        try:
            order = None
            customer = None

            # Clean order number formatting
            if order_number:
                clean_ord = str(order_number).replace("#", "").strip()
                order = db.query(Order).filter(
                    (Order.order_number == clean_ord) | 
                    (Order.order_number == f"ORD-{clean_ord}") |
                    (Order.order_number == clean_ord.upper())
                ).first()

                if order:
                    customer = db.query(Customer).filter(Customer.id == order.customer_id).first()

            if not customer:
                if customer_code:
                    customer = db.query(Customer).filter(Customer.customer_code == customer_code.strip()).first()
                elif email:
                    customer = db.query(Customer).filter(Customer.email == email.strip()).first()

            if not order and not customer:
                return {
                    "success": False,
                    "error": "No matching customer or order found with provided identifiers."
                }

            result_data = {}

            if customer:
                result_data["customer"] = {
                    "id": customer.id,
                    "customer_code": customer.customer_code,
                    "name": customer.name,
                    "email": customer.email,
                    "company": customer.company,
                    "tier": customer.tier
                }

            if order:
                # Calculate days since delivery
                days_since_delivery = None
                now = datetime.now(timezone.utc)
                if order.delivery_date:
                    deliv_tz = order.delivery_date.replace(tzinfo=timezone.utc) if order.delivery_date.tzinfo is None else order.delivery_date
                    days_since_delivery = (now - deliv_tz).days

                # Find tickets for this order
                tickets = db.query(SupportTicket).filter(SupportTicket.order_id == order.id).all()

                result_data["order"] = {
                    "id": order.id,
                    "order_number": order.order_number,
                    "order_date": order.order_date.isoformat() if order.order_date else None,
                    "delivery_date": order.delivery_date.isoformat() if order.delivery_date else None,
                    "days_since_delivery": days_since_delivery,
                    "status": order.status,
                    "total_amount": order.total_amount,
                    "currency": order.currency,
                    "refund_status": order.refund_status,
                    "items": order.items,
                    "shipping_address": order.shipping_address,
                    "notes": order.notes,
                    "associated_tickets": [{
                        "ticket_number": t.ticket_number,
                        "subject": t.subject,
                        "status": t.status,
                        "priority": t.priority,
                        "issue_description": t.issue_description
                    } for t in tickets]
                }
            elif customer:
                # List recent orders for customer
                cust_orders = db.query(Order).filter(Order.customer_id == customer.id).all()
                result_data["recent_orders"] = [{
                    "order_number": o.order_number,
                    "order_date": o.order_date.isoformat() if o.order_date else None,
                    "status": o.status,
                    "total_amount": o.total_amount
                } for o in cust_orders]

            return {
                "success": True,
                "data": result_data
            }
        except Exception as e:
            return {"success": False, "error": f"Order lookup failed: {str(e)}"}
        finally:
            db.close()

customer_order_lookup_tool = CustomerOrderLookupTool()
