"""Mutation 1: Metadata Perturbation (Non-adversarial)."""

import datetime
from pathlib import Path
from typing import Union
import pikepdf
from .base import BaseMutation


class MetadataMutation(BaseMutation):
    """Perturbs or updates document metadata (Author, Producer, Creation/Mod Dates).

    Simulates routine document management actions (e.g. Adobe Acrobat re-saving,
    metadata scrubbing, or enterprise export pipelines).
    """

    def __init__(self):
        super().__init__(name="metadata_mutation")

    def mutate(
        self,
        input_pdf_path: Union[str, Path],
        output_pdf_path: Union[str, Path],
        intensity: float = 1.0
    ) -> Path:
        input_pdf_path = Path(input_pdf_path)
        output_pdf_path = Path(output_pdf_path)
        output_pdf_path.parent.mkdir(parents=True, exist_ok=True)

        now_str = datetime.datetime.now().strftime("D:%Y%m%d%H%M%S")

        with pikepdf.open(input_pdf_path) as pdf:
            docinfo = pdf.docinfo

            if intensity <= 0.3:
                # Mild intensity: update ModDate and touch Producer
                docinfo["/ModDate"] = now_str
                docinfo["/Producer"] = "Standard PDF Printer v10.4"
            elif intensity <= 0.7:
                # Moderate intensity: rewrite author, creator, dates
                docinfo["/Author"] = "Department of Administration"
                docinfo["/Title"] = "Quarterly Operational Summary"
                docinfo["/Creator"] = "Microsoft Word for Office 365"
                docinfo["/Producer"] = "macOS Version 14.2 Quartz PDFContext"
                docinfo["/CreationDate"] = now_str
                docinfo["/ModDate"] = now_str
            else:
                # Severe intensity: completely scrub or sanitize non-essential info dict
                keys_to_clear = list(docinfo.keys())
                for k in keys_to_clear:
                    del docinfo[k]
                # Keep bare minimal standard fields to look like an anonymized export
                docinfo["/Producer"] = "Acrobat Distiller 21.0"
                docinfo["/CreationDate"] = now_str

            pdf.save(output_pdf_path)

        return output_pdf_path
