"""Feature Extractor module based on PDFRate / Mimicus feature sets."""

import math
import re
from pathlib import Path
from typing import Dict, Any, Union
import pikepdf
from src.config import FEATURE_NAMES


def calculate_entropy(data: bytes) -> float:
    """Calculates Shannon entropy of raw byte data (0.0 to 8.0)."""
    if not data:
        return 0.0
    entropy = 0.0
    length = len(data)
    counts = [0] * 256
    for b in data:
        counts[b] += 1
    for count in counts:
        if count > 0:
            p = count / length
            entropy -= p * math.log2(p)
    return float(entropy)


class PDFFeatureExtractor:
    """Extracts structural and statistical features inspired by PDFRate/Mimicus."""

    def __init__(self):
        self.feature_names = FEATURE_NAMES

    def extract_features(self, pdf_path: Union[str, Path]) -> Dict[str, float]:
        """Extract a structured dictionary of features from a PDF file."""
        pdf_path = Path(pdf_path)
        if not pdf_path.exists():
            raise FileNotFoundError(f"PDF file not found: {pdf_path}")

        raw_bytes = pdf_path.read_bytes()
        file_size = float(len(raw_bytes))
        byte_entropy = calculate_entropy(raw_bytes)

        # Baseline default features
        features: Dict[str, float] = {name: 0.0 for name in self.feature_names}
        features["file_size"] = file_size
        features["byte_entropy"] = byte_entropy

        # Regex-based scans on raw bytes as an auxiliary/fallback layer
        # (This mimics fast static triage tools and catches unparsed or raw markers)
        features["count_javascript"] = float(len(re.findall(rb"/JavaScript", raw_bytes)))
        features["count_js"] = float(len(re.findall(rb"/JS", raw_bytes)))
        features["count_openaction"] = float(len(re.findall(rb"/OpenAction", raw_bytes)))
        features["count_aa"] = float(len(re.findall(rb"/AA", raw_bytes)))
        features["count_acroform"] = float(len(re.findall(rb"/AcroForm", raw_bytes)))
        features["count_launch"] = float(len(re.findall(rb"/Launch", raw_bytes)))
        features["count_embedded_files"] = float(len(re.findall(rb"/EmbeddedFiles", raw_bytes)))
        features["count_annot"] = float(len(re.findall(rb"/Annot", raw_bytes)))
        features["count_uri"] = float(len(re.findall(rb"/URI", raw_bytes)))
        features["count_richmedia"] = float(len(re.findall(rb"/RichMedia", raw_bytes)))

        # Structural extraction via pikepdf
        try:
            with pikepdf.open(pdf_path) as pdf:
                # Number of pages
                try:
                    features["num_pages"] = float(len(pdf.pages))
                except Exception:
                    features["num_pages"] = 0.0

                # Indirect objects and streams
                num_objects = 0
                num_streams = 0
                num_compressed_streams = 0
                has_objstm = 0.0
                has_xref_stream = 0.0

                for obj in pdf.objects:
                    num_objects += 1
                    try:
                        if isinstance(obj, pikepdf.Stream):
                            num_streams += 1
                            if "/Filter" in obj:
                                num_compressed_streams += 1
                            if obj.get("/Type") == "/ObjStm":
                                has_objstm = 1.0
                            if obj.get("/Type") == "/XRef":
                                has_xref_stream = 1.0
                    except Exception:
                        continue

                features["num_objects"] = float(num_objects)
                features["num_indirect_objects"] = float(num_objects)
                features["num_streams"] = float(num_streams)
                features["num_compressed_streams"] = float(num_compressed_streams)
                features["ratio_compressed_streams"] = (
                    num_compressed_streams / num_streams if num_streams > 0 else 0.0
                )
                features["has_objstm"] = has_objstm
                features["has_xref_stream"] = has_xref_stream

                # Trailer inspection
                try:
                    features["num_trailer_entries"] = float(len(pdf.trailer))
                except Exception:
                    features["num_trailer_entries"] = 0.0

                # Document Information / Metadata inspection
                try:
                    doc_info = pdf.docinfo
                    meta_str = str(doc_info)
                    features["metadata_length"] = float(len(meta_str))
                    features["has_title"] = 1.0 if "/Title" in doc_info else 0.0
                    features["has_author"] = 1.0 if "/Author" in doc_info else 0.0
                    features["has_creator"] = 1.0 if "/Creator" in doc_info else 0.0
                    features["has_producer"] = 1.0 if "/Producer" in doc_info else 0.0
                    features["has_creation_date"] = 1.0 if "/CreationDate" in doc_info else 0.0
                    features["has_mod_date"] = 1.0 if "/ModDate" in doc_info else 0.0
                except Exception:
                    pass

        except Exception as e:
            # If parsing fails partially, features already contain raw regex heuristics
            pass

        return features

    def extract_feature_vector(self, pdf_path: Union[str, Path]) -> list:
        """Returns the features as an ordered numeric list matching FEATURE_NAMES."""
        feats = self.extract_features(pdf_path)
        return [feats[name] for name in self.feature_names]
