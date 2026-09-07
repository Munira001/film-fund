"""Generate test PDF files from document templates

Automatically creates all 4 sample PDFs for testing.
"""

import os
from pathlib import Path

try:
    from reportlab.lib.pagesizes import letter
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
    from reportlab.lib.enums import TA_CENTER
except ImportError:
    print("ERROR: reportlab not installed")
    print("Install with: python -m pip install reportlab")
    exit(1)


def create_filmmaker_script_pdf():
    """Generate filmmaker script PDF"""
    doc = SimpleDocTemplate(
        "tests/sample_documents/filmmaker_script.pdf",
        pagesize=letter,
        topMargin=0.5*inch,
        bottomMargin=0.5*inch
    )
    
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor='black',
        alignment=TA_CENTER,
        spaceAfter=12,
    )
    
    content = []
    
    content.append(Paragraph("THE LAST DAWN", title_style))
    content.append(Paragraph("A Film Script", styles['Normal']))
    content.append(Spacer(1, 0.2*inch))
    
    content.append(Paragraph("<b>Director:</b> Sarah Chen", styles['Normal']))
    content.append(Paragraph("<b>Genre:</b> Science Fiction / Drama", styles['Normal']))
    content.append(Paragraph("<b>Logline:</b> When Earth's last satellite fails, a disillusioned engineer must lead humanity's final mission.", styles['Normal']))
    content.append(Spacer(1, 0.2*inch))
    
    content.append(Paragraph("<b>Runtime:</b> 112 minutes", styles['Normal']))
    content.append(Paragraph("<b>Current Stage:</b> Pre-production", styles['Normal']))
    content.append(Paragraph("<b>Estimated Budget:</b> $1,200,000 USD", styles['Normal']))
    content.append(Paragraph("<b>Urgency Level:</b> URGENT", styles['Normal']))
    content.append(Paragraph("<b>Funding Needed By:</b> March 15, 2025", styles['Normal']))
    content.append(Spacer(1, 0.2*inch))
    
    content.append(Paragraph("<b>Filming Locations:</b>", styles['Normal']))
    content.append(Paragraph("- Los Angeles, California", styles['Normal']))
    content.append(Paragraph("- Mojave Desert, California", styles['Normal']))
    content.append(Paragraph("- San Francisco, California", styles['Normal']))
    content.append(Spacer(1, 0.2*inch))
    
    content.append(Paragraph("<b>MULTIMEDIA ASSETS</b>", styles['Heading2']))
    content.append(Paragraph("Video Pitch: https://vimeo.com/sarahchenfilms/the-last-dawn-pitch", styles['Normal']))
    content.append(Paragraph("Visual Reel: https://vimeo.com/sarahchenfilms/last-dawn-visuals", styles['Normal']))
    
    doc.build(content)
    print("✅ Created: filmmaker_script.pdf")


