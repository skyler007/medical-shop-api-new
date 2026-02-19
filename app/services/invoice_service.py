from reportlab.lib.pagesizes import A4
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_RIGHT, TA_LEFT
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

    def generate_invoice_pdf(self, order, invoice, file_obj):
        """
        Generate invoice PDF dynamically into memory (BytesIO buffer)
        file_obj = io.BytesIO()
        """

        doc = SimpleDocTemplate(
            file_obj,
            pagesize=A4,
            rightMargin=30,
            leftMargin=30,
            topMargin=30,
            bottomMargin=30
        )

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

        # Header
        story.append(Paragraph(self.shop_name, title_style))
        story.append(Paragraph(self.shop_address, subtitle_style))
        story.append(Paragraph(
            f"Phone: {self.shop_phone} | Email: {self.shop_email}",
            subtitle_style
        ))
        story.append(Paragraph(f"GSTIN: {self.shop_gst}", subtitle_style))
        story.append(Spacer(1, 0.3 * inch))

        # Invoice Title
        story.append(Paragraph("<b>TAX INVOICE</b>", heading_style))
        story.append(Spacer(1, 0.2 * inch))

        # Invoice Details
        details_data = [
            ['Invoice No:', invoice.invoice_number,
             'Invoice Date:', invoice.invoice_date.strftime('%d-%m-%Y %I:%M %p')],
            ['Order No:', order.order_number,
             'Order Date:', order.order_date.strftime('%d-%m-%Y %I:%M %p')],
        ]

        details_table = Table(details_data, colWidths=[1.5*inch, 2*inch, 1.5*inch, 2*inch])
        details_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (2, 0), (2, -1), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ]))

        story.append(details_table)
        story.append(Spacer(1, 0.3 * inch))

        # Customer
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
        ]))

        story.append(customer_table)
        story.append(Spacer(1, 0.4 * inch))

        # Items Table
        items_data = [['#', 'Medicine Name', 'Qty', 'Pkg', 'Price', 'Amount']]

        for idx, item in enumerate(order.order_items, 1):
            items_data.append([
                str(idx),
                item.medicine.name,
                str(item.quantity),
                item.packaging_type.title(),
                f"₹{item.price_per_unit:.2f}",
                f"₹{item.total_price:.2f}"
            ])

        items_table = Table(
            items_data,
            colWidths=[0.4*inch, 3*inch, 0.6*inch, 0.8*inch, 1*inch, 1.2*inch]
        )

        items_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1a472a')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1),
             [colors.white, colors.HexColor('#f0f0f0')]),
        ]))

        story.append(items_table)
        story.append(Spacer(1, 0.3 * inch))

        # Totals
        totals_data = [
            ['', '', '', '', 'Subtotal:', f"₹{invoice.subtotal:.2f}"]
        ]

        if invoice.discount > 0:
            totals_data.append(
                ['', '', '', '', 'Discount:', f"-₹{invoice.discount:.2f}"]
            )

        if invoice.tax_amount > 0:
            totals_data.append(
                ['', '', '', '', f'GST ({invoice.tax_rate}%):',
                 f"₹{invoice.tax_amount:.2f}"]
            )

        totals_data.append(
            ['', '', '', '', 'Total Amount:',
             f"₹{invoice.total_amount:.2f}"]
        )

        totals_table = Table(
            totals_data,
            colWidths=[0.4*inch, 3*inch, 0.6*inch, 0.8*inch, 1*inch, 1.2*inch]
        )

        totals_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTNAME', (4, -1), (-1, -1), 'Helvetica-Bold'),
            ('LINEABOVE', (4, -1), (-1, -1), 1, colors.black),
        ]))

        story.append(totals_table)
        story.append(Spacer(1, 0.4 * inch))

        # Footer
        footer_style = ParagraphStyle(
            'Footer',
            parent=styles['Normal'],
            fontSize=8,
            textColor=colors.grey,
            alignment=TA_CENTER
        )

        story.append(Spacer(1, 0.5 * inch))
        story.append(Paragraph("Thank you for your business! | धन्यवाद!", footer_style))
        story.append(Paragraph(
            "For any queries, please contact us at the above details",
            footer_style
        ))

        # Build PDF into memory buffer
        doc.build(story)
