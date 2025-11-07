"""Script to generate sample loan policy PDF documents."""

from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY
import os

# Get the directory of this script
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))


def create_loan_policy_v1():
    """Create internal loan policy document."""
    pdf_path = os.path.join(SCRIPT_DIR, "loan_policy_v1.pdf")
    doc = SimpleDocTemplate(pdf_path, pagesize=letter)
    styles = getSampleStyleSheet()
    story = []

    # Title
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor='darkblue',
        spaceAfter=30,
        alignment=TA_CENTER
    )
    story.append(Paragraph("Internal Loan Approval Policy", title_style))
    story.append(Spacer(1, 0.3 * inch))
    story.append(Paragraph("Version 1.0 - Effective Date: January 2024", styles['Normal']))
    story.append(Spacer(1, 0.5 * inch))

    # Section 1
    story.append(Paragraph("1. Credit Score Requirements", styles['Heading2']))
    story.append(Spacer(1, 0.2 * inch))
    
    content = """
    All loan applicants must meet minimum credit score requirements based on loan type:
    
    • Personal Loans: Minimum credit score of 620
    • Auto Loans: Minimum credit score of 600  
    • Home Purchase/Refinance: Minimum credit score of 640
    • Business Loans: Minimum credit score of 680
    
    Applicants with credit scores below these thresholds require executive approval and must provide
    additional documentation including proof of income stability and collateral where applicable.
    """
    story.append(Paragraph(content, styles['BodyText']))
    story.append(Spacer(1, 0.3 * inch))

    # Section 2
    story.append(Paragraph("2. Debt-to-Income Ratio Standards", styles['Heading2']))
    story.append(Spacer(1, 0.2 * inch))
    
    content = """
    The maximum allowable debt-to-income (DTI) ratio is 43% for all loan types. This includes:
    
    • All existing debt obligations (mortgages, car loans, credit cards, student loans)
    • The proposed new loan payment
    • Property taxes and insurance (for home loans)
    
    Applicants exceeding this ratio may be approved with:
    • Significant compensating factors (high credit score, substantial assets)
    • Larger down payment (minimum 20% for home loans)
    • Co-borrower with qualifying income
    """
    story.append(Paragraph(content, styles['BodyText']))
    story.append(Spacer(1, 0.3 * inch))

    # Section 3
    story.append(Paragraph("3. Employment and Income Verification", styles['Heading2']))
    story.append(Spacer(1, 0.2 * inch))
    
    content = """
    All applicants must demonstrate stable income through:
    
    • Minimum 6 months of continuous employment with current employer
    • For self-employed: 2 years of business operation with consistent income
    • Documentation requirements:
      - Recent pay stubs (last 2 months)
      - W-2 forms or tax returns (last 2 years)
      - Bank statements (last 3 months)
    
    Income must be verifiable and sufficient to support the proposed loan payment while maintaining
    the maximum DTI ratio of 43%.
    """
    story.append(Paragraph(content, styles['BodyText']))
    story.append(Spacer(1, 0.3 * inch))

    # Section 4
    story.append(Paragraph("4. Adverse Credit Events", styles['Heading2']))
    story.append(Spacer(1, 0.2 * inch))
    
    content = """
    The following waiting periods apply after adverse credit events:
    
    • Bankruptcy (Chapter 7): Minimum 7 years from discharge date
    • Bankruptcy (Chapter 13): Minimum 4 years from discharge date (2 years with extenuating circumstances)
    • Foreclosure: Minimum 7 years from completion date
    • Short Sale/Deed-in-Lieu: Minimum 4 years from completion date
    • Late Payments: No more than 2 late payments in the last 12 months
    
    Exceptions may be granted for documented extenuating circumstances (medical emergency, job loss
    due to economic conditions) with executive approval.
    """
    story.append(Paragraph(content, styles['BodyText']))
    story.append(Spacer(1, 0.3 * inch))

    # Section 5
    story.append(Paragraph("5. Loan-to-Value Ratios", styles['Heading2']))
    story.append(Spacer(1, 0.2 * inch))
    
    content = """
    Maximum loan-to-value (LTV) ratios by loan type:
    
    • Primary Residence Purchase: 95% LTV (with mortgage insurance)
    • Primary Residence Refinance: 90% LTV
    • Second Home: 85% LTV
    • Investment Property: 80% LTV
    • Auto Loans: 110% of MSRP or current value (whichever is lower)
    
    Higher LTV ratios require:
    • Excellent credit score (750+)
    • Lower DTI ratio (under 35%)
    • Significant liquid reserves (6+ months of payments)
    """
    story.append(Paragraph(content, styles['BodyText']))
    story.append(Spacer(1, 0.3 * inch))

    # Section 6
    story.append(Paragraph("6. Reserve Requirements", styles['Heading2']))
    story.append(Spacer(1, 0.2 * inch))
    
    content = """
    Minimum reserve requirements after closing:
    
    • Primary Residence: 2 months of PITI (Principal, Interest, Taxes, Insurance)
    • Second Home: 4 months of PITI
    • Investment Property: 6 months of PITI
    • Business Loans: 6 months of operating expenses
    
    Reserves must be in liquid, readily accessible accounts (checking, savings, money market).
    Retirement accounts may be considered at 60% of value.
    """
    story.append(Paragraph(content, styles['BodyText']))
    story.append(Spacer(1, 0.3 * inch))

    # Section 7
    story.append(Paragraph("7. Risk-Based Pricing", styles['Heading2']))
    story.append(Spacer(1, 0.2 * inch))
    
    content = """
    Interest rates are determined by risk assessment:
    
    • Base Rate: Prime rate + 0.5% for excellent credit (750+, DTI < 30%)
    • Standard Rate: Prime rate + 2-4% for good credit (680-749, DTI 30-40%)
    • High Risk Rate: Prime rate + 4-8% for fair credit (620-679, DTI 40-43%)
    
    Additional rate adjustments:
    • +0.25% for credit scores 620-679
    • +0.50% for LTV > 85%
    • +0.25% for cash-out refinance
    • -0.25% for automatic payment enrollment
    """
    story.append(Paragraph(content, styles['BodyText']))

    doc.build(story)
    print(f"Generated: {pdf_path}")


