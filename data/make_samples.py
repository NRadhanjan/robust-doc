"""Synthetic and representative sample PDF generator for full 100-sample benchmark dataset."""

from pathlib import Path
import pikepdf
from src.config import SAMPLES_DIR


def create_benign_pdf(filepath: Path, index: int = 1):
    """Generates a clean standard PDF document with realistic variation."""
    pdf = pikepdf.new()
    num_pages = (index % 5) + 1
    for p in range(num_pages):
        pdf.add_blank_page(page_size=(595.276, 841.890))  # A4

    # Varied benign metadata
    titles = ["Annual Financial Audit", "Quarterly Academic Review", "Technical Specifications", "Operational Protocol", "User Manual"]
    authors = ["Dr. H. Vance", "Corporate Compliance Board", "Systems Architecture Group", "Alice Smith", "Prof. K. Davies"]
    producers = ["ReportGen PDF Suite 2.0", "Adobe Acrobat Pro 2023", "LibreOffice 7.5", "Quartz PDFContext", "PDFlib 9.3"]

    t = titles[index % len(titles)]
    a = authors[index % len(authors)]
    prod = producers[index % len(producers)]

    with pdf.open_metadata() as meta:
        meta["dc:title"] = f"{t} - Part {index}"
        meta["dc:creator"] = [a]

    pdf.docinfo["/Title"] = f"{t} - Part {index}"
    pdf.docinfo["/Author"] = a
    pdf.docinfo["/Producer"] = prod
    pdf.docinfo["/CreationDate"] = f"D:2025{index%12 + 1:02d}01120000"

    # Some benign files have annotations or forms
    if index % 3 == 0:
        pdf.Root.AcroForm = pikepdf.Dictionary(
            Fields=pikepdf.Array(),
            NeedAppearances=pikepdf.Boolean(False)
        )

    pdf.save(filepath)


def create_malicious_pdf(filepath: Path, index: int = 1):
    """Generates structurally suspicious PDFs with varied real execution vectors."""
    pdf = pikepdf.new()
    pdf.add_blank_page(page_size=(595.276, 841.890))

    mode = index % 5

    if mode == 0:
        # Standard JavaScript OpenAction
        js_code = "app.alert({cMsg: 'Exploit Triggered: Security Alert', nIcon: 1});"
        js_stream = pdf.make_stream(js_code.encode("utf-8"))
        js_action = pikepdf.Dictionary(
            Type=pikepdf.Name("/Action"),
            S=pikepdf.Name("/JavaScript"),
            JS=js_stream
        )
        pdf.Root.OpenAction = js_action

    elif mode == 1:
        # Launch Action trigger (cmd/powershell/calc simulation)
        launch_action = pikepdf.Dictionary(
            Type=pikepdf.Name("/Action"),
            S=pikepdf.Name("/Launch"),
            F=pikepdf.String("calc.exe")
        )
        pdf.Root.OpenAction = launch_action

    elif mode == 2:
        # Additional Actions (/AA) on document open
        js_code = "this.exportDataObject({cName: 'payload.exe', nLaunch: 1});"
        js_stream = pdf.make_stream(js_code.encode("utf-8"))
        aa_dict = pikepdf.Dictionary(
            O=pikepdf.Dictionary(
                Type=pikepdf.Name("/Action"),
                S=pikepdf.Name("/JavaScript"),
                JS=js_stream
            )
        )
        pdf.Root.AA = aa_dict

    elif mode == 3:
        # Embedded Files + Names/JavaScript tree trigger
        dummy_bin = b"MZ\x90\x00\x03\x00\x00\x00\x04\x00\x00\x00\xff\xff\x00\x00"
        bin_stream = pdf.make_stream(dummy_bin)
        ef_dict = pikepdf.Dictionary(F=bin_stream)
        file_spec = pikepdf.Dictionary(
            Type=pikepdf.Name("/Filespec"),
            F=pikepdf.String("dropper.bin"),
            EF=ef_dict
        )
        names_dict = pikepdf.Dictionary(
            EmbeddedFiles=pikepdf.Dictionary(
                Names=pikepdf.Array([pikepdf.String("drop"), file_spec])
            )
        )
        pdf.Root.Names = names_dict

        # OpenAction executing JavaScript
        js_code = "var f = this.getDataObjectContents('drop');"
        js_stream = pdf.make_stream(js_code.encode("utf-8"))
        pdf.Root.OpenAction = pikepdf.Dictionary(
            Type=pikepdf.Name("/Action"),
            S=pikepdf.Name("/JavaScript"),
            JS=js_stream
        )

    elif mode == 4:
        # Combined JavaScript with URI redirection and AcroForm action
        js_code = "app.launchURL('http://malicious-c2-server.com/beacon', true);"
        js_stream = pdf.make_stream(js_code.encode("utf-8"))
        pdf.Root.OpenAction = pikepdf.Dictionary(
            Type=pikepdf.Name("/Action"),
            S=pikepdf.Name("/JavaScript"),
            JS=js_stream
        )
        pdf.Root.AcroForm = pikepdf.Dictionary(
            Fields=pikepdf.Array(),
            NeedAppearances=pikepdf.Boolean(True)
        )

    # Malicious/exploit kit metadata patterns
    kit_names = [
        "PDF-Generator-ExploitKit-v3",
        "NeutrinoPDF-Builder",
        "AnglerEK-Packer",
        "BlackholePDF-Engine",
        "MetasploitPDF-Dropper"
    ]
    pdf.docinfo["/Producer"] = kit_names[index % len(kit_names)]
    pdf.docinfo["/CreationDate"] = "D:20200101000000"

    pdf.save(filepath)


def generate_full_benchmark_samples():
    """Generates 40 benign and 40 malicious synthetic samples (80 total).
    Together with the 20 real downloaded samples, this gives exactly 100 PDF samples.
    """
    SAMPLES_DIR.mkdir(parents=True, exist_ok=True)
    
    print("[*] Generating 40 synthetic benign samples...")
    for i in range(1, 41):
        create_benign_pdf(SAMPLES_DIR / f"benign_sample_{i:02d}.pdf", index=i)

    print("[*] Generating 40 synthetic malicious samples...")
    for i in range(1, 41):
        create_malicious_pdf(SAMPLES_DIR / f"malicious_sample_{i:02d}.pdf", index=i)

    print(f"[+] 80 synthetic samples ready in {SAMPLES_DIR}")


if __name__ == "__main__":
    generate_full_benchmark_samples()
