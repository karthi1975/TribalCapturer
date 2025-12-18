"""
PDF generation service for knowledge entry exports.

Uses ReportLab to generate professional PDF documents with branded headers,
metadata tables, and formatted content.
"""
from io import BytesIO
from datetime import datetime
from typing import List
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    PageBreak,
    KeepTogether
)
from reportlab.lib.enums import TA_CENTER, TA_LEFT

from ..models.knowledge_entry import KnowledgeEntry


# Brand colors
HEADER_COLOR = colors.HexColor('#1976d2')  # Material-UI primary blue
LIGHT_GRAY = colors.HexColor('#f5f5f5')


def _sanitize_text(text: str) -> str:
    """
    Sanitize text content to prevent PDF injection and handle special characters.

    Args:
        text: Raw text input

    Returns:
        Sanitized text safe for PDF generation
    """
    if not text:
        return ""

    # Replace problematic characters
    text = text.replace('&', '&amp;')
    text = text.replace('<', '&lt;')
    text = text.replace('>', '&gt;')

    return text


def _format_knowledge_type(knowledge_type: str) -> str:
    """Format knowledge type enum to human-readable string."""
    type_map = {
        'diagnosis_specialty': 'Diagnosis → Specialty',
        'provider_preference': 'Provider Preference',
        'continuity_care': 'Continuity of Care',
        'pre_visit_requirement': 'Pre-Visit Requirement',
        'scheduling_workflow': 'Scheduling Workflow',
        'general_knowledge': 'General Knowledge'
    }
    return type_map.get(knowledge_type, knowledge_type)


def _format_datetime(dt) -> str:
    """Format datetime to readable string."""
    if not dt:
        return "N/A"
    if isinstance(dt, str):
        try:
            dt = datetime.fromisoformat(dt.replace('Z', '+00:00'))
        except:
            return dt
    return dt.strftime('%B %d, %Y at %I:%M %p')


def _create_header_footer(canvas, doc):
    """
    Create header and footer for each page.

    Args:
        canvas: ReportLab canvas object
        doc: Document object
    """
    canvas.saveState()

    # Header
    canvas.setFillColor(HEADER_COLOR)
    canvas.rect(0, doc.height + doc.topMargin + 0.25*inch,
                doc.width + 2*doc.leftMargin, 0.75*inch, fill=True)

    canvas.setFillColor(colors.white)
    canvas.setFont('Helvetica-Bold', 16)
    canvas.drawString(doc.leftMargin, doc.height + doc.topMargin + 0.5*inch,
                      "Tribal Knowledge Portal")

    canvas.setFont('Helvetica', 11)
    canvas.drawString(doc.leftMargin, doc.height + doc.topMargin + 0.3*inch,
                      "Knowledge Entry Export")

    # Footer
    canvas.setFillColor(colors.gray)
    canvas.setFont('Helvetica', 9)

    # Page number
    page_text = f"Page {doc.page} of {doc._pageNumber if hasattr(doc, '_pageNumber') else '?'}"
    canvas.drawString(doc.leftMargin, 0.5*inch, page_text)

    # Generated timestamp
    timestamp_text = f"Generated: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}"
    canvas.drawRightString(doc.width + doc.leftMargin, 0.5*inch, timestamp_text)

    canvas.restoreState()