def create_budget_pdf():
    """Generate production budget PDF"""
    doc = SimpleDocTemplate(
        "tests/sample_documents/production_budget.pdf",
        pagesize=letter,
        topMargin=0.5*inch,
        bottomMargin=0.5*inch
    )
    
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=20,
        textColor='black',
        alignment=TA_CENTER,
        spaceAfter=12,
    )
    
    content = []
    
    content.append(Paragraph("THE LAST DAWN - PRODUCTION BUDGET", title_style))
    content.append(Paragraph("January 2025", styles['Normal']))
    content.append(Spacer(1, 0.2*inch))
    
    content.append(Paragraph("<b>EXECUTIVE SUMMARY</b>", styles['Heading2']))
    content.append(Paragraph("Total Project Budget: $1,200,000.00 USD", styles['Normal']))
    content.append(Paragraph("Total Funding Secured: $350,000.00", styles['Normal']))
    content.append(Paragraph("Funding Gap: $850,000.00", styles['Normal']))
    content.append(Paragraph("Grant Funding Requested: $600,000.00", styles['Normal']))
    content.append(Paragraph("Investor Funding Needed: $250,000.00", styles['Normal']))
    content.append(Spacer(1, 0.2*inch))
    
    content.append(Paragraph("<b>DETAILED BUDGET BREAKDOWN</b>", styles['Heading2']))
    content.append(Paragraph("Development Phase: $45,000", styles['Normal']))
    content.append(Paragraph("Pre-Production Phase: $185,000", styles['Normal']))
    content.append(Paragraph("Production Phase: $650,000", styles['Normal']))
    content.append(Paragraph("Post-Production Phase: $200,000", styles['Normal']))
    content.append(Paragraph("Marketing & Distribution: $100,000", styles['Normal']))
    content.append(Paragraph("Contingency (10%): $20,000", styles['Normal']))
    content.append(Spacer(1, 0.2*inch))
    
    content.append(Paragraph("<b>FUNDING SOURCES</b>", styles['Heading2']))
    content.append(Paragraph("Producer Capital: $100,000", styles['Normal']))
    content.append(Paragraph("Private Investor: $200,000", styles['Normal']))
    content.append(Paragraph("Arts Council Grant: $50,000", styles['Normal']))
    content.append(Spacer(1, 0.2*inch))
    
    content.append(Paragraph("<b>KEY COST DRIVERS</b>", styles['Heading2']))
    content.append(Paragraph("Principal Photography: $450,000 (37.5%)", styles['Normal']))
    content.append(Paragraph("Visual Effects: $200,000 (16.7%)", styles['Normal']))
    content.append(Paragraph("Post-Production: $200,000 (16.7%)", styles['Normal']))
    
    doc.build(content)
    print("✅ Created: production_budget.pdf")


def create_schedule_pdf():
    """Generate production schedule PDF"""
    doc = SimpleDocTemplate(
        "tests/sample_documents/shooting_schedule.pdf",
        pagesize=letter,
        topMargin=0.5*inch,
        bottomMargin=0.5*inch
    )
    
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=20,
        textColor='black',
        alignment=TA_CENTER,
        spaceAfter=12,
    )
    
    content = []
    
    content.append(Paragraph("THE LAST DAWN - PRODUCTION SCHEDULE", title_style))
    content.append(Paragraph("Master Timeline", styles['Normal']))
    content.append(Spacer(1, 0.2*inch))
    
    content.append(Paragraph("<b>OVERALL PROJECT TIMELINE</b>", styles['Heading2']))
    content.append(Paragraph("Project Start Date: January 15, 2025", styles['Normal']))
    content.append(Paragraph("Estimated Completion: October 30, 2025", styles['Normal']))
    content.append(Paragraph("Funding Deadline: March 15, 2025 (CRITICAL)", styles['Normal']))
    content.append(Spacer(1, 0.2*inch))
    
    content.append(Paragraph("<b>PHASE BREAKDOWN</b>", styles['Heading2']))
    content.append(Paragraph("Development: Jan 15 - Feb 14, 2025 (4 weeks)", styles['Normal']))
    content.append(Paragraph("Pre-Production: Feb 15 - Mar 31, 2025 (6 weeks)", styles['Normal']))
    content.append(Paragraph("Principal Photography: Apr 1 - May 29, 2025 (28 days)", styles['Normal']))
    content.append(Paragraph("Post-Production: May 30 - Oct 30, 2025 (22 weeks)", styles['Normal']))
    content.append(Spacer(1, 0.2*inch))
    
    content.append(Paragraph("<b>CRITICAL MILESTONES</b>", styles['Heading2']))
    content.append(Paragraph("Funding Deadline: March 15, 2025", styles['Normal']))
    content.append(Paragraph("First Day of Shoot: April 1, 2025", styles['Normal']))
    content.append(Paragraph("Last Day of Shoot: May 29, 2025", styles['Normal']))
    content.append(Paragraph("Rough Cut: July 15, 2025", styles['Normal']))
    content.append(Paragraph("Final Cut: October 15, 2025", styles['Normal']))
    content.append(Spacer(1, 0.2*inch))
    
    content.append(Paragraph("<b>MILESTONE FUNDING SCHEDULE</b>", styles['Heading2']))
    content.append(Paragraph("Before Feb 15: $230,000", styles['Normal']))
    content.append(Paragraph("Before Apr 1: $450,000", styles['Normal']))
    content.append(Paragraph("Before Jun 1: $200,000", styles['Normal']))

    doc.build(content)
    print("✅ Created: shooting_schedule.pdf")