def create_best_practices():
    """Create industry best practices document."""
    pdf_path = os.path.join(SCRIPT_DIR, "best_practices.pdf")
    doc = SimpleDocTemplate(pdf_path, pagesize=letter)
    styles = getSampleStyleSheet()
    story = []

    # Title
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor='darkgreen',
        spaceAfter=30,
        alignment=TA_CENTER
    )
    story.append(Paragraph("Loan Underwriting Best Practices", title_style))
    story.append(Spacer(1, 0.3 * inch))
    story.append(Paragraph("Industry Standards and Guidelines - 2024", styles['Normal']))
    story.append(Spacer(1, 0.5 * inch))

    # Introduction
    story.append(Paragraph("Introduction", styles['Heading2']))
    story.append(Spacer(1, 0.2 * inch))
    
    content = """
    This document outlines industry best practices for loan underwriting, based on guidelines from
    federal agencies, industry associations, and market standards. These practices should be followed
    to ensure prudent lending decisions while maintaining compliance with regulatory requirements.
    """
    story.append(Paragraph(content, styles['BodyText']))
    story.append(Spacer(1, 0.3 * inch))

    # Section 1
    story.append(Paragraph("1. Ability to Repay", styles['Heading2']))
    story.append(Spacer(1, 0.2 * inch))
    
    content = """
    The fundamental principle of responsible lending is ensuring the borrower's ability to repay:
    
    • Verify stable income from reliable sources
    • Calculate accurate debt-to-income ratios including all obligations
    • Consider residual income after debt payments
    • Assess employment stability and industry outlook
    • Review asset reserves for cushion against unexpected events
    
    Key Metrics:
    • Front-end DTI (housing expense ratio): Maximum 28%
    • Back-end DTI (total debt ratio): Maximum 36-43%
    • Residual income: Minimum varies by family size and location
    """
    story.append(Paragraph(content, styles['BodyText']))
    story.append(Spacer(1, 0.3 * inch))

    # Section 2
    story.append(Paragraph("2. Credit History Evaluation", styles['Heading2']))
    story.append(Spacer(1, 0.2 * inch))
    
    content = """
    Comprehensive credit review beyond the credit score:
    
    • Payment history patterns across all credit types
    • Length of credit history (older is better)
    • Credit mix (variety indicates experience)
    • Recent inquiries (multiple may indicate financial stress)
    • Credit utilization ratio (under 30% is optimal)
    • Public records (judgments, liens, bankruptcies)
    
    Red Flags:
    • Recent late payments without explanation
    • High credit utilization (over 80%)
    • Multiple recent inquiries
    • Collections or charge-offs
    • Inconsistent payment patterns
    """
    story.append(Paragraph(content, styles['BodyText']))
    story.append(Spacer(1, 0.3 * inch))

    # Section 3
    story.append(Paragraph("3. Property Valuation Standards", styles['Heading2']))
    story.append(Spacer(1, 0.2 * inch))
    
    content = """
    For secured loans, proper collateral valuation is essential:
    
    • Use licensed, independent appraisers
    • Require recent comparable sales (last 6 months)
    • Consider market conditions and trends
    • Verify property condition through inspection
    • Review title for liens or encumbrances
    
    Conservative Valuation Approach:
    • Use lower of purchase price or appraised value
    • Apply market condition adjustments
    • Consider property type and marketability
    • Factor in necessary repairs or defects
    """
    story.append(Paragraph(content, styles['BodyText']))
    story.append(Spacer(1, 0.3 * inch))

    # Section 4
    story.append(Paragraph("4. Risk Mitigation Strategies", styles['Heading2']))
    story.append(Spacer(1, 0.2 * inch))
    
    content = """
    Implement appropriate risk mitigation measures:
    
    • Require private mortgage insurance for high LTV loans
    • Establish escrow accounts for taxes and insurance
    • Obtain appropriate property and liability insurance
    • Set aside reserves for anticipated expenses
    • Consider loan terms appropriate to borrower situation
    
    Compensating Factors:
    • Excellent credit history can offset higher DTI
    • Substantial reserves mitigate income concerns
    • Low LTV reduces default risk
    • Stable long-term employment
    • Significant equity in other properties
    """
    story.append(Paragraph(content, styles['BodyText']))
    story.append(Spacer(1, 0.3 * inch))

    # Section 5
    story.append(Paragraph("5. Documentation Requirements", styles['Heading2']))
    story.append(Spacer(1, 0.2 * inch))
    
    content = """
    Maintain complete documentation for each loan:
    
    • Completed loan application with signatures
    • Credit reports from all three bureaus
    • Income verification (pay stubs, tax returns, W-2s)
    • Asset verification (bank statements, investment accounts)
    • Employment verification (VOE or verbal verification)
    • Property appraisal and title report
    • All disclosures and borrower acknowledgments
    
    Documentation must be:
    • Current (typically within 90 days)
    • Complete and legible
    • From reliable third-party sources
    • Verified for accuracy and authenticity
    """
    story.append(Paragraph(content, styles['BodyText']))
    story.append(Spacer(1, 0.3 * inch))

    # Section 6
    story.append(Paragraph("6. Fair Lending Compliance", styles['Heading2']))
    story.append(Spacer(1, 0.2 * inch))
    
    content = """
    Ensure compliance with fair lending regulations:
    
    • Apply consistent underwriting standards to all applicants
    • Base decisions on objective, credit-related factors
    • Avoid discrimination based on protected classes
    • Provide adverse action notices when required
    • Maintain detailed records of decision rationale
    
    Protected Classes:
    • Race, color, national origin
    • Religion
    • Sex (including gender identity and sexual orientation)
    • Familial status
    • Disability
    • Age (for certain loan types)
    """
    story.append(Paragraph(content, styles['BodyText']))

    doc.build(story)
    print(f"Generated: {pdf_path}")


if __name__ == "__main__":
    print("Generating loan policy PDF documents...")
    create_loan_policy_v1()
    create_best_practices()
    print("PDF generation complete!")