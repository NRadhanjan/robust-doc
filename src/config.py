"""Configuration and constants for the PDF Feature Robustness Study."""

from pathlib import Path

# Paths
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
SAMPLES_DIR = DATA_DIR / "samples"
MUTATIONS_DIR = DATA_DIR / "generated_mutations"
MODELS_DIR = BASE_DIR / "models_saved"
REPORTS_DIR = BASE_DIR / "reports"

for dir_path in [SAMPLES_DIR, MUTATIONS_DIR, MODELS_DIR, REPORTS_DIR]:
    dir_path.mkdir(parents=True, exist_ok=True)

# PDFRate / Mimicus inspired feature schema
FEATURE_NAMES = [
    # General document structural features
    "file_size",
    "byte_entropy",
    "num_pages",
    "num_objects",
    "num_streams",
    "num_compressed_streams",
    "ratio_compressed_streams",
    
    # Suspicious structural elements & triggers
    "count_javascript",
    "count_js",
    "count_openaction",
    "count_aa",  # Additional Actions
    "count_acroform",
    "count_launch",
    "count_embedded_files",
    "count_annot",
    "count_uri",
    "count_richmedia",
    
    # Object structure & relationships
    "num_indirect_objects",
    "num_trailer_entries",
    "has_xref_stream",
    "has_objstm",  # Object stream presence
    
    # Metadata features (traditionally fragile)
    "metadata_length",
    "has_title",
    "has_author",
    "has_creator",
    "has_producer",
    "has_creation_date",
    "has_mod_date"
]

# Baseline Model Path
BASELINE_MODEL_PATH = MODELS_DIR / "baseline_random_forest.joblib"
