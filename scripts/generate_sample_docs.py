import os
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

DOCS_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../data/documents"))
os.makedirs(DOCS_DIR, exist_ok=True)

def create_refund_policy():
    pdf_path = os.path.join(DOCS_DIR, "refund_policy.pdf")
    doc = SimpleDocTemplate(pdf_path, pagesize=letter)
    styles = getSampleStyleSheet()
    story = []

    title_style = ParagraphStyle(
        "DocTitle",
        parent=styles["Heading1"],
        fontSize=20,
        leading=24,
        textColor=colors.HexColor("#1e293b"),
        spaceAfter=14
    )
    h2_style = ParagraphStyle(
        "DocH2",
        parent=styles["Heading2"],
        fontSize=14,
        leading=18,
        textColor=colors.HexColor("#0f172a"),
        spaceBefore=10,
        spaceAfter=6
    )
    body_style = ParagraphStyle(
        "DocBody",
        parent=styles["Normal"],
        fontSize=10,
        leading=14,
        textColor=colors.HexColor("#334155"),
        spaceAfter=8
    )

    story.append(Paragraph("Enterprise Cloud & Hardware Return & Refund Policy", title_style))
    story.append(Paragraph("<b>Effective Date:</b> January 1, 2024 | <b>Document Version:</b> 3.2 | <b>Ref:</b> POL-REF-2024", body_style))
    story.append(Spacer(1, 12))

    story.append(Paragraph("Section 1: General Policy Overview", h2_style))
    story.append(Paragraph(
        "1.1 Standard Return Window: Customers are eligible for product returns and refund requests within thirty (30) calendar days from the confirmed date of delivery. "
        "Requests submitted after 30 days are ineligible for standard refunds and will be routed to the warranty replacement program.",
        body_style
    ))
    story.append(Paragraph(
        "1.2 Proof of Purchase: A valid order number (e.g., ORD-1024 or 1024) and proof of purchase are required for all return processing.",
        body_style
    ))

    story.append(Paragraph("Section 2: Restocking Fees & Condition Exceptions", h2_style))
    story.append(Paragraph(
        "2.1 Standard Restocking Fee: All returned hardware items in good working condition are subject to a standard fifteen percent (15%) restocking fee deducted from the gross purchase amount.",
        body_style
    ))
    story.append(Paragraph(
        "2.2 Defective or Damaged Goods (DOA): If an item arrives defective, damaged in transit, or fails within thirty (30) days of delivery, "
        "the 15% restocking fee is strictly waived. The customer is entitled to a one hundred percent (100%) full refund of the total purchase amount, including all taxes.",
        body_style
    ))
    story.append(Paragraph(
        "2.3 Enterprise Software Licenses: Digital enterprise software licenses are non-refundable once activated unless accompanied by an SLA breach verification.",
        body_style
    ))
    story.append(Paragraph(
        "2.4 Return Shipping: Prepaid return shipping labels are provided free of charge for defective items. Standard voluntary returns incur customer-paid return freight.",
        body_style
    ))

    story.append(Paragraph("Section 3: Refund Calculation Examples", h2_style))
    story.append(Paragraph(
        "Example A (Defective Item): Total Order $2,499.00 -> Restocking Fee 0% -> Full Refund Amount: $2,499.00.<br/>"
        "Example B (Voluntary Return): Total Order $1,000.00 -> Restocking Fee 15% ($150.00) -> Net Refund Amount: $850.00.",
        body_style
    ))

    doc.build(story)
    print(f"Generated: {pdf_path}")

