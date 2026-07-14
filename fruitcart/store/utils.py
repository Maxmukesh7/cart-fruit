import io
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

def generate_invoice_pdf(order):
    """
    Generates a professional PDF invoice for the given order using ReportLab
    and returns a BytesIO buffer of the PDF data.
    """
    buffer = io.BytesIO()
    
    # Page size: letter (612 x 792 points)
    # Margins: 0.5 inch (36 points)
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        leftMargin=36,
        rightMargin=36,
        topMargin=36,
        bottomMargin=36
    )

    story = []
    styles = getSampleStyleSheet()

    # Theme colors
    primary_color = colors.HexColor("#2E7D32")    # Deep Green
    secondary_color = colors.HexColor("#37474F")  # Dark Slate
    light_bg = colors.HexColor("#F1F8E9")         # Very light green
    divider_color = colors.HexColor("#E0E0E0")     # Light Grey

    # Styles
    title_style = ParagraphStyle(
        'InvoiceTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=24,
        leading=28,
        textColor=primary_color
    )

    subtitle_style = ParagraphStyle(
        'InvoiceSubtitle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=10,
        leading=14,
        textColor=colors.HexColor("#757575")
    )

    section_heading = ParagraphStyle(
        'SectionHeading',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=12,
        leading=16,
        textColor=secondary_color
    )

    body_style = ParagraphStyle(
        'InvoiceBody',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        leading=13,
        textColor=colors.HexColor("#212121")
    )

    body_bold = ParagraphStyle(
        'InvoiceBodyBold',
        parent=body_style,
        fontName='Helvetica-Bold'
    )

    table_header_style = ParagraphStyle(
        'TableHeader',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=10,
        leading=14,
        textColor=colors.white
    )

    # 1. Header (Logo / Details Grid)
    header_left = [
        Paragraph("🍊 <b>FruitCart</b>", title_style),
        Spacer(1, 4),
        Paragraph("Fresh seasonal fruits delivered straight to your doorstep.", subtitle_style),
        Paragraph("hello@fruitcart.com | +91 98765 43210", subtitle_style),
    ]

    invoice_no = f"FC{1000 + order.pk}"
    order_date = order.created_at.strftime('%d %B %Y, %I:%M %p')

    # Compute payment status message
    if order.status == 'Delivered':
        payment_status = "PAID"
    elif order.status == 'Cancelled':
        payment_status = "CANCELLED"
    else:
        payment_status = "PENDING ON DELIVERY"

    header_right = [
        Paragraph("<b>INVOICE</b>", ParagraphStyle('InvText', parent=title_style, alignment=2)),
        Spacer(1, 4),
        Paragraph(f"<b>Invoice No:</b> {invoice_no}", ParagraphStyle('InvDetail1', parent=body_style, alignment=2)),
        Paragraph(f"<b>Order ID:</b> #{order.pk}", ParagraphStyle('InvDetail2', parent=body_style, alignment=2)),
        Paragraph(f"<b>Date:</b> {order_date}", ParagraphStyle('InvDetail3', parent=body_style, alignment=2)),
    ]

    header_table = Table([[header_left, header_right]], colWidths=[320, 220])
    header_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('PADDING', (0, 0), (-1, -1), 0),
    ]))
    story.append(header_table)
    story.append(Spacer(1, 20))

    # Thin Divider Line
    story.append(Table([[""]], colWidths=[540], rowHeights=[1], style=TableStyle([
        ('LINEBELOW', (0, 0), (-1, -1), 1, divider_color),
        ('PADDING', (0, 0), (-1, -1), 0),
    ])))
    story.append(Spacer(1, 15))

    # 2. Shipping & Payment Block
    shipping_info = [
        Paragraph("<b>SHIPPED TO:</b>", section_heading),
        Spacer(1, 4),
        Paragraph(f"<b>{order.full_name}</b>", body_bold),
        Paragraph(f"Phone: {order.phone}", body_style),
        Paragraph(f"{order.address}", body_style),
        Paragraph(f"{order.city} - {order.pincode}", body_style),
    ]

    payment_info = [
        Paragraph("<b>PAYMENT DETAILS:</b>", section_heading),
        Spacer(1, 4),
        Paragraph("<b>Method:</b> Cash on Delivery (COD)", body_style),
        Paragraph(f"<b>Status:</b> <font color='{ '#1B5E20' if payment_status == 'PAID' else '#B71C1C' }'><b>{payment_status}</b></font>", body_style),
        Paragraph(f"<b>Order Status:</b> {order.status}", body_style),
    ]

    details_table = Table([[shipping_info, payment_info]], colWidths=[270, 270])
    details_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('PADDING', (0, 0), (-1, -1), 0),
    ]))
    story.append(details_table)
    story.append(Spacer(1, 25))

    # 3. Order Items Table
    items_table_data = [
        [
            Paragraph("Item Details", table_header_style),
            Paragraph("Price / Unit", table_header_style),
            Paragraph("Quantity", table_header_style),
            Paragraph("Subtotal", ParagraphStyle('THRight', parent=table_header_style, alignment=2)),
        ]
    ]

    for item in order.items.all():
        unit_str = f" / {item.unit_display}" if item.unit_display else ""
        items_table_data.append([
            Paragraph(item.fruit_name, body_style),
            Paragraph(f"₹{item.price}{unit_str}", body_style),
            Paragraph(str(item.quantity), body_style),
            Paragraph(f"₹{item.subtotal}", ParagraphStyle('TDRight', parent=body_style, alignment=2)),
        ])

    # Grand Total row
    items_table_data.append([
        Paragraph("<b>Grand Total</b>", body_bold),
        "",
        "",
        Paragraph(f"<b>₹{order.total_amount}</b>", ParagraphStyle('TotalRight', parent=body_bold, alignment=2)),
    ])

    items_table = Table(items_table_data, colWidths=[240, 120, 80, 100])
    
    # Table styles setup
    table_styles = [
        ('BACKGROUND', (0, 0), (-1, 0), primary_color),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('PADDING', (0, 0), (-1, -1), 8),
        ('SPAN', (0, -1), (2, -1)),
        ('BACKGROUND', (0, -1), (-1, -1), light_bg),
    ]

    # Row backgrounds and bottom lines
    for i in range(1, len(items_table_data) - 1):
        if i % 2 == 0:
            table_styles.append(('BACKGROUND', (0, i), (-1, i), colors.HexColor("#F9F9F9")))
        table_styles.append(('LINEBELOW', (0, i), (-1, i), 0.5, divider_color))

    items_table.setStyle(TableStyle(table_styles))
    story.append(items_table)
    story.append(Spacer(1, 35))

    # 4. Computer-Generated Note / Footer
    footer_style = ParagraphStyle(
        'InvoiceFooter',
        parent=styles['Normal'],
        fontName='Helvetica-Oblique',
        fontSize=9,
        leading=13,
        alignment=1,
        textColor=colors.HexColor("#9E9E9E")
    )
    story.append(Paragraph("Thank you for shopping with FruitCart! 🍒", footer_style))
    story.append(Spacer(1, 4))
    story.append(Paragraph("This is a computer-generated invoice. No physical signature is required.", footer_style))

    doc.build(story)
    buffer.seek(0)
    return buffer