def _create_entry_content(entry: KnowledgeEntry, styles) -> List:
    """
    Create PDF content elements for a single knowledge entry.

    Args:
        entry: Knowledge entry object
        styles: ReportLab styles

    Returns:
        List of PDF elements (paragraphs, tables, spacers)
    """
    story = []

    # Metadata table
    metadata_data = [
        ['Medical Assistant:', _sanitize_text(entry.ma_name)],
        ['Facility:', _sanitize_text(entry.facility)],
        ['Specialty Service:', _sanitize_text(entry.specialty_service)],
        ['Provider:', _sanitize_text(entry.provider_name) if entry.provider_name else 'N/A'],
        ['Knowledge Type:', _format_knowledge_type(entry.knowledge_type)],
        ['Status:', entry.status.upper()],
        ['Continuity of Care:', 'Yes' if entry.is_continuity_care else 'No'],
        ['Created:', _format_datetime(entry.created_at)],
        ['Last Updated:', _format_datetime(entry.updated_at)],
    ]

    metadata_table = Table(metadata_data, colWidths=[2.0*inch, 4.5*inch])
    metadata_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), LIGHT_GRAY),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
        ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
        ('ALIGN', (1, 0), (1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 11),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.gray),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('LEFTPADDING', (0, 0), (-1, -1), 10),
        ('RIGHTPADDING', (0, 0), (-1, -1), 10),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
    ]))

    story.append(metadata_table)
    story.append(Spacer(1, 0.3*inch))

    # Divider
    divider_table = Table([['─' * 80]], colWidths=[6.5*inch])
    divider_table.setStyle(TableStyle([
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.gray),
        ('FONTSIZE', (0, 0), (-1, -1), 8),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
    ]))
    story.append(divider_table)
    story.append(Spacer(1, 0.2*inch))

    # Knowledge Description header
    description_header = Paragraph(
        "<b>Knowledge Description:</b>",
        styles['Heading2']
    )
    story.append(description_header)
    story.append(Spacer(1, 0.15*inch))

    # Knowledge Description content
    description_style = ParagraphStyle(
        'Description',
        parent=styles['BodyText'],
        fontSize=10,
        leading=14,
        alignment=TA_LEFT,
        spaceBefore=0,
        spaceAfter=0,
    )

    sanitized_description = _sanitize_text(entry.knowledge_description)
    description_para = Paragraph(sanitized_description, description_style)
    story.append(description_para)

    return story


def generate_single_entry_pdf(entry: KnowledgeEntry) -> BytesIO:
    """
    Generate a PDF for a single knowledge entry.

    Args:
        entry: Knowledge entry object

    Returns:
        BytesIO buffer containing the PDF

    Raises:
        ValueError: If entry is None or invalid
    """
    if not entry:
        raise ValueError("Entry cannot be None")

    # Create buffer
    buffer = BytesIO()

    # Create document
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=0.75*inch,
        leftMargin=0.75*inch,
        topMargin=1.0*inch,
        bottomMargin=0.75*inch,
    )

    # Get styles
    styles = getSampleStyleSheet()

    # Build story
    story = _create_entry_content(entry, styles)

    # Build PDF
    doc.build(story, onFirstPage=_create_header_footer, onLaterPages=_create_header_footer)

    # Reset buffer position
    buffer.seek(0)

    return buffer


def generate_bulk_entries_pdf(entries: List[KnowledgeEntry]) -> BytesIO:
    """
    Generate a PDF with multiple knowledge entries (one per page).

    Args:
        entries: List of knowledge entry objects

    Returns:
        BytesIO buffer containing the PDF

    Raises:
        ValueError: If entries is None or empty
    """
    if not entries:
        raise ValueError("Entries list cannot be empty")

    if len(entries) > 1000:
        raise ValueError("Cannot generate PDF for more than 1000 entries")

    # Create buffer
    buffer = BytesIO()

    # Create document
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=0.75*inch,
        leftMargin=0.75*inch,
        topMargin=1.0*inch,
        bottomMargin=0.75*inch,
    )

    # Store total pages for footer
    doc._pageNumber = len(entries)

    # Get styles
    styles = getSampleStyleSheet()

    # Build story with all entries
    story = []
    for i, entry in enumerate(entries):
        # Add entry content
        entry_story = _create_entry_content(entry, styles)
        story.extend(entry_story)

        # Add page break between entries (except for the last one)
        if i < len(entries) - 1:
            story.append(PageBreak())

    # Build PDF
    doc.build(story, onFirstPage=_create_header_footer, onLaterPages=_create_header_footer)

    # Reset buffer position
    buffer.seek(0)

    return buffer
