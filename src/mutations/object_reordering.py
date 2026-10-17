"""Mutation 3: Object Reordering and Linearization Restructuring."""

from pathlib import Path
from typing import Union
import pikepdf
from .base import BaseMutation


class ObjectReorderingMutation(BaseMutation):
    """Restructures PDF object order and cross-reference layouts.

    Simulates 'Fast Web View' linearization, xref restructuring, and indirect
    object table reorganizations that occur during web publication.
    """

    def __init__(self):
        super().__init__(name="object_reordering")

    def mutate(
        self,
        input_pdf_path: Union[str, Path],
        output_pdf_path: Union[str, Path],
        intensity: float = 1.0
    ) -> Path:
        input_pdf_path = Path(input_pdf_path)
        output_pdf_path = Path(output_pdf_path)
        output_pdf_path.parent.mkdir(parents=True, exist_ok=True)

        with pikepdf.open(input_pdf_path) as pdf:
            if intensity <= 0.3:
                # Mild intensity: simple clean resave with standard serialization
                pdf.save(output_pdf_path, linearize=False)
            elif intensity <= 0.7:
                # Medium intensity: Linearize the document (reorders objects for Fast Web View)
                try:
                    pdf.save(output_pdf_path, linearize=True)
                except Exception:
                    # Fallback to standard save if linearization is not supported on this structure
                    pdf.save(output_pdf_path, linearize=False)
            else:
                # High intensity: Linearize and reorder page resources or toggle object streams
                try:
                    pdf.save(
                        output_pdf_path,
                        linearize=True,
                        object_stream_mode=pikepdf.ObjectStreamMode.generate
                    )
                except Exception:
                    pdf.save(
                        output_pdf_path,
                        linearize=False,
                        object_stream_mode=pikepdf.ObjectStreamMode.disable
                    )

        return output_pdf_path
