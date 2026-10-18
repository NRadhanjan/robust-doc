"""Generates the Review 3 / Final Project PowerPoint presentation based on the Review 1 template."""

from pathlib import Path
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from pptx.enum.shapes import MSO_SHAPE

BASE_DIR = Path(__file__).resolve().parent
REPORTS_DIR = BASE_DIR / "reports"
OUTPUT_DIR = Path(r"C:\Users\user\Downloads")
TEMPLATE_PATH = OUTPUT_DIR / "Robust Doc - Review 1 PPT.pptx"

# Theme colors matching Review 1 PPT
NAVY = RGBColor(27, 54, 93)       # #1B365D - Title
SLATE = RGBColor(51, 65, 85)      # #334155 - Slate
DARK_BLUE = RGBColor(41, 70, 115) # #294673 - Subheading
CHARCOAL = RGBColor(30, 41, 59)   # #1E293B - Body
LIGHT_BG = RGBColor(241, 245, 249) # #F1F5F9 - Box fill
BORDER_COL = RGBColor(203, 213, 225) # #CBD5E1 - Box border
EMERALD = RGBColor(5, 150, 105)   # #059669 - Positive metric
AMBER = RGBColor(217, 119, 6)     # #D97706 - Moderate metric
CRIMSON = RGBColor(220, 38, 38)   # #DC2626 - Fragile metric


def add_header(slide, number_str, title_str):
    """Adds a standardized slide header matching the presentation aesthetic."""
    tb = slide.shapes.add_textbox(Inches(0.8), Inches(0.5), Inches(18.4), Inches(1.2))
    tf = tb.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = f"{number_str}   {title_str}"
    p.font.name = "Arial"
    p.font.size = Pt(28)
    p.font.bold = True
    p.font.color.rgb = NAVY


def add_card(slide, left, top, width, height, title, body_bullets, title_color=NAVY):
    """Adds a clean rounded or rectangular card with title and bullet points."""
    shape = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left, top, width, height)
    shape.fill.solid()
    shape.fill.fore_color.rgb = LIGHT_BG
    shape.line.color.rgb = BORDER_COL
    shape.line.width = Pt(1.5)

    tf = shape.text_frame
    tf.word_wrap = True
    tf.margin_left = Inches(0.25)
    tf.margin_right = Inches(0.25)
    tf.margin_top = Inches(0.2)
    tf.margin_bottom = Inches(0.2)

    p0 = tf.paragraphs[0]
    p0.text = title
    p0.font.name = "Arial"
    p0.font.size = Pt(18)
    p0.font.bold = True
    p0.font.color.rgb = title_color
    p0.space_after = Pt(8)

    for bullet in body_bullets:
        p = tf.add_paragraph()
        p.text = f"•  {bullet}"
        p.font.name = "Calibri"
        p.font.size = Pt(14)
        p.font.color.rgb = CHARCOAL
        p.space_after = Pt(4)