def create_employee_handbook():
    pdf_path = os.path.join(DOCS_DIR, "employee_handbook.pdf")
    doc = SimpleDocTemplate(pdf_path, pagesize=letter)
    styles = getSampleStyleSheet()
    story = []

    title_style = ParagraphStyle("DocTitle", parent=styles["Heading1"], fontSize=18, leading=22, textColor=colors.HexColor("#1e293b"))
    h2_style = ParagraphStyle("DocH2", parent=styles["Heading2"], fontSize=13, leading=16, textColor=colors.HexColor("#0f172a"))
    body_style = ParagraphStyle("DocBody", parent=styles["Normal"], fontSize=10, leading=14, textColor=colors.HexColor("#334155"))

    story.append(Paragraph("Enterprise Global Employee Handbook & Guidelines", title_style))
    story.append(Spacer(1, 10))
    story.append(Paragraph("Section 4: Paid Time Off (PTO) & Leave", h2_style))
    story.append(Paragraph("Full-time employees receive 20 days of paid time off per calendar year, accruing at 1.67 days per month. Unused PTO up to 5 days can roll over to the subsequent year.", body_style))
    story.append(Paragraph("Section 5: Remote Work & Equipment Reimbursement", h2_style))
    story.append(Paragraph("Employees in hybrid and remote classifications receive a one-time $1,000 home office stipend and a recurring $75 monthly internet reimbursement.", body_style))

    doc.build(story)
    print(f"Generated: {pdf_path}")

def create_product_documentation():
    pdf_path = os.path.join(DOCS_DIR, "product_documentation.pdf")
    doc = SimpleDocTemplate(pdf_path, pagesize=letter)
    styles = getSampleStyleSheet()
    story = []

    title_style = ParagraphStyle("DocTitle", parent=styles["Heading1"], fontSize=18, leading=22, textColor=colors.HexColor("#1e293b"))
    h2_style = ParagraphStyle("DocH2", parent=styles["Heading2"], fontSize=13, leading=16, textColor=colors.HexColor("#0f172a"))
    body_style = ParagraphStyle("DocBody", parent=styles["Normal"], fontSize=10, leading=14, textColor=colors.HexColor("#334155"))

    story.append(Paragraph("Enterprise Cloud Suite - Technical Architecture & SLAs", title_style))
    story.append(Spacer(1, 10))
    story.append(Paragraph("Section 1: Service Level Agreement (SLA)", h2_style))
    story.append(Paragraph("Enterprise Cloud Suite guarantees 99.95% monthly uptime. If monthly availability falls below 99.95%, enterprise customers are credited 10% of their monthly recurring charge. If availability falls below 99.0%, credits increase to 25%.", body_style))
    story.append(Paragraph("Section 2: API Rate Limits and Throughput", h2_style))
    story.append(Paragraph("Enterprise tier endpoints permit up to 5,000 requests per minute with a burst allowance of 10,000 RPM. Webhook deliveries retry up to 5 times with exponential backoff.", body_style))

    doc.build(story)
    print(f"Generated: {pdf_path}")

def create_customer_support_policy():
    pdf_path = os.path.join(DOCS_DIR, "customer_support_policy.pdf")
    doc = SimpleDocTemplate(pdf_path, pagesize=letter)
    styles = getSampleStyleSheet()
    story = []

    title_style = ParagraphStyle("DocTitle", parent=styles["Heading1"], fontSize=18, leading=22, textColor=colors.HexColor("#1e293b"))
    h2_style = ParagraphStyle("DocH2", parent=styles["Heading2"], fontSize=13, leading=16, textColor=colors.HexColor("#0f172a"))
    body_style = ParagraphStyle("DocBody", parent=styles["Normal"], fontSize=10, leading=14, textColor=colors.HexColor("#334155"))

    story.append(Paragraph("Customer Support Escalation & Compensation Policy", title_style))
    story.append(Spacer(1, 10))
    story.append(Paragraph("Section 1: Ticket Priority Response Windows", h2_style))
    story.append(Paragraph("Urgent tickets must receive a technical engineer response within 1 hour. High priority tickets within 4 hours. Medium and Low priority tickets within 24 business hours.", body_style))
    story.append(Paragraph("Section 2: Customer Goodwill Credits", h2_style))
    story.append(Paragraph("Customer success managers have discretionary authorization to issue customer goodwill credits up to $500 for unresolved technical disruptions exceeding 48 hours.", body_style))

    doc.build(story)
    print(f"Generated: {pdf_path}")

if __name__ == "__main__":
    create_refund_policy()
    create_employee_handbook()
    create_product_documentation()
    create_customer_support_policy()
    print("All sample PDF documents generated successfully.")
