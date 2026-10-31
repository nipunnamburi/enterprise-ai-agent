from typing import Dict, Any, List, Optional
from sqlalchemy import func
from app.core.database import SessionLocal
from app.models.business import Customer, Order, Product, SupportTicket, Sale
from app.tools.base import BaseTool

class QueryDatabaseTool(BaseTool):
    name = "query_database"
    description = (
        "Safely queries structured enterprise business data from PostgreSQL/SQLite. "
        "Supports querying entities: 'customers', 'orders', 'products', 'support_tickets', 'sales'. "
        "All queries are strictly parameterized and guarded against SQL injection."
    )
    category = "database"

    def get_parameters_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "entity": {
                    "type": "string",
                    "enum": ["customers", "orders", "products", "support_tickets", "sales"],
                    "description": "The enterprise table/entity to query."
                },
                "filters": {
                    "type": "object",
                    "description": "Key-value filter criteria (e.g. {'status': 'delivered'}, {'region': 'North America', 'quarter': 'Q3', 'year': 2024}, {'tier': 'Enterprise'})."
                },
                "aggregation": {
                    "type": "string",
                    "enum": ["none", "count", "sum_revenue", "avg_revenue"],
                    "description": "Optional aggregation calculation (e.g. 'sum_revenue' for sales)."
                },
                "limit": {
                    "type": "integer",
                    "description": "Maximum number of rows to return (default: 10, max: 50).",
                    "default": 10
                }
            },
            "required": ["entity"]
        }

    def run(
        self, 
        entity: str, 
        filters: Optional[Dict[str, Any]] = None, 
        aggregation: str = "none", 
        limit: int = 10, 
        **kwargs
    ) -> Dict[str, Any]:
        filters = filters or {}
        limit = min(max(1, limit), 50)
        db = SessionLocal()

        try:
            if entity == "customers":
                query = db.query(Customer)
                if "customer_code" in filters:
                    query = query.filter(Customer.customer_code == str(filters["customer_code"]))
                if "email" in filters:
                    query = query.filter(Customer.email == str(filters["email"]))
                if "tier" in filters:
                    query = query.filter(Customer.tier == str(filters["tier"]))
                if "name" in filters:
                    query = query.filter(Customer.name.ilike(f"%{filters['name']}%"))
                
                rows = query.limit(limit).all()
                data = [{
                    "id": r.id,
                    "customer_code": r.customer_code,
                    "name": r.name,
                    "email": r.email,
                    "company": r.company,
                    "tier": r.tier,
                    "created_at": r.created_at.isoformat() if r.created_at else None
                } for r in rows]

            elif entity == "orders":
                query = db.query(Order)
                if "order_number" in filters:
                    query = query.filter(Order.order_number == str(filters["order_number"]))
                if "status" in filters:
                    query = query.filter(Order.status == str(filters["status"]))
                if "customer_id" in filters:
                    query = query.filter(Order.customer_id == str(filters["customer_id"]))
                if "refund_status" in filters:
                    query = query.filter(Order.refund_status == str(filters["refund_status"]))
                
                rows = query.limit(limit).all()
                data = [{
                    "id": r.id,
                    "order_number": r.order_number,
                    "customer_id": r.customer_id,
                    "order_date": r.order_date.isoformat() if r.order_date else None,
                    "status": r.status,
                    "total_amount": r.total_amount,
                    "currency": r.currency,
                    "items": r.items,
                    "refund_status": r.refund_status,
                    "delivery_date": r.delivery_date.isoformat() if r.delivery_date else None
                } for r in rows]

            elif entity == "products":
                query = db.query(Product)
                if "sku" in filters:
                    query = query.filter(Product.sku == str(filters["sku"]))
                if "category" in filters:
                    query = query.filter(Product.category == str(filters["category"]))
                if "name" in filters:
                    query = query.filter(Product.name.ilike(f"%{filters['name']}%"))
                
                rows = query.limit(limit).all()
                data = [{
                    "id": r.id,
                    "sku": r.sku,
                    "name": r.name,
                    "category": r.category,
                    "price": r.price,
                    "stock": r.stock,
                    "warranty_days": r.warranty_days
                } for r in rows]

            elif entity == "support_tickets":
                query = db.query(SupportTicket)
                if "ticket_number" in filters:
                    query = query.filter(SupportTicket.ticket_number == str(filters["ticket_number"]))
                if "status" in filters:
                    query = query.filter(SupportTicket.status == str(filters["status"]))
                if "priority" in filters:
                    query = query.filter(SupportTicket.priority == str(filters["priority"]))
                if "order_id" in filters:
                    query = query.filter(SupportTicket.order_id == str(filters["order_id"]))
                
                rows = query.limit(limit).all()
                data = [{
                    "id": r.id,
                    "ticket_number": r.ticket_number,
                    "customer_id": r.customer_id,
                    "order_id": r.order_id,
                    "subject": r.subject,
                    "issue_description": r.issue_description,
                    "status": r.status,
                    "priority": r.priority,
                    "created_at": r.created_at.isoformat() if r.created_at else None
                } for r in rows]

            elif entity == "sales":
                query = db.query(Sale)
                if "region" in filters:
                    query = query.filter(Sale.region == str(filters["region"]))
                if "quarter" in filters:
                    query = query.filter(Sale.quarter == str(filters["quarter"]))
                if "year" in filters:
                    query = query.filter(Sale.year == int(filters["year"]))
                if "product_sku" in filters:
                    query = query.filter(Sale.product_sku == str(filters["product_sku"]))

                if aggregation == "sum_revenue":
                    total_rev = query.with_entities(func.sum(Sale.revenue)).scalar() or 0.0
                    total_target = query.with_entities(func.sum(Sale.target_revenue)).scalar() or 0.0
                    return {
                        "success": True,
                        "entity": entity,
                        "aggregation": aggregation,
                        "total_actual_revenue": round(total_rev, 2),
                        "total_target_revenue": round(total_target, 2),
                        "records_matched": query.count()
                    }

                rows = query.limit(limit).all()
                data = [{
                    "id": r.id,
                    "region": r.region,
                    "quarter": r.quarter,
                    "year": r.year,
                    "product_sku": r.product_sku,
                    "units_sold": r.units_sold,
                    "revenue": r.revenue,
                    "target_revenue": r.target_revenue
                } for r in rows]
            else:
                return {"success": False, "error": f"Invalid entity: {entity}"}

            return {
                "success": True,
                "entity": entity,
                "count": len(data),
                "data": data
            }
        except Exception as e:
            return {"success": False, "error": f"Database query error: {str(e)}"}
        finally:
            db.close()

query_database_tool = QueryDatabaseTool()
