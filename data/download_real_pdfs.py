"""Download 10 real-world Benign PDFs and 10 real Security/Exploit PoC PDFs from GitHub."""

import urllib.request
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
SAMPLES_DIR = BASE_DIR / "data" / "samples"
SAMPLES_DIR.mkdir(parents=True, exist_ok=True)

# 10 Real Benign PDFs from Mozilla PDF.js repository
BENIGN_URLS = [
    ("benign_real_01_160F.pdf", "https://raw.githubusercontent.com/mozilla/pdf.js/master/test/pdfs/160F-2019.pdf"),
    ("benign_real_02_90ms.pdf", "https://raw.githubusercontent.com/mozilla/pdf.js/master/test/pdfs/90ms_rksj_h_sample.pdf"),
    ("benign_real_03_arabic.pdf", "https://raw.githubusercontent.com/mozilla/pdf.js/master/test/pdfs/ArabicCIDTrueType.pdf"),
    ("benign_real_04_stream_cycle.pdf", "https://raw.githubusercontent.com/mozilla/pdf.js/master/test/pdfs/ContentStreamCycleType3insideType3.pdf"),
    ("benign_real_05_stream_nocycle.pdf", "https://raw.githubusercontent.com/mozilla/pdf.js/master/test/pdfs/ContentStreamNoCycleType3insideType3.pdf"),
    ("benign_real_06_embedded_font.pdf", "https://raw.githubusercontent.com/mozilla/pdf.js/master/test/pdfs/Embedded_font.pdf"),
    ("benign_real_07_ghostscript.pdf", "https://raw.githubusercontent.com/mozilla/pdf.js/master/test/pdfs/GHOSTSCRIPT-698804-1-fuzzed.pdf"),
    ("benign_real_08_unicode_map.pdf", "https://raw.githubusercontent.com/mozilla/pdf.js/master/test/pdfs/IdentityToUnicodeMap_charCodeOf.pdf"),
    ("benign_real_09_indexed_cs.pdf", "https://raw.githubusercontent.com/mozilla/pdf.js/master/test/pdfs/IndexedCS_negative_and_high.pdf"),
    ("benign_real_10_pdfbox.pdf", "https://raw.githubusercontent.com/mozilla/pdf.js/master/test/pdfs/PDFBOX-3148-2-fuzzed.pdf")
]

# 10 Real Security & Exploit PoC PDFs from published CVE and Pentest Research Repositories
MALICIOUS_POC_URLS = [
    ("malicious_real_01_cve2024_4367.pdf", "https://raw.githubusercontent.com/s4vvysec/CVE-2024-4367-POC/main/malicious.pdf"),
    ("malicious_real_02_cve2019_14811.pdf", "https://raw.githubusercontent.com/matejsmycka/CVE-2019-14811-in-pdf-exploit/main/exploit.pdf"),
    ("malicious_real_03_pentest_xss.pdf", "https://raw.githubusercontent.com/klausnitzer/pentest-pdf-collection/main/pdf_files/20250820_120401_xss_text.pdf"),
    ("malicious_real_04_pentest_js_annot.pdf", "https://raw.githubusercontent.com/klausnitzer/pentest-pdf-collection/main/pdf_files/20250820_120506_js_annot.pdf"),
    ("malicious_real_05_pentest_attach.pdf", "https://raw.githubusercontent.com/klausnitzer/pentest-pdf-collection/main/pdf_files/20250820_143923_attach_scripts.pdf"),
    ("malicious_real_06_cve2024_ex1.pdf", "https://raw.githubusercontent.com/weae26/cve-2024-4367-poc/main/ex1-fixed.pdf"),
    ("malicious_real_07_cve2024_final1.pdf", "https://raw.githubusercontent.com/weae26/cve-2024-4367-poc/main/final.pdf"),
    ("malicious_real_08_cve2024_final2.pdf", "https://raw.githubusercontent.com/weae26/cve-2024-4367-poc/main/final2.pdf"),
    ("malicious_real_09_cve2024_final3.pdf", "https://raw.githubusercontent.com/weae26/cve-2024-4367-poc/main/final3.pdf"),
    ("malicious_real_10_cve2024_final4.pdf", "https://raw.githubusercontent.com/weae26/cve-2024-4367-poc/main/final4.pdf")
]

HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}


def download_file(filename: str, url: str) -> bool:
    dest = SAMPLES_DIR / filename
    try:
        req = urllib.request.Request(url, headers=HEADERS)
        with urllib.request.urlopen(req, timeout=20) as resp:
            data = resp.read()
            if len(data) > 100:
                dest.write_bytes(data)
                print(f"[+] Downloaded {filename:<35} ({len(data)/1024:6.1f} KB)")
                return True
            else:
                print(f"[-] Empty or too small: {filename}")
                return False
    except Exception as e:
        print(f"[-] Failed to download {filename}: {e}")
        return False


def run_download():
    print("=" * 65)
    print(" DOWNLOADING REAL-WORLD BENIGN & SECURITY RESEARCH PDF SAMPLES ")
    print("=" * 65)

    print("\n--- 1. Downloading 10 Real Benign PDFs (from Mozilla pdf.js) ---")
    b_success = sum(download_file(name, url) for name, url in BENIGN_URLS)

    print("\n--- 2. Downloading 10 Real Exploit PoC PDFs (from CVE Research) ---")
    m_success = sum(download_file(name, url) for name, url in MALICIOUS_POC_URLS)

    print("\n" + "=" * 65)
    print(f"[SUMMARY] Successfully acquired:")
    print(f"  * Benign PDFs    : {b_success} / 10")
    print(f"  * Malicious PoCs : {m_success} / 10")
    print(f"  * Location       : {SAMPLES_DIR}")
    print("=" * 65)


if __name__ == "__main__":
    run_download()
