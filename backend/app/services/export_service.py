import io
import csv
from decimal import Decimal
from datetime import datetime
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import func

from ..models.customers import Customer
from ..models.segments import Segment
from ..models.transactions import Transaction

from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

async def generate_customers_csv(db: AsyncSession) -> io.StringIO:
    """
    Generate CSV file of all customers and their segment assignments.
    """
    csv_buffer = io.StringIO()
    writer = csv.writer(csv_buffer)
    
    # Write header
    writer.writerow([
        "Customer ID", "External ID", "Age", "Gender", "Region", "Membership Status",
        "Annual Income (INR)", "Total Spend (INR)", "Avg Order Value (INR)", "CLV Estimate",
        "Purchase Frequency", "Days Since Last Purchase", "Cart Abandonment Rate",
        "Return Rate", "Email Open Rate", "App Usage Score", "Loyalty Points", "Referrals",
        "RFM Score", "Engagement Index", "Churn Probability", "Value Tier", "Predicted 90d CLV",
        "Preferred Category", "Segment ID", "Segment Name"
    ])
    
    # Fetch customers and segments
    result = await db.execute(
        select(Customer)
        .options(selectinload(Customer.segment))
        .order_by(Customer.external_id.asc())
    )
    customers = result.scalars().all()
    
    for c in customers:
        writer.writerow([
            str(c.id), c.external_id, c.age, c.gender, c.region, c.membership_status,
            float(c.annual_income or 0.0), float(c.total_spend or 0.0), float(c.avg_order_value or 0.0),
            float(c.clv_estimate or 0.0), c.purchase_frequency, c.days_since_last_purchase,
            float(c.cart_abandonment_rate or 0.0), float(c.return_rate or 0.0),
            float(c.email_open_rate or 0.0), float(c.app_usage_score or 0.0),
            c.loyalty_points, c.referral_count,
            float(c.rfm_score or 0.0), float(c.engagement_index or 0.0),
            float(c.churn_probability or 0.0), c.value_tier,
            float(c.predicted_clv_90d or 0.0), c.preferred_category,
            c.segment_id, c.segment.name if c.segment else "Unassigned"
        ])
        
    csv_buffer.seek(0)
    return csv_buffer

