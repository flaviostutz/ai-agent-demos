"""Script to generate loan approval rule documents (PDFs)."""

import os
from pathlib import Path
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import (
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)


def create_internal_rules_pdf(output_path: str) -> None:
    """Create internal loan approval rules PDF."""
    doc = SimpleDocTemplate(output_path, pagesize=letter)
    story = []
    styles = getSampleStyleSheet()

    # Title
    title_style = ParagraphStyle(
        "CustomTitle", parent=styles["Heading1"], fontSize=24, textColor=colors.HexColor("#1f4788")
    )
    story.append(Paragraph("Internal Loan Approval Rules", title_style))
    story.append(Spacer(1, 0.3 * inch))

    # Document metadata
    story.append(Paragraph("<b>Document Version:</b> 2.1", styles["Normal"]))
    story.append(Paragraph("<b>Last Updated:</b> October 2025", styles["Normal"]))
    story.append(Paragraph("<b>Classification:</b> Internal Use Only", styles["Normal"]))
    story.append(Spacer(1, 0.5 * inch))

    # Section 1: Credit Score Requirements
    story.append(Paragraph("1. Credit Score Requirements", styles["Heading2"]))
    story.append(Spacer(1, 0.2 * inch))

    credit_data = [
        ["Credit Score Range", "Risk Category", "Max Loan Amount", "Required Down Payment"],
        ["740-850", "Excellent", "No limit", "5%"],
        ["670-739", "Good", "$500,000", "10%"],
        ["580-669", "Fair", "$250,000", "20%"],
        ["Below 580", "Poor", "Case-by-case", "30%+"],
    ]

    credit_table = Table(credit_data, colWidths=[1.5 * inch, 1.3 * inch, 1.5 * inch, 1.7 * inch])
    credit_table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.grey),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
                ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, 0), 10),
                ("BOTTOMPADDING", (0, 0), (-1, 0), 12),
                ("BACKGROUND", (0, 1), (-1, -1), colors.beige),
                ("GRID", (0, 0), (-1, -1), 1, colors.black),
            ]
        )
    )
    story.append(credit_table)
    story.append(Spacer(1, 0.3 * inch))

    # Section 2: Debt-to-Income Ratio
    story.append(Paragraph("2. Debt-to-Income (DTI) Ratio Guidelines", styles["Heading2"]))
    story.append(Spacer(1, 0.2 * inch))
    story.append(Paragraph(
        "The debt-to-income ratio is calculated as: <b>(Monthly Debt Payments + Proposed Loan Payment) / Gross Monthly Income</b>",
        styles["Normal"],
    ))
    story.append(Spacer(1, 0.1 * inch))

    dti_rules = """
    <bullet>•</bullet> <b>DTI ≤ 36%:</b> Preferred range - Standard approval process<br/>
    <bullet>•</bullet> <b>DTI 37-43%:</b> Acceptable with compensating factors (high credit score, substantial reserves)<br/>
    <bullet>•</bullet> <b>DTI 44-50%:</b> Requires senior approval and strong compensating factors<br/>
    <bullet>•</bullet> <b>DTI > 50%:</b> Generally declined unless exceptional circumstances<br/>
    """
    story.append(Paragraph(dti_rules, styles["Normal"]))
    story.append(Spacer(1, 0.3 * inch))

    # Section 3: Employment Requirements
    story.append(Paragraph("3. Employment and Income Verification", styles["Heading2"]))
    story.append(Spacer(1, 0.2 * inch))

    employment_rules = """
    <b>Minimum Requirements:</b><br/>
    <bullet>•</bullet> <b>Employed:</b> Minimum 2 years with current employer or in same field<br/>
    <bullet>•</bullet> <b>Self-Employed:</b> Minimum 2 years of tax returns showing consistent income<br/>
    <bullet>•</bullet> <b>Recent Job Change:</b> Acceptable if within same field with salary increase<br/>
    <bullet>•</bullet> <b>Unemployed:</b> Not eligible unless significant liquid assets (12+ months reserves)<br/>
    <br/>
    <b>Income Documentation:</b><br/>
    <bullet>•</bullet> Most recent 2 pay stubs<br/>
    <bullet>•</bullet> W-2 forms for previous 2 years<br/>
    <bullet>•</bullet> Tax returns for self-employed applicants<br/>
    """
    story.append(Paragraph(employment_rules, styles["Normal"]))
    story.append(Spacer(1, 0.3 * inch))

    # Section 4: Loan-to-Value Ratios
    story.append(Paragraph("4. Loan-to-Value (LTV) Ratios", styles["Heading2"]))
    story.append(Spacer(1, 0.2 * inch))

    ltv_data = [
        ["Property Type", "Max LTV (Excellent Credit)", "Max LTV (Good Credit)", "Max LTV (Fair Credit)"],
        ["Primary Residence", "95%", "90%", "80%"],
        ["Second Home", "90%", "85%", "75%"],
        ["Investment Property", "85%", "80%", "70%"],
        ["Unsecured Loan", "N/A", "N/A", "N/A"],
    ]

    ltv_table = Table(ltv_data, colWidths=[1.8 * inch, 1.5 * inch, 1.4 * inch, 1.3 * inch])
    ltv_table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.grey),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
                ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, 0), 9),
                ("BOTTOMPADDING", (0, 0), (-1, 0), 12),
                ("BACKGROUND", (0, 1), (-1, -1), colors.beige),
                ("GRID", (0, 0), (-1, -1), 1, colors.black),
            ]
        )
    )
    story.append(ltv_table)
    story.append(Spacer(1, 0.3 * inch))

    # Section 5: Red Flags
    story.append(Paragraph("5. Automatic Decline Criteria", styles["Heading2"]))
    story.append(Spacer(1, 0.2 * inch))

    red_flags = """
    Applications must be declined if any of the following conditions are present:<br/>
    <bullet>•</bullet> Active bankruptcy or bankruptcy within last 2 years<br/>
    <bullet>•</bullet> Foreclosure within last 5 years<br/>
    <bullet>•</bullet> Recent loan default within last 3 years<br/>
    <bullet>•</bullet> Fraudulent information discovered during verification<br/>
    <bullet>•</bullet> Criminal conviction related to financial crimes<br/>
    <bullet>•</bullet> DTI ratio above 60% without exceptional circumstances<br/>
    <bullet>•</bullet> Credit score below 500<br/>
    <bullet>•</bullet> Insufficient or unverifiable income<br/>
    """
    story.append(Paragraph(red_flags, styles["Normal"]))
    story.append(Spacer(1, 0.3 * inch))

    # Section 6: Approval Limits
    story.append(Paragraph("6. Approval Authority Levels", styles["Heading2"]))
    story.append(Spacer(1, 0.2 * inch))

    approval_data = [
        ["Loan Amount", "Risk Score", "Approval Authority"],
        ["Up to $50,000", "0-40", "Loan Officer"],
        ["Up to $50,000", "41-60", "Senior Loan Officer"],
        ["$50,001-$250,000", "0-40", "Senior Loan Officer"],
        ["$50,001-$250,000", "41-60", "Loan Manager"],
        ["Over $250,000", "Any", "Credit Committee"],
        ["Any Amount", "61+", "Credit Committee"],
    ]

    approval_table = Table(approval_data, colWidths=[1.8 * inch, 1.5 * inch, 2.5 * inch])
    approval_table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.grey),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
                ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, 0), 10),
                ("BOTTOMPADDING", (0, 0), (-1, 0), 12),
                ("BACKGROUND", (0, 1), (-1, -1), colors.beige),
                ("GRID", (0, 0), (-1, -1), 1, colors.black),
            ]
        )
    )
    story.append(approval_table)

    # Build PDF
    doc.build(story)
    print(f"Created: {output_path}")


