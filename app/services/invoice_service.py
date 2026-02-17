from reportlab.lib.pagesizes import A4
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_RIGHT, TA_LEFT
from reportlab.pdfgen import canvas
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()

class InvoiceGenerator:
    def __init__(self):
        self.shop_name = os.getenv("SHOP_NAME", "Sanjivani Medical Store")
        self.shop_address = os.getenv("SHOP_ADDRESS", "123 Main Street, City")
        self.shop_phone = os.getenv("SHOP_PHONE", "+91-9876543210")
        self.shop_email = os.getenv("SHOP_EMAIL", "info@medical.com")
        self.shop_gst = os.getenv("SHOP_GST", "22AAAAA0000A1Z5")
        
    def generate_invoice_pdf(self, order, invoice, output_path):
        """Generate professional invoice PDF"""
        
        doc = SimpleDocTemplate(output_path, pagesize=A4,
                                rightMargin=30, leftMargin=30,
                                topMargin=30, bottomMargin=30)
        
        story = []
        styles = getSampleStyleSheet()
        
        # Custom styles
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#1a472a'),
            spaceAfter=6,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        )
        
        subtitle_style = ParagraphStyle(
            'Subtitle',
            parent=styles['Normal'],
            fontSize=10,
            textColor=colors.grey,
            alignment=TA_CENTER,
            spaceAfter=12
        )
        
        heading_style = ParagraphStyle(
            'Heading',
            parent=styles['Heading2'],
            fontSize=12,
            textColor=colors.HexColor('#1a472a'),
            spaceAfter=12,
            fontName='Helvetica-Bold'
        )
        
        # Header - Shop Name
        story.append(Paragraph(self.shop_name, title_style))
        story.append(Paragraph(f"{self.shop_address}", subtitle_style))
        story.append(Paragraph(f"Phone: {self.shop_phone} | Email: {self.shop_email}", subtitle_style))
        story.append(Paragraph(f"GSTIN: {self.shop_gst}", subtitle_style))
        story.append(Spacer(1, 0.3*inch))
        
        # Invoice Title
        invoice_title = f"<b>TAX INVOICE</b>"
        story.append(Paragraph(invoice_title, heading_style))
        story.append(Spacer(1, 0.2*inch))
        
        # Invoice and Customer Details
        details_data = [
            ['Invoice No:', invoice.invoice_number, 'Invoice Date:', invoice.invoice_date.strftime('%d-%m-%Y %I:%M %p')],
            ['Order No:', order.order_number, 'Order Date:', order.order_date.strftime('%d-%m-%Y %I:%M %p')],
        ]
        
        details_table = Table(details_data, colWidths=[1.5*inch, 2*inch, 1.5*inch, 2*inch])
        details_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (2, 0), (2, -1), 'Helvetica-Bold'),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ]))
        story.append(details_table)
        story.append(Spacer(1, 0.2*inch))
        
        # Customer Details
        story.append(Paragraph("<b>Bill To:</b>", heading_style))
        customer_data = [
            ['Name:', order.customer.name],
            ['Phone:', order.customer.phone],
        ]
        if order.customer.address:
            customer_data.append(['Address:', order.customer.address])
        
        customer_table = Table(customer_data, colWidths=[1.5*inch, 5*inch])
        customer_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ]))
        story.append(customer_table)
        story.append(Spacer(1, 0.3*inch))
        
        # Items Table Header
        items_data = [['#', 'Medicine Name', 'Qty', 'Pkg', 'Price', 'Amount']]
        
        # Items
        for idx, item in enumerate(order.order_items, 1):
            items_data.append([
                str(idx),
                item.medicine.name,
                str(item.quantity),
                item.packaging_type.title(),
                f"₹{item.price_per_unit:.2f}",
                f"₹{item.total_price:.2f}"
            ])
        
        # Create items table
        items_table = Table(items_data, colWidths=[0.4*inch, 3*inch, 0.6*inch, 0.8*inch, 1*inch, 1.2*inch])
        items_table.setStyle(TableStyle([
            # Header
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1a472a')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
            
            # Body
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
            ('ALIGN', (0, 1), (0, -1), 'CENTER'),
            ('ALIGN', (1, 1), (1, -1), 'LEFT'),
            ('ALIGN', (2, 1), (-1, -1), 'RIGHT'),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f0f0f0')]),
            ('TOPPADDING', (0, 1), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 1), (-1, -1), 6),
        ]))
        story.append(items_table)
        story.append(Spacer(1, 0.3*inch))
        
        # Totals
        totals_data = [
            ['', '', '', '', 'Subtotal:', f"₹{invoice.subtotal:.2f}"],
        ]
        
        if invoice.discount > 0:
            totals_data.append(['', '', '', '', 'Discount:', f"-₹{invoice.discount:.2f}"])
        
        if invoice.tax_amount > 0:
            totals_data.append(['', '', '', '', f'GST ({invoice.tax_rate}%):', f"₹{invoice.tax_amount:.2f}"])
        
        totals_data.append(['', '', '', '', 'Total Amount:', f"₹{invoice.total_amount:.2f}"])
        
        totals_table = Table(totals_data, colWidths=[0.4*inch, 3*inch, 0.6*inch, 0.8*inch, 1*inch, 1.2*inch])
        totals_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -2), 9),
            ('FONTNAME', (4, -1), (-1, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (4, -1), (-1, -1), 11),
            ('ALIGN', (4, 0), (-1, -1), 'RIGHT'),
            ('LINEABOVE', (4, -1), (-1, -1), 1, colors.black),
            ('TOPPADDING', (0, 0), (-1, -1), 4),
            ('BOTTOMPADDING', (0, 0), (-1, -2), 4),
            ('BOTTOMPADDING', (4, -1), (-1, -1), 8),
        ]))
        story.append(totals_table)
        story.append(Spacer(1, 0.4*inch))
        
        # Payment Status
        payment_status = f"<b>Payment Status:</b> {invoice.payment_status.title()}"
        if invoice.payment_method:
            payment_status += f" | <b>Payment Method:</b> {invoice.payment_method.title()}"
        story.append(Paragraph(payment_status, styles['Normal']))
        story.append(Spacer(1, 0.3*inch))
        
        # Footer
        footer_style = ParagraphStyle(
            'Footer',
            parent=styles['Normal'],
            fontSize=8,
            textColor=colors.grey,
            alignment=TA_CENTER
        )
        story.append(Spacer(1, 0.5*inch))
        story.append(Paragraph("Thank you for your business! | धन्यवाद!", footer_style))
        story.append(Paragraph("For any queries, please contact us at the above details", footer_style))
        
        # Build PDF
        doc.build(story)
        return output_path