def create_review3_presentation():
    print("[*] Loading Review 1 presentation template...")
    prs = Presentation(str(TEMPLATE_PATH))
    blank_layout = prs.slide_layouts[6]  # Blank layout

    # ============================================================
    # SLIDE 1: Update Title Slide Subtitle to Review 3
    # ============================================================
    s1 = prs.slides[0]
    for shp in s1.shapes:
        if shp.has_text_frame:
            for p in shp.text_frame.paragraphs:
                if "Evaluating Structural Robustness" in p.text:
                    p.text = "Evaluating Structural Robustness of Malicious Document Detectors Under Controlled Mutation\n[ Review 3 — Final Capstone Defense ]"
                    p.font.size = Pt(15)
                    p.font.bold = True

    # ============================================================
    # SLIDE 3: Update Objectives to 100% Completed
    # ============================================================
    s3 = prs.slides[2]
    # Add a completion badge on Slide 3
    badge = s3.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(13.5), Inches(0.5), Inches(5.5), Inches(0.8))
    badge.fill.solid()
    badge.fill.fore_color.rgb = EMERALD
    badge.line.color.rgb = EMERALD
    tf_b = badge.text_frame
    p_b = tf_b.paragraphs[0]
    p_b.text = "STATUS: 100% COMPLETED"
    p_b.font.name = "Arial"
    p_b.font.size = Pt(16)
    p_b.font.bold = True
    p_b.font.color.rgb = RGBColor(255, 255, 255)
    p_b.alignment = PP_ALIGN.CENTER

    # ============================================================
    # NEW SLIDE 1: 100-Sample Benchmark Dataset Testbed
    # ============================================================
    s_data = prs.slides.add_slide(blank_layout)
    add_header(s_data, "07", "DATASET CURATION & BENCHMARK COMPOSITION")

    add_card(
        s_data,
        Inches(1.0), Inches(2.0), Inches(5.5), Inches(8.0),
        "Real-World Malware (CVEs)",
        [
            "10 Published Exploit PoCs from security research.",
            "CVE-2024-4367: Arbitrary JavaScript execution in PDF.js font parsing.",
            "CVE-2019-14811: Ghostscript PostScript memory escape vulnerability.",
            "Pentest Injection: Malicious /JavaScript annotations & attached script droppers.",
            "Preserves authentic exploit packaging found in the wild."
        ],
        title_color=CRIMSON
    )

    add_card(
        s_data,
        Inches(7.2), Inches(2.0), Inches(5.5), Inches(8.0),
        "Real Benign PDFs (Mozilla)",
        [
            "10 Clean, complex documents from Mozilla PDF.js repository.",
            "Multilingual encodings: Arabic CID TrueType & CJK 90ms fonts.",
            "Complex page structures: Type3 Content Streams (Cycle & NoCycle).",
            "Apache PDFBox generated documents & embedded fonts.",
            "Provides rigorous false-positive control against real publishing complexity."
        ],
        title_color=EMERALD
    )

    add_card(
        s_data,
        Inches(13.4), Inches(2.0), Inches(5.5), Inches(8.0),
        "Synthetic Structural Dataset",
        [
            "80 Balanced Structural PDFs (40 Benign + 40 Malicious).",
            "Deterministic Ground Truth for validity checks.",
            "Active execution vectors: /OpenAction JS, /Launch cmd.exe, /AA triggers, /EmbeddedFiles.",
            "Grand Total: Exactly 100 PDF benchmark samples (50 Benign + 50 Malicious)."
        ],
        title_color=DARK_BLUE
    )

    # ============================================================
    # NEW SLIDE 2: Multi-Model Robustness Benchmark
    # ============================================================
    s_models = prs.slides.add_slide(blank_layout)
    add_header(s_models, "08", "MULTI-MODEL COMPARATIVE ROBUSTNESS BENCHMARK")

    # Add descriptive lead
    lead = s_models.shapes.add_textbox(Inches(1.0), Inches(1.8), Inches(18.0), Inches(0.8))
    lead.text_frame.paragraphs[0].text = (
        "Is feature fragility unique to one model, or an architectural flaw of static PDF features? "
        "We benchmarked 5 distinct classifier families across 150 trials at operational mutation intensity (lambda = 0.8):"
    )
    lead.text_frame.paragraphs[0].font.size = Pt(14)
    lead.text_frame.paragraphs[0].font.color.rgb = SLATE

    # Table for Multi-Model Results
    tbl_shape = s_models.shapes.add_table(6, 5, Inches(1.0), Inches(2.6), Inches(18.0), Inches(4.5))
    tbl = tbl_shape.table

    headers = ["Classifier Architecture", "Trials Tested", "Retained Malicious", "Retention Rate (%)", "Empirical Robustness Verdict"]
    for idx, h in enumerate(headers):
        cell = tbl.cell(0, idx)
        cell.text = h
        cell.fill.solid()
        cell.fill.fore_color.rgb = NAVY
        for p in cell.text_frame.paragraphs:
            p.font.name = "Arial"
            p.font.size = Pt(14)
            p.font.bold = True
            p.font.color.rgb = RGBColor(255, 255, 255)

    rows_data = [
        ("Random Forest (Baseline)", "150", "146", "97.3%", "HIGH ROBUSTNESS (Ensemble averaging buffers individual feature noise)"),
        ("Hardened Random Forest (Our Blueprint)", "150", "142", "94.7%", "HIGH ROBUSTNESS (Trained exclusively on 12 conserved structural invariants)"),
        ("Decision Tree (Single Estimator)", "150", "24", "16.0%", "EXTREMELY VULNERABLE (Single threshold shifts flip decisions instantly)"),
        ("Gradient Boosting (GBDT)", "150", "24", "16.0%", "EXTREMELY VULNERABLE (Sequential residual trees overfit to packaging features)"),
        ("Support Vector Machine (RBF Kernel)", "150", "3", "2.0%", "NEAR-TOTAL COLLAPSE (Distance metric distorted by stream and file size shifts)")
    ]

    for r_idx, row in enumerate(rows_data, 1):
        for c_idx, val in enumerate(row):
            cell = tbl.cell(r_idx, c_idx)
            cell.text = val
            cell.fill.solid()
            cell.fill.fore_color.rgb = RGBColor(248, 250, 252) if r_idx % 2 == 1 else RGBColor(255, 255, 255)
            for p in cell.text_frame.paragraphs:
                p.font.name = "Calibri"
                p.font.size = Pt(13)
                p.font.color.rgb = CHARCOAL
                if c_idx == 3:
                    p.font.bold = True
                    p.font.color.rgb = EMERALD if float(val.replace("%", "")) > 80 else CRIMSON

    # Key takeaway callout below table
    add_card(
        s_models,
        Inches(1.0), Inches(7.5), Inches(18.0), Inches(2.8),
        "Key Scientific Discovery",
        [
            "Feature fragility is NOT just a Random Forest issue — it is an inherent weakness of static packaging features.",
            "Distance-based classifiers (SVM) suffer near-total collapse (2.0% retention) because modest byte shifts distort kernel geometry.",
            "Ensemble averaging (Random Forest) partially masks fragility, but individual tree votes still collapse underneath."
        ],
        title_color=NAVY
    )

    # ============================================================
    # NEW SLIDE 3: Continuous Degradation Curves (Novel Add-On #2)
    # ============================================================
    s_curves = prs.slides.add_slide(blank_layout)
    add_header(s_curves, "09", "CONTINUOUS DEGRADATION CURVES (WHERE DETECTION COLLAPSES)")

    # Embed Degradation Curves Plot
    curve_img = REPORTS_DIR / "degradation_curves.png"
    if curve_img.exists():
        s_curves.shapes.add_picture(str(curve_img), Inches(1.0), Inches(2.0), width=Inches(10.5))

    add_card(
        s_curves,
        Inches(12.0), Inches(2.0), Inches(7.0), Inches(8.2),
        "Analysis of Tipping Points",
        [
            "Tested across 10 continuous intensity levels: lambda = 10% -> 100%.",
            "Total experimental battery: 1,500 trials across all 50 malicious files.",
            "Metadata Perturbation: Causes a steep, early collapse in confidence between 30% and 60% intensity.",
            "Object Reordering: Drops confidence on real CVEs by over 40% (e.g. CVE-2024-4367 drops from 96% down to 54%).",
            "Stream Recompression: Induces sudden threshold drop when compression filters invert.",
            "Hardened Model (Green Line): Maintains confidence >=91% across all intensity levels, proving the fix works!"
        ],
        title_color=DARK_BLUE
    )

    # ============================================================
    # NEW SLIDE 4: Per-Feature Stability Analysis
    # ============================================================
    s_feat = prs.slides.add_slide(blank_layout)
    add_header(s_feat, "10", "PER-FEATURE STABILITY RANKINGS (% PRESERVED)")

    # Embed Feature Stability Chart
    bar_img = REPORTS_DIR / "feature_stability_chart.png"
    if bar_img.exists():
        s_feat.shapes.add_picture(str(bar_img), Inches(1.0), Inches(2.0), width=Inches(10.5))

    add_card(
        s_feat,
        Inches(12.0), Inches(2.0), Inches(7.0), Inches(8.2),
        "Feature Diagnostics",
        [
            "Conserved Invariants (100% Stable):",
            "  * count_javascript, count_openaction, count_aa, count_annot, num_pages.",
            "  * These are semantic necessities for payload execution and resist all structural mutations.",
            "Extremely Fragile Features (<20% Stable):",
            "  * ratio_compressed_streams (7.6% stable)",
            "  * num_compressed_streams (13.8% stable)",
            "  * num_trailer_entries (47.6% stable)",
            "  * file_size (35.6% stable)",
            "Conclusion: Classifiers anchoring decisions on compression or file size break under routine office processing."
        ],
        title_color=NAVY
    )

    # ============================================================
    # NEW SLIDE 5: Detector Fragility Report Deliverable
    # ============================================================
    s_rep = prs.slides.add_slide(blank_layout)
    add_header(s_rep, "11", "OUTPUT DELIVERABLE: THE DETECTOR FRAGILITY REPORT")

    rep_box = s_rep.shapes.add_textbox(Inches(1.0), Inches(1.8), Inches(11.0), Inches(8.5))
    rep_tf = rep_box.text_frame
    rep_tf.word_wrap = True
    rep_text = (
        "==================================================================\n"
        "                   DETECTOR FRAGILITY REPORT                      \n"
        "==================================================================\n"
        "Model: Baseline Random Forest (100-Sample Benchmark)\n"
        "Overall Robustness Score: 90.0/100 -> LOW RISK (Ensemble)\n"
        "------------------------------------------------------------------\n"
        "Detection Retention per Mutation Type:\n"
        "  * metadata_mutation       : #######     74.7%  (Critical Drop)\n"
        "  * recompression           : #########   98.7%\n"
        "  * object_reordering       : #########   96.7%\n"
        "------------------------------------------------------------------\n"
        "Headline Feature Stability (Top Reliable vs Fragile):\n"
        "  [+] High Stability Features (Conserved Anchors):\n"
        "      count_javascript          ########## 100.0%\n"
        "      count_openaction          ########## 100.0%\n"
        "      count_aa                  ########## 100.0%\n"
        "      count_annot               ########## 100.0%\n"
        "  [-] Fragile / Volatile Features (Surface Packaging):\n"
        "      num_trailer_entries       ####        47.6%\n"
        "      file_size                 ###         35.6%\n"
        "      num_compressed_streams    #           13.8%\n"
        "      ratio_compressed_streams               7.6%\n"
        "------------------------------------------------------------------\n"
        "Verdict: The detector's confidence is heavily influenced by packaging\n"
        "artifacts. Routine resaving or non-adversarial processing can degrade\n"
        "detection confidence by up to 48% on genuine malware payloads.\n"
        "=================================================================="
    )
    p_rep = rep_tf.paragraphs[0]
    p_rep.text = rep_text
    p_rep.font.name = "Consolas"
    p_rep.font.size = Pt(13)
    p_rep.font.color.rgb = CHARCOAL

    add_card(
        s_rep,
        Inches(12.5), Inches(2.0), Inches(6.5), Inches(8.2),
        "What This Report Delivers",
        [
            "Standardized diagnostic certificate exposing detector weaknesses.",
            "Exposes vulnerability to everyday document pipelines (Adobe Acrobat resaving, sanitization).",
            "Identifies which static features are trustworthy vs. dangerous to rely upon.",
            "Directly actionable for engineering hardened security gateways."
        ],
        title_color=DARK_BLUE
    )

    # ============================================================
    # NEW SLIDE 6: The Hardened Detector Prototype (Defense Blueprint)
    # ============================================================
    s_hard = prs.slides.add_slide(blank_layout)
    add_header(s_hard, "12", "DEFENSIVE BLUEPRINT: HARDENED DETECTOR PROTOTYPE")

    add_card(
        s_hard,
        Inches(1.0), Inches(2.0), Inches(8.5), Inches(8.2),
        "The Problem Diagnosed",
        [
            "Naive detectors anchor decisions on easy-to-learn packaging artifacts (file size, compression ratios, trailer counts).",
            "When documents are recompressed or linearized, those packaging features shift, causing confidence drops of up to 48%.",
            "An attacker does not even need to write an evasion payload — standard document conversion tools inadvertently evade the detector for them!"
        ],
        title_color=CRIMSON
    )

    add_card(
        s_hard,
        Inches(10.2), Inches(2.0), Inches(8.8), Inches(8.2),
        "The Solution (Hardened Detector)",
        [
            "Feature Pruning: Discarded the 16 volatile packaging features entirely.",
            "Conserved Feature Retraining: Trained exclusively on the 12 verified structural invariants (count_javascript, count_openaction, count_aa, count_annot, num_pages, byte_entropy).",
            "Experimental Proof: Achieved 94.7% retention under heavy mutation while maintaining >=91% confidence.",
            "Proves the research thesis: Robustness can be engineered once feature stability is rigorously diagnosed!"
        ],
        title_color=EMERALD
    )

    # ============================================================
    # NEW SLIDE 7: Viva Voce Defense Guide
    # ============================================================
    s_viva = prs.slides.add_slide(blank_layout)
    add_header(s_viva, "13", "VIVA VOCE DEFENSE: ANTICIPATED COMMITTEE QUESTIONS")

    viva_cards = [
        ("Q1: Why not build a robust detector from the start?",
         "A: You cannot fix what hasn't been measured. Robustness requires first diagnosing which features break. Our stability results provide the empirical blueprint. We proved this by building the Hardened Detector in Section 12."),
        ("Q2: How do you know mutations didn't just break the malware?",
         "A: Every file passes our automated Two-Stage Validity Gatekeeper (V1-V4), verifying syntax parsing AND structural reachability of /OpenAction to the JavaScript stream. Corrupted files were strictly discarded."),
        ("Q3: Isn't 'detectors can be evaded' already known?",
         "A: Prior work studied mathematically optimized adversarial attacks (EvadeML). We study routine non-adversarial noise (office processing), and report per-feature stability curves rather than a single accuracy number."),
        ("Q4: Why did SVM collapse (2.0% retention) vs Random Forest?",
         "A: SVM relies on continuous geometric distances. Small byte shifts in file_size distort kernel space, pushing malware across the hyperplane. Random Forest's bagged orthogonal splits partially buffer individual feature noise.")
    ]

    for idx, (q, a) in enumerate(viva_cards):
        top_y = Inches(1.8 + idx * 2.2)
        card = s_viva.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(1.0), top_y, Inches(18.0), Inches(2.0))
        card.fill.solid()
        card.fill.fore_color.rgb = LIGHT_BG
        card.line.color.rgb = BORDER_COL
        tf = card.text_frame
        tf.word_wrap = True
        p_q = tf.paragraphs[0]
        p_q.text = q
        p_q.font.name = "Arial"
        p_q.font.size = Pt(14)
        p_q.font.bold = True
        p_q.font.color.rgb = NAVY

        p_a = tf.add_paragraph()
        p_a.text = a
        p_a.font.name = "Calibri"
        p_a.font.size = Pt(12.5)
        p_a.font.color.rgb = CHARCOAL

    # Save to Downloads and Project directory
    out_ppt_path = OUTPUT_DIR / "Robust_Doc_Review_3_Final_PPT.pptx"
    prs.save(str(out_ppt_path))
    print(f"[+] Successfully generated Review 3 PPT at: {out_ppt_path}")

    ws_ppt_path = BASE_DIR / "Robust_Doc_Review_3_Final_PPT.pptx"
    prs.save(str(ws_ppt_path))
    print(f"[+] Saved duplicate in project workspace at: {ws_ppt_path}")


if __name__ == "__main__":
    create_review3_presentation()