def create_best_practices_pdf(output_path: str) -> None:
    """Create industry best practices PDF."""
    doc = SimpleDocTemplate(output_path, pagesize=letter)
    story = []
    styles = getSampleStyleSheet()

    # Title
    title_style = ParagraphStyle(
        "CustomTitle", parent=styles["Heading1"], fontSize=24, textColor=colors.HexColor("#2c5f2d")
    )
    story.append(Paragraph("Loan Approval Industry Best Practices", title_style))
    story.append(Spacer(1, 0.3 * inch))

    # Document metadata
    story.append(Paragraph("<b>Source:</b> Financial Industry Standards Board", styles["Normal"]))
    story.append(Paragraph("<b>Last Updated:</b> October 2025", styles["Normal"]))
    story.append(Paragraph("<b>Classification:</b> Public", styles["Normal"]))
    story.append(Spacer(1, 0.5 * inch))

    # Introduction
    story.append(Paragraph("Executive Summary", styles["Heading2"]))
    story.append(Spacer(1, 0.2 * inch))
    intro_text = """
    This document outlines industry-standard best practices for consumer loan approval processes.
    These guidelines are based on regulatory requirements, risk management principles, and
    decades of lending experience across the financial services industry.
    """
    story.append(Paragraph(intro_text, styles["Normal"]))
    story.append(Spacer(1, 0.3 * inch))

    # Section 1: The 5 C's of Credit
    story.append(Paragraph("1. The Five C's of Credit Assessment", styles["Heading2"]))
    story.append(Spacer(1, 0.2 * inch))

    five_cs = """
    <b>Character:</b><br/>
    <bullet>•</bullet> Credit history and payment patterns<br/>
    <bullet>•</bullet> Credit score as primary indicator<br/>
    <bullet>•</bullet> References and background checks<br/>
    <br/>
    <b>Capacity:</b><br/>
    <bullet>•</bullet> Debt-to-income ratio analysis<br/>
    <bullet>•</bullet> Employment stability and income verification<br/>
    <bullet>•</bullet> Other financial obligations<br/>
    <br/>
    <b>Capital:</b><br/>
    <bullet>•</bullet> Down payment and reserves<br/>
    <bullet>•</bullet> Net worth and liquid assets<br/>
    <bullet>•</bullet> Savings patterns<br/>
    <br/>
    <b>Collateral:</b><br/>
    <bullet>•</bullet> Property value and appraisal<br/>
    <bullet>•</bullet> Loan-to-value ratio<br/>
    <bullet>•</bullet> Asset quality and marketability<br/>
    <br/>
    <b>Conditions:</b><br/>
    <bullet>•</bullet> Economic environment<br/>
    <bullet>•</bullet> Purpose of the loan<br/>
    <bullet>•</bullet> Industry and market conditions<br/>
    """
    story.append(Paragraph(five_cs, styles["Normal"]))
    story.append(Spacer(1, 0.3 * inch))

    # Section 2: Risk-Based Pricing
    story.append(Paragraph("2. Risk-Based Pricing Principles", styles["Heading2"]))
    story.append(Spacer(1, 0.2 * inch))

    pricing_text = """
    Interest rates and terms should reflect the risk profile of each borrower:<br/>
    <br/>
    <b>Low Risk (Score 0-30):</b><br/>
    <bullet>•</bullet> Prime rates (typically 5-7%)<br/>
    <bullet>•</bullet> Flexible terms up to 30 years<br/>
    <bullet>•</bullet> Minimal fees<br/>
    <br/>
    <b>Medium Risk (Score 31-60):</b><br/>
    <bullet>•</bullet> Near-prime rates (typically 7-10%)<br/>
    <bullet>•</bullet> Standard terms 15-20 years<br/>
    <bullet>•</bullet> Standard fees<br/>
    <br/>
    <b>High Risk (Score 61+):</b><br/>
    <bullet>•</bullet> Sub-prime rates (typically 10-15%)<br/>
    <bullet>•</bullet> Shorter terms or additional security required<br/>
    <bullet>•</bullet> Higher fees and stricter conditions<br/>
    """
    story.append(Paragraph(pricing_text, styles["Normal"]))
    story.append(Spacer(1, 0.3 * inch))

    # Section 3: Documentation Standards
    story.append(Paragraph("3. Required Documentation Standards", styles["Heading2"]))
    story.append(Spacer(1, 0.2 * inch))

    doc_standards = """
    <b>Minimum Documentation Requirements:</b><br/>
    <bullet>•</bullet> <b>Identity Verification:</b> Government-issued photo ID, SSN verification<br/>
    <bullet>•</bullet> <b>Income Verification:</b> Pay stubs (last 30 days), W-2s (2 years), tax returns<br/>
    <bullet>•</bullet> <b>Asset Verification:</b> Bank statements (2-3 months), investment account statements<br/>
    <bullet>•</bullet> <b>Employment Verification:</b> Direct employer contact, employment letter<br/>
    <bullet>•</bullet> <b>Credit Authorization:</b> Signed authorization for credit report<br/>
    <bullet>•</bullet> <b>Property Documentation:</b> Purchase agreement, appraisal (if applicable)<br/>
    """
    story.append(Paragraph(doc_standards, styles["Normal"]))
    story.append(Spacer(1, 0.3 * inch))

    # Section 4: Regulatory Compliance
    story.append(Paragraph("4. Regulatory Compliance Requirements", styles["Heading2"]))
    story.append(Spacer(1, 0.2 * inch))

    compliance_text = """
    All loan decisions must comply with:<br/>
    <bullet>•</bullet> <b>Equal Credit Opportunity Act (ECOA):</b> No discrimination based on protected classes<br/>
    <bullet>•</bullet> <b>Fair Credit Reporting Act (FCRA):</b> Proper use of credit reports<br/>
    <bullet>•</bullet> <b>Truth in Lending Act (TILA):</b> Clear disclosure of terms and costs<br/>
    <bullet>•</bullet> <b>Fair Housing Act:</b> Equal access to housing credit<br/>
    <bullet>•</bullet> <b>Dodd-Frank Act:</b> Ability-to-repay requirements<br/>
    <bullet>•</bullet> <b>State Regulations:</b> Comply with applicable state lending laws<br/>
    """
    story.append(Paragraph(compliance_text, styles["Normal"]))
    story.append(Spacer(1, 0.3 * inch))

    # Section 5: Adverse Action
    story.append(Paragraph("5. Adverse Action Notifications", styles["Heading2"]))
    story.append(Spacer(1, 0.2 * inch))

    adverse_text = """
    When a loan is declined or offered on less favorable terms, provide:<br/>
    <bullet>•</bullet> Written notice within 30 days<br/>
    <bullet>•</bullet> Specific reasons for the decision<br/>
    <bullet>•</bullet> Credit score used in decision<br/>
    <bullet>•</bullet> Credit reporting agency contact information<br/>
    <bullet>•</bullet> Right to obtain free credit report<br/>
    <bullet>•</bullet> Right to dispute information<br/>
    """
    story.append(Paragraph(adverse_text, styles["Normal"]))
    story.append(Spacer(1, 0.3 * inch))

    # Section 6: Quality Control
    story.append(Paragraph("6. Quality Control and Monitoring", styles["Heading2"]))
    story.append(Spacer(1, 0.2 * inch))

    qc_text = """
    <b>Ongoing Monitoring Requirements:</b><br/>
    <bullet>•</bullet> Regular audits of loan decision quality<br/>
    <bullet>•</bullet> Review of approval/denial rates by demographic groups<br/>
    <bullet>•</bullet> Performance tracking of approved loans<br/>
    <bullet>•</bullet> Periodic review and update of underwriting criteria<br/>
    <bullet>•</bullet> Staff training on regulatory requirements<br/>
    <bullet>•</bullet> Documentation of exceptions and their justifications<br/>
    """
    story.append(Paragraph(qc_text, styles["Normal"]))

    # Build PDF
    doc.build(story)
    print(f"Created: {output_path}")


def main():
    """Generate both PDF documents."""
    # Ensure documents directory exists
    docs_dir = Path(__file__).parent.parent / "data" / "documents"
    docs_dir.mkdir(parents=True, exist_ok=True)

    # Generate PDFs
    internal_rules_path = docs_dir / "internal_loan_approval_rules.pdf"
    best_practices_path = docs_dir / "loan_approval_best_practices.pdf"

    print("Generating loan approval rule documents...")
    create_internal_rules_pdf(str(internal_rules_path))
    create_best_practices_pdf(str(best_practices_path))
    print("\nPDF generation complete!")
    print(f"Documents saved in: {docs_dir}")


if __name__ == "__main__":
    main()
