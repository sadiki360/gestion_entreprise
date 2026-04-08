from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from django.http import HttpResponse
from io import BytesIO
from datetime import datetime


def export_ventes_pdf(ventes):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4,
                            rightMargin=2*cm, leftMargin=2*cm,
                            topMargin=2*cm, bottomMargin=2*cm)

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle('title', fontSize=18, fontName='Helvetica-Bold',
                                  alignment=TA_CENTER, spaceAfter=20)
    subtitle_style = ParagraphStyle('subtitle', fontSize=10, fontName='Helvetica',
                                     alignment=TA_CENTER, textColor=colors.grey, spaceAfter=20)

    elements = []

    elements.append(Paragraph("Rapport des Ventes", title_style))
    elements.append(Paragraph(f"Généré le {datetime.now().strftime('%d/%m/%Y à %H:%M')}", subtitle_style))
    elements.append(Spacer(1, 0.5*cm))

    total_general = sum(float(v.total) for v in ventes)
    summary_data = [
        ['Total des ventes', 'Chiffre d\'affaires'],
        [str(len(ventes)), f"{round(total_general, 2)} DH"],
    ]
    summary_table = Table(summary_data, colWidths=[8*cm, 8*cm])
    summary_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#0d6efd')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 11),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 1), (-1, -1), 14),
        ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f8f9fa')),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.HexColor('#f8f9fa')]),
        ('TOPPADDING', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
    ]))
    elements.append(summary_table)
    elements.append(Spacer(1, 1*cm))

    data = [['#', 'Client', 'Date', 'Total']]
    for v in ventes:
        data.append([
            str(v.id),
            str(v.client),
            v.date_vente.strftime('%d/%m/%Y'),
            f"{v.total} DH",
        ])

    table = Table(data, colWidths=[2*cm, 7*cm, 5*cm, 4*cm])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#343a40')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 9),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f8f9fa')]),
        ('GRID', (0, 0), (-1, -1), 0.3, colors.HexColor('#dee2e6')),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
    ]))
    elements.append(table)

    doc.build(elements)
    buffer.seek(0)

    response = HttpResponse(buffer, content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="rapport_ventes.pdf"'
    return response


def export_facture_pdf(vente):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4,
                            rightMargin=2*cm, leftMargin=2*cm,
                            topMargin=2*cm, bottomMargin=2*cm)

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle('title', fontSize=20, fontName='Helvetica-Bold',
                                  alignment=TA_CENTER, spaceAfter=10)
    normal_style = ParagraphStyle('normal', fontSize=10, fontName='Helvetica', spaceAfter=6)

    elements = []

    elements.append(Paragraph(f"FACTURE #{vente.id}", title_style))
    elements.append(Paragraph(f"Date : {vente.date_vente.strftime('%d/%m/%Y à %H:%M')}", normal_style))
    elements.append(Paragraph(f"Client : {vente.client}", normal_style))
    elements.append(Spacer(1, 1*cm))

    lignes = vente.lignes.all()
    data = [['Produit', 'Quantité', 'Prix unitaire', 'Sous-total']]
    for ligne in lignes:
        sous_total = float(ligne.quantite) * float(ligne.prix_unitaire)
        data.append([
            str(ligne.produit),
            str(ligne.quantite),
            f"{ligne.prix_unitaire} DH",
            f"{round(sous_total, 2)} DH",
        ])

    data.append(['', '', 'TOTAL', f"{vente.total} DH"])

    table = Table(data, colWidths=[7*cm, 3*cm, 4*cm, 4*cm])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#343a40')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('ROWBACKGROUNDS', (0, 1), (-1, -2), [colors.white, colors.HexColor('#f8f9fa')]),
        ('GRID', (0, 0), (-1, -1), 0.3, colors.HexColor('#dee2e6')),
        ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
        ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#0d6efd')),
        ('TEXTCOLOR', (0, -1), (-1, -1), colors.white),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
    ]))
    elements.append(table)

    doc.build(elements)
    buffer.seek(0)

    response = HttpResponse(buffer, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="facture_{vente.id}.pdf"'
    return response