async def generate_executive_pdf(db: AsyncSession) -> io.BytesIO:
    """
    Generate a formatted ReportLab PDF containing segmentation KPIs and executive overview.
    """
    pdf_buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        pdf_buffer,
        pagesize=letter,
        rightMargin=40, leftMargin=40, topMargin=40, bottomMargin=40
    )
    
    styles = getSampleStyleSheet()
    
    # Custom styles
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=24,
        leading=28,
        textColor=colors.HexColor('#0F172A'), # Slate 900
        spaceAfter=15
    )
    
    subtitle_style = ParagraphStyle(
        'DocSubtitle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=12,
        leading=16,
        textColor=colors.HexColor('#64748B'), # Slate 500
        spaceAfter=30
    )
    
    h1_style = ParagraphStyle(
        'SectionH1',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=16,
        leading=20,
        textColor=colors.HexColor('#0F172A'),
        spaceBefore=15,
        spaceAfter=10,
        keepWithNext=True
    )
    
    body_style = ParagraphStyle(
        'BodyTextCustom',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=10,
        leading=14,
        textColor=colors.HexColor('#334155'), # Slate 700
        spaceAfter=10
    )

    table_header_style = ParagraphStyle(
        'TableHeader',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=9,
        leading=11,
        textColor=colors.white
    )

    table_cell_style = ParagraphStyle(
        'TableCell',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        leading=11,
        textColor=colors.HexColor('#1E293B')
    )

    story = []
    
    # Title & Metadata
    story.append(Paragraph("CustomerIQ Executive Analytics Report", title_style))
    story.append(Paragraph(f"Generated on {datetime.now().strftime('%d %B %Y at %H:%M:%S')} · Confidential Business Intelligence", subtitle_style))
    story.append(Spacer(1, 10))
    
    # KPIs section
    story.append(Paragraph("1. High-Level Performance KPIs", h1_style))
    
    # Compute DB stats
    total_cust = await db.scalar(select(func.count(Customer.id))) or 0
    total_rev = await db.scalar(select(func.sum(Customer.total_spend))) or Decimal('0.00')
    avg_clv = await db.scalar(select(func.avg(Customer.clv_estimate))) or Decimal('0.00')
    avg_churn = await db.scalar(select(func.avg(Customer.churn_probability))) or Decimal('0.00')
    
    kpi_data = [
        [
            Paragraph("<b>Total Customers</b>", body_style),
            Paragraph(f"{total_cust:,}", body_style)
        ],
        [
            Paragraph("<b>Total Enterprise Revenue</b>", body_style),
            Paragraph(f"INR {float(total_rev):,.2f}", body_style)
        ],
        [
            Paragraph("<b>Average Customer Lifetime Value (CLV)</b>", body_style),
            Paragraph(f"INR {float(avg_clv):,.2f}", body_style)
        ],
        [
            Paragraph("<b>Average Churn Probability</b>", body_style),
            Paragraph(f"{float(avg_churn)*100:.2f}%", body_style)
        ]
    ]
    
    kpi_table = Table(kpi_data, colWidths=[200, 300])
    kpi_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#F8FAFC')),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#E2E8F0')),
        ('PADDING', (0,0), (-1,-1), 8),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
    ]))
    story.append(kpi_table)
    story.append(Spacer(1, 20))
    
    # Segments Table
    story.append(Paragraph("2. Customer Segment Profile & Strategy", h1_style))
    
    # Query segments
    seg_res = await db.execute(select(Segment).order_by(Segment.priority_score.desc()))
    segments = seg_res.scalars().all()
    
    seg_rows = [[
        Paragraph("<b>Segment Name</b>", table_header_style),
        Paragraph("<b>Size</b>", table_header_style),
        Paragraph("<b>Rev Share</b>", table_header_style),
        Paragraph("<b>Avg CLV</b>", table_header_style),
        Paragraph("<b>Marketing Strategy</b>", table_header_style),
    ]]
    
    for s in segments:
        seg_rows.append([
            Paragraph(s.name, table_cell_style),
            Paragraph(f"{s.size:,}", table_cell_style),
            Paragraph(f"{float(s.revenue_share or 0)*100:.1f}%", table_cell_style),
            Paragraph(f"INR {float(s.avg_clv or 0):,.2f}", table_cell_style),
            Paragraph(s.marketing_strategy or "N/A", table_cell_style),
        ])
        
    seg_table = Table(seg_rows, colWidths=[100, 50, 60, 90, 230])
    seg_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#1E293B')),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#E2E8F0')),
        ('PADDING', (0,0), (-1,-1), 6),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor('#F8FAFC')])
    ]))
    
    story.append(seg_table)
    story.append(Spacer(1, 20))
    
    # Add Recommendations section
    story.append(Paragraph("3. Executive Strategic Recommendations", h1_style))
    story.append(Paragraph(
        "Based on machine learning cluster profiles and predictive churn models, we recommend the following strategic actions:",
        body_style
    ))
    story.append(Paragraph(
        "<b>A. Target the high-revenue Premium Loyalists:</b> This segment drives a major share of total revenue. Implement premium loyalty benefits (e.g. customized offers and early-access campaigns) to protect CLV.",
        body_style
    ))
    story.append(Paragraph(
        "<b>B. Win-back campaign for Dormant Champions:</b> Customers with high lifetime spend but no purchase in the last 6 months are at risk. Send personalized re-engagement vouchers to reactivate them.",
        body_style
    ))
    story.append(Paragraph(
        "<b>C. Onboard New Explorers effectively:</b> Keep churn risk low by providing helpful welcome sequences and low-barrier product offerings immediately post-registration.",
        body_style
    ))
    
    doc.build(story)
    pdf_buffer.seek(0)
    return pdf_buffer