def create_profile_pdf():
    """Generate filmmaker profile PDF"""
    doc = SimpleDocTemplate(
        "tests/sample_documents/filmmaker_profile.pdf",
        pagesize=letter,
        topMargin=0.5*inch,
        bottomMargin=0.5*inch
    )
    
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor='black',
        alignment=TA_CENTER,
        spaceAfter=12,
    )
    
    content = []
    
    content.append(Paragraph("FILMMAKER PROFILE", title_style))
    content.append(Paragraph("SARAH CHEN", title_style))
    content.append(Spacer(1, 0.2*inch))
    
    content.append(Paragraph("<b>CONTACT INFORMATION</b>", styles['Heading2']))
    content.append(Paragraph("Name: Sarah Chen", styles['Normal']))
    content.append(Paragraph("Title: Director / Producer", styles['Normal']))
    content.append(Paragraph("Email: sarah.chen@zenithfilms.com", styles['Normal']))
    content.append(Paragraph("Phone: (415) 555-0142", styles['Normal']))
    content.append(Paragraph("Website: www.sarahchenfilms.com", styles['Normal']))
    content.append(Spacer(1, 0.2*inch))
    
    content.append(Paragraph("<b>PROFESSIONAL BACKGROUND</b>", styles['Heading2']))
    content.append(Paragraph("Years of Experience: 8 years", styles['Normal']))
    content.append(Paragraph("Experience Level: Established", styles['Normal']))
    content.append(Paragraph("Primary Role: Director / Producer", styles['Normal']))
    content.append(Spacer(1, 0.2*inch))
    
    content.append(Paragraph("<b>FILMOGRAPHY</b>", styles['Heading2']))
    content.append(Paragraph("Silent Signal (2023) - $400,000 - Best Director Award", styles['Normal']))
    content.append(Paragraph("Echoes (2021) - $150,000 - Audience Award", styles['Normal']))
    content.append(Paragraph("Neon City (2019) - $45,000 - Best Short", styles['Normal']))
    content.append(Spacer(1, 0.2*inch))
    
    content.append(Paragraph("<b>GRANT HISTORY</b>", styles['Heading2']))
    content.append(Paragraph("California Arts Council Grant (2023): $50,000", styles['Normal']))
    content.append(Paragraph("San Francisco Film Society Grant (2022): $35,000", styles['Normal']))
    content.append(Paragraph("Regional Independent Film Fund (2021): $40,000", styles['Normal']))
    content.append(Spacer(1, 0.2*inch))
    
    content.append(Paragraph("<b>CURRENT PROJECT</b>", styles['Heading2']))
    content.append(Paragraph("Project: The Last Dawn (Feature Film)", styles['Normal']))
    content.append(Paragraph("Status: Pre-production", styles['Normal']))
    content.append(Paragraph("Funding Needed: $850,000", styles['Normal']))
    content.append(Paragraph("Funding Deadline: March 15, 2025 (URGENT)", styles['Normal']))
    
    doc.build(content)
    print("✅ Created: filmmaker_profile.pdf")


def main():
    """Create all test PDFs"""
    # Create sample_documents folder if it doesn't exist
    os.makedirs("tests/sample_documents", exist_ok=True)
    
    print("\n" + "="*70)
    print("GENERATING TEST PDF FILES")
    print("="*70 + "\n")
    
    try:
        create_filmmaker_script_pdf()
        create_budget_pdf()
        create_schedule_pdf()
        create_profile_pdf()
        
        print("\n" + "="*70)
        print("✅ ALL TEST PDFs CREATED SUCCESSFULLY!")
        print("="*70)
        print("\nFiles created in: tests/sample_documents/")
        print("- filmmaker_script.pdf")
        print("- production_budget.pdf")
        print("- shooting_schedule.pdf")
        print("- filmmaker_profile.pdf")
        print("\nReady for document extraction testing!\n")
        
        return 0
        
    except Exception as e:
        print(f"\n❌ Error creating PDFs: {str(e)}")
        return 1


if __name__ == "__main__":
    exit(main())