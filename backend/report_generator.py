from reportlab.platypus import (SimpleDocTemplate,Paragraph,Spacer,Image,Table,TableStyle,PageBreak)
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
import os
from datetime import datetime
from insurance import *
from config import (damage_colors,display_names,damage_to_part,AMBIGUOUS_CLASSES)
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.styles import ParagraphStyle
from utils import *
def generate_pdf_report(inspection_results):
    # ============================================================
    # PDF SETUP & GLOBAL STYLES
    # Controls:
    # - PDF filename
    # - Title styling
    # - Section heading styling
    # ============================================================
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    pdf_path = os.path.join(BASE_DIR,"Damage_Report.pdf")
    doc = SimpleDocTemplate(pdf_path)
    styles = getSampleStyleSheet()

    title_style = ParagraphStyle("TitleStyle",parent=styles["Title"],fontSize=24,textColor=colors.HexColor("#1F4E79"),alignment=TA_CENTER)
    section_style = ParagraphStyle("SectionStyle",parent=styles["Heading2"],fontSize=18,textColor=colors.HexColor("#3F6625"))
    elements = []
    # ============================================================
    # REPORT COVER / HEADER SECTION
    # Controls:
    # - Report title
    # - Subtitle
    # - Generated timestamp
    # ============================================================
    elements.append(Paragraph("AI VEHICLE DAMAGE INSPECTION REPORT",title_style))

    elements.append(Spacer(1,15))

    elements.append(Paragraph("Insurance-Oriented Multi-View Vehicle Damage Assessment",styles["Italic"]))

    elements.append(Spacer(1,10))

    elements.append(Paragraph(f"Generated On: {datetime.now().strftime('%d-%m-%Y %H:%M:%S')}",styles["Normal"]))

    elements.append(Spacer(1,10))

    summary_data = [["Vehicle Side", "Damage Status", "Damage Count"]]

    policy_type = inspection_results.get("policy_type","third_party")

    sides = [(side,data) for side,data in inspection_results.items() if side != "policy_type"]

    elements.append(Spacer(1,20))
    # ============================================================
    # REPORT OVERVIEW SECTION
    # Controls:
    # - Vehicle views listed
    # - AI models listed
    # - Overall damage summary table
    # ============================================================
    elements.append(Paragraph("VEHICLE VIEWS ANALYSED",section_style))

    elements.append(Spacer(1,10))

    for side,_ in sides:
        elements.append(Paragraph(f"✓ {side}",styles["BodyText"]))
    
    elements.append(Paragraph("AI MODELS USED",section_style))

    elements.append(Spacer(1,10))

    elements.append(Paragraph("• Damage Model (YOLOv8)",styles["BodyText"]))

    elements.append(Paragraph("• Parts Model (YOLOv8)",styles["BodyText"]))

    elements.append(Spacer(1,15))

    elements.append(Paragraph("OVERALL DAMAGE SUMMARY",section_style))

    elements.append(Spacer(1,10))

    total_damage_count = 0
    total_raw_cost = 0
    total_covered_cost = 0
    total_customer_cost = 0
    # ============================================================
    # PER-VIEW ANALYSIS SECTION
    # One page generated for each vehicle side.
    #
    # Controls:
    # - Annotated image size
    # - Component table
    # - Severity colouring
    # - Cost table
    # ============================================================
    for index,(side,data) in enumerate(sides):

        damage_count = len(data["damages"])
        total_damage_count += damage_count
        status = (
            "Damaged"
            if damage_count > 0
            else "No Damage")

        summary_data.append([side,status,str(damage_count)])

    summary_table = Table(summary_data,colWidths=[150,150,120])

    summary_table.setStyle(
        TableStyle([
            ('BACKGROUND',(0,0),(-1,0),colors.darkblue),
            ('TEXTCOLOR',(0,0),(-1,0),colors.white),
            ('GRID',(0,0),(-1,-1),1,colors.black)]))

    elements.append(summary_table)

    elements.append(Spacer(1,20))

    elements.append(PageBreak())

    for index,(side,data) in enumerate(sides):

        pdf_image_path = os.path.join("static",data["image"])

        elements.append(Spacer(1,10))

        elements.append(Paragraph(f"{side} VIEW ANALYSIS",section_style))

        elements.append(Spacer(1,10))

        if os.path.exists(pdf_image_path):

            elements.append(Image(pdf_image_path,width=350,height=250))
            elements.append(Spacer(1,10))
            elements.append(Paragraph(f"Figure: {side} View Damage Inspection",styles["Italic"]))
            elements.append(Spacer(1,10))

        elements.append(Spacer(1,10))

        damaged_parts = set()
        part_severity = {}

        for item in data["damage_details"]:

            damage_name = item["damage"]

            raw_cost,\
            covered_cost,\
            customer_cost = calculate_damage_cost(
                damage_name,
                item["severity"],
                policy_type
            )

            total_raw_cost += raw_cost
            total_covered_cost += covered_cost
            total_customer_cost += customer_cost

            # Ambiguous classes -> IoU mapping

            if damage_name in AMBIGUOUS_CLASSES:

                damage_box = item["box"]

                best_part = None
                best_iou = 0

                for part_item in data["part_boxes"]:

                    iou = calculate_iou(
                        damage_box,
                        part_item["box"]
                    )

                    if iou > best_iou:

                        best_iou = iou
                        best_part = part_item["name"]

                if best_part and best_iou > 0.20:

                    damaged_parts.add(best_part)
                    part_severity[best_part] = item["severity"]

            # Normal classes -> direct mapping

            else:

                mapped_part = damage_to_part.get(
                    damage_name
                )

                if mapped_part:

                    damaged_parts.add(mapped_part)
                    part_severity[mapped_part] = item["severity"]

        all_components = set(data["parts"])

        for damaged in damaged_parts:
            all_components.add(damaged)

        table_data = [["Component", "Status", "Severity"]]

        for part in sorted(all_components):

            status = (
                "Damaged"
                if part in damaged_parts
                else "No Damage"
            )

            severity = "-"

            if status == "Damaged":

                severity = part_severity.get(
                    part,
                    "-"
                )
            table_data.append([
                part,
                status,
                severity.title()
                if severity != "-"
                else "-"
            ])

        table = Table(
            table_data,
            colWidths=[180,120,100]
        )
        # ------------------------------------------------------------
        # COMPONENT TABLE COLOURS
        #
        # Severe   -> Red
        # Moderate -> Orange
        # Minor    -> Green
        # No Damage-> Light Green
        #
        # Change colours here.
        # ------------------------------------------------------------
        table_style = [
            ('BACKGROUND',(0,0),(-1,0),colors.darkblue),
            ('TEXTCOLOR',(0,0),(-1,0),colors.white),
            ('FONTNAME',(0,0),(-1,0),'Helvetica-Bold'),
            ('GRID',(0,0),(-1,-1),1,colors.black)
        ]

        for row in range(1,len(table_data)):

            status = table_data[row][1]
            severity = str(table_data[row][2]).lower()

            if severity == "severe":

                table_style.append(
                    (
                        'BACKGROUND',
                        (0,row),
                        (-1,row),
                        colors.HexColor("#F4CCCC")
                    )
                )

            elif severity == "moderate":

                table_style.append(
                    (
                        'BACKGROUND',
                        (0,row),
                        (-1,row),
                        colors.HexColor("#FCE5CD")
                    )
                )

            elif severity == "minor":

                table_style.append(
                    (
                        'BACKGROUND',
                        (0,row),
                        (-1,row),
                        colors.HexColor("#D9EAD3")
                    )
                )

            elif status == "No Damage":

                table_style.append(
                    (
                        'BACKGROUND',
                        (0,row),
                        (-1,row),
                        colors.HexColor("#E8F5E9")
                    )
                )

        table.setStyle(
            TableStyle(table_style)
        )

        elements.append(table)
        cost_data = [["Damage", "Severity", "Raw Cost", "Covered", "Customer Pays"]]

        for item in data["damage_details"]:

            raw_cost,\
            covered_cost,\
            customer_cost = calculate_damage_cost(
                item["damage"],
                item["severity"],
                policy_type
            )

            cost_data.append([
                display_names.get(
                    item["damage"],
                    item["damage"]
                ),
                item["severity"].title(),
                f"Rs. {raw_cost:,}",
                f"Rs. {covered_cost:,}",
                f"Rs. {customer_cost:,}"
            ])
        # ------------------------------------------------------------
        # DAMAGE COST TABLE
        #
        # Controls:
        # - Raw repair cost display
        # - Insurance covered amount
        # - Customer payable amount
        # - Column widths
        # ------------------------------------------------------------
        cost_table = Table(
            cost_data,
            colWidths=[140,90,90,90,90]
        )

        cost_table.setStyle(
            TableStyle([
                ('BACKGROUND',(0,0),(-1,0),colors.darkblue),
                ('TEXTCOLOR',(0,0),(-1,0),colors.white),
                ('GRID',(0,0),(-1,-1),1,colors.black)
            ])
        )

        elements.append(Spacer(1,10))
        elements.append(cost_table)

        if index != len(sides)-1:
            elements.append(PageBreak())
    elements.append(PageBreak())
    # ============================================================
    # FINAL ASSESSMENT PAGE
    #
    # Controls:
    # - Total damages
    # - Affected vehicle sides
    # - Overall severity
    # - Recommendation text
    # ============================================================
    elements.append(Paragraph("FINAL ASSESSMENT", section_style))
    elements.append(Spacer(1,15))
    affected_sides = []

    for side, data in sides:
        if len(data["damages"]) > 0:
            affected_sides.append(side)

    overall_severity = (
        "Low"
        if total_damage_count <= 2
        else "Moderate"
        if total_damage_count <= 5
        else "High"
    )
    assessment_data = [
        ["Total Damage Instances", str(total_damage_count)],
        ["Affected Vehicle Sides", ", ".join(affected_sides)],
        ["Overall Severity", overall_severity],
        ["Insurance Policy", policy_type.upper()]
    ]
    # ------------------------------------------------------------
    # FINAL ASSESSMENT TABLE STYLING
    #
    # Left column background colour
    # Table borders
    # Font weight
    # ------------------------------------------------------------
    assessment_table = Table(
        assessment_data,
        colWidths=[220,250]
    )

    assessment_table.setStyle(
        TableStyle([
            ('GRID',(0,0),(-1,-1),1,colors.black),
            ('BACKGROUND',(0,0),(0,-1),colors.HexColor("#D9EAD3")),
            ('FONTNAME',(0,0),(0,-1),'Helvetica-Bold')
        ])
    )

    elements.append(assessment_table)

    elements.append(Spacer(1,15))

    elements.append(PageBreak())
    # ============================================================
    # FINAL BILL PAGE
    #
    # Controls:
    # - Total repair cost
    # - Insurance contribution
    # - Customer payable amount
    #
    # This is the last page of the report.
    # ============================================================
    elements.append(Paragraph("FINAL BILL SUMMARY",section_style))

    bill_data = [["Description", "Amount"],["Total Repair Cost", f"Rs. {total_raw_cost:,}"],["Insurance Contribution", f"Rs. {total_covered_cost:,}"],["Customer Payable Amount", f"Rs. {total_customer_cost:,}"],["Policy Type", policy_type.upper()]]

    bill_table = Table(bill_data,colWidths=[250,180])
    # ------------------------------------------------------------
    # BILL TABLE STYLING
    #
    # Header row colour
    # Highlighted payable row colour
    # Grid styling
    # ------------------------------------------------------------
    bill_table.setStyle(
        TableStyle([
            ('BACKGROUND',(0,0),(-1,0),colors.darkblue),
            ('TEXTCOLOR',(0,0),(-1,0),colors.white),
            ('FONTNAME',(0,0),(-1,0),'Helvetica-Bold'),
            ('GRID',(0,0),(-1,-1),1,colors.black),

            ('BACKGROUND',(0,-1),(-1,-1),colors.HexColor("#FFF2CC")),
            ('FONTNAME',(0,-1),(-1,-1),'Helvetica-Bold')
        ])
    )

    elements.append(bill_table)

    elements.append(Spacer(1,20))
    
    
    doc.build(elements)

    print("PDF PATH =", os.path.abspath(pdf_path))
    print("FILE EXISTS =", os.path.exists(pdf_path))
    print("PDF SIZE =", os.path.getsize(pdf_path))
    return pdf_path